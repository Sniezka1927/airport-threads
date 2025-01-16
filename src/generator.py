import random
import time
from dataclasses import dataclass, asdict
from multiprocessing import Process
from utils import ensure_files_exists
from utils import timestamp, append_passenger, log
from consts import (
    ENTRANCE_FILE,
    PASSENGER_GENERATION_MIN_DELAY,
    PASSENGER_GENERATION_MAX_DELAY,
    DANGEROUS_ITEMS_PROBABILITY,
    VIP_PROBABILITY,
    MIN_LUGGAGE_WEIGHT,
    MAX_LUGGAGE_WEIGHT,
    LOCATIONS,
    MESSAGES
)


@dataclass
class Passenger:
    id: int
    gender: str
    luggageWeight: float
    hasDangerousItems: bool
    isVIP: bool
    controlPassed: int = 0


current_id = 0


def get_next_id() -> int:
    """Pasażerowie maja globalne ID,w celu uniknięcia duplikatów"""
    global current_id
    current_id += 1
    return current_id


def generate_passenger() -> Passenger:
    """Generuj pojedynczego pasażera"""
    return Passenger(
        id=get_next_id(),
        gender=random.choice(['M', 'F']),
        luggageWeight=round(random.uniform(MIN_LUGGAGE_WEIGHT, MAX_LUGGAGE_WEIGHT), 2),
        hasDangerousItems=random.random() < DANGEROUS_ITEMS_PROBABILITY,
        isVIP=random.random() < VIP_PROBABILITY,
    )


def generate_continuously():
    """Główna pętla generatora, Sprawdz czy wymagane pliki istnieją i generuje pasażerów w nieskończoność"""
    ensure_files_exists([ENTRANCE_FILE])
    while True:
        passenger = generate_passenger()
        append_passenger(ENTRANCE_FILE, asdict(passenger))
        log(f"{timestamp()} - {LOCATIONS.ENTRANCE}: "
              f"{MESSAGES.NEW_PASSENGER}: ID={passenger.id}, "
              f"Płeć={passenger.gender}, "
              f"Bagaż={passenger.luggageWeight}kg, "
              f"VIP={'Tak' if passenger.isVIP else 'Nie'}")

        time.sleep(random.uniform(PASSENGER_GENERATION_MIN_DELAY,
                                  PASSENGER_GENERATION_MAX_DELAY))


if __name__ == "__main__":
    print("Uruchamianie generatora pasażerów...")
    process = Process(target=generate_continuously)
    process.start()

    try:
        process.join()
    except KeyboardInterrupt:
        print("\nZatrzymywanie generatora pasażerów...")
        process.terminate()
        print("Generator zatrzymany.")