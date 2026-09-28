import pandas as pd

FILE = "data/HI-Small/HI-Small_Trans.csv"

# Read a manageable sample for development
df = pd.read_csv(FILE, nrows=200_000)

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

print("Rows loaded:", len(df))

print("\nTime range:")
print(df["Timestamp"].min())
print(df["Timestamp"].max())

print("\nAccounts:")
print("Unique sender accounts:", df["Account"].nunique())
print("Unique receiver accounts:", df["Account.1"].nunique())

print("\nTransaction amount:")
print(df["Amount Paid"].describe())

# Number of transactions per sender account
sender_counts = df.groupby("Account").size()

print("\nTop accounts by transaction count:")
print(sender_counts.sort_values(ascending=False).head(10))

# Accounts with many transactions in the sample
busy_accounts = sender_counts[sender_counts >= 5]

print("\nAccounts with at least 5 transactions:")
print(len(busy_accounts))

# Multiple counterparties
counterparties = (
    df.groupby("Account")["Account.1"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nTop accounts by unique counterparties:")
print(counterparties.head(10))