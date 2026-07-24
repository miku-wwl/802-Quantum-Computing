"""Small, testable client for the Quokka OpenQASM 2 REST endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from .config import AssessmentConfig


class QuokkaError(RuntimeError):
    """Raised when a Quokka request or response is invalid."""


@dataclass
class QuokkaClient:
    config: AssessmentConfig
    session: requests.Session | None = None

    def submit_qasm(self, qasm: str, shots: int | None = None) -> dict[str, Any]:
        """Submit OpenQASM 2 and return the validated JSON response."""

        if "OPENQASM 2.0;" not in qasm:
            raise ValueError("Quokka submissions must contain OPENQASM 2.0.")

        effective_shots = shots if shots is not None else self.config.shots
        if effective_shots <= 0:
            raise ValueError("shots must be positive")

        http = self.session or requests.Session()
        try:
            response = http.post(
                self.config.quokka_qasm_url,
                json={"script": qasm, "count": effective_shots},
                timeout=self.config.request_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise QuokkaError(f"Quokka request failed: {exc}") from exc

        self._validate_payload(payload)
        return payload

    @staticmethod
    def _validate_payload(payload: Any) -> None:
        if not isinstance(payload, dict):
            raise QuokkaError("Quokka response must be a JSON object")
        result = payload.get("result")
        if not isinstance(result, dict) or not result:
            raise QuokkaError("Quokka response has no non-empty 'result' object")
        if not all(isinstance(values, list) for values in result.values()):
            raise QuokkaError("Each Quokka classical register must contain a list")

    @staticmethod
    def register_values(payload: dict[str, Any], register: str) -> list[int]:
        """Return one classical register as normalized integer bits.

        The current Quokka endpoint represents a one-bit register as
        ``[[0], [1], ...]`` while older course examples show ``[0, 1, ...]``.
        Both documented shapes are accepted.
        """

        QuokkaClient._validate_payload(payload)
        result = payload["result"]
        if register not in result:
            raise QuokkaError(f"Classical register {register!r} is absent")
        raw_values = result[register]
        values = [
            value[0] if isinstance(value, list) and len(value) == 1 else value
            for value in raw_values
        ]
        if any(value not in (0, 1, False, True) for value in values):
            raise QuokkaError(f"Register {register!r} contains non-binary values")
        return [int(value) for value in values]
