# Task 3 source and adaptation note

The starting point was the course-supplied notebook:

`Week-12/AS2_Files/AS2_Files/Quantum_Tic_Tac_Toe__AS2.ipynb`

The course-material directory is intentionally excluded from Git. The
submitted notebook is generated from `scripts/build_task3_notebook.py` so its
structure is reviewable and reproducible.

The adaptation preserves the starter's nine-qubit board and gate-based move
model. It replaces:

- notebook-level `pip install` commands with the repository's locked `uv`
  environment;
- wildcard imports with explicit imports;
- `google.colab.widgets.Grid` with portable `ipywidgets`;
- notebook-only game classes with an importable, automatically tested module.

The missing gate operations, winning triples, interaction flow, tests, and
evidence are completed in subsequent assessment milestones.
