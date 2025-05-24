# core/logger.py
import os
import csv
from datetime import datetime

class EventLogger:
    def __init__(self, log_dir="data/logs"):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(log_dir, f"log_{timestamp}.csv")
        self.file = open(self.path, "w", newline="")
        self.writer = csv.writer(self.file)
        self.writer.writerow(["turn", "event_type", "bunny_name", "age", "location", "details", "controller"])

    def log(self, turn, event_type, bunny, detail, controller="FSM"):
        self.writer.writerow([
            turn,
            event_type,
            bunny.name,
            bunny.age,
            f"({bunny.x},{bunny.y})",
            detail,
            controller
        ])
        self.file.flush()

    def close(self):
        self.file.close()
