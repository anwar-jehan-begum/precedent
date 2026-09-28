import pandas as pd

file_path = "data/HI-Small/HI-Small_Trans.csv"

df = pd.read_csv(file_path)

print("\n===== AMOUNT STATISTICS =====")

print(df["Amount Paid"].describe(
    percentiles=[0.50, 0.75, 0.90, 0.95, 0.99, 0.995, 0.999]
))

print("\n===== LAUNDERING AMOUNT STATISTICS =====")

laundering = df[df["Is Laundering"] == 1]

print(laundering["Amount Paid"].describe(
    percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]
))

print("\n===== NORMAL AMOUNT STATISTICS =====")

normal = df[df["Is Laundering"] == 0]

print(normal["Amount Paid"].describe(
    percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]
))

print("\n===== LAUNDERING PAYMENT FORMATS =====")

print(
    laundering["Payment Format"]
    .value_counts()
)

print("\n===== LAUNDERING CURRENCIES =====")

print(
    laundering["Payment Currency"]
    .value_counts()
)

print("\n===== LAUNDERING BANK PAIRS =====")

bank_pairs = (
    laundering
    .groupby(["From Bank", "To Bank"])
    .size()
    .sort_values(ascending=False)
    .head(10)
)

print(bank_pairs)