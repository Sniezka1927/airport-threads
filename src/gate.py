import time
from queue_handler import Queue, Empty
from consts import (
    SECURITY_CHECKED_FILE,
    STAIRS_FILE,
    STAIRS_CAPACITY,
    MESSAGES,
    LOCATIONS,
)
from utils import read_passengers, save_passengers, timestamp, log


def select_optimal_passengers(
    passengers: list, remaining_capacity: int, remaining_luggage: int
) -> list:
    """
    Wybiera grupę pasażerów, którzy zmieszczą się na schodach i ich bagaże zmieszczą się w samolocie
    """
    if not passengers:
        return []

    # Posortuj pasażerów po wadze bagażu
    # sorted_passengers = sorted(passengers, key=lambda x: x.get('luggageWeight', 0))

    selected = []
    current_luggage = 0

    # Wybierz pasażerów, którzy zmieszczą się na schodach i ich bagaże zmieszczą się w samolocie
    for passenger in passengers:
        passenger_luggage = passenger.get("luggageWeight", 0)
        if (
            len(selected) < remaining_capacity
            and current_luggage + passenger_luggage <= remaining_luggage
        ):
            selected.append(passenger)
            current_luggage += passenger_luggage

    return selected


def handle_passengers(queue: Queue):
    """
    Obsługuje pasażerów czekających na wejście na pokład samolotu
    """
    try:
        signal, airplane_capacity, luggage_limit = queue.get()

        try:
            signal = queue.get()
            if signal == "close_airport":
                return
        except Empty:
            pass

        # Jeśli otrzymano sygnał o gotowości samolotu
        if signal == "airplane_ready":
            log(f"{timestamp()} - {LOCATIONS.GATE}: {MESSAGES.RECEIVED_AIRPLANE_READY}")
            boarded_passengers = 0
            total_luggage = 0

            # Główna pętla obsługi pasażerów
            while boarded_passengers < int(airplane_capacity):
                # Odczytaj aktualną listę pasażerów przed każdą iteracją
                passengers = read_passengers(SECURITY_CHECKED_FILE)
                if not passengers:
                    time.sleep(1)  # Czekaj na nowych pasażerów
                    continue

                # Czekaj na opuszczenie schodów przez pasażerów
                while len(read_passengers(STAIRS_FILE)) > 0:
                    time.sleep(0.5)
                    # Ponownie sprawdź pasażerów z kontroli bezpieczeństwa
                    passengers = read_passengers(SECURITY_CHECKED_FILE)

                remaining_capacity = min(
                    STAIRS_CAPACITY, int(airplane_capacity) - boarded_passengers
                )
                remaining_luggage = int(luggage_limit) - total_luggage

                # Wybierz pasażerów, którzy zmieszczą się na schodach i ich bagaże zmieszczą się w samolocie
                batch = select_optimal_passengers(
                    passengers, remaining_capacity, remaining_luggage
                )

                if not batch:
                    time.sleep(1)  # Czekaj na nowych pasażerów jeśli nie można wybrać grupy
                    continue

                batch_luggage = sum(
                    passenger.get("luggageWeight", 0) for passenger in batch
                )

                log(
                    f"{timestamp()} - {LOCATIONS.GATE}: wchodzi {len(batch)} (Waga bagaży: {batch_luggage}kg) {MESSAGES.MOVING_PASSENGERS}"
                )

                # Aktualizuj listę pasażerów w pliku security checked
                current_security_checked = read_passengers(SECURITY_CHECKED_FILE)
                new_security_checked = [p for p in current_security_checked if p not in batch]
                
                # Zapisz zaktualizowane listy
                save_passengers(STAIRS_FILE, batch)
                save_passengers(SECURITY_CHECKED_FILE, new_security_checked)

                boarded_passengers += len(batch)
                total_luggage += batch_luggage
                time.sleep(1)  # Czas na przejście grupy pasażerów
    except Empty:
        pass

def process_passengers(queue: Queue):
    """Główna funkcja obsługująca pasażerów na bramce"""
    log(f"{timestamp()} - {LOCATIONS.GATE}: {MESSAGES.GATE_READY}")
    while True:
        handle_passengers(queue)
        time.sleep(1)
