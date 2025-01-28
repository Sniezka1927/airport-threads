import os
import time
import sys
from generator import Passenger
from consts import (
    MESSAGE_SEPARATOR,
    MAX_PASSENGERS,
    FLIGHT_CAPACITY,
    FLIGHT_DEPARTURE_TIME,
)


class Lounge:
    def __init__(self, security_read_pipe, dispatcher_read_pipe, dispatcher_write_pipe):
        self.security_read_pipe = security_read_pipe
        self.dispatcher_read_pipe = dispatcher_read_pipe
        self.dispatcher_write_pipe = dispatcher_write_pipe
        self.available_plane_id = -1
        self.available_plane_capacity = 0
        self.dispatcher_buffer = ""  # Dodajemy bufor dla dyspozytora

    def check_for_plane(self):
        if self.available_plane_id != -1:
            return
        try:
            data = os.read(self.dispatcher_read_pipe, 100).decode()
            if data:
                self.dispatcher_buffer += data
                while MESSAGE_SEPARATOR in self.dispatcher_buffer:
                    message, self.dispatcher_buffer = self.dispatcher_buffer.split(
                        MESSAGE_SEPARATOR, 1
                    )
                    msg_type, plane_id, capacity = message.split("|")
                    print(
                        f"Odebrano wiadomość od dyspozytora: {msg_type}, {plane_id}, {capacity}"
                    )
                    if msg_type == "PLANE_READY":
                        self.available_plane_id = int(plane_id)
                        self.available_plane_capacity = int(capacity)
                        print(
                            f"Otrzymano informację o gotowym samolocie: {self.available_plane_id} (pojemność: {capacity})"
                        )

        except BlockingIOError:
            pass


def departure_lounge(security_read_pipe, dispatcher_read_pipe, dispatcher_write_pipe):
    try:
        security_buffer = ""  # Zmieniamy nazwę dla jasności
        waiting_passengers = []
        passengers_count = 0
        lounge = Lounge(security_read_pipe, dispatcher_read_pipe, dispatcher_write_pipe)

        while True:
            # Sprawdzamy samolot przed każdą iteracją
            lounge.check_for_plane()

            # Próbujemy odczytać nowych pasażerów
            try:
                data = os.read(security_read_pipe, 100).decode()
                if data:
                    security_buffer += data

                    while MESSAGE_SEPARATOR in security_buffer:
                        message, security_buffer = security_buffer.split(
                            MESSAGE_SEPARATOR, 1
                        )
                        if message == "END":
                            if passengers_count >= MAX_PASSENGERS:
                                return
                            continue

                        pid, is_vip, baggage_weight, gender = message.split("|")
                        passenger = Passenger(
                            int(pid), is_vip == "True", int(baggage_weight), gender
                        )
                        waiting_passengers.append(passenger)
                        passengers_count += 1
                        print(
                            f"Poczekalnia odlotów: {passenger} dołączył do poczekalni"
                        )

                        # Jeśli mamy samolot i wystarczającą liczbę pasażerów
                        if (
                            lounge.available_plane_id != -1
                            and len(waiting_passengers)
                            >= lounge.available_plane_capacity
                        ):

                            # Sortuj pasażerów - VIP pierwsi
                            waiting_passengers.sort(key=lambda x: (not x.is_vip, x.pid))
                            boarding_passengers = waiting_passengers[
                                : lounge.available_plane_capacity
                            ]
                            waiting_passengers = waiting_passengers[
                                lounge.available_plane_capacity :
                            ]

                            print(
                                f"\nROZPOCZĘCIE BOARDINGU DO SAMOLOTU {lounge.available_plane_id}"
                            )
                            for p in boarding_passengers:
                                print(f"Boarding: {p}")

                            # Wysyłamy potwierdzenie do dyspozytora
                            boarding_complete_msg = f"BOARDING_COMPLETE|{lounge.available_plane_id}{MESSAGE_SEPARATOR}"
                            os.write(
                                dispatcher_write_pipe, boarding_complete_msg.encode()
                            )

                            # Symulacja czasu odlotu
                            time.sleep(FLIGHT_DEPARTURE_TIME)
                            print(f"SAMOLOT {lounge.available_plane_id} ODLECIAŁ\n")

                            # Resetujemy dostępny samolot
                            lounge.available_plane_id = -1
                            lounge.available_plane_capacity = 0

            except BlockingIOError:
                time.sleep(0.1)
                continue

            # Krótka przerwa aby nie obciążać CPU
            time.sleep(0.1)

    except KeyboardInterrupt:
        sys.exit(0)
