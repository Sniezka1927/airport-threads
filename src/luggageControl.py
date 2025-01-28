import time
from multiprocessing import Process
from queue_handler import Queue
from consts import (
    AIRPORT_LUGGAGE_LIMIT,
    ENTRANCE_FILE,
    LUGGAGE_CHECKED_FILE,
    LUGGAGE_REJECTED_FILE,
    MESSAGES,
    LOCATIONS,
)
from utils import (
    ensure_files_exists,
    read_passengers,
    save_passengers,
    timestamp,
    append_passenger,
    log,
)


def get_first_passenger():
    """Pobierz i usuń pierwszego pasażera z pliku wejściowego"""
    data = read_passengers(ENTRANCE_FILE)
    if not data:
        return None
    # Usuń i zwróć pierwszego pasażera
    first_passenger = data.pop(0)

    save_passengers(ENTRANCE_FILE, data)

    return first_passenger


def validate_passenger(passenger):
    """Sprawdzamy bagaż pasażera, czy nie przekracza limitu"""
    log(
        f"{timestamp()} - {LOCATIONS.LUGGAGE}: ID={passenger['id']} {MESSAGES.LUGGAGE_CHECK_BEGIN}"
    )

    # Sprawdź wagę bagażu
    if passenger["luggageWeight"] <= AIRPORT_LUGGAGE_LIMIT:
        append_passenger(LUGGAGE_CHECKED_FILE, passenger)
        log(
            f"{timestamp()} - {LOCATIONS.LUGGAGE}: Pasażer ID={passenger['id']} {MESSAGES.LUGGAGE_CHECK_OK} "
        )
    else:
        append_passenger(LUGGAGE_REJECTED_FILE, passenger)
        log(
            f"{timestamp()} - {LOCATIONS.LUGGAGE}: Pasażer ID={passenger['id']} {MESSAGES.LUGGAGE_CHECK_REJECT}"
        )


def check_luggage_continuously(queue: Queue):
    """Główna pętla kontroli bagażowej, sprawdza czy pliki istnieją i sprawdza bagaże wszystkich pasażerów,
    w przypadku otrzymania informacjii o zamknięciu lotniska kontorla zatrzymuje się"""
    ensure_files_exists([ENTRANCE_FILE, LUGGAGE_CHECKED_FILE, LUGGAGE_REJECTED_FILE])
    while True:
        if not queue.empty():
            signal = queue.get()
            if signal == "close_airport":
                return

        passenger = get_first_passenger()

        if passenger is not None:
            validate_passenger(passenger)

        time.sleep(1)


if __name__ == "__main__":
    print("Uruchamianie kontroli biletowo-bagażowej...")
    queue = Queue()
    process = Process(target=check_luggage_continuously, args=(queue,))
    process.start()

    try:
        process.join()
    except KeyboardInterrupt:
        print("\nZatrzymywanie kontroli biletowo-bagażowej...")
        process.terminate()
        print("Kontrola zatrzymana.")
