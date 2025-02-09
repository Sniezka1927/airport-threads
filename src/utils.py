import os
import fcntl
import signal
import errno
import time
from typing import List
import sys
from datetime import datetime
from consts import LOGS_FILE, LOGS_DIRECTORY
from pathlib import Path
from consts import (
    AIRPORT_AIRPLANES_COUNT,
    VIP_PROBABILITY,
    DANGEROUS_ITEMS_PROBABILITY,
    STAIRS_CAPACITY,
    AIRPLANE_CAPACITY,
    MIN_AIRPLANE_LUGGAGE_CAPACITY,
    AIRPORT_LUGGAGE_LIMIT,
    MIN_LUGGAGE_WEIGHT,
    MAX_LUGGAGE_WEIGHT,
    MAX_AIRPLANE_LUGGAGE_CAPACITY,
    MAX_ACCEPTABLE_PASSENGERS_PROCESSES,
    MAX_PASSENGER_PROCESSES,
    MIN_FLIGHT_DURATION,
    MAX_FLIGHT_DURATION,
)


def handle_system_error(operation: str, filename: str, error: OSError):
    """
    Obsługa błędów systemowych z wykorzystaniem errno
    """
    error_code = error.errno
    error_message = os.strerror(error_code)  # odpowiednik perror w Pythonie
    error_details = f"{operation} na pliku {filename} nie powiodła się: {error_message} (errno: {error_code})"

    # Logowanie błędu
    with open(LOGS_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp()} - BŁĄD: {error_details}\n")

    # Wyświetlenie błędu na stderr
    sys.stderr.write(f"{error_details}\n")

    # Obsługa specyficznych błędów
    if error_code == errno.EACCES:
        sys.stderr.write("Brak wymaganych uprawnień do pliku\n")
    elif error_code == errno.ENOENT:
        sys.stderr.write("Plik nie istnieje\n")
    elif error_code == errno.ENOSPC:
        sys.stderr.write("Brak miejsca na dysku\n")
    elif error_code == errno.EAGAIN:
        sys.stderr.write("Brak dostępu do zasobów\n")
    elif error_code == errno.EEXIST:
        sys.stderr.write("Plik już istnieje\n")
    elif error_code == errno.EMFILE:
        sys.stderr.write("Za dużo otwartych plików\n")
    elif error_code == errno.EBADF:
        sys.stderr.write("Nieprawidłowy deskryptor pliku\n")
    elif error_code == errno.EIO:
        sys.stderr.write("Błąd wejścia/wyjścia\n")
    elif error_code == errno.EBUSY:
        sys.stderr.write("Zasób jest zajęty\n")
    elif error_code == errno.EINTR:
        sys.stderr.write("Przerwana operacja systemowa\n")


def ensure_files_exists(filenames: List[str]):
    """Upewnij się, że wszystkie potrzebne pliki istnieją z odpowiednimi prawami"""
    for filename in filenames:
        try:
            # Tworzenie pliku z prawami tylko dla właściciela (0o600)
            flags = os.O_CREAT | os.O_WRONLY
            mode = 0o600

            fd = os.open(filename, flags, mode)
            with os.fdopen(fd, "w") as f:
                if os.path.getsize(filename) == 0:
                    f.write("")

        except OSError as e:
            handle_system_error("Tworzenie", filename, e)
            raise


def serialize_passenger(passenger) -> str:
    """Serializacja pasażera do postaci tekstowej"""
    return f"{passenger['id']};{passenger['gender']};{passenger['luggageWeight']};{passenger['hasDangerousItems']};{passenger['isVIP']};{passenger['controlPassed']}"


def str_to_bool(string: str) -> bool:
    return string.lower() == "true"


def deserialize_passenger(line: str):
    """Odczytanie pasażera z linii tekstu"""
    data = line.strip().split(";")
    passenger = {
        "id": int(data[0]),
        "gender": data[1],
        "luggageWeight": float(data[2]),
        "hasDangerousItems": str_to_bool(data[3]),
        "isVIP": str_to_bool(data[4]),
        "controlPassed": int(data[5]),
    }
    return passenger


def read_passengers(filename: str) -> List[dict]:
    """Bezpieczne czytanie pasażerów z pliku z lockowaniem"""
    try:
        with open(filename, "r") as f:
            # Ustawienie blokady na odczyt
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                lines = f.readlines()
                passengers = [
                    deserialize_passenger(line) for line in lines if line.strip()
                ]
                return passengers
            finally:
                # Zdjęcie blokady po zakończeniu odczytu
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except OSError as e:
        handle_system_error("Odczyt", filename, e)
        return []
    except Exception as e:
        return []


def save_passengers(filename: str, passengers: List[dict]):
    """Bezpieczny zapis pasażerów do pliku z lockowaniem"""
    try:
        with open(filename, "w") as f:
            # Ustawienie blokady na zapis
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                for passenger in passengers:
                    line = serialize_passenger(passenger) + "\n"
                    f.write(line)
            finally:
                # Zdjęcie blokady po zakończeniu zapisu
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except OSError as e:
        handle_system_error("Zapis", filename, e)
        raise
    except Exception as e:
        log(
            f"{timestamp()} - BŁĄD: Nie udało się zapisać pasażerów do {filename}: {str(e)}"
        )
        raise


def append_passenger(filename: str, passenger: dict):
    """Bezpieczne dodawanie pasażera do pliku z lockowaniem"""
    try:
        with open(filename, "a") as f:
            # Ustawienie blokady na plik
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                line = serialize_passenger(passenger) + "\n"
                f.write(line)
            finally:
                # Zdjęcie blokady
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except OSError as e:
        handle_system_error("Dodawanie pasażera", filename, e)
        raise
    except Exception as e:
        log(
            f"{timestamp()} - BŁĄD: Nie udało się dodać pasażera do {filename}: {str(e)}"
        )
        raise


def timestamp() -> str:
    """Zwraca aktualny znacznik czasu w formacie HH:MM:SS"""
    return datetime.now().strftime("%H:%M:%S")


def log(message: str, output_file: str = LOGS_FILE, to_console: bool = True):
    """Logowanie wiadomości do pliku i/lub konsoli w celu zbierania statystyk"""
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

    if to_console:
        print(message)


def read_log_to_list(file_content):
    """Funckja pomocnicza do odczytu pliku logów do listy linii"""
    return [line.strip() for line in file_content.split("\n") if line.strip()]


def get_latest_log_entries():
    """Odczytaj logów z najnowszej symulacji"""
    try:
        log_path = Path(LOGS_DIRECTORY)
        log_files = list(log_path.glob("logs_*.txt"))

        if not log_files:
            return None, None

        # Wyciągnij timestamp z nazwy pliku
        log_timestamps = [(int(f.stem.split("_")[1]), f) for f in log_files]

        # Znajdź najnowszy plik
        latest_timestamp, latest_file = max(log_timestamps, key=lambda x: x[0])

        # Odczytaj zawartość pliku i ją zwróć
        content = latest_file.read_text(encoding="utf-8")
        return read_log_to_list(content), latest_timestamp

    except Exception as e:
        print(f"Error reading log file: {e}")
        return None


def validate_config():
    """ "Sprawdza poprawność konfiguracji"""
    if not (AIRPORT_AIRPLANES_COUNT > 0):
        raise ValueError("AIRPORT_AIRPLANES_COUNT musi być większe od 0")
    if not (VIP_PROBABILITY >= 0 and VIP_PROBABILITY <= 1):
        raise ValueError("VIP_PROBABILITY musi być między 0 a 1")
    if not (DANGEROUS_ITEMS_PROBABILITY >= 0 and DANGEROUS_ITEMS_PROBABILITY <= 1):
        raise ValueError("DANGEROUS_ITEMS_PROBABILITY musi być między 0 a 1")
    if not (STAIRS_CAPACITY > 0 and STAIRS_CAPACITY <= AIRPLANE_CAPACITY):
        raise ValueError(f"STAIRS_CAPACITY musi być między 0 a {AIRPLANE_CAPACITY}")
    if not (AIRPLANE_CAPACITY > 0):
        raise ValueError("AIRPLANE_CAPACITY musi być większe od 0")
    if not (MIN_AIRPLANE_LUGGAGE_CAPACITY >= AIRPLANE_CAPACITY * AIRPORT_LUGGAGE_LIMIT):
        raise ValueError(
            f"MIN_AIRPLANE_LUGGAGE_CAPACITY musi być większe bądź równe {AIRPLANE_CAPACITY * AIRPORT_LUGGAGE_LIMIT}"
        )
    if not (MIN_LUGGAGE_WEIGHT >= 0 and MIN_LUGGAGE_WEIGHT <= MAX_LUGGAGE_WEIGHT):
        raise ValueError(
            "MIN_LUGGAGE_CAPACITY musi być większe bądź równa 0 i mniejsze bądź równe MAX_LUGGAGE_WEIGHT"
        )
    if not (MAX_PASSENGER_PROCESSES <= MAX_ACCEPTABLE_PASSENGERS_PROCESSES):
        raise ValueError(
            "MAX_PASSENGER_PROCESSES musi być mniejsze bądź równe MAX_ACCEPTABLE_PASSENGERS_PROCESSES"
        )
    if not (MAX_AIRPLANE_LUGGAGE_CAPACITY >= MIN_AIRPLANE_LUGGAGE_CAPACITY):
        raise ValueError(
            "MAX_AIRPLANE_LUGGAGE_CAPACITY musi bć większe bądź róœne MIN_AIRPLANE_LUGGAGE_CAPACITY"
        )
    if not (MIN_FLIGHT_DURATION >= 0 and MIN_FLIGHT_DURATION <= MAX_FLIGHT_DURATION):
        raise ValueError(
            "MIN_FLIGHT_DURATION musi być większe bądź równe 0 i mniejsze bądź równe MAX_FLIGHT_DURATION"
        )
    if not (MAX_PASSENGER_PROCESSES >= AIRPLANE_CAPACITY):
        raise ValueError(
            "MAX_PASSENGER_PROCESSES musi być większe bądź równe AIRPLANE_CAPACITY"
        )


def terminate_process(pid: int, source: str = ""):
    """Zabija proces o podanym PID"""
    try:
        # Zabij proces sygnałem SIGTERM
        os.kill(pid, signal.SIGTERM)

        time.sleep(0.5)

        try:
            # Check czy istnieje proces o podanym PID
            os.kill(pid, 0)
            # Jeśli dalej istnieje proces o podanym PID, zabij go
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            # Process został zakończony
            pass

    except ProcessLookupError:
        print(f"Nie znalezionmu procesu o PID: {pid} z: {source}")
