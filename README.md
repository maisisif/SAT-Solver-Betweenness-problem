# **Betweenness SAT Solver**

This project builds a solver for the Betweenness problem by reducing it to the Boolean Satisfiability Problem (SAT). The main logic is written in Python and encodes the input problem into CNF (Conjunctive Normal Form) before using the Glucose 4.2 SAT solver to get a solution.

The Glucose binary is not included in the repository, it has to be compiled from the [source](https://github.com/audemard/glucose/releases/tag/4.2.1) and the resulting `glucose-simp` copied into the project folder as `glucose`:
```text
cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5 .
make
```



## Problem description

Given a set of elements $\{1, \dots, n\}$ and a set $T$ of triples $(a, b, c)$ of distinct elements, decide whether there exists an ordering of the elements such that for every triple, $b$ is placed somewhere between $a$ and $c$.

The goal is to find a bijection $\pi : \{1, \dots, n\} \to \{1, \dots, n\}$ (the position of each element) such that for every triple $(a, b, c) \in T$ it holds that $\pi(a) < \pi(b) < \pi(c)$ or $\pi(c) < \pi(b) < \pi(a)$. The elements of a triple do not have to be next to each other in the ordering. The problem is NP-complete ([Opatrný, 1979](https://en.wikipedia.org/wiki/Betweenness_problem)).

An example of a valid input format is:

```text
5 3
1 2 3
2 4 5
3 5 4
```

Where the first line contains n and m:
- n stands for number of elements
- m stands for number of triples (each triple a b c on a new line, meaning b has to be between a and c)

Elements are numbered from 1 to n, everything after # is a comment.


## Encoding

TODO

## User documentation
Basic usage:
```text
betweenness.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}]
```
Command-line options:

- -h, --help
Show a help message and exit.

- -i INPUT, --input INPUT
The instance file for the Betweenness problem.
Default: "instances/small-sat.in".

- -o OUTPUT, --output OUTPUT
Output file for the DIMACS CNF formula.
Default: "formula.cnf".

- -s SOLVER, --solver SOLVER
The SAT solver to be used (compiled Glucose binary).
Default: "glucose".

- -v {0,1}, --verb {0,1}
Verbosity level of the SAT solver (0 = quiet, 1 = default).
Default: 1.

## Example instances
- small-sat.in: A small satisfiable instance with 5 elements (only solutions are 1 2 4 5 3 and its reverse)
- small-unsat.in: A small unsatisfiable instance with 4 elements, where no two triples contradict each other directly
- tiny-unsat.in: The smallest unsatisfiable instance, each of the 3 elements has to be in the middle


## Experiments
TODO
