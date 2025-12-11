# SAT Solvers



### TODO:

- [X] Parser from a String format to an AST (Abstract Syntax Tree)
- [X] Conversion from AST to CNF AST
- [X] CNF AST to CNF DIMACS
- [X] Implement DPLL algorithm
- [X] Implement CDCL algorithm

- [ ] Refine CDCL with VSIDS and other improvements
- [ ] Test DPLL and CDCL using an external solver and known datasets + generated data
- [ ] Test the preprocessing pipeline using bruteforcing

### Times:

**DPLL**: Can only solve 50- instances and some lucky 100-  
**CDCL (from DPLL)**: 5.5s   
**CDCL with VSIDS instad of DLIS**: 0.45s


### References:

DIMACS CNF Format:   
https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html

DPLL, CDCL:
https://users.aalto.fi/~tjunttil/2020-DP-AUT/notes-sat/cdcl.html