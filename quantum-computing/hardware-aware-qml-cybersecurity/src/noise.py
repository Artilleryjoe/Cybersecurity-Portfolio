from qiskit_aer.noise import NoiseModel, depolarizing_error


def depolarizing_noise_model(single_qubit_err: float = 0.001, two_qubit_err: float = 0.01):
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(single_qubit_err, 1), ["x", "y", "z", "rx", "ry", "rz", "h", "p"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(two_qubit_err, 2), ["cx", "cz"])
    return noise_model
