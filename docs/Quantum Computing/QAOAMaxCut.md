# QAOA Max-Cut Optimization Experiment (Background Tutorial)

Iron Dillo Cybersecurity evaluated IBM's Quantum Approximate Optimization Algorithm (QAOA) workflow to understand how hybrid quantum-classical loops can reinforce segmentation strategies for veteran-owned cybersecurity services across East Texas, including **Lindale** and **Tyler**. This document preserves the full background tutorial requested by the research team so future analysts can reproduce each step.

---

## Overview

- **Goal:** Partition a graph into two sets so that the number of traversed edges (the "cut") is maximized.
- **Use Case:** Supports individuals, small businesses, and rural operations that require resilient network zoning and workload isolation.
- **Approach:** Follow Qiskit's QAOA pattern to solve both a five-node validation problem and a 100-node utility-scale instance mapped to IBM Quantum® hardware.

---

## Requirements

Before starting, install the following:

- Qiskit SDK v1.0 or later with visualization support: `pip install "qiskit[visualization]"`
- Qiskit Runtime 0.22 or later: `pip install qiskit-ibm-runtime`
- Supporting scientific libraries: Matplotlib, Rustworkx, NumPy, SciPy

---

## Setup

```python
import matplotlib
import matplotlib.pyplot as plt
import rustworkx as rx
from rustworkx.visualization import mpl_draw as draw_graph
import numpy as np
from scipy.optimize import minimize
from collections import defaultdict
from typing import Sequence

from qiskit.quantum_info import SparsePauliOp
from qiskit.circuit.library import QAOAAnsatz
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import Session, EstimatorV2 as Estimator
from qiskit_ibm_runtime import SamplerV2 as Sampler
```

---

## Part I. Small-Scale QAOA

The first portion illustrates each step of solving the Max-Cut problem for a five-node graph using a quantum computer.

### Classical Formulation

Consider minimizing a function \(f(x)\) over binary variables:

$$
\min_{x \in \{0,1\}^n} f(x)
$$

where \(x\) is a vector whose components correspond to each node in the graph. Constraining each component to \(0\) or \(1\) represents exclusion or inclusion in the cut. For an edge \((i, j)\), the term

$$
x_i + x_j - 2 x_i x_j
$$

returns 1 if exactly one endpoint is in the cut. The maximization objective is therefore:

$$
\max_{x \in \{0,1\}^n} \sum_{(i,j)} x_i + x_j - 2x_i x_j
$$

which is equivalent to minimizing:

$$
\min_{x \in \{0,1\}^n} \sum_{(i,j)} 2 x_i x_j - x_i - x_j.
$$

### Build the Graph

```python
n = 5

graph = rx.PyGraph()
graph.add_nodes_from(np.arange(0, n, 1))
edge_list = [
    (0, 1, 1.0),
    (0, 2, 1.0),
    (0, 4, 1.0),
    (1, 2, 1.0),
    (2, 3, 1.0),
    (3, 4, 1.0),
]
graph.add_edges_from(edge_list)
draw_graph(graph, node_size=600, with_labels=True)
```

### Step 1: Map to a Quantum Problem

1. Convert the classical optimization to Quadratic Unconstrained Binary Optimization (QUBO) form:

   $$
   \min_{x \in \{0,1\}^n} x^T Q x,
   $$

   where \(Q\) is an \(n \times n\) matrix of real numbers.

2. Rewrite the optimization as a Hamiltonian whose ground state minimizes the cost function:

    $$
    H_C = \sum_{(i,j)\in E} Q_{ij} Z_i Z_j + \sum_i b_i Z_i
    $$

   For unweighted Max-Cut, \(b_i = 0\) and \(Q_{ij} = 1\) for every edge.

3. Create a quantum circuit (the QAOA Ansatz) that prepares quantum states with high overlap to the Hamiltonian's ground state.

```python
def build_max_cut_paulis(graph: rx.PyGraph) -> list[tuple[str, float]]:
    """Convert the graph to a Pauli list."""
    pauli_list = []
    for edge in list(graph.edge_list()):
        weight = graph.get_edge_data(edge[0], edge[1])
        pauli_list.append(("ZZ", [edge[0], edge[1]], weight))
    return pauli_list

max_cut_paulis = build_max_cut_paulis(graph)
cost_hamiltonian = SparsePauliOp.from_sparse_list(max_cut_paulis, n)
print("Cost Function Hamiltonian:", cost_hamiltonian)
```

```
Cost Function Hamiltonian: SparsePauliOp(['IIIZZ', 'IIZIZ', 'ZIIIZ', 'IIZZI', 'IZZII', 'ZZIII'],
              coeffs=[1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j, 1.+0.j])
```

### Step 2: Construct the QAOA Circuit

The QAOA circuit alternates between the cost Hamiltonian \(H_C\) and a mixing Hamiltonian \(H_m\):

```python
circuit = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=2)
circuit.measure_all()

circuit.draw("mpl")
```

The Ansatz parameters are \(\beta\) and \(\gamma\) rotation angles:

```python
circuit.parameters
```

```
ParameterView([ParameterVectorElement(β[0]), ParameterVectorElement(β[1]), ParameterVectorElement(γ[0]), ParameterVectorElement(γ[1])])
```

### Step 3: Optimize for Hardware Execution

Use the Qiskit transpiler to map the logical circuit onto an IBM Quantum backend:

```python
service = QiskitRuntimeService()
backend = service.least_busy(
    operational=True, simulator=False, min_num_qubits=127
)
print(backend)

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)

candidate_circuit = pm.run(circuit)
candidate_circuit.draw("mpl", fold=False, idle_wires=False)
```

```
<IBMBackend('ibm_pittsburgh')>
```

### Step 4: Execute with Qiskit Primitives

Initialize parameters and define the Estimator-based cost function:

```python
initial_gamma = np.pi
initial_beta = np.pi / 2
init_params = [initial_beta, initial_beta, initial_gamma, initial_gamma]
```

```python
def cost_func_estimator(params, ansatz, hamiltonian, estimator):
    # Transform the observable defined on virtual qubits to
    # an observable defined on all physical qubits
    isa_hamiltonian = hamiltonian.apply_layout(ansatz.layout)

    pub = (ansatz, isa_hamiltonian, params)
    job = estimator.run([pub])

    results = job.result()[0]
    cost = results.data.evs

    objective_func_vals.append(cost)

    return cost
```

Run the optimization loop:

```python
objective_func_vals = []  # Global variable
with Session(backend=backend) as session:
    estimator = Estimator(mode=session)
    estimator.options.default_shots = 1000

    # Error suppression / mitigation
    estimator.options.dynamical_decoupling.enable = True
    estimator.options.dynamical_decoupling.sequence_type = "XY4"
    estimator.options.twirling.enable_gates = True
    estimator.options.twirling.num_randomizations = "auto"

    result = minimize(
        cost_func_estimator,
        init_params,
        args=(candidate_circuit, cost_hamiltonian, estimator),
        method="COBYLA",
        tol=1e-2,
    )
    print(result)
```

```
 message: Optimization terminated successfully.
 success: True
  status: 1
     fun: -2.6647130127038308
       x: [ 3.611e+00  1.851e+00  2.833e+00  2.674e+00]
    nfev: 35
   maxcv: 0.0
```

Plot convergence:

```python
plt.figure(figsize=(12, 6))
plt.plot(objective_func_vals)
plt.xlabel("Iteration")
plt.ylabel("Cost")
plt.show()
```

Assign optimal parameters and sample with the Sampler primitive:

```python
optimized_circuit = candidate_circuit.assign_parameters(result.x)
optimized_circuit.draw("mpl", fold=False, idle_wires=False)
```

```python
sampler = Sampler(mode=backend)
sampler.options.default_shots = 10000

sampler.options.dynamical_decoupling.enable = True
sampler.options.dynamical_decoupling.sequence_type = "XY4"
sampler.options.twirling.enable_gates = True
sampler.options.twirling.num_randomizations = "auto"

pub = (optimized_circuit,)
job = sampler.run([pub], shots=int(1e4))
counts_int = job.result()[0].data.meas.get_int_counts()
counts_bin = job.result()[0].data.meas.get_counts()
shots = sum(counts_int.values())
final_distribution_int = {key: val / shots for key, val in counts_int.items()}
final_distribution_bin = {key: val / shots for key, val in counts_bin.items()}
print(final_distribution_int)
```

```
{23: 0.0089, 4: 0.0117, 18: 0.0357, 11: 0.1428, 28: 0.0043, 20: 0.1529, 13: 0.0363, 22: 0.1451, 21: 0.0381, 14: 0.0076, 10: 0.042, 15: 0.0059, 12: 0.0093, 26: 0.0498, 9: 0.1422, 7: 0.0116, 5: 0.0444, 17: 0.0073, 29: 0.0052, 27: 0.0106, 30: 0.0087, 2: 0.005, 0: 0.0041, 8: 0.0105, 19: 0.0082, 24: 0.0101, 31: 0.0045, 25: 0.0075, 6: 0.0072, 1: 0.0094, 3: 0.0055, 16: 0.0076}
```

### Step 5: Post-Process Results

```python
def to_bitstring(integer, num_bits):
    result = np.binary_repr(integer, width=num_bits)
    return [int(digit) for digit in result]

keys = list(final_distribution_int.keys())
values = list(final_distribution_int.values())
most_likely = keys[np.argmax(np.abs(values))]
most_likely_bitstring = to_bitstring(most_likely, len(graph))
most_likely_bitstring.reverse()

print("Result bitstring:", most_likely_bitstring)
```

```
Result bitstring: [0, 0, 1, 0, 1]
```

Visualize the distribution:

```python
matplotlib.rcParams.update({"font.size": 10})
final_bits = final_distribution_bin
values = np.abs(list(final_bits.values()))
top_4_values = sorted(values, reverse=True)[:4]
positions = []
for value in top_4_values:
    positions.append(np.where(values == value)[0])
fig = plt.figure(figsize=(11, 6))
ax = fig.add_subplot(1, 1, 1)
plt.xticks(rotation=45)
plt.title("Result Distribution")
plt.xlabel("Bitstrings (reversed)")
plt.ylabel("Probability")
ax.bar(list(final_bits.keys()), list(final_bits.values()), color="tab:grey")
for p in positions:
    ax.get_children()[int(p[0])].set_color("tab:purple")
plt.show()
```

Plot the best cut:

```python
def plot_result(G, x):
    colors = ["tab:grey" if i == 0 else "tab:purple" for i in x]
    pos, _default_axes = rx.spring_layout(G), plt.axes(frameon=True)
    rx.visualization.mpl_draw(
        G, node_color=colors, node_size=100, alpha=0.8, pos=pos
    )

plot_result(graph, most_likely_bitstring)
```

Evaluate the cut value:

```python
def evaluate_sample(x: Sequence[int], graph: rx.PyGraph) -> float:
    assert len(x) == len(
        list(graph.nodes())
    ), "The length of x must coincide with the number of nodes in the graph."
    return sum(
        x[u] * (1 - x[v]) + x[v] * (1 - x[u])
        for u, v in list(graph.edge_list())
    )

cut_value = evaluate_sample(most_likely_bitstring, graph)
print("The value of the cut is:", cut_value)
```

---

## Part II. Utility-Scale QAOA (100 Qubits)

Scale the workflow to a 100-node weighted graph using the backend's coupling map.

### Build the Large Graph

```python
n = 100  # Number of nodes in graph
graph_100 = rx.PyGraph()
graph_100.add_nodes_from(np.arange(0, n, 1))
elist = []
for edge in backend.coupling_map:
    if edge[0] < n and edge[1] < n:
        elist.append((edge[0], edge[1], 1.0))
graph_100.add_edges_from(elist)
draw_graph(graph_100, node_size=200, with_labels=True, width=1)
```

### Map to a Hamiltonian

```python
max_cut_paulis_100 = build_max_cut_paulis(graph_100)

cost_hamiltonian_100 = SparsePauliOp.from_sparse_list(max_cut_paulis_100, 100)
print("Cost Function Hamiltonian:", cost_hamiltonian_100)
```

> **Note:** The printed `SparsePauliOp` spans hundreds of terms; truncate the output in presentations for readability.

### Generate and Transpile the Circuit

```python
circuit_100 = QAOAAnsatz(cost_operator=cost_hamiltonian_100, reps=1)
circuit_100.measure_all()

circuit_100.draw("mpl", fold=False, scale=0.2, idle_wires=False)
```

```python
pm = generate_preset_pass_manager(optimization_level=3, backend=backend)

candidate_circuit_100 = pm.run(circuit_100)
candidate_circuit_100.draw("mpl", fold=False, scale=0.1, idle_wires=False)
```

### Optimize Parameters on Hardware

```python
initial_gamma = np.pi
initial_beta = np.pi / 2
init_params = [initial_beta, initial_gamma]

objective_func_vals = []  # Global variable
with Session(backend=backend) as session:
    estimator = Estimator(mode=session)

    estimator.options.default_shots = 1000
    estimator.options.dynamical_decoupling.enable = True
    estimator.options.dynamical_decoupling.sequence_type = "XY4"
    estimator.options.twirling.enable_gates = True
    estimator.options.twirling.num_randomizations = "auto"

    result = minimize(
        cost_func_estimator,
        init_params,
        args=(candidate_circuit_100, cost_hamiltonian_100, estimator),
        method="COBYLA",
    )
    print(result)
```

```
 message: Optimization terminated successfully.
 success: True
  status: 1
     fun: -18.589441985445966
       x: [ 2.754e+00  4.178e+00]
    nfev: 30
   maxcv: 0.0
```

Assign parameters and sample:

```python
optimized_circuit_100 = candidate_circuit_100.assign_parameters(result.x)
optimized_circuit_100.draw("mpl", fold=False, idle_wires=False)
```

```python
sampler = Sampler(mode=backend)
sampler.options.default_shots = 10000

sampler.options.dynamical_decoupling.enable = True
sampler.options.dynamical_decoupling.sequence_type = "XY4"
sampler.options.twirling.enable_gates = True
sampler.options.twirling.num_randomizations = "auto"

pub = (optimized_circuit_100,)
job = sampler.run([pub], shots=int(1e4))

counts_int = job.result()[0].data.meas.get_int_counts()
counts_bin = job.result()[0].data.meas.get_counts()
shots = sum(counts_int.values())
final_distribution_100_int = {
    key: val / shots for key, val in counts_int.items()
}
```

Plot convergence:

```python
plt.figure(figsize=(12, 6))
plt.plot(objective_func_vals)
plt.xlabel("Iteration")
plt.ylabel("Cost")
plt.show()
```

### Post-Process Utility-Scale Results

Helper constants and evaluators:

```python
_PARITY = np.array(
    [-1 if bin(i).count("1") % 2 else 1 for i in range(256)],
    dtype=np.complex128,
)

def evaluate_sparse_pauli(state: int, observable: SparsePauliOp) -> complex:
    """Utility for evaluating the expectation value of a measured state."""
    packed_uint8 = np.packbits(observable.paulis.z, axis=1, bitorder="little")
    state_bytes = np.frombuffer(
        state.to_bytes(packed_uint8.shape[1], "little"), dtype=np.uint8
    )
    reduced = np.bitwise_xor.reduce(packed_uint8 & state_bytes, axis=1)
    return np.sum(observable.coeffs * _PARITY[reduced])


def best_solution(samples, hamiltonian):
    """Find solution with lowest cost."""
    min_cost = 1000
    min_sol = None
    for bit_str in samples.keys():
        candidate_sol = int(bit_str)
        fval = evaluate_sparse_pauli(candidate_sol, hamiltonian).real
        if fval <= min_cost:
            min_sol = candidate_sol

    return min_sol
```

Identify the best cut:

```python
best_sol_100 = best_solution(final_distribution_100_int, cost_hamiltonian_100)
best_sol_bitstring_100 = to_bitstring(int(best_sol_100), len(graph_100))
best_sol_bitstring_100.reverse()

print("Result bitstring:", best_sol_bitstring_100)
```

```
Result bitstring: [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1]
```

Visualize and evaluate:

```python
plot_result(graph_100, best_sol_bitstring_100)

cut_value_100 = evaluate_sample(best_sol_bitstring_100, graph_100)
print("The value of the cut is:", cut_value_100)
```

```
The value of the cut is: 104
```

Convert samples to objective values and plot the cumulative distribution function:

```python
def _plot_cdf(objective_values: dict, ax, color):
    x_vals = sorted(objective_values.keys(), reverse=True)
    y_vals = np.cumsum([objective_values[x] for x in x_vals])
    ax.plot(x_vals, y_vals, color=color)


def plot_cdf(dist, ax, title):
    _plot_cdf(
        dist,
        ax,
        "C1",
    )
    ax.vlines(min(list(dist.keys())), 0, 1, "C1", linestyle="--")

    ax.set_title(title)
    ax.set_xlabel("Objective function value")
    ax.set_ylabel("Cumulative distribution function")
    ax.grid(alpha=0.3)


def samples_to_objective_values(samples, hamiltonian):
    """Convert the samples to objective function values."""

    objective_values = defaultdict(float)
    for bit_str, prob in samples.items():
        candidate_sol = int(bit_str)
        fval = evaluate_sparse_pauli(candidate_sol, hamiltonian).real
        objective_values[fval] += prob

    return objective_values

result_dist = samples_to_objective_values(
    final_distribution_100_int, cost_hamiltonian_100
)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
plot_cdf(result_dist, ax, "Eagle device")
```

---

## Conclusions

- **Validation:** QAOA identified a high-quality cut for the five-node instance, matching analytical expectations.
- **Utility Scale:** The 100-node run produced a cut value of 104, demonstrating quantum-assisted segmentation potential for complex East Texas infrastructure.
- **Operational Fit:** Runtime primitives with lightweight mitigation allow Iron Dillo to explore quantum-enhanced defenses without compromising our commitment to clarity, speed, and trustworthiness.

---

## Resources

- Qiskit SDK documentation: <https://docs.quantum.ibm.com/>
- Qiskit Runtime service: <https://quantum.ibm.com/services/runtime>
- Rustworkx graph utilities: <https://qiskit.org/documentation/rustworkx/>

