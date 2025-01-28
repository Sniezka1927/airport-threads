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

        if not queue.empty():
            signal = queue.get()
            if signal == "close_airport":
                return

        # Jeśli otrzymano sygnał o gotowości samolotu
        if signal == "airplane_ready":
            log(f"{timestamp()} - {LOCATIONS.GATE}: {MESSAGES.RECEIVED_AIRPLANE_READY}")
            passengers = read_passengers(SECURITY_CHECKED_FILE)
            boarded_passengers = 0
            total_luggage = 0

            # Główna pętla obsługi pasażerów
            while boarded_passengers < airplane_capacity and passengers:
                # Czekaj na opuszczenie schodów przez pasażerów
                while len(read_passengers(STAIRS_FILE)) > 0:
                    time.sleep(0.5)

                remaining_capacity = min(
                    STAIRS_CAPACITY, airplane_capacity - boarded_passengers
                )
                remaining_luggage = luggage_limit - total_luggage

                # Wybierz pasażerów, którzy zmieszczą się na schodach i ich bagaże zmieszczą się w samolocie
                batch = select_optimal_passengers(
                    passengers, remaining_capacity, remaining_luggage
                )

                if not batch:
                    break

                batch_luggage = sum(
                    passenger.get("luggageWeight", 0) for passenger in batch
                )

                log(
                    f"{timestamp()} - {LOCATIONS.GATE}: wchodzi {len(batch)} (Waga bagaży: {batch_luggage}kg) {MESSAGES.MOVING_PASSENGERS}"
                )

                # Usuń pasażerów z listy oczekujących
                new_passengers = []
                for passenger in passengers:
                    if passenger not in batch:
                        new_passengers.append(passenger)
                passengers = new_passengers

                save_passengers(STAIRS_FILE, batch)
                save_passengers(SECURITY_CHECKED_FILE, passengers)

                boarded_passengers += len(batch)
                total_luggage += batch_luggage
                time.sleep(1)  # Time to move the group
    except Empty:
        pass


def process_passengers(queue: Queue):
    """Główna funkcja obsługująca pasażerów na bramce"""
    log(f"{timestamp()} - {LOCATIONS.GATE}: {MESSAGES.GATE_READY}")
    while True:
        handle_passengers(queue)
        time.sleep(1)
