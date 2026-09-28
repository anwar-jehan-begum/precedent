from typing import List, Dict


def evaluate_predictions(
    predictions: List[str],
    actuals: List[int]
) -> Dict:

    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have the same length")

    total = len(actuals)

    correct = 0
    false_positives = 0
    false_negatives = 0

    for prediction, actual in zip(predictions, actuals):

        prediction = prediction.upper()

        # ESCALATE = suspicious / laundering
        predicted_laundering = 1 if prediction == "ESCALATE" else 0

        if predicted_laundering == actual:
            correct += 1

        if predicted_laundering == 1 and actual == 0:
            false_positives += 1

        if predicted_laundering == 0 and actual == 1:
            false_negatives += 1

    accuracy = correct / total if total else 0

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }