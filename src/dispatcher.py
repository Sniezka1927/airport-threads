import time
import os
from multiprocessing import Process, Queue, Value
from consts import (
    SECURITY_CHECKED_FILE,
    AIRPORT_AIRPLANES_COUNT,
    AIRPLANE_CAPACITY,
    MIN_PASSENGERS_TO_BOARD,
    MIN_AIRPLANE_LUGGAGE_CAPACITY,
    MAX_AIRPLANE_LUGGAGE_CAPACITY,
    MAX_PASSENGERS_FOR_SHUTDOWN,
    MESSAGES,
    LOCATIONS
)
from gate import process_passengers
from airplane import board_passengers
from utils import read_passengers, timestamp, log
from random import  randint

class Dispatcher:
    def __init__(self):
        self.gate_queue = Queue()
        self.airplane_queue = Queue()
        self.luggage_queue = Queue()

        # Ustawienie minimalnych praw dostępu dla kolejek, prawa tylko dla właściciela
        for queue in [self.gate_queue, self.airplane_queue, self.luggage_queue]:
            fd = queue._reader.fileno()
            os.fchmod(fd, 0o600)
            fd = queue._writer.fileno()
            os.fchmod(fd, 0o600)

        self.active_processes = []
        self.running = True
        # Pamięci współdzielonej dla dostępnych samolotów
        self.available_airplanes = Value('i', AIRPORT_AIRPLANES_COUNT)

    def dispatcher_loop(self):
        """Głowna pętla dyspozytora, sprawdza czy są pasażerowie do obsłużenia i czy są dostępne samoloty"""
        while self.running:
            # Usuń zakończone loty (procesy samolotów)
            self.active_processes = [p for p in self.active_processes if p.is_alive()]
            passengers = read_passengers(SECURITY_CHECKED_FILE)
            num_passengers = len(passengers)

            # Jeśli jest wystarczająca liczba pasażerów i są dostępne samoloty, przygotuj samolot do odlotu
            if num_passengers >= MIN_PASSENGERS_TO_BOARD and self.available_airplanes.value > 0:
                with self.available_airplanes.get_lock():
                    self.available_airplanes.value -= 1
                # Limit bagażu dla samolotu
                luggage_limit = randint(MIN_AIRPLANE_LUGGAGE_CAPACITY, MAX_AIRPLANE_LUGGAGE_CAPACITY)
                log(
                    f"{timestamp()} - {LOCATIONS.DISPATCHER}: {MESSAGES.AIRPLANE_READY} (dostępnych: {self.available_airplanes.value})")

                # Tworzenie nowego procesu dla samolotu
                airplane_process = Process(target=board_passengers,
                                           args=(self.airplane_queue, AIRPLANE_CAPACITY, luggage_limit,
                                                 self.available_airplanes))
                airplane_process.start()
                self.active_processes.append(airplane_process)

                # Przekaż informacje o gotowości samolotu do bramki
                self.gate_queue.put(("airplane_ready", AIRPLANE_CAPACITY, luggage_limit))

                signal = self.airplane_queue.get()
                # Jeśli wszyscy pasażerowie weszli na pokład, pozwól na start samolotu
                if signal == "boarding_complete":
                    self.airplane_queue.put("takeoff_allowed")
            else:
                time.sleep(1)

            # Sprawdź czy lotnisko nie jest przepełnione, jeżeli tak, zamknij lotnisko
            if num_passengers >= MAX_PASSENGERS_FOR_SHUTDOWN:
                log(
                    f"{timestamp()} - {LOCATIONS.DISPATCHER}: {MESSAGES.OVERPOPULATE}")
                self.luggage_queue.put("close_airport")
                self.gate_queue.put(("close_airport", None, None))



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

        # Czyszczenie kolejek
        for queue in [self.gate_queue, self.airplane_queue, self.luggage_queue]:
            queue.close()
            queue.join_thread()

        # Czyszcenie pamięci współdzielonej
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