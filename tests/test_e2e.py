import sys
from dataclasses import asdict
import threading
import time
from src.consts import AIRPLANE_CAPACITY, ENTRANCE_FILE, LUGGAGE_CHECKED_FILE, SECURITY_CHECKED_FILE, \
    LUGGAGE_REJECTED_FILE, SECURITY_REJECTED_FILE, MIN_PASSENGERS_TO_BOARD, FLIGHT_DURATION, STAIRS_FILE, \
    AIRPORT_LUGGAGE_LIMIT
from src.dispatcher import Dispatcher
from src.generator import generate_passenger as _generate_passenger
from src.cleanup import clear_files
from src.luggageControl import validate_passenger
from src.securityControl import process_passengers, SecurityCheckpoint
from src.utils import save_passengers, read_passengers
from src.gate import process_passengers as gate_process_passengers


def generate_passengers(count: int, male_count: int = 0, with_items: bool = False, is_vip: bool = False) -> list[dict]:
    passengers = []
    for i in range(count):
        passenger = _generate_passenger()
        passenger.hasDangerousItems = with_items
        passenger.isVIP = is_vip
        if i < male_count:
            passenger.gender = 'M'
        else:
            passenger.gender = 'F'
        passenger.luggageWeight = AIRPORT_LUGGAGE_LIMIT - 1
        passengers.append(asdict(passenger))
    return passengers


def gate_process_wrapper(gate_queue, stop_event):
    try:
        while not stop_event.is_set():
            gate_process_passengers(gate_queue)
            time.sleep(0.1)
    except Exception as e:
        print(f"Gate process error: {e}")


def dispatcher_loop_wrapper(dispatcher, stop_event):
    try:
        while not stop_event.is_set():
            dispatcher.dispatcher_loop()
            time.sleep(0.1)
    except Exception as e:
        print(f"Dispatcher error: {e}")


if __name__ == "__main__":
    clear_files(False)

    stop_event = threading.Event()

    clear_files(False)
    dispatcher = Dispatcher()

    gate_thread = threading.Thread(target=gate_process_wrapper, args=(dispatcher.gate_queue, stop_event))
    gate_thread.daemon = True
    gate_thread.start()

    dispatcher_thread = threading.Thread(target=dispatcher_loop_wrapper, args=(dispatcher, stop_event))
    dispatcher_thread.daemon = True
    dispatcher_thread.start()

    try:
        passengers_count = MIN_PASSENGERS_TO_BOARD * 2
        # Wejście na lotnisko
        initial_passengers = generate_passengers(passengers_count, AIRPLANE_CAPACITY / 2, False, False)
        save_passengers(ENTRANCE_FILE, initial_passengers)
        assert len(read_passengers(ENTRANCE_FILE)) == passengers_count

        # Kontola Biletowo bagażowa
        for passenger in initial_passengers:
            validate_passenger(passenger)

        assert len(read_passengers(LUGGAGE_CHECKED_FILE)) == passengers_count
        assert len(read_passengers(LUGGAGE_REJECTED_FILE)) == 0

        # Kontrola bezpieczeństwa
        checkpoint = SecurityCheckpoint()
        for _ in range((passengers_count // 6) + 1):
            process_passengers(checkpoint)

        assert len(read_passengers(SECURITY_CHECKED_FILE)) >= 0
        assert len(read_passengers(SECURITY_REJECTED_FILE)) == 0
        assert len(read_passengers(LUGGAGE_CHECKED_FILE)) == 0

        # Czas na wejście na pokład
        time.sleep(10)

        # Czas na powrót samolotów
        time.sleep(FLIGHT_DURATION + 5)

        with dispatcher.available_airplanes.get_lock():
            assert dispatcher.available_airplanes.value == 5

        assert len(read_passengers(SECURITY_REJECTED_FILE)) == 0
        assert len(read_passengers(LUGGAGE_CHECKED_FILE)) == 0
        assert len(read_passengers(LUGGAGE_REJECTED_FILE)) == 0
        assert len(read_passengers(STAIRS_FILE)) == 0
        assert len(read_passengers(ENTRANCE_FILE)) == 0

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        sys.exit(0)


