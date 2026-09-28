from data.alert_generator import generate_alerts


FILE = "data/HI-Small/HI-Small_Trans.csv"


alerts = generate_alerts(
    FILE,
    nrows=200_000,
    max_alerts=20
)


print("\n==============================")
print("GENERATED AML ALERTS")
print("==============================")

print("Number of alerts:", len(alerts))

for alert in alerts[:5]:

    print("\nAlert:")
    
    for key, value in alert.items():
        print(f"{key}: {value}")