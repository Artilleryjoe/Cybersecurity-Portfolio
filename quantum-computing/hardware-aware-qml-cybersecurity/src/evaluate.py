from sklearn.metrics import accuracy_score, confusion_matrix, f1_score


def metrics(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    return {"accuracy": float(acc), "f1": float(f1), "fpr": float(fpr)}
