import pandas as pd

file_path = "data/HI-Small/HI-Small_Trans.csv"

df = pd.read_csv(file_path)

print("\n===== DATASET STATS =====")

print("\nTotal transactions:")
print(len(df))

print("\nLaundering distribution:")
print(df["Is Laundering"].value_counts())

print("\nLaundering percentage:")
print(df["Is Laundering"].value_counts(normalize=True) * 100)

print("\nPayment formats:")
print(df["Payment Format"].value_counts())

print("\nCurrencies:")
print(df["Payment Currency"].value_counts().head(10))

print("\nMissing values:")
print(df.isnull().sum())