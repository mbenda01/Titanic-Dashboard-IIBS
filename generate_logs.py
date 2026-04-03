import json
import random
import time
import os
from datetime import datetime, timezone, timedelta

os.makedirs("logs", exist_ok=True)

pages = ["vue_generale", "analyse_survie", "filtres", "donnees_brutes"]
classes = [1, 2, 3]
sexes = ["male", "female"]
age_groups = ["Enfant (0-12)", "Ado (13-18)", "Adulte (19-35)", "Senior (36-60)", "Aine (60+)"]

# Simule des événements sur les 24 dernières heures
base_time = datetime.now(timezone.utc) - timedelta(hours=24)

with open("logs/app.log", "a") as f:
    for i in range(300):
        # Timestamp réparti sur 24h pour avoir un beau line chart
        ts = base_time + timedelta(seconds=i * 288)

        # Visite de page
        event = {
            "timestamp": ts.isoformat(),
            "event_type": "page_visit",
            "details": {
                "page": random.choice(pages)
            }
        }
        f.write(json.dumps(event) + "\n")

        # Filtre appliqué (simulé toutes les 2 visites)
        if i % 2 == 0:
            event2 = {
                "timestamp": (ts + timedelta(seconds=10)).isoformat(),
                "event_type": "filter_apply",
                "details": {
                    "classes": random.sample(classes, k=random.randint(1, 3)),
                    "sexes": random.sample(sexes, k=random.randint(1, 2)),
                    "n_result": random.randint(50, 800)
                }
            }
            f.write(json.dumps(event2) + "\n")

        # Export CSV (simulé occasionnellement)
        if i % 15 == 0:
            event3 = {
                "timestamp": (ts + timedelta(seconds=20)).isoformat(),
                "event_type": "export_csv",
                "details": {
                    "rows": random.randint(100, 700)
                }
            }
            f.write(json.dumps(event3) + "\n")

print("✅ Logs générés dans logs/app.log")
print(f"   → ~{300 + 150 + 20} événements simulés sur 24h")