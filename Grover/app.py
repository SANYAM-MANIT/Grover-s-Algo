import math
from flask import Flask, render_template, request
from qiskit import QuantumCircuit, transpile, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

app = Flask(__name__)

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

    if request.method == "POST":
        password = request.form["password"]

        # validation
        if not all(c in '01' for c in password):
            results = {"Error": "Only binary allowed"}
        else:
            results = run_grover(password)

    return render_template("index.html", results=results, password=password)

if __name__ == "__main__":
    app.run(debug=True)