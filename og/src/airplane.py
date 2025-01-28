import sys
import time
from multiprocessing import Queue, Value
from consts import STAIRS_FILE, FLIGHT_DURATION, TOTAL_PASSENGER_CHECKS, MESSAGES, LOCATIONS
from utils import read_passengers, save_passengers, timestamp, log

def board_passengers(airplane_queue: Queue, airplane_capacity: int, luggage_limit: int, available_airplanes: Value):
    """Proces obsługujący wejście pasażerów na pokład samolotu """
    boarded_passengers = 0
    total_luggage = 0
    remaining_luggage = 0
    total_checks = 0
    try:
        # Główna pętla obsługi pasażerów
        while boarded_passengers < airplane_capacity and total_checks <= TOTAL_PASSENGER_CHECKS:
            total_checks += 1
            passengers_on_stairs = read_passengers(STAIRS_FILE)

            # Jeśli są pasażerowie na schodach to obsłuż ich
            if len(passengers_on_stairs) > 0:
                current_luggage = sum(passenger.get('luggageWeight', 0) for passenger in passengers_on_stairs)
                log(f"{timestamp()} - {LOCATIONS.AIRPLANE}: {len(passengers_on_stairs)} {MESSAGES.PASSENGERS_BOARDED}")
                boarded_passengers += len(passengers_on_stairs)
                total_luggage += current_luggage
                save_passengers(STAIRS_FILE, [])
                time.sleep(2)
            else:
                time.sleep(1)


        # Jeżeli przekroczono limit bagażu, ogranicz go do limitu, następny samolot zabierze pozostały bagaż
        if total_luggage > luggage_limit:
            remaining_luggage = total_luggage - luggage_limit
            total_luggage = luggage_limit


        log(f"{timestamp()} - {LOCATIONS.AIRPLANE}: {MESSAGES.BOARDING_COMPLETED}")
        # Wyslij sygnał o zakończeniu wejścia pasażerów
        airplane_queue.put("boarding_complete")

        signal = airplane_queue.get()
        passengers_on_stairs = read_passengers(STAIRS_FILE)
        # Upewnij się, że wszyscy pasażerowie opuścili schody i zezwól na start samolotu
        if signal == "takeoff_allowed" and len(passengers_on_stairs) == 0:
            log(f"{timestamp()} - {LOCATIONS.AIRPLANE}: {MESSAGES.FLIGHT_START}")
            time.sleep(FLIGHT_DURATION)
            log(f"{timestamp()} - {LOCATIONS.AIRPLANE}: {MESSAGES.FLIGHT_ENDED}")
            # Zwiększ liczbę dostępnych samolotów
            with available_airplanes.get_lock():
                available_airplanes.value += 1
                log(f"{timestamp()} - {LOCATIONS.AIRPLANE}: {MESSAGES.AIRPLANE_RETURNED} (dostępnych: {available_airplanes.value})")
                sys.exit()
    except KeyboardInterrupt:
        print(f"{timestamp()} - {LOCATIONS.AIRPLANE}: kończenie procesu")
        save_passengers(STAIRS_FILE, [])