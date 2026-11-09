import subprocess
from argparse import ArgumentParser


# Working principle of the code:
# 1) read the instance from file
# 2) translate it into SAT formula in DIMACS CNF format
# 3) save CNF to formula.cnf
# 4) call glucose SAT solver on formula.cnf
# 5) based on the results, check which element is before which
#  and build the ordering from it
# 6) print the output

def load_instance(input_file_name):
    # read the input instance
    #format of the file:
    #first line, first element is n = num of elements
    #first line, second element is m = num of triples
    #then m lines, each one is a triple "a b c" which means b has to be between a and c
    #elements are numbered from 1 to n, everything after # is a comment
    global NR_ELEMENTS, NR_TRIPLES, NR_VARS
    numbers = []
    with open(input_file_name, "r") as file:
        for line in file:
            line = line.split("#")[0].split()
            numbers.extend(int(i) for i in line)

    #take n and m
    NR_ELEMENTS = numbers[0]
    NR_TRIPLES = numbers[1]
    NR_VARS = NR_ELEMENTS*(NR_ELEMENTS-1)//2

    #read all triples(skip n and m)
    triples = []
    for i in range(NR_TRIPLES):
        a, b, c = numbers[2+3*i], numbers[3+3*i], numbers[4+3*i]
        triples.append((a, b, c))

    return triples

def encode(instance):
    # given the instance, create a cnf formula, i.e. a list of lists of integers
    #variables: Before(i,j) for i < j is used when element i is before element j
    #           ¬Before(i,j) is used when element j is before element i
    #so we dont need variables for i > j, and for each pair exactly one is before the other
    #
    #for the ordering to be correct it has to be:
    #   transitive:
    #       if i before j and j before k, then i before k
    #       it is enough to forbid cycles of length 3, for i < j < k there are only 2 of them:
    #       i -> j -> k -> i  forbid it by adding the clause (¬Before(i,j) v ¬Before(j,k) v Before(i,k))
    #       i -> k -> j -> i  forbid it by adding the clause (Before(i,j) v Before(j,k) v ¬Before(i,k))
    #   betweenness:
    #       for triple (a,b,c), b has to be between a and c, so a < b < c or c < b < a
    #       this is the same as Before(a,b) <-> Before(b,c), which gives 2 clauses
    #       (¬Before(a,b) v Before(b,c)) and (Before(a,b) v ¬Before(b,c))
    #
    #obtained in the end:
    # 2 clauses for each 3 elements i < j < k and 2 clauses for each triple
    # total num of variables is n*(n-1)/2, one for each pair
    # also return the total number of variables used

    cnf = []

    #transitivity
    for i in range(1, NR_ELEMENTS+1):
        for j in range(i+1, NR_ELEMENTS+1):
            for k in range(j+1, NR_ELEMENTS+1):
                cnf.append([-before(i,j), -before(j,k), before(i,k), 0])
                cnf.append([before(i,j), before(j,k), -before(i,k), 0])

    #betweenness
    for a, b, c in instance:
        cnf.append([-before(a,b), before(b,c), 0])
        cnf.append([before(a,b), -before(b,c), 0])

    return (cnf, NR_VARS)

def pair_to_varID(i, j):
    #number of the variable Before(i,j) for i < j, starting from 1
    #pairs go in order (1,2), (1,3), ..., (1,n), (2,3), ..., (n-1,n)
    return (i-1)*NR_ELEMENTS - (i-1)*i//2 + (j-i)

def before(i, j):
    #literal for "i is before j"
    #if i > j then it is negation of Before(j,i)
    if i < j:
        return pair_to_varID(i, j)
    return -pair_to_varID(j, i)

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    # print CNF into formula.cnf in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + '\n')

    # call the solver and return the output
    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)

def print_result(result, instance):
    for line in result.stdout.decode('utf-8').split('\n'):
        print(line)                 # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself

    # check the returned result
    if (result.returncode == 20):       # returncode for SAT is 10, for UNSAT is 20
        print("There is no ordering that satisfies all the triples.")
        return

    # parse the model from the output of the solver
    # the model starts with 'v'
    model = []
    for line in result.stdout.decode('utf-8').split('\n'):
        if line.startswith("v"):    # there might be more lines of the model, each starting with 'v'
            vars = line.split(" ")
            vars.remove("v")
            model.extend(int(v) for v in vars)
    model.remove(0) # 0 is the end of the model, just ignore it

    print()
    print("##################################################################")
    print("###########[ Human readable result of the betweenness ]###########")
    print("##################################################################")
    print()

    # decode the meaning of the assignment
    #position of element i = num of elements that are before i
    position = {}
    for i in range(1, NR_ELEMENTS+1):
        position[i] = 0
        for j in range(1, NR_ELEMENTS+1):
            if j != i and is_true(model, before(j, i)):
                position[i] += 1
    order = sorted(position, key=lambda i: position[i])

    print("Order: " + ' '.join(str(i) for i in order))
    print()

    #check if every triple is satisfied in the found order
    for a, b, c in instance:
        ok = position[a] < position[b] < position[c] or position[c] < position[b] < position[a]
        print(str(b) + " between " + str(a) + " and " + str(c) + ": " + ("OK" if ok else "NOT OK"))

def is_true(model, lit):
    #model[v-1] is v if v is true and -v if v is false
    return model[abs(lit) - 1] == lit

if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="instances/small-sat.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0,2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # get the input instance
    instance = load_instance(args.input)

    # encode the problem to create CNF formula
    cnf, nr_vars = encode(instance)

    # call the SAT solver and get the result
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

    # interpret the result and print it in a human-readable format
    print_result(result, instance)
