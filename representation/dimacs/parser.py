from .dimacs_cnf import DimacsCNF
from .clause import Clause

def parse(path: str) -> DimacsCNF:
    """
    Returns the Dimacs CNF obtained by parsing the given file.

    :param path: the file path
    :return: the CNF represented in the file
    """
    clauses = list()
    n_vars = -1
    for line in open(path):
        line = line.strip()
        if line[0] == 'c':
            continue
        if line[0] == 'p':
            tokens = line.split(' ')
            if n_vars == -1:
                n_vars = int(tokens[2])
            else:
                raise IOError("Invalid file format. Multiple lines start with p")
        else:
            tokens = line.split(' ')
            clause = Clause(
                literals=[int(t) for t in tokens[:-1]]
            )
            clauses.append(clause)

    return DimacsCNF(
        clauses,
        n_vars=n_vars
    )