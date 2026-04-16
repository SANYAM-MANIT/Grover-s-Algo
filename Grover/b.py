import math
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# --- SETTINGS ---
print("Enter Correct password : ")
target_data = input(); # The binary index of your "practical data"
n_qubits = len(target_data);
# ----------------

def apply_oracle(qc, target, n):
    """Marks the target state with a negative phase"""
    # 1. Flip 0s to 1s so the logic triggers on the target
    for i, bit in enumerate(reversed(target)):
        if bit == '0':
            qc.x(i)
    
    # 2. Multi-Controlled Z (The Marker)
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    
    # 3. Flip back
    for i, bit in enumerate(reversed(target)):
        if bit == '0':
            qc.x(i)

def apply_diffuser(qc, n):
    """Amplifies the marked state (Inversion about the mean)"""
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    qc.x(range(n))
    qc.h(range(n))

# --- MAIN CIRCUIT CONSTRUCTION ---
q = QuantumRegister(n_qubits, 'q')
c = ClassicalRegister(n_qubits, 'c')
qc = QuantumCircuit(q, c)

# Step 1: Initial Superposition
qc.h(range(n_qubits))

# Step 2: Grover Iterations (The Loop)
# For 4 qubits, iterations = 3. For 10 qubits, iterations = 25.
iterations = int(math.pi/4 * math.sqrt(2**n_qubits))
for _ in range(iterations):
    apply_oracle(qc, target_data, n_qubits)
    apply_diffuser(qc, n_qubits)

# Step 3: Measurement
qc.measure(q, c)

# --- EXECUTION ---
backend = AerSimulator()
transpiled_qc = transpile(qc, backend)
result = backend.run(transpiled_qc, shots=1024).result()
counts = result.get_counts()

print("\n--- ANALYSIS ---")
for state, count in counts.items():
    prob = (count / 1024) * 100
    print(f"State {state}: Probability {prob:.2f}%")