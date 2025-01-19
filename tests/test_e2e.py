import sys
import multiprocessing as mp
from dataclasses import asdict
import time
from src.consts import (
    AIRPLANE_CAPACITY,
    ENTRANCE_FILE,
    LUGGAGE_CHECKED_FILE,
    SECURITY_CHECKED_FILE,
    LUGGAGE_REJECTED_FILE,
    SECURITY_REJECTED_FILE,
    MIN_PASSENGERS_TO_BOARD,
    FLIGHT_DURATION,
    STAIRS_FILE,
    AIRPORT_LUGGAGE_LIMIT
)
from src.dispatcher import Dispatcher
from src.generator import generate_passenger
from src.cleanup import clear_files
from src.luggageControl import validate_passenger
from src.securityControl import process_passengers, SecurityCheckpoint
from src.utils import save_passengers, read_passengers, validate_config
from src.gate import process_passengers as gate_process_passengers


def generate_passengers(count: int, male_count: int = 0, with_items: bool = False, is_vip: bool = False) -> list[dict]:
    passengers = []
    for i in range(count):
        passenger = generate_passenger()
        passenger.hasDangerousItems = with_items
        passenger.isVIP = is_vip
        if i < male_count:
            passenger.gender = 'M'
        else:
            passenger.gender = 'F'
        passenger.luggageWeight = AIRPORT_LUGGAGE_LIMIT - 1
        passengers.append(asdict(passenger))
    return passengers


def run_e2e_test():
    clear_files(False)
    validate_config()

    dispatcher = Dispatcher()
    dispatcher_process = mp.Process(target=dispatcher.dispatcher_loop)
    gate_process = mp.Process(target=gate_process_passengers, args=(dispatcher.gate_queue,))

    processes = [dispatcher_process, gate_process]

    try:

        for process in processes:
            process.start()

        passengers_count = MIN_PASSENGERS_TO_BOARD * 2

        # Entrance
        initial_passengers = generate_passengers(passengers_count, AIRPLANE_CAPACITY / 2, False, False)
        save_passengers(ENTRANCE_FILE, initial_passengers)
        assert len(read_passengers(ENTRANCE_FILE)) == passengers_count

        # Luggage control
        for passenger in initial_passengers:
            validate_passenger(passenger)
        assert len(read_passengers(LUGGAGE_CHECKED_FILE)) == passengers_count
        assert len(read_passengers(LUGGAGE_REJECTED_FILE)) == 0

        # Security control
        checkpoint = SecurityCheckpoint()
        for _ in range((passengers_count // 6) + 1):
            process_passengers(checkpoint)
        assert len(read_passengers(SECURITY_CHECKED_FILE)) >= 0
        assert len(read_passengers(SECURITY_REJECTED_FILE)) == 0
        assert len(read_passengers(LUGGAGE_CHECKED_FILE)) == 0

        # Czas na boarding
        time.sleep(10)

        # Czas na powrót samolotów
        time.sleep(FLIGHT_DURATION + 5)

        with dispatcher.available_airplanes.get_lock():
            assert dispatcher.available_airplanes.value == 5

        assert len(read_passengers(SECURITY_REJECTED_FILE)) == 0
        assert len(read_passengers(LUGGAGE_CHECKED_FILE)) == 0
        assert len(read_passengers(LUGGAGE_REJECTED_FILE)) == 0
        assert len(read_passengers(STAIRS_FILE)) == 0

        print("OK!")
    finally:
        print("\nKończenie procesów...")

        dispatcher.terminate_all_processes()

        if dispatcher_process.is_alive():
            dispatcher_process.terminate()

        if gate_process.is_alive():
            gate_process.terminate()

        for process in processes:
            process.join(timeout=1)


if __name__ == "__main__":
    run_e2e_test()
