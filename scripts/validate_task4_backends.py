"""Compare one fixed Task 4 model on exact, Aer, and real Quokka backends."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission" / "Task_4_Quantum_ML"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mse802 import AssessmentConfig, QuokkaClient
from mse802.quantum_ml import (
    execute_quantum_classifier,
    generate_bar_stripe_data,
)


def main() -> None:
    data = generate_bar_stripe_data()
    angles = np.array([0.2, -0.4, 0.6, 0.8, -0.3, 0.5])
    shots = 256
    config = AssessmentConfig.from_env()
    client = QuokkaClient(config)
    records: list[dict[str, object]] = []

    for index, (sample, label, name) in enumerate(
        zip(data.features, data.labels, data.names, strict=True)
    ):
        exact = execute_quantum_classifier(sample, angles, backend="exact")
        aer = execute_quantum_classifier(
            sample,
            angles,
            backend="aer",
            shots=shots,
            seed=config.seed + index,
        )
        quokka = execute_quantum_classifier(
            sample,
            angles,
            backend="quokka",
            shots=shots,
            quokka_client=client,
        )
        records.append(
            {
                "sample_index": index,
                "sample_name": name,
                "pixels": sample.tolist(),
                "label": int(label),
                "exact_probability_one": exact.probability_one,
                "aer": {
                    "probability_one": aer.probability_one,
                    "counts": aer.counts,
                    "seed": config.seed + index,
                },
                "quokka": {
                    "probability_one": quokka.probability_one,
                    "counts": quokka.counts,
                    "raw_payload": quokka.raw_payload,
                },
                "absolute_aer_quokka_difference": abs(
                    aer.probability_one - quokka.probability_one
                ),
                "quokka_qasm": quokka.qasm,
            }
        )
        print(
            name,
            f"exact={exact.probability_one:.4f}",
            f"aer={aer.probability_one:.4f}",
            f"quokka={quokka.probability_one:.4f}",
        )

    evidence = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": config.quokka_qasm_url,
        "shots_per_sample": shots,
        "angles": angles.tolist(),
        "purpose": "fixed-parameter backend validation; not optimizer training",
        "records": records,
    }
    (OUTPUT / "task4_backend_validation.json").write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
