# MSE802 Assessment 2 - 30 Commit Delivery Plan

All work is performed on the `task` branch. Every numbered milestone must:

1. produce one coherent, reviewable change;
2. pass the checks relevant to that change;
3. be committed with the `A2-XX` prefix; and
4. be pushed immediately to `origin/task`.

## Foundation

1. Create this delivery plan, rubric matrix, and final submission structure.
2. Add shared configuration, a safe Quokka REST client, local backends, and tests.

## Task 1 - Entanglement Demonstrations

3. Create the Task 1 notebook structure, theory, and citation framework.
4. Implement and validate the Cirq Bell-state local simulation and plots.
5. Add Cirq-to-OpenQASM conversion, execute on Quokka, and retain raw evidence.
6. Complete Task 1 analysis, reproducibility checks, and rubric self-review.

## Task 2 - Qiskit Circuits

7. Create the Task 2 notebook and implement the specified Qiskit circuit.
8. Export OpenQASM, validate with Aer, and explain measurement results.
9. Design and implement an original multi-qubit, multi-gate QASM circuit.
10. Execute both Task 2 circuits on Quokka and retain raw evidence.
11. Add circuit diagrams, histograms, endianness notes, and interpretation.
12. Complete Task 2 reproducibility checks and rubric self-review.

## Task 3 - Investigate a Quantum Code

13. Copy the supplied starter notebook and remove Colab-only imports.
14. Implement the Not, O, X, and SWAP quantum operations.
15. Implement eight win conditions, reset behavior, and measurement state handling.
16. Replace the Colab grid with native local `ipywidgets`.
17. Add automated tests and deterministic gameplay scenarios.
18. Run multiple games and retain circuit/result evidence.
19. Create, render, inspect, and finalize the Task 3 Word report.

## Task 4 - Machine Learning Quantum Analysis

20. Copy the supplied starter and localize it with a deterministic data split.
21. Refactor and explain data encoding, parameterized blocks, and circuit inputs.
22. Add switchable Quokka and local Aer quantum execution backends.
23. Record per-iteration metric/time data and create both required plots.
24. Add a fully classical baseline with no quantum circuit.
25. Benchmark quantum and classical efficiency/effectiveness and retain results.
26. Create, render, inspect, and finalize the Task 4 Word report.

## Submission

27. Normalize citations, captions, metadata, and references across deliverables.
28. Execute every notebook from a clean kernel and complete the rubric matrix.
29. Finalize the submission folder and peer-review guide; scan for secrets/privacy.
30. Build the final ZIP, manifest, and checksums; run final verification and push.

## Submission Layout

```text
submission/
  README.md
  Task_1_Entanglement/
  Task_2_Qiskit/
  Task_3_Quantum_Tic_Tac_Toe/
  Task_4_Quantum_ML/
```

Only files required for assessment review and submission belong under
`submission/`. Source utilities, tests, generated QA images, virtual
environments, local credentials, and course materials remain outside it.
