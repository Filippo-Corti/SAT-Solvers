# SAT Solving, DPLL and CDCL

Boolean satisfiability (SAT) is the problem of determining whether there exists an assignment of truth values to 
variables that makes a propositional logic formula true.
SAT is a central problem in computer science, with applications in automated reasoning, verification, planning, 
optimization, and artificial intelligence. 

This repository contains a minimal pipeline for solving 
logical consequence problems using propositional SAT solving. 
A logical consequence problem asks whether a theory $\Gamma$ models a formula $A$:

$$
\begin{aligned}
\Gamma \vDash A
\end{aligned}
$$

This typically reduces to checking the **unsatisfiability** of the formula:

$$
\begin{aligned}
F = \Gamma_1 \wedge \Gamma_2 \wedge ... \wedge \Gamma_N \wedge \lnot A
\end{aligned}
$$

The repository includes formula parsing, preprocessing to an equisatisfiable conjunctive normal form (CNF), and a couple of SAT solvers.

### DPLL

DPLL (Davis–Putnam–Logemann–Loveland) is a classic backtracking-based algorithm for SAT. 
It improves brute force search using unit propagation and pure literal elimination, allowing exponential reductions in search space.

### CDCL

CDCL (Conflict-Driven Clause Learning) extends DPLL with modern enhancements such as clause learning, backjumping, 
and more advanced heuristics, making it the foundation of today's state-of-the-art SAT solvers.


## Contents of the Repository:

Source code:

* `examples/` contains datasets and benchmark CNF instances used to test the solvers;
* `representation/` contains the logic for parsing propositional formulas into Abstract Syntax Trees (ASTs) 
and generating DIMACS CNF representations;
* `preprocessing/` implements the transformation from a logical consequence problem into:
  * **IFNF** (Implication Free Normal Form);
  * **NNF** (Negation Normal Form);
  * *Equisatisfiable* **CNF**, suitable for SAT solving;
* `sat_solvers/` implements three solvers:
  * A **Brute-Force Solver**, used as ground-truth for small problems;
  * A **DPLL Solver**;
  * A **CDCL Solver**.

Additional files:

* [`example.ipynb`](example.ipynb) - Notebook demostrating the full pipeline, using CDCL;
* [`test_cnfs.py`](test_cnfs.py) - File to test the solvers using some of the CNF-SAT benchmarks; 
* [`test_theories.py`](test_theories.py) - File to test the solvers on some instances of logical consequence problems.


## References:

DIMACS CNF Format:
https://jix.github.io/varisat/manual/0.2.0/formats/dimacs.html

DPLL, CDCL:
https://users.aalto.fi/~tjunttil/2020-DP-AUT/notes-sat/cdcl.html

Benchmark Problems for SAT:
https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html