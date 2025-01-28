import time
import os
from queue_handler import Queue, Empty
from consts import (
    SECURITY_CHECKED_FILE,
    AIRPORT_AIRPLANES_COUNT,
    AIRPLANE_CAPACITY,
    MIN_PASSENGERS_TO_BOARD,
    MIN_AIRPLANE_LUGGAGE_CAPACITY,
    MAX_AIRPLANE_LUGGAGE_CAPACITY,
    MAX_PASSENGERS_FOR_SHUTDOWN,
    MESSAGES,
    LOCATIONS,
    TO_AIRPLANE_QUEUE,
    TO_GATE_QUEUE,
    TO_LUGGAGE_QUEUE,
    FROM_AIRPLANE_QUEUE,
    FROM_GATE_QUEUE,
    FROM_LUGGAGE_QUEUE,
)
from airplane import board_passengers
from utils import read_passengers, timestamp, log, terminate_process
from random import randint


class Dispatcher:
    def __init__(self):
        self.to_gate_queue = Queue(TO_GATE_QUEUE)
        self.from_gate_queue = Queue(FROM_GATE_QUEUE)
        self.to_airplane_queue = Queue(TO_AIRPLANE_QUEUE)
        self.from_airplane_queue = Queue(FROM_AIRPLANE_QUEUE)
        self.to_luggage_queue = Queue(TO_LUGGAGE_QUEUE)
        self.from_luggage_queue = Queue(FROM_LUGGAGE_QUEUE)
        self.airplane_pids = set()  # Zbiór aktywnych PID-ów samolotów
        self.running = True
        self.available_airplanes = AIRPORT_AIRPLANES_COUNT
        self.is_boarding = False

    def create_airplane_process(self, airplane_capacity, luggage_limit):
        """Tworzy nowy proces samolotu używając os.fork()"""
        pid = os.fork()

        if pid == 0:
            # Proces dziecka (samolot)
            try:
                board_passengers(
                    self.from_airplane_queue,
                    self.to_airplane_queue,
                    airplane_capacity,
                    luggage_limit,
                )
                os._exit(0)
            except KeyboardInterrupt:
                os._exit(0)
        else:
            # Proces rodzica (dispatcher)
            self.airplane_pids.add(pid)
            log(
                f"{timestamp()} - {LOCATIONS.DISPATCHER}: Utworzono nowy samolot (PID: {pid})"
            )
            return pid

    def check_finished_airplanes(self):
        """Sprawdza czy któryś z procesów samolotów zakończył pracę"""
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid > 0 and pid in self.airplane_pids:
                self.airplane_pids.remove(pid)
                self.available_airplanes += 1
                exit_code = os.WEXITSTATUS(status)
                log(
                    f"{timestamp()} - {LOCATIONS.DISPATCHER}: Samolot (PID: {pid}) zakończył pracę"
                    + f" {'poprawnie' if exit_code == 0 else 'z błędem'}"
                )
        except OSError:
            pass

    def dispatcher_loop(self):
        """Główna pętla dyspozytora"""
        while self.running:
            # Sprawdź zakończone procesy samolotów
            self.check_finished_airplanes()

            passengers = read_passengers(SECURITY_CHECKED_FILE)
            num_passengers = len(passengers)

            try:
                signal = self.from_airplane_queue.get()
                if signal == "boarding_complete":
                    self.to_airplane_queue.put("takeoff_allowed")
                    self.is_boarding = False
            except Empty:
                pass

            # Uruchom nowy samolot jeśli są spełnione warunki
            if (
                num_passengers >= MIN_PASSENGERS_TO_BOARD
                and self.available_airplanes > 0
                and not self.is_boarding
            ):
                self.is_boarding = True
                self.available_airplanes -= 1
                luggage_limit = randint(
                    MIN_AIRPLANE_LUGGAGE_CAPACITY, MAX_AIRPLANE_LUGGAGE_CAPACITY
                )
                log(
                    f"{timestamp()} - {LOCATIONS.DISPATCHER}: {MESSAGES.AIRPLANE_READY} "
                    f"(dostępnych: {self.available_airplanes})"
                )

                # Tworzenie nowego procesu samolotu
                self.create_airplane_process(AIRPLANE_CAPACITY, luggage_limit)

                # Przekaż informacje o gotowości samolotu do bramki
                self.to_gate_queue.put(
                    ("airplane_ready", AIRPLANE_CAPACITY, luggage_limit)
                )
            else:
                time.sleep(1)

            # Sprawdź przepełnienie lotniska
            if num_passengers >= MAX_PASSENGERS_FOR_SHUTDOWN:
                log(f"{timestamp()} - {LOCATIONS.DISPATCHER}: {MESSAGES.OVERPOPULATE}")
                self.to_luggage_queue.put("close_airport")
                self.to_gate_queue.put(("close_airport", None, None))
                break

    def terminate_all_processes(self):
        """Czyści stan dyspozytora bez kończenia procesów"""
        self.running = False
        for pid in list(self.airplane_pids):
            terminate_process(pid, "airplane")
        self.airplane_pids.clear()
        self.available_airplanes = None
        print("Dispatcher zakończył pracę.")
