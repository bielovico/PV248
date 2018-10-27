import numpy as np
import numpy.linalg as la
import sys

input_file = sys.argv[1]

class Solution:
    def __init__(self, variable_names, solved):
        self.variable_names = variable_names
        self.solved = solved

    def __str__(self):
        s = 'solution: '
        for i in range(len(self.variable_names)):
            if i > 0:
                s += ', '
            s += '{} = {}'.format(self.variable_names[i], self.solved.tolist()[i][0])
        return s

with open(input_file) as f:
    eqns = f.readlines()

b = []
coefficients = []

for eqn in eqns:
    vars = {}
    eqn = eqn.split('=')
    const = int(eqn[1].strip())
    b.append([const])
    coeffs = eqn[0].split('+')
    for cs in coeffs:
        cs = cs.split('-')
        first = cs[0].strip()
        if first != '':
            if len(first) == 1:
                vars[first] = 1
            else:
                vars[first[-1]] = int(first[:-1])
        if len(cs) > 1:
            for var in cs[1:]:
                var = var.strip()
                if len(var) == 1:
                    vars[var] = -1
                else:
                    vars[var[-1]] = -int(var[:-1])
    coefficients.append(vars)

variables = set()
for d in coefficients:
    variables.update(d.keys())
variable_names = sorted(variables)

a = []
for d in coefficients:
    e = []
    for v in variable_names:
        c = d.get(v)
        if c is not None:
            e.append(c)
        else:
            e.append(0)
    a.append(e)

a = np.array(a)
b = np.array(b)
ab = np.hstack((a,b))
rank_a = la.matrix_rank(a)
rank_ab = la.matrix_rank(ab)
n = len(variables)

if rank_a != rank_ab:
    print('no solution')
elif n > rank_a:
    print('solution space dimension: {:d}'.format(n-rank_a))
else:
    x = la.solve(a, b)
    print(Solution(variable_names, x))
