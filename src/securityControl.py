import time
from multiprocessing import Process
from typing import List, Dict, Optional
from dataclasses import dataclass
from consts import (
    MAX_CONTROL_PASSES,
    SECURITY_CHECKED_FILE,
    SECURITY_REJECTED_FILE,
    MESSAGES,
    LOCATIONS,
    SECURITY_CHECKPOINTS_COUNT,
    MAX_PASSENGERS_PER_CHECKPOINT,
)
from utils import (
    ensure_files_exists,
    read_passengers,
    save_passengers,
    timestamp,
    append_passenger,
    log,
    terminate_process,
)
from luggageControl import get_file_name


class SecurityStation:
    def __init__(self, station_id):
        self.station_id = station_id
        self.current_passengers = []
        self.current_gender = None
        self.file_name = get_file_name(station_id)

    def can_add_passenger(self, passenger):
        if not self.current_passengers:
            return True
        return (
            len(self.current_passengers) < MAX_PASSENGERS_PER_CHECKPOINT
            and self.current_gender == passenger["gender"]
        )

    def add_passenger(self, passenger):
        if not self.current_passengers:
            self.current_gender = passenger["gender"]
        self.current_passengers.append(passenger)

    def remove_passenger(self, passenger):
        self.current_passengers.remove(passenger)
        if not self.current_passengers:
            self.current_gender = None

    def requires_skip(self, passenger, waiting_queue):
        skip = waiting_queue[0]["id"] != passenger["id"]
        if skip:
            waiting_queue[0]["controlPassed"] += 1
        return waiting_queue

    def control(self):
        for passenger in self.current_passengers:
            log(
                f"{timestamp()} - {LOCATIONS.SECURITY}: {MESSAGES.SECURITY_CONTROL_BEGIN}"
            )
            if passenger["hasDangerousItems"]:
                log(
                    f"{timestamp()} - {LOCATIONS.SECURITY}: Stanowisko {self.station_id}: Pasażer ID={passenger['id']} "
                    f"(przepuścił: {passenger.get('controlPassed', 0)} osób) Płeć={passenger['gender']} {MESSAGES.SECURITY_CONTROL_REJECT}"
                )
                append_passenger(SECURITY_REJECTED_FILE, passenger)
                terminate_process(int(passenger["id"]), "security")
            else:
                log(
                    f"{timestamp()} - {LOCATIONS.SECURITY}: Stanowisko {self.station_id}: Pasażer ID={passenger['id']} "
                    f"(przepuścił: {passenger.get('controlPassed', 0)} osób) Płeć={passenger['gender']} {MESSAGES.SECURITY_CONTROL_OK}"
                )
                append_passenger(SECURITY_CHECKED_FILE, passenger)

        self.current_passengers = []
        self.current_gender = None

    def get_next_passengers(self):
        waiting_queue = read_passengers(self.file_name)
        waiting_vips = [p for p in waiting_queue if p["isVIP"]]
        passengers_with_skip_limit = [
            p for p in waiting_queue if p["controlPassed"] >= MAX_CONTROL_PASSES
        ]
        remaining_passengers = [
            p
            for p in waiting_queue
            if p not in waiting_vips and p not in passengers_with_skip_limit
        ]

        for passenger in passengers_with_skip_limit:
            if self.can_add_passenger(passenger):
                self.add_passenger(passenger)
                waiting_queue.remove(passenger)
                if len(self.current_passengers) == MAX_PASSENGERS_PER_CHECKPOINT:
                    break

        for passenger in waiting_vips:
            if self.can_add_passenger(passenger):
                waiting_queue = self.requires_skip(passenger, waiting_queue)
                self.add_passenger(passenger)
                waiting_queue.remove(passenger)
                if len(self.current_passengers) == MAX_PASSENGERS_PER_CHECKPOINT:
                    break

        for passenger in remaining_passengers:
            if self.can_add_passenger(passenger):
                waiting_queue = self.requires_skip(passenger, waiting_queue)
                self.add_passenger(passenger)
                waiting_queue.remove(passenger)
                if len(self.current_passengers) == MAX_PASSENGERS_PER_CHECKPOINT:
                    break

        if self.current_passengers:
            self.control()

        save_passengers(self.file_name, waiting_queue)


class SecurityCheckpoint:
    def __init__(self, num_stations: int = SECURITY_CHECKPOINTS_COUNT):
        self.stations = [SecurityStation(i) for i in range(num_stations)]


def process_passengers(checkpoint: SecurityCheckpoint):
    """Główna funkcja przetwarzająca pasażerów na stanowiskach kontroli bezpieczeństwa"""

    for station in checkpoint.stations:
        station.get_next_passengers()


def check_security_continuously():
    """Główna pętla kontroli bezpieczeństwa, sprawdza czy pliki istnieją i przetwarza pasażerów w nieskończoność"""
    ensure_files_exists([SECURITY_CHECKED_FILE, SECURITY_REJECTED_FILE])
    checkpoint = SecurityCheckpoint()

    while True:
        process_passengers(checkpoint)
        time.sleep(1)


if __name__ == "__main__":
    print("Uruchamianie kontroli bezpieczeństwa...")
    process = Process(target=check_security_continuously)
    process.start()

    try:
        process.join()
    except KeyboardInterrupt:
        print("\nZatrzymywanie kontroli bezpieczeństwa...")
        process.terminate()
        print("Kontrola zatrzymana.")
