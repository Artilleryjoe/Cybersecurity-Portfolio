from qiskit.circuit.library import RealAmplitudes, ZFeatureMap, ZZFeatureMap
from qiskit_machine_learning.algorithms import QSVC, VQC
from qiskit_machine_learning.kernels import FidelityQuantumKernel
from qiskit_machine_learning.optimizers import COBYLA, SPSA
from sklearn.svm import SVC


def build_angle_qsvc(n_features: int):
    fmap = ZFeatureMap(feature_dimension=n_features, reps=1)
    kernel = FidelityQuantumKernel(feature_map=fmap)
    return QSVC(quantum_kernel=kernel), fmap


def build_zz_qsvc(n_features: int, reps: int = 2):
    fmap = ZZFeatureMap(feature_dimension=n_features, reps=reps, entanglement="linear")
    kernel = FidelityQuantumKernel(feature_map=fmap)
    return QSVC(quantum_kernel=kernel), fmap


def build_vqc(n_features: int, optimizer_name: str = "COBYLA", maxiter: int = 100):
    feature_map = ZZFeatureMap(feature_dimension=n_features, reps=1, entanglement="linear")
    ansatz = RealAmplitudes(num_qubits=n_features, reps=1, entanglement="linear")
    optimizer = COBYLA(maxiter=maxiter) if optimizer_name.upper() == "COBYLA" else SPSA(maxiter=maxiter)
    return VQC(feature_map=feature_map, ansatz=ansatz, optimizer=optimizer)


def build_classical_svm():
    return SVC(kernel="rbf")
