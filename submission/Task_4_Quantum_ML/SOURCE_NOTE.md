# Task 4 source and adaptation note

The starting point was the course-supplied notebook:

`Week-12/AS2_Files/AS2_Files/Quantum_ML_AS2.ipynb`

The course-material directory is intentionally excluded from Git. The
submitted notebook is generated from `scripts/build_task4_notebook.py`.

The local adaptation:

- removes the unused Google Colab file-upload import;
- replaces the hard-coded HTTP endpoint with project configuration;
- replaces global random calls with explicit seeded generators;
- separates dataset, circuit, backend, optimization, and benchmark logic into
  testable project code; and
- retains the starter's 2×2 non-uniform bar/stripe dataset and recursive model
  concept.
