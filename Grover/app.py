import math
import os
from flask import Flask, render_template, request
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

app = Flask(__name__, template_folder="Templates")

def run_grover(target_data):
    n_qubits = len(target_data)
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
    def apply_diffuser(qc, n):
        qc.h(range(n))
        qc.x(range(n))
        qc.h(n-1)
        qc.mcx(list(range(n-1)), n-1)
        qc.h(n-1)
        qc.x(range(n))
        qc.h(range(n))
    q = QuantumRegister(n_qubits)
    c = ClassicalRegister(n_qubits)
    qc = QuantumCircuit(q, c)
    qc.h(range(n_qubits))
    iterations = int(math.pi/4 * math.sqrt(2**n_qubits))
    for _ in range(iterations):
        apply_oracle(qc, target_data, n_qubits)
        apply_diffuser(qc, n_qubits)
    qc.measure(q, c)
    backend = AerSimulator()
    result = backend.run(transpile(qc, backend), shots=1024).result()
    counts = result.get_counts()
    # Convert to percentage
    probs = {state: round((count/1024)*100, 2) for state, count in counts.items()}
    return probs


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    password = ""
    classical_time = None
    quantum_time = None

    if request.method == "POST":
        password = request.form["password"]

        if not all(c in '01' for c in password):
            results = {"Error": "Only binary allowed"}
        else:
            results = run_grover(password)

            n = len(password)

            # number of operations
            classical_time = 2 ** n
            quantum_time = int(math.sqrt(2 ** n))

    return render_template(
        "index.html",
        results=results,
        password=password,
        classical_time=classical_time,
        quantum_time=quantum_time
    )
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
