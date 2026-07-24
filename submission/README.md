# MSE802 Assessment 2 — Final Submission Folder

This directory is the complete peer-review and upload set for all four
assessment tasks. The notebooks already contain executed outputs. Reviewers can
inspect every result without a Quokka account or another remote run.

## Team

- **Weilai Wang**
- **Xiaotong Sun**

This is a shared team submission. Both members participated in all four tasks;
see [team_contribution.md](team_contribution.md) for the contribution record.

Shared repository:
[miku-wwl/802-Quantum-Computing](https://github.com/miku-wwl/802-Quantum-Computing)

## Primary deliverables

| Task | Main file(s) | Supporting evidence |
|---|---|---|
| 1 — Entanglement | `Task_1_Entanglement/Task_1_Entanglement.ipynb` | Bell-state QASM, local/Quokka histograms, raw response and timestamped metadata |
| 2 — Qiskit circuits | `Task_2_Qiskit/Task_2_Qiskit.ipynb` | specified and original circuits, standard/Quokka QASM, local figures, two raw responses and metadata |
| 3 — Quantum Tic-Tac-Toe | `Task_3_Quantum_Tic_Tac_Toe/Task_3_Quantum_Tic_Tac_Toe.ipynb` and `Task_3_Quantum_Tic_Tac_Toe/Task_3_Quantum_Tic_Tac_Toe_Report.docx` | four game circuits, four diagrams, seeded JSON evidence and visual summary |
| 4 — Quantum ML | `Task_4_Quantum_ML/Task_4_Quantum_ML.ipynb` and `Task_4_Quantum_ML/Task_4_Quantum_ML_Report.docx` | backend validation, optimization trace, classical baseline, benchmark tables and figures |

`SUBMISSION_AUDIT.json` records the automated deliverable checks.
`PRIVACY_AUDIT.json` records the credential/local-path scan. Start a human
review with `PEER_REVIEW_GUIDE.md`.

## Review and execution

For a fast review, open the executed notebooks and Word reports directly.
Do not regenerate the captured Quokka files: they are retained evidence from
the submitted remote runs.

For a full local verification from the repository root:

```powershell
uv sync --frozen
uv run python scripts/verify_environment.py
uv run pytest
uv run python scripts/audit_submission.py
uv run python scripts/check_submission_privacy.py
```

The final ZIP and SHA-256 manifest are generated outside this directory at the
last packaging milestone, so the upload folder contains no build cache,
virtual environment, course-source directory, or credentials.
