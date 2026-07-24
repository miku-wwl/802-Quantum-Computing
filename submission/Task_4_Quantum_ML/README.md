# Task 4 — Quantum Machine Learning

## Primary deliverables

- `Task_4_Quantum_ML.ipynb` — executed analysis notebook.
- `Task_4_Quantum_ML_Report.docx` — comprehensive report.
- `task4_quantum_classical_benchmark.json` — complete comparison protocol and results.
- `task4_quantum_classical_comparison.png` — effectiveness/efficiency summary.

## Reproducibility

From the repository root:

```powershell
uv sync --frozen
uv run python scripts/generate_task4_circuit_evidence.py
uv run python scripts/generate_task4_optimization_evidence.py
uv run python scripts/generate_task4_classical_evidence.py
uv run python scripts/generate_task4_benchmark.py
uv run python scripts/build_task4_notebook.py
uv run jupyter nbconvert --to notebook --execute `
  submission/Task_4_Quantum_ML/Task_4_Quantum_ML.ipynb `
  --inplace --ExecutePreprocessor.timeout=180
```

`task4_backend_validation.json` is retained from a real Quokka run and should
not be regenerated unless remote access is intentionally being revalidated.
All training and benchmark commands above run locally. Seeds, split indices,
shots, model parameters, raw traces, resource counts, and timing protocol are
retained beside the notebook.

## Interpretation boundary

The dataset contains four generated images and the test partition contains one
sample. Both implementations classify all four supplied items correctly. This
is a pipeline demonstration, not evidence of generalisation or quantum
advantage.
