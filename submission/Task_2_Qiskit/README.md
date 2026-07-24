# Task 2 — Qiskit and OpenQASM

## Primary deliverable

Open `Task_2_Qiskit.ipynb` and run all cells from top to bottom. The notebook:

1. constructs the specified two-qubit circuit in Qiskit;
2. exports and validates standard OpenQASM 2;
3. executes the circuit locally with Aer and remotely with Quokka;
4. defines an original three-qubit OpenQASM circuit;
5. executes and compares that circuit on both backends; and
6. explains Qiskit's `q[n-1] ... q[0]` display order and the observed backend difference.

## Environment and execution

From the repository root:

```powershell
uv sync --extra dev
uv run jupyter nbconvert --to notebook --execute --inplace `
  submission/Task_2_Qiskit/Task_2_Qiskit.ipynb `
  --ExecutePreprocessor.timeout=240
```

Remote execution also requires a local `.env` containing `QUOKKA_ENDPOINT`; no
credential or private configuration is included in this folder. Existing raw
responses allow the submitted evidence to be reviewed without repeating the
remote calls.

## Evidence map

| Evidence | File |
|---|---|
| Executed analysis | `Task_2_Qiskit.ipynb` |
| Specified circuit diagram | `task2_specified_circuit.png` |
| Specified local distribution | `task2_specified_local_histogram.png` |
| Specified standard / Quokka QASM | `task2_specified_standard.qasm`, `task2_specified_quokka.qasm` |
| Specified remote evidence | `task2_specified_quokka_raw.json`, `task2_specified_quokka_metadata.json` |
| Original circuit diagram | `task2_custom_circuit.png` |
| Original local distribution | `task2_custom_local_histogram.png` |
| Original standard / Quokka QASM | `task2_custom_standard.qasm`, `task2_custom_quokka.qasm` |
| Original remote evidence | `task2_custom_quokka_raw.json`, `task2_custom_quokka_metadata.json` |
| Backend comparison | `task2_aer_quokka_comparison.png` |

## Review note

The assessment diagram labels its controlled block with `C`, rather than a
standard controlled-X symbol. This submission interprets it as CNOT/CX with
`q[0]` as control and `q[1]` as target, and states that interpretation explicitly
in the notebook. The original circuit's large Aer/Quokka probability difference
is retained and analysed honestly; a backend convention difference is a
testable hypothesis, not asserted as a proven cause.
