import time
import os
from multiprocessing import Process
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
from gate import process_passengers
from airplane import board_passengers
from utils import read_passengers, timestamp, log
from random import randint


class Dispatcher:
    def __init__(self):
        self.to_gate_queue = Queue(TO_GATE_QUEUE)
        self.from_gate_queue = Queue(FROM_GATE_QUEUE)
        self.to_airplane_queue = Queue(TO_AIRPLANE_QUEUE)
        self.from_airplane_queue = Queue(FROM_AIRPLANE_QUEUE)
        self.to_luggage_queue = Queue(TO_LUGGAGE_QUEUE)
        self.from_luggage_queue = Queue(FROM_LUGGAGE_QUEUE)
        self.active_processes = []
        self.running = True
        self.available_airplanes = AIRPORT_AIRPLANES_COUNT
        self.is_boarding = False

    def dispatcher_loop(self):
        """Głowna pętla dyspozytora, sprawdza czy są pasażerowie do obsłużenia i czy są dostępne samoloty"""
        while self.running:
            # Usuń zakończone loty (procesy samolotów)
            self.active_processes = [p for p in self.active_processes if p.is_alive()]
            passengers = read_passengers(SECURITY_CHECKED_FILE)
            num_passengers = len(passengers)

            try:
                signal = self.from_airplane_queue.get()
                # Jeśli wszyscy pasażerowie weszli na pokład, pozwól na start samolotu
                if signal == "boarding_complete":
                    self.to_airplane_queue.put("takeoff_allowed")
                    self.is_boarding = False
                elif signal == "fly_completed":
                    self.available_airplanes += 1
            except Empty:
                pass

            # Jeśli jest wystarczająca liczba pasażerów i są dostępne samoloty, przygotuj samolot do odlotu
            if (
                num_passengers >= MIN_PASSENGERS_TO_BOARD
                and self.available_airplanes > 0
                and not self.is_boarding
            ):

                self.is_boarding = True
                self.available_airplanes -= 1
                # Limit bagażu dla samolotu
                luggage_limit = randint(
                    MIN_AIRPLANE_LUGGAGE_CAPACITY, MAX_AIRPLANE_LUGGAGE_CAPACITY
                )
                log(
                    f"{timestamp()} - {LOCATIONS.DISPATCHER}: {MESSAGES.AIRPLANE_READY} (dostępnych: {self.available_airplanes})"
                )

                # Tworzenie nowego procesu dla samolotu
                airplane_process = Process(
                    target=board_passengers,
                    args=(
                        self.from_airplane_queue,
                        self.to_airplane_queue,
                        AIRPLANE_CAPACITY,
                        luggage_limit,
                    ),
                )
                airplane_process.start()
                self.active_processes.append(airplane_process)

                # Przekaż informacje o gotowości samolotu do bramki
                self.to_gate_queue.put(
                    ("airplane_ready", AIRPLANE_CAPACITY, luggage_limit)
                )
            else:
                time.sleep(1)

            # Sprawdź czy lotnisko nie jest przepełnione, jeżeli tak, zamknij lotnisko
            if num_passengers >= MAX_PASSENGERS_FOR_SHUTDOWN:
                log(f"{timestamp()} - {LOCATIONS.DISPATCHER}: {MESSAGES.OVERPOPULATE}")
                self.to_luggage_queue.put("close_airport")
                self.to_gate_queue.put(("close_airport", None, None))

    def terminate_all_processes(self):
        """Zatrzymuje wszystkie procesy samolotów i czysci kolejki"""
        self.running = False
        print("\nKończenie procesów samolotów...")

        # Kończenie procesów samolotów
        for process in self.active_processes:
            if process.is_alive():
                print(f"Kończenie procesu samolotu (PID: {process.pid})")
                process.terminate()

        # Czekanie na zakończenie procesów
        for process in self.active_processes:
            process.join(timeout=2)

        self.available_airplanes = None

        print("Zakończone wszystkie procesy samolotów.")


def main():
    dispatcher = Dispatcher()

    dispatcher_process = Process(target=dispatcher.dispatcher_loop)
    gate_process = Process(target=process_passengers, args=(dispatcher.gate_queue,))

    try:
        dispatcher_process.start()
        gate_process.start()

        dispatcher_process.join()
        gate_process.join()

    except KeyboardInterrupt:
        dispatcher.terminate_all_processes()

        if dispatcher_process.is_alive():
            dispatcher_process.terminate()

        if gate_process.is_alive():
            gate_process.terminate()

        dispatcher_process.join()
        gate_process.join()


if __name__ == "__main__":
    main()
