from utils import get_latest_log_entries
from datetime import datetime
from consts import MESSAGES, LOCATIONS, STAIRS_CAPACITY, AIRPLANE_CAPACITY, AIRPORT_LUGGAGE_LIMIT, STATS_DIRECTORY
import json

class Statistics:
    """Klasa do zbierania i zapisywania statystyk z logów"""
    def __init__(self):
        logs, timestamp = get_latest_log_entries()
        self.logs = logs
        self.timestamp = timestamp
        self.duration = 0
        self.entered = 0
        self.total_luggage_controls = 0
        self.luggage_checked = 0
        self.luggage_rejected = 0
        self.total_security_controls = 0
        self.security_checked = 0
        self.security_rejected = 0
        self.stairs_used = 0
        self.passengers = 0
        self.airplanes_ready = 0
        self.flights_started = 0
        self.flights_completed = 0
        self.was_shutdown = False

    def get_location(self, log: str):
        start = log.find('-') + 1  # Position after the first '-'
        end = log.find(':', start)  # First ':' after the '-'
        return log[start:end].strip()

    def set_duration(self):
        start_time = self.logs[0][0:self.logs[0].find('-')].strip()
        end_time = self.logs[-1][0:self.logs[-1].find('-')].strip()

        time_format = "%H:%M:%S"
        start = datetime.strptime(start_time, time_format)
        end = datetime.strptime(end_time, time_format)

        duration = end - start
        self.duration = duration.total_seconds()


    def process_generator_logs(self, log: str):
        self.entered += 1

    def process_luggage_logs(self, log: str):
        if MESSAGES.LUGGAGE_CHECK_OK in log:
            self.luggage_checked += 1
        elif MESSAGES.LUGGAGE_CHECK_REJECT in log:
            self.luggage_rejected += 1
        elif MESSAGES.LUGGAGE_CHECK_BEGIN in log:
            self.total_luggage_controls += 1

    def process_security_logs(self, log: str):
        if MESSAGES.SECURITY_CONTROL_OK in log:
            self.security_checked += 1
        elif MESSAGES.SECURITY_CONTROL_REJECT in log:
            self.security_rejected += 1
        elif MESSAGES.SECURITY_CONTROL_BEGIN in log:
            self.total_security_controls += 1

    def process_gate_logs(self, log: str):
        if MESSAGES.MOVING_PASSENGERS in log:
            self.stairs_used += 1
        if MESSAGES.RECEIVED_AIRPLANE_READY in log:
            self.airplanes_ready += 1

    def process_dispatcher_logs(self, log: str):
        if MESSAGES.OVERPOPULATE in log:
            self.was_shutdown = True

    def process_airplane_logs(self, log: str):
        if MESSAGES.FLIGHT_START in log:
            self.flights_started += 1
        elif MESSAGES.FLIGHT_ENDED in log:
            self.flights_completed += 1
        elif MESSAGES.PASSENGERS_BOARDED in log:
            start = log.find(f"{LOCATIONS.AIRPLANE}: ") + len(f"{LOCATIONS.AIRPLANE}: ")
            end = log.find(" ", start)
            self.passengers += int(log[start:end])

    def collect(self):
        """Zbiera i zapisuje statystyki do pliku"""
        self.set_duration()
        for log in self.logs:
            location = self.get_location(log)
            if location == LOCATIONS.ENTRANCE:
                self.process_generator_logs(log)
            elif location == LOCATIONS.LUGGAGE:
                self.process_luggage_logs(log)
            elif location == LOCATIONS.SECURITY:
                self.process_security_logs(log)
            elif location == LOCATIONS.GATE:
                self.process_gate_logs(log)
            elif location == LOCATIONS.DISPATCHER:
                self.process_dispatcher_logs(log)
            elif location == LOCATIONS.AIRPLANE:
                self.process_airplane_logs(log)
            else:
                continue

    def save(self):
        stats_dict = {
            "duration": self.duration,
            "passengers": {
                "entered": self.entered,
                "boarded": self.passengers
            },
            "luggage_control": {
                "total_controls": self.total_luggage_controls,
                "checked": self.luggage_checked,
                "rejected": self.luggage_rejected
            },
            "security_control": {
                "total_controls": self.total_security_controls,
                "checked": self.security_checked,
                "rejected": self.security_rejected
            },
            "stairs": {
                "times_used": self.stairs_used
            },
            "airplanes": {
                "ready": self.airplanes_ready,
                "started": self.flights_started,
                "completed": self.flights_completed
            },
            "airport": {
                "was_shutdown": self.was_shutdown,
                "stairs_capacity": STAIRS_CAPACITY,
                "luggage_limit": AIRPORT_LUGGAGE_LIMIT,
                "airplane_capacity": AIRPLANE_CAPACITY
            }
        }

        print("Stats:", stats_dict)

        savepath = f"{STATS_DIRECTORY}/statistics_{self.timestamp}.json"


        with open(savepath, 'w', encoding='utf-8') as f:
            json.dump(stats_dict, f, indent=4, ensure_ascii=False)

def main():
    stats = Statistics()
    stats.collect()
    stats.save()

if __name__ == "__main__":
    main()