import os
import random
import time
import signal
from dataclasses import dataclass, asdict
from utils import timestamp, append_passenger, log, ensure_files_exists
from consts import (
    ENTRANCE_FILE,
    PASSENGER_GENERATION_MIN_DELAY,
    PASSENGER_GENERATION_MAX_DELAY,
    DANGEROUS_ITEMS_PROBABILITY,
    VIP_PROBABILITY,
    MIN_LUGGAGE_WEIGHT,
    MAX_LUGGAGE_WEIGHT,
    MAX_PASSENGER_PROCESSES,
    LOCATIONS,
    MESSAGES,
)

child_pids = set()


@dataclass
class Passenger:
    id: int
    gender: str
    luggageWeight: float
    hasDangerousItems: bool
    isVIP: bool
    controlPassed: int = 0


def generate_passenger(pid) -> Passenger:
    return Passenger(
        id=pid,
        gender=random.choice(["M", "F"]),
        luggageWeight=round(random.uniform(MIN_LUGGAGE_WEIGHT, MAX_LUGGAGE_WEIGHT), 2),
        hasDangerousItems=random.random() < DANGEROUS_ITEMS_PROBABILITY,
        isVIP=random.random() < VIP_PROBABILITY,
    )


def handle_passenger(passenger):
    append_passenger(ENTRANCE_FILE, asdict(passenger))
    log(
        f"{timestamp()} - {LOCATIONS.ENTRANCE}: "
        f"{MESSAGES.NEW_PASSENGER}: ID={passenger.id}, "
        f"Płeć={passenger.gender}, "
        f"Bagaż={passenger.luggageWeight}kg, "
        f"VIP={'Tak' if passenger.isVIP else 'Nie'}"
    )


def cleanup_children():
    for pid in child_pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            continue
    child_pids.clear()


def parent_signal_handler(signum, frame):
    """Handler dla procesu głównego"""
    os.write(1, b"\nZatrzymywanie generatora pasazerow...\n")
    cleanup_children()
    os.write(1, b"Generator zatrzymany.\n")
    os._exit(0)


def child_signal_handler(signum, frame):
    """Handler dla procesów potomnych"""
    # os.write(1, f"Proces pasażera {os.getpid()} kończy działanie\n".encode())
    os.kill(os.getpid(), signal.SIGKILL)  # Wymuszamy natychmiastowe zakończenie


def cleanup_zombies():
    try:
        while True:
            wpid, status = os.waitpid(-1, os.WNOHANG)
            if wpid == 0:
                break
            child_pids.discard(wpid)
    except ChildProcessError:
        pass


def generate_continuously():
    signal.signal(signal.SIGINT, parent_signal_handler)
    signal.signal(signal.SIGTERM, parent_signal_handler)

    ensure_files_exists([ENTRANCE_FILE])

    while True:
        if len(child_pids) < MAX_PASSENGER_PROCESSES:
            pid = os.fork()
            if pid == 0:
                # Proces potomny
                try:
                    signal.signal(signal.SIGINT, child_signal_handler)
                    signal.signal(signal.SIGTERM, child_signal_handler)

                    passenger = generate_passenger(os.getpid())
                    handle_passenger(passenger)

                    # Czekamy na sygnał zakończenia
                    signal.pause()

                except Exception as e:
                    print(f"Błąd w procesie potomnym: {e}")
                    os._exit(1)
            else:
                # Proces główny
                child_pids.add(pid)
                # Czyścimy zakończone procesy potomne
                cleanup_zombies()
        else:
            cleanup_zombies()
        time.sleep(
            random.uniform(
                PASSENGER_GENERATION_MIN_DELAY, PASSENGER_GENERATION_MAX_DELAY
            )
        )
