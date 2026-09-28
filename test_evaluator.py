from agent.evaluator import evaluate_predictions


predictions = [
    "ESCALATE",
    "CLEAR",
    "ESCALATE",
    "CLEAR",
    "ESCALATE"
]

actuals = [
    1,
    0,
    0,
    0,
    1
]

result = evaluate_predictions(predictions, actuals)

print("===== EVALUATION =====")
print("Total:", result["total"])
print("Correct:", result["correct"])
print("Accuracy:", result["accuracy"])
print("False Positives:", result["false_positives"])
print("False Negatives:", result["false_negatives"])
