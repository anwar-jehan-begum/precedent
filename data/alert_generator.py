import pandas as pd


def generate_alerts(
    file_path,
    nrows=200_000,
    max_alerts=100
):

    df = pd.read_csv(file_path, nrows=nrows)

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    df = df.sort_values(
        ["Account", "Timestamp"]
    ).reset_index(drop=True)

    # -----------------------------------------
    # High-value threshold
    # -----------------------------------------

    high_value_threshold = df["Amount Paid"].quantile(0.99)

    alerts = []

    # -----------------------------------------
    # Analyze each account
    # -----------------------------------------

    for account, group in df.groupby("Account"):

        group = group.sort_values("Timestamp").copy()

        # Previous transaction time
        group["previous_timestamp"] = (
            group["Timestamp"].shift(1)
        )

        # Time since previous transaction
        group["minutes_since_previous"] = (
            group["Timestamp"]
            - group["previous_timestamp"]
        ).dt.total_seconds() / 60

        # -----------------------------------------
        # For each transaction
        # -----------------------------------------

        for index, row in group.iterrows():

            reasons = []

            # Rule 1: High-value transaction
            if row["Amount Paid"] >= high_value_threshold:
                reasons.append("high_value_transaction")

            # Rule 2: Rapid movement
            if (
                pd.notna(row["minutes_since_previous"])
                and row["minutes_since_previous"] <= 30
            ):
                reasons.append("rapid_movement")

            # -----------------------------------------
            # Recent 30-minute window
            # -----------------------------------------

            start_time = row["Timestamp"] - pd.Timedelta(
                minutes=30
            )

            recent = group[
                (group["Timestamp"] >= start_time)
                & (group["Timestamp"] <= row["Timestamp"])
            ]

            # Rule 3: Multiple transfers
            if len(recent) >= 3:
                reasons.append("multiple_transfers")

            # Rule 4: Multiple counterparties
            unique_counterparties = (
                recent["Account.1"].nunique()
            )

            if unique_counterparties >= 3:
                reasons.append("multiple_counterparties")

            # -----------------------------------------
            # Generate alert only if at least
            # two signals are present
            # -----------------------------------------

            if len(reasons) < 2:
                continue

            alert = {
                "alert_id": f"AML-{len(alerts) + 1:05d}",

                "customer_id": str(
                    row["Account"]
                ),

                "amount": float(
                    row["Amount Paid"]
                ),

                "currency": row[
                    "Payment Currency"
                ],

                "timestamp": str(
                    row["Timestamp"]
                ),

                "from_bank": str(
                    row["From Bank"]
                ),

                "to_bank": str(
                    row["To Bank"]
                ),

                "counterparty": str(
                    row["Account.1"]
                ),

                "payment_format": row[
                    "Payment Format"
                ],

                "transaction_pattern": ", ".join(
                    reasons
                ),

                # Ground truth.
                # DO NOT send this field to the AI.
                "is_laundering": int(
                    row["Is Laundering"]
                )
            }

            alerts.append(alert)

            if len(alerts) >= max_alerts:
                return alerts

    return alerts