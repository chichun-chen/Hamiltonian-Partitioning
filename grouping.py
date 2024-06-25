import os
import pennylane as qml
import numpy as np

# Parameters
file = "H2_Hamiltonian.txt"
grouping_type = "qwc" # Can be 'qwc' (qubit-wise commuting), 'commuting', or 'anticommuting'.


def read_raw_Hamiltonian(filename=""):
    path = os.path.abspath(filename)
    H = []
    ops = []
    coeffs = []
    with open(path) as f:
        f.readline() # Skip header
        qubits, terms, groups = f.readline()[:-1].split(' ')

        for _ in range(int(terms)):
            s = f.readline()[:-1].split(' ')
            coeffs.append(float(s[0]))
            ops.append(s[1])
            
        H.append((ops, coeffs))
    return H, int(qubits), int(terms), int(groups)

def To_pennylane(Hg:list, grouping_type=None):
    obs = []
    coeffs = []
    for i in range(len(Hg)):
        for j,p in enumerate(str_to_Pauli(Hg[i][0])):
            obs.append(p)
            coeffs.append(Hg[i][1][j])
    qmlH = qml.Hamiltonian(coeffs, obs, grouping_type=grouping_type)
    return qmlH

def str_to_Pauli(H:list):
    ops = []
    for string in H:
        obs = None
        for i,c in enumerate(string):
            if not obs:
                obs = char_to_Pauli(c,i)
            else:
                if char_to_Pauli(c,i):
                    obs = obs @ char_to_Pauli(c,i)
        if not obs: obs = qml.Identity(0)
        ops.append(obs)
    return ops

def char_to_Pauli(c:str, i:int):
    if c == 'X':
        return qml.PauliX(i)
    elif c == 'Y':
        return qml.PauliY(i)
    elif c == 'Z':
        return qml.PauliZ(i)
    else:
        return None

def measure_format(P, qubits):
    P_str = Pauli_to_char(P.name)
    
    op = ['I']*qubits
    j = 0
    for i in P.wires.tolist():
        op[i] = P_str[j]
        j += 1
    return "".join(op)

def Pauli_to_char(L):
    STR = []
    if isinstance(L, list):
        for i in L:
            STR.append(i[-1])
        return STR
    else:
        if L == 'Identity':
            STR.append('I')
        else:
            STR.append(L[-1])
        return STR


if __name__ == '__main__':
    H, qubits, terms, _ = read_raw_Hamiltonian(filename=file)
    Hp = To_pennylane(H, grouping_type)
    
    savepath = os.path.abspath(grouping_type + '_' + file)
    with open(savepath, 'w') as f:
        f.write("#Header: # of qubit | # of terms | # of groups")
        f.write("{} {} {}\n".format(qubits, len(Hp.ops), len(Hp.grouping_indices)))
        for g in Hp.grouping_indices:
            f.write("{}\n".format(len(g)))
            for i in g:
                op = measure_format(Hp.ops[i], qubits)
                f.write("{} {}\n".format(np.round(np.real(Hp.coeffs[i]),8), op ))
            f.write("\n")
