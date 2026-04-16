from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator
import math
pi = math.pi

print('\nGrovers Algorithm')
print('------------------\n')

q = QuantumRegister(4,'q')
c = ClassicalRegister(4,'c')
qc = QuantumCircuit(q,c)

print('\nInitialising Circuit...\n')
### Initialisation ###

qc.h(q[0])
qc.h(q[1])
qc.h(q[2])
qc.h(q[3])

for i in range(3):
    ### 0000 Oracle ###
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[3])
    
    qc.cp(pi/4, q[0], q[3])
    qc.cx(q[0], q[1])
    qc.cp(-pi/4, q[1], q[3])
    qc.cx(q[0], q[1])
    qc.cp(pi/4, q[1], q[3])
    qc.cx(q[1], q[2])
    qc.cp(-pi/4, q[2], q[3])
    qc.cx(q[0], q[2])
    qc.cp(pi/4, q[2], q[3])
    qc.cx(q[1], q[2])
    qc.cp(-pi/4, q[2], q[3])
    qc.cx(q[0], q[2])
    qc.cp(pi/4, q[2], q[3])
    
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[3])



    #### Amplification ####
    qc.h(q[0])
    qc.h(q[1])
    qc.h(q[2])
    qc.h(q[3])
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[3])
    
    qc.cp(pi/4, q[0], q[3])
    qc.cx(q[0], q[1])
    qc.cp(-pi/4, q[1], q[3])
    qc.cx(q[0], q[1])
    qc.cp(pi/4, q[1], q[3])
    qc.cx(q[1], q[2])
    qc.cp(-pi/4, q[2], q[3])
    qc.cx(q[0], q[2])
    qc.cp(pi/4, q[2], q[3])
    qc.cx(q[1], q[2])
    
    qc.cp(-pi/4, q[2], q[3])
    qc.cx(q[0], q[2])
    qc.cp(pi/4, q[2], q[3])
    
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[3])
    qc.h(q[0])
    qc.h(q[1])
    qc.h(q[2])
    qc.h(q[3])


### Measurment ###
qc.barrier(q)
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])
qc.measure(q[2], c[2])
qc.measure(q[3], c[3])


print('\nExecuting job....\n')

backend = AerSimulator() # Using local Aer simulator
circ = transpile(qc, backend) # Rewrites the circuit to match the backend's basis gates and coupling map

result = backend.run(qc,shots=1024).result()
counts = result.get_counts(qc)

print('RESULT: ',counts,'\n')
print('Press any key to close')
input()