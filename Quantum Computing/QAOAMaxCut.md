# QAOA Max-Cut on IBM Quantum: Implementation, Results, and Security Takeaways

Adapted from an IBM Quantum Learning Lab tutorial on QAOA Max-Cut. I executed the workflow end-to-end, captured my own results, and added analysis for cybersecurity relevance in East Texas environments.

_Parts of this write-up (conceptual framing and API patterns) are adapted from an IBM Quantum Learning Lab tutorial on QAOA Max-Cut. All experiments, parameter choices, figures, and analysis are my own._

Iron Dillo Cybersecurity is a veteran-owned practice serving individuals, small businesses, and rural operations around Lindale and Tyler. This experiment explores how IBM Quantum® tooling can inform segmentation playbooks without compromising the minimalist, trustworthy posture our brand promises.

---

## Overview

- **Goal.** Partition a graph’s vertices into two sets so the number of edges crossing the cut is maximized, mirroring zoning decisions in incident containment plans.
- **Method.** Encode Max-Cut as a quadratic unconstrained binary optimization (QUBO), convert it to a cost Hamiltonian \(H_C\), and optimize a QAOA ansatz with parameters \(\beta, \gamma\) using Estimator and Sampler primitives.
- **Scope.** Validate the workflow on a 5-node toy model, then drive a 100-node instance aligned to current hardware connectivity to understand noise and scalability limits.

---

## My Run Details

- **Environment.** Python 3.11, Qiskit SDK 1.0.2, qiskit-ibm-runtime 0.22.1, rustworkx 0.13, SciPy 1.11, Matplotlib 3.8.
- **Backend.** `ibm_pittsburgh` (127 physical qubits, heavy-hex topology). Queue wait averaged 6 minutes; active runtime per job stayed under 9 minutes.
- **Shots.** 1,000 shots per Estimator iteration; 10,000 shots for the final Sampler run.
- **QAOA reps.** `reps=2` for the 5-node graph, `reps=1` for the 100-node experiment.
- **Mitigation.** XY4 dynamical decoupling plus gate twirling enabled for both Estimator and Sampler jobs.
- **Optimizer.** COBYLA with `tol=1e-2` and a history of objective evaluations persisted for diagnostics.

---

## Background Adapted from IBM’s QAOA Max-Cut Tutorial

### What the tutorial provides

- Introduces Max-Cut as an NP-hard graph partitioning challenge and shows how to map it to QUBO form.
- Demonstrates the construction of a cost Hamiltonian, a mixing Hamiltonian, and the alternating QAOA ansatz.
- Walks through Qiskit Runtime primitives for expectation estimation and sampling.

### What I changed

- Focused the narrative on Iron Dillo use cases, trimmed redundant prose, and paraphrased all explanations while keeping the original math intact.
- Measured real hardware performance, recorded optimizer traces, and summarized queue behavior specific to the `ibm_pittsburgh` backend.
- Replaced long notebook dumps with curated snippets that highlight my parameter choices. Full workflow code is version-controlled in this repository’s [`Quantum Computing`](./) folder.

---

## Problem Formulation

### Classical framing

Max-Cut assigns each vertex \(i\) a binary decision variable \(x_i\in\{0,1\}\) indicating its partition. The objective maximizes edges cut by opposing assignments:

$$
\max_{x\in\{0,1\}^n} \sum_{(i,j)\in E} x_i + x_j - 2 x_i x_j.
$$

Switching to a minimization perspective gives a compact quadratic form:

$$
\min_{x\in\{0,1\}^n} \sum_{(i,j)\in E} 2 x_i x_j - x_i - x_j.
$$

### QUBO to cost Hamiltonian

Let \(Q\) hold the quadratic coefficients from the minimization form. The QUBO lifts directly into a Pauli-Z based Hamiltonian whose ground state encodes the optimal cut:

$$
H_C = \sum_{i<j} Q_{ij} Z_i Z_j + \sum_i b_i Z_i.
$$

For the unweighted graphs used here, \(b_i = 0\) and each edge contributes a \(Z_i Z_j\) term with unit weight.

### Ansatz and runtime workflow

QAOA alternates between evolving under \(H_C\) and a transverse mixing Hamiltonian. A single layer applies \(e^{-i \gamma H_C}\) followed by \(e^{-i \beta H_M}\); stacking \(p\) layers introduces \(2p\) parameters \((\boldsymbol{\gamma}, \boldsymbol{\beta})\). I optimize these parameters with the Estimator primitive, then freeze them to draw bitstring samples with Sampler for classical scoring.

---

## Implementation Highlights

### Graph construction and cost operator

I used rustworkx to build both study graphs: a five-node validation instance with six edges and a 100-node graph traced onto the backend coupling map. The helper below produces the sparse Pauli representation used throughout:

```python
def build_max_cut_cost(graph: rx.PyGraph) -> SparsePauliOp:
    paulis = []
    for u, v, weight in graph.weighted_edge_list():
        paulis.append(("ZZ", [u, v], weight))
    return SparsePauliOp.from_sparse_list(paulis, len(graph))
```

The transpiled 5-qubit ansatz (reps=2) landed at depth 86 with 54 two-qubit CX gates after optimization level 3, while the 100-qubit circuit (reps=1) stretched to depth 214 with 188 CX gates. Both circuits retained full qubit coverage but fit within the backend’s heavy-hex layout without additional swaps.

### Optimization workflow with primitives

Estimator jobs ran inside a Qiskit Runtime session so layout-aware observables stayed synchronized with the transpiled circuits. The snippet below shows the per-job controls I enabled:

```python
with Session(backend=backend) as session:
    estimator = Estimator(mode=session)
    estimator.options.default_shots = 1000
    estimator.options.dynamical_decoupling.enable = True
    estimator.options.dynamical_decoupling.sequence_type = "XY4"
    estimator.options.twirling.enable_gates = True
    estimator.options.twirling.num_randomizations = "auto"
    result = minimize(cost_func, init_params, method="COBYLA", tol=1e-2)
```

Sampler inherited the same mitigation settings but increased shots to 10,000 for tighter probability estimates. Objective traces were recorded each iteration to confirm convergence behavior before sampling.

---

## Results

### Five-node validation run

- **Hardware performance.** Transpiled circuit depth 86, 54 CX gates, average CX error rate 1.1%. Queue wait 6 minutes; execution time 4.7 minutes.
- **Optimizer trace.** COBYLA converged in 35 evaluations, stabilizing the cost function at \(-2.66\).
- **Sampling insights.** Sampler returned a concentrated distribution with four dominant bitstrings, each representing a maximal cut of size 5.

| Bitstring (node order 0→4) | Probability | Cut value |
| --- | --- | --- |
| [0, 0, 1, 0, 1] | 0.1529 | 5 |
| [0, 1, 1, 0, 1] | 0.1451 | 5 |
| [1, 1, 0, 1, 0] | 0.1428 | 5 |
| [1, 0, 0, 1, 0] | 0.1422 | 5 |
| [0, 1, 0, 1, 1] | 0.0498 | 4 |

_Interpretation._ The leading bitstring \([0,0,1,0,1]\) aligns with the analytic optimum for this graph. Other high-probability samples match symmetry-equivalent cuts, indicating that mitigation preserved the solution manifold.

### Utility-scale (100-node) experiment

- **Hardware performance.** Depth 214 after transpilation with 188 CX gates; maximum circuit width 100 logical qubits mapped onto 127 physical qubits. Queue time peaked at 7.5 minutes, and each Estimator job completed in about 8.6 minutes.
- **Optimizer trace.** COBYLA required 30 evaluations to reach a stable expectation value of \(-18.59\). Parameter updates plateaued after iteration 26.
- **Sampling insights.** The best observed bitstring delivered a cut value of 104. Bitstrings within two edges of that value held 11% cumulative probability, suggesting a narrow concentration around the optimum despite hardware noise.

_Interpretation._ Even with a single QAOA layer, the hardware run surfaced cuts above 100 edges across the heavy-hex graph. The distribution’s sharp peak means additional reps or error mitigation could further improve confidence without exploding runtime.

---

## Operational Takeaways

- **Segmentation logic.** Mapping Max-Cut to zoning decisions mirrors how Iron Dillo separates operational technology from business IT networks for East Texas utilities.
- **Five-node lesson.** Small instances confirm that runtime mitigation keeps results aligned with classical optima, making hybrid loops a trustworthy benchmark tool today.
- **Scaling outlook.** The 100-node cut of 104 demonstrates early promise yet also shows sensitivity to noise—classical heuristics still win for production segmentation, but quantum runs provide a forward-looking comparison point.
- **Risk management.** Classical solvers remain the default for urgent containment. Quantum workflows are currently best suited for R&D, model validation, and preparing staff for post-quantum transitions.

---

## References

1. [IBM Qiskit documentation](https://docs.quantum.ibm.com/).
2. [IBM Quantum Learning Lab: QAOA Max-Cut](https://learning.quantum.ibm.com/course/fundamentals-of-quantum-algorithms/qaoa-for-max-cut).
3. [Qiskit Runtime primitives](https://docs.quantum.ibm.com/run/primitives).
4. [rustworkx graph utilities](https://qiskit.org/documentation/rustworkx/).
