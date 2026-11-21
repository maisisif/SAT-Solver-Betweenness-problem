# **Betweenness SAT Solver**

This project builds a solver for the Betweenness problem by reducing it to the Boolean Satisfiability Problem (SAT). The main logic is written in Python and encodes the input problem into CNF (Conjunctive Normal Form) before using the Glucose 4.2 SAT solver to get a solution.

The repository contains a compiled binary `glucose` (macOS, Apple Silicon). On other systems it has to be compiled from the [source](https://github.com/audemard/glucose/releases/tag/4.2.1) using `cmake .` and `make`, and the resulting `glucose-simp` copied into the project folder as `glucose`.



## Problem description

Given a set of elements $\{1, \dots, n\}$ and a set $T$ of triples $(a, b, c)$ of distinct elements, decide whether there exists an ordering of the elements such that for every triple, $b$ is placed somewhere between $a$ and $c$.

The goal is to find a bijection $\pi : \{1, \dots, n\} \to \{1, \dots, n\}$ (the position of each element) such that for every triple $(a, b, c) \in T$ it holds that $\pi(a) < \pi(b) < \pi(c)$ or $\pi(c) < \pi(b) < \pi(a)$. The elements of a triple do not have to be next to each other in the ordering. The problem is known to be NP-complete.

An example of a valid input format is:

```text
5 3
1 2 3
2 4 5
3 5 4
```

Where the first line contains n and m:
- n stands for number of elements
- m stands for number of triples

After that there are exactly m lines, each one containing a triple a b c, which means that b has to be between a and c. More precisely:
- all values are integers separated by spaces
- the elements are numbered from 1 to n, so $1 \le a, b, c \le n$
- a, b, c have to be three different elements
- the triples a b c and c b a mean the same thing, since b only has to be somewhere between a and c
- everything after # until the end of the line is a comment and is ignored


## Encoding

Start by defining a variable $x_{i,j}$ for each pair of elements $1 \le i < j \le n$:
- If $x_{i,j}$ is True, element $i$ is placed before element $j$.
- If $x_{i,j}$ is False, element $j$ is placed before element $i$.

There are no variables for $i > j$, since "$j$ is before $i$" is just $\neg x_{i,j}$. To make the notation shorter, for any two distinct elements $i, j$ we write $B_{i,j}$ for the literal saying that $i$ is before $j$:

$$B_{i,j} = \begin{cases} x_{i,j} & \text{if } i < j \\ \neg x_{j,i} & \text{if } i > j \end{cases}$$

For every pair exactly one of $B_{i,j}$, $B_{j,i}$ is true, so every two elements are compared and the relation is antisymmetric without any extra clauses. The following constraints are added:

- The relation has to be transitive, i.e. $B_{i,j} \wedge B_{j,k} \Rightarrow B_{i,k}$ for all distinct $i, j, k$. If this does not hold, then $B_{k,i}$ is true and the elements form a cycle $i \to j \to k \to i$, so it is enough to forbid all cycles of length 3. For $i < j < k$ there are only two such cycles, $i \to j \to k \to i$ and $i \to k \to j \to i$, which gives:

$$\bigwedge_{1 \le i < j < k \le n} \big(\neg x_{i,j} \vee \neg x_{j,k} \vee x_{i,k}\big) \wedge \big(x_{i,j} \vee x_{j,k} \vee \neg x_{i,k}\big)$$

- For every triple $(a, b, c) \in T$, element $b$ has to be between $a$ and $c$, i.e. $(B_{a,b} \wedge B_{b,c}) \vee (B_{c,b} \wedge B_{b,a})$. Since $B_{c,b} = \neg B_{b,c}$ and $B_{b,a} = \neg B_{a,b}$, this is the same as $B_{a,b} \Leftrightarrow B_{b,c}$, which gives:

$$\bigwedge_{(a, b, c) \in T} \big(\neg B_{a,b} \vee B_{b,c}\big) \wedge \big(B_{a,b} \vee \neg B_{b,c}\big)$$

Obtained in the end:
- $\binom{n}{2} = \frac{n(n-1)}{2}$ variables
- $2\binom{n}{3} + 2m$ clauses (for example 10 variables and 26 clauses for `small-sat.in` with $n = 5$, $m = 3$)

The ordering is decoded from a satisfying assignment by computing the position of every element as the number of elements before it plus one, $\pi(i) = 1 + |\{ j \ne i : B_{j,i} \text{ is true} \}|$.

The CNF is written in the standard DIMACS format.

### Alternative encoding

Another option is to use variables $p_{i,k}$ for $1 \le i, k \le n$, meaning that element $i$ is at position $k$. Then we would need:
- every element has a position: $\bigwedge_{i=1}^{n} \bigvee_{k=1}^{n} p_{i,k}$
- every element has at most one position: $\bigwedge_{i=1}^{n} \bigwedge_{1 \le k < l \le n} (\neg p_{i,k} \vee \neg p_{i,l})$
- every position has at most one element: $\bigwedge_{k=1}^{n} \bigwedge_{1 \le i < j \le n} (\neg p_{i,k} \vee \neg p_{j,k})$
- for every triple $(a, b, c) \in T$ and positions $k_1 \ne k_2$ of $a$ and $b$, the element $c$ has to be on the other side of $b$:

$$\bigwedge_{1 \le k_1 < k_2 \le n} \Big(\neg p_{a,k_1} \vee \neg p_{b,k_2} \vee \bigvee_{k_2 < k \le n} p_{c,k}\Big) \wedge \bigwedge_{1 \le k_2 < k_1 \le n} \Big(\neg p_{a,k_1} \vee \neg p_{b,k_2} \vee \bigvee_{1 \le k < k_2} p_{c,k}\Big)$$

This needs $n^2$ variables, about $n^3$ clauses for the permutation constraints and $n(n-1)$ long clauses for every triple. The chosen encoding needs only about half of the variables, about $n^3/3$ clauses for transitivity and just 2 clauses of size 2 for every triple, so we decided to use it.

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

Output format:

First the whole output of Glucose is printed (lines starting with `c` are comments and statistics, the line starting with `s` is the result and the lines starting with `v` are the satisfying assignment). If the instance is satisfiable, the found ordering is printed after it together with a check of every triple, for example for `small-sat.in`:

```text
Order: 3 5 4 2 1

2 between 1 and 3: OK
4 between 2 and 5: OK
5 between 3 and 4: OK
```

The order goes from left to right, so here element 3 is the first one and element 1 is the last one. If the instance is unsatisfiable, only the message `There is no ordering that satisfies all the triples.` is printed after the output of Glucose.

The CNF formula itself can be seen in the file given by `-o` (`formula.cnf` by default) and more statistics of the solver are shown with `-v 1`.

## Example instances
- small-sat.in: A small satisfiable instance with 5 elements (only solutions are 1 2 4 5 3 and its reverse)
- small-unsat.in: A small unsatisfiable instance with 4 elements, where no two triples contradict each other directly
- tiny-unsat.in: The smallest unsatisfiable instance, each of the 3 elements has to be in the middle


## Experiments
Experiments were run on a MacBook Pro with an Apple M3 Pro chip and 18 GB of RAM, using Python 3.13. Time was measured with hyperfine and it includes the whole run of the script (reading the instance, encoding, writing the CNF and running Glucose).

```text
Benchmark 1: python3 betweenness.py -i instances/small-sat.in -o formula.cnf -s glucose
  Time (mean ± σ):      31.4 ms ±   2.8 ms    [User: 22.1 ms, System: 7.4 ms]
  Range (min … max):    29.1 ms …  40.5 ms    50 runs

Benchmark 1: python3 betweenness.py -i instances/small-unsat.in -o formula.cnf -s glucose
  Time (mean ± σ):      32.0 ms ±   2.7 ms    [User: 22.5 ms, System: 7.6 ms]
  Range (min … max):    29.2 ms …  37.1 ms    50 runs

Benchmark 1: python3 betweenness.py -i instances/tiny-unsat.in -o formula.cnf -s glucose
  Time (mean ± σ):      34.5 ms ±   3.1 ms    [User: 23.9 ms, System: 8.4 ms]
  Range (min … max):    29.1 ms …  40.4 ms    50 runs
```

All three instances are solved almost immediately, most of the time is just starting Python and Glucose. Glucose solves all of them without any search (0 conflicts).

The size of the formula depends mostly on the number of elements: there are $2\binom{n}{3}$ transitivity clauses, which is about $n^3/3$, while every triple adds only 2 clauses. So to get an instance that takes at least 10 seconds, it would need a very large number of elements, and Glucose would spend most of the time on reading and simplifying the huge formula, not on searching for the ordering. Because of that, no such instance is included.
