import numpy as np
from sklearn.preprocessing import MinMaxScaler


def scale_for_quantum_angles(X):
    scaler = MinMaxScaler(feature_range=(0, np.pi))
    return scaler.fit_transform(X), scaler
