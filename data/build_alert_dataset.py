import pandas as pd

from data.alert_generator import generate_alerts


FILE = "data/HI-Small/HI-Small_Trans.csv"


# Generate a larger pool
alerts = generate_alerts(
    FILE,
    nrows=200_000,
    max_alerts=20_000
)

df = pd.DataFrame(alerts)

print("\nGenerated:", len(df))

print("\nGround truth:")
print(df["is_laundering"].value_counts())


# Separate classes
laundering = df[df["is_laundering"] == 1]
normal = df[df["is_laundering"] == 0]


print("\nLaundering alerts:", len(laundering))
print("Normal alerts:", len(normal))


# Keep all laundering alerts.
# Take a larger normal sample.
normal_sample = normal.sample(
    n=min(len(normal), len(laundering) * 20),
    random_state=42
)


evaluation = pd.concat(
    [laundering, normal_sample],
    ignore_index=True
)


# Shuffle
evaluation = evaluation.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


output_file = "data/evaluation_alerts.csv"

evaluation.to_csv(
    output_file,
    index=False
)


print("\n==============================")
print("EVALUATION DATASET")
print("==============================")

print("Saved:", output_file)
print("Total:", len(evaluation))

print("\nGround truth:")
print(
    evaluation["is_laundering"].value_counts()
)

print("\nSaved successfully!")