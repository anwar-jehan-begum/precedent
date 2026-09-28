from data.alert_generator import generate_alerts


FILE = "data/HI-Small/HI-Small_Trans.csv"


alerts = generate_alerts(
    FILE,
    nrows=200_000,
    max_alerts=5000
)

print("\n==============================")
print("ALERT QUALITY")
print("==============================")

print("Total alerts:", len(alerts))

laundering = sum(
    alert["is_laundering"] == 1
    for alert in alerts
)

normal = sum(
    alert["is_laundering"] == 0
    for alert in alerts
)

print("Laundering alerts:", laundering)
print("Normal alerts:", normal)

if alerts:
    print(
        "Laundering percentage:",
        round(laundering / len(alerts) * 100, 2),
        "%"
    )

print("\nPatterns:")

pattern_counts = {}

for alert in alerts:

    pattern = alert["transaction_pattern"]

    pattern_counts[pattern] = (
        pattern_counts.get(pattern, 0) + 1
    )

for pattern, count in sorted(
    pattern_counts.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{pattern}: {count}")