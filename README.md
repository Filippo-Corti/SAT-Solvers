# SAT Solvers



### TODO:

- [X] Parser from a String format to an AST (Abstract Syntax Tree)
- [X] Conversion from AST to CNF AST
- [X] CNF AST to CNF DIMACS
- [X] Implement DPLL algorithm
- [X] Implement CDCL algorithm

- [X] Refine CDCL with VSIDS and other improvements
- [X] Add a way to configure CDCL simply
- [X] Test DPLL and CDCL using known datasets

- [ ] Build a utility class that handles theories and formulas directly (from a file)
- [ ] Make a python notebook that shows how the solver can be used
- [ ] Fix DPLL, copying from CDCL
- [ ] Build a bruteforce solver
- [ ] Test the preprocessing pipeline using bruteforcing
- [ ] Clean up README and we should be done

### Times on the AIM dataset:

- **DPLL**: Can only solve 50- instances and some lucky 100-
- **CDCL (from DPLL)**: 5.5s
- **CDCL with VSIDS instad of DLIS**: 0.45s
- **CDCL with VSIDS instad of DLIS (+ restarts)**: 0.45s


### Times on the UF250 dataset:

- **CDCL with VSIDS instad of DLIS (+ restarts)**: 
  - Runs uf250-01 (SAT) in 30s
  - Runs uf250-02 (SAT) in 33s
  - Runs uf250-010 (SAT) in 1m35s
  - Half of uf150 + half of uuf150: 5m52s

- **CDCL with VSIDS instad of DLIS (+ restarts + forgetting)**: 
  - Runs uf250-01 (SAT) in 3s
  - Runs uf250-02 (SAT) in 12m41s
  - Runs uf250-010 (SAT) in 45s
  - Half of uf150 + half of uuf150: 4m48s

### References:

DIMACS CNF Format:   
https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html

DPLL, CDCL:
https://users.aalto.fi/~tjunttil/2020-DP-AUT/notes-sat/cdcl.html

Benchmark for SAT Problems:
https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html