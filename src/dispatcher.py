import os
import time
import random
import sys
from consts import (
    MESSAGE_SEPARATOR,
    DISPATCHER_INTERVAL,
    MIN_PLANE_CAPACITY,
    MAX_PLANE_CAPACITY,
    MSG_PLANE_READY,
    MSG_BOARDING_COMPLETE,
    MSG_END,
)


class Plane:
    def __init__(self, plane_id, capacity):
        self.plane_id = plane_id
        self.capacity = capacity
        self.status = "ready"  # ready, boarding, departed

    def __str__(self):
        return f"Samolot {self.plane_id} (pojemność: {self.capacity}, status: {self.status})"


def dispatcher(write_pipe, read_pipe):
    try:
        plane_id = 1
        buffer = ""
        active_plane = None

        while True:
            # Sprawdź czy jest aktywny lot w trakcie boardingu
            if active_plane is None:
                # Generuj nowy samolot
                capacity = random.randint(MIN_PLANE_CAPACITY, MAX_PLANE_CAPACITY)
                active_plane = Plane(plane_id, capacity)
                print(f"\nDyspozytor: Nowy samolot gotowy: {active_plane}")

                # Wyślij informację o gotowym samolocie
                message = f"{MSG_PLANE_READY}|{plane_id}|{capacity}"
                os.write(write_pipe, f"{message}{MESSAGE_SEPARATOR}".encode())
                plane_id += 1

            # Sprawdź odpowiedź od lounge
            try:
                data = os.read(read_pipe, 100).decode()
                if data:
                    buffer += data
                    while MESSAGE_SEPARATOR in buffer:
                        message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                        if message == MSG_END:
                            print("Dyspozytor: Otrzymano sygnał zakończenia pracy")
                            os.write(
                                write_pipe, f"{MSG_END}{MESSAGE_SEPARATOR}".encode()
                            )
                            return

                        msg_type, completed_plane_id = message.split("|")
                        if msg_type == MSG_BOARDING_COMPLETE:
                            print(
                                f"Dyspozytor: Boarding samolotu {completed_plane_id} zakończony"
                            )
                            if (
                                active_plane
                                and str(active_plane.plane_id) == completed_plane_id
                            ):
                                active_plane.status = "departed"
                                active_plane = None
                                # Czekaj przed przygotowaniem kolejnego samolotu
                                time.sleep(DISPATCHER_INTERVAL)

            except BlockingIOError:
                time.sleep(0.1)
                continue

    except KeyboardInterrupt:
        os.write(write_pipe, f"{MSG_END}{MESSAGE_SEPARATOR}".encode())
        sys.exit(0)
