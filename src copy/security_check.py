import os
import time
import random
import sys
from generator import Passenger
from consts import (
    MAX_PASSENGERS_PER_STATION,
    SECURITY_CHECK_PROBABILITY,
    MESSAGE_SEPARATOR,
    MAX_SKIP,
)


class SecurityStation:
    def __init__(self, station_id):
        self.station_id = station_id
        self.current_passengers = []
        self.waiting_queue = []
        self.current_gender = None
        self.control_in_progress = False  # Flaga wskazująca czy trwa kontrola
        self.expect_more_passengers = True

    def can_add_passenger(self, passenger):
        if self.control_in_progress:
            return False
        if not self.current_passengers:
            return True
        return (
            len(self.current_passengers) < MAX_PASSENGERS_PER_STATION
            and self.current_gender == passenger.gender
        )

    def add_passenger(self, passenger):
        if not self.current_passengers:
            self.current_gender = passenger.gender
        self.current_passengers.append(passenger)
        print(f"Stanowisko {self.station_id}: Dodano do kontroli: {passenger}")

    def remove_passenger(self, passenger):
        self.current_passengers.remove(passenger)
        if not self.current_passengers:
            self.current_gender = None

    def requires_skip(self, passenger):
        skip = self.waiting_queue[0].pid != passenger.pid
        if skip:
            self.waiting_queue[0].skipped += 1

    def control(self, passenger):
        status = False
        if random.random() < SECURITY_CHECK_PROBABILITY:
            print(
                f"Stanowisko {self.station_id}: {passenger} przeszedł kontrolę bezpieczeństwa."
            )
            status = True
        else:
            print(
                f"Stanowisko {self.station_id}: {passenger} nie przeszedł kontroli bezpieczeństwa."
            )
        self.remove_passenger(passenger)
        return status


def security_check(station_id, read_pipe, write_pipe):
    try:
        buffer = ""
        station = SecurityStation(station_id)

        while True:
            try:
                if station.expect_more_passengers:
                    data = os.read(read_pipe, 100).decode()

                    if data:
                        buffer += data
                        while MESSAGE_SEPARATOR in buffer:
                            message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                            if message == "END":
                                station.expect_more_passengers = False
                                continue

                            pid, is_vip, baggage_weight, gender = message.split("|")
                            passenger = Passenger(
                                int(pid), is_vip == "True", int(baggage_weight), gender
                            )

                            # Dodaj do kolejki oczekujących
                            station.waiting_queue.append(passenger)
                            print(
                                f"Stanowisko {station_id}: Nowy pasażer w kolejce: {passenger}"
                            )
            except BlockingIOError:
                pass

            # Przetwarzanie kolejki
            if len(station.current_passengers) < MAX_PASSENGERS_PER_STATION:
                waiting_vips = [p for p in station.waiting_queue if p.is_vip]
                passengers_with_skip_limit = [
                    p for p in station.waiting_queue if p.skipped >= MAX_SKIP
                ]
                remaining_passengers = [
                    p
                    for p in station.waiting_queue
                    if p not in waiting_vips and p not in passengers_with_skip_limit
                ]

                for passenger in passengers_with_skip_limit:
                    if station.can_add_passenger(passenger):
                        station.add_passenger(passenger)
                        station.waiting_queue.remove(passenger)
                        if (
                            len(station.current_passengers)
                            >= MAX_PASSENGERS_PER_STATION
                        ):
                            break

                for passenger in waiting_vips:
                    if station.can_add_passenger(passenger):
                        station.requires_skip(passenger)
                        station.add_passenger(passenger)
                        station.waiting_queue.remove(passenger)
                        if (
                            len(station.current_passengers)
                            >= MAX_PASSENGERS_PER_STATION
                        ):
                            break

                for passenger in remaining_passengers:
                    if station.can_add_passenger(passenger):
                        station.requires_skip(passenger)
                        station.add_passenger(passenger)
                        station.waiting_queue.remove(passenger)
                        if (
                            len(station.current_passengers)
                            >= MAX_PASSENGERS_PER_STATION
                        ):
                            break

            # Obsługa aktualnie kontrolowanych pasażerów
            if station.current_passengers:
                # Jeśli jest tylko jeden pasażer, kontroluj go indywidualnie
                if len(station.current_passengers) == 1:
                    passenger = station.current_passengers[0]
                    print(
                        f"Stanowisko {station_id}: Rozpoczęcie kontroli indywidualnej dla {passenger}"
                    )
                    time.sleep(1.0)  # Stały czas kontroli 1 sekunda

                    if station.control(passenger):
                        os.write(
                            write_pipe,
                            f"{passenger.pid}|{passenger.is_vip}|{passenger.baggage_weight}|{passenger.gender}{MESSAGE_SEPARATOR}".encode(),
                        )

                # Jeśli są dwie osoby, kontroluj je grupowo
                elif len(station.current_passengers) == MAX_PASSENGERS_PER_STATION:
                    print(
                        f"Stanowisko {station_id}: Rozpoczęcie kontroli grupowej dla {len(station.current_passengers)} pasażerów"
                    )
                    time.sleep(1.0)  # Stały czas kontroli 1 sekunda

                    # Kontrola wszystkich pasażerów w grupie
                    for passenger in station.current_passengers[:]:
                        if station.control(passenger):
                            os.write(
                                write_pipe,
                                f"{passenger.pid}|{passenger.is_vip}|{passenger.baggage_weight}|{passenger.gender}{MESSAGE_SEPARATOR}".encode(),
                            )

    except KeyboardInterrupt:
        sys.exit(0)
