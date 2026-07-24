# MSE802 Assessment 2 — Peer Review Guide

Please review the submitted work against the assessment brief, focusing first
on correctness and evidence. The notebooks are already executed; no remote
Quokka request is needed.

## Suggested review order

1. Read each notebook's introduction, circuit explanation, results,
   interpretation, conclusion, and references.
2. Review the Task 3 and Task 4 Word reports for completeness and readability.
3. Use the evidence files to spot-check that written claims match captured
   results.
4. Record only actionable feedback: file/section, issue, and proposed change.

## Task-specific questions

### Task 1 — Entanglement

- Does the notebook correctly explain how H followed by CNOT prepares
  $(|00\rangle+|11\rangle)/\sqrt{2}$?
- Do local and Quokka results contain only correlated `00` and `11` outcomes?
- Are finite-shot differences interpreted without claiming exact 50/50 counts?
- Can you trace the Quokka claim to the QASM, raw response, timestamp and
  histogram?

Expected cross-check: local counts are `00=527, 11=497`; Quokka counts are
`00=504, 11=520`, each from 1,024 shots.

### Task 2 — Qiskit and OpenQASM

- Does the specified circuit match the assessment diagram and state the chosen
  interpretation of its controlled gate?
- Does the original circuit use multiple qubits and gate types and remain valid
  OpenQASM 2?
- Are Qiskit bit ordering and both backend results explained clearly?
- Is the large original-circuit Aer/Quokka difference reported as an observed
  discrepancy rather than assigned an unproven cause?

Expected cross-check for the specified circuit: Aer gives `01=524, 10=500`;
Quokka gives `01=494, 10=530`.

### Task 3 — Quantum Tic-Tac-Toe

- Do O, X, Not and SWAP change the actual circuit state as documented?
- Are all eight winning triples, bit-order reversal, scoring and replay
  implemented correctly?
- Does the local widget support the complete move/measure/replay flow?
- Do the four saved games demonstrate direct rotations, Not, SWAP and an open
  random board?
- Does the Word report document functionality, circuit generation, gates,
  evidence and limitations?

Expected cross-check: four seeded game records and four matching QASM circuits
are present; the open-board result is described as one reproducible sample, not
as a deterministic strategy.

### Task 4 — Quantum machine learning

- Is the four-image classification problem and exact pixel-to-qubit input
  location unambiguous?
- Is the recursive RY–RY–CX model, six-parameter count and one-qubit readout
  explained correctly?
- Are optimization MAE, elapsed time, circuit count and shot count retained?
- Is the classical baseline genuinely free of QASM, circuits and shots?
- Are effectiveness, efficiency and tiny-dataset limitations compared fairly?

Expected cross-check: the quantum optimization uses 543 circuits and 139,008
shots. Both models classify all four supplied points correctly; full-dataset
MAE is 0.2754 for the quantum model and 0.0246 for the classical model. The
submission explicitly makes no quantum-advantage claim.

## Global checks

- Four distinct task folders and all primary deliverables are present.
- Notebook headings, figures, equations, conclusions and references are clear.
- Saved evidence agrees with the narrative and no result appears fabricated.
- Task 3 and Task 4 reports open cleanly and have no clipped or blank pages.
- No student-name placeholder, local absolute path, credential, course source,
  virtual environment or notebook checkpoint appears in the folder.

Automated checks are summarized in `SUBMISSION_AUDIT.json` and
`PRIVACY_AUDIT.json`. Human review should concentrate on conceptual accuracy,
clarity, and whether any assessment instruction has been interpreted
differently from the marker's likely expectation.
