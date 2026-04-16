import math
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# --- SETTINGS ---
charset = "abcdefghijklmnopqrstuvwxyz0123456789"
user_password = input("Enter password (lowercase + digits only): ")

# --- ENCODE ---
def encode_password(password, charset):
    bits_per_char = math.ceil(math.log2(len(charset)))
    binary = ""
    for ch in password:
        if ch not in charset:
            raise ValueError("Invalid character in password")
        index = charset.index(ch)
        binary += format(index, f'0{bits_per_char}b')
    return binary, bits_per_char

def decode_password(binary, charset, bits_per_char):
    password = ""
    for i in range(0, len(binary), bits_per_char):
        chunk = binary[i:i+bits_per_char]
        index = int(chunk, 2)
        password += charset[index]
    return password

binary_password, bits_per_char = encode_password(user_password, charset)
n_qubits = len(binary_password)

# --- ORACLE ---
def apply_oracle(qc, target, n):
    for i, bit in enumerate(reversed(target)):
        if bit == '0':
            qc.x(i)

    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)

    for i, bit in enumerate(reversed(target)):
        if bit == '0':
            qc.x(i)

# --- DIFFUSER ---
def apply_diffuser(qc, n):
    qc.h(range(n))
    qc.x(range(n))

    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)

    qc.x(range(n))
    qc.h(range(n))

# --- CIRCUIT ---
q = QuantumRegister(n_qubits)
c = ClassicalRegister(n_qubits)
qc = QuantumCircuit(q, c)

qc.h(range(n_qubits))

iterations = int(math.pi/4 * math.sqrt(2**n_qubits))

for _ in range(iterations):
    apply_oracle(qc, binary_password, n_qubits)
    apply_diffuser(qc, n_qubits)

qc.measure(q, c)

# --- RUN ---
backend = AerSimulator()
result = backend.run(transpile(qc, backend), shots=1024).result()
counts = result.get_counts()

# --- OUTPUT ---
best_binary = max(counts, key=counts.get)
guessed_password = decode_password(best_binary, charset, bits_per_char)

print("\n🔍 Results:")
for state, count in counts.items():
    print(state, ":", (count/1024)*100, "%")

print("\n✅ Actual password:   ", user_password)
print("🤖 Guessed password: ", guessed_password)