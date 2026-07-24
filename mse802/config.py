"""Environment-backed configuration used by assessment notebooks."""

from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class AssessmentConfig:
    """Runtime settings with safe, reproducible defaults."""

    quokka_base_url: str
    quokka_qasm_path: str
    shots: int
    seed: int
    request_timeout_seconds: float

    @property
    def quokka_qasm_url(self) -> str:
        base = self.quokka_base_url.rstrip("/")
        path = "/" + self.quokka_qasm_path.lstrip("/")
        return base + path

    @classmethod
    def from_env(cls) -> "AssessmentConfig":
        load_dotenv()
        return cls(
            quokka_base_url=os.getenv(
                "QUOKKA_BASE_URL", "https://quokka1.quokkacomputing.com"
            ),
            quokka_qasm_path=os.getenv("QUOKKA_QASM_PATH", "/qsim/qasm"),
            shots=int(os.getenv("MSE802_SHOTS", "1024")),
            seed=int(os.getenv("MSE802_SEED", "802")),
            request_timeout_seconds=float(
                os.getenv("QUOKKA_TIMEOUT_SECONDS", "30")
            ),
        )
