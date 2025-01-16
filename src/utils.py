import os
import fcntl
import errno
from typing import List, Dict
import json
import sys
from datetime import datetime
from consts import LOGS_FILE, LOGS_DIRECTORY
from pathlib import Path

def ensure_files_exists(filenames: List[str]):
    """Upewnij się, że wszystkie potrzebne pliki istnieją z odpowiednimi prawami"""
    for filename in filenames:
        try:
            # Tworzenie pliku z prawami tylko dla właściciela (0o600)
            flags = os.O_CREAT | os.O_WRONLY
            mode = 0o600

            fd = os.open(filename, flags, mode)
            with os.fdopen(fd, 'w') as f:
                if os.path.getsize(filename) == 0:
                    f.write('[]')

        except OSError as e:
            handle_system_error("Tworzenie", filename, e)
            raise


def append_passenger(filename: str, passenger: dict):
    """Bezpieczne dodawanie pasażera do pliku z lockowaniem"""
    try:
        with open(filename, 'r+') as f:
            # Ustawienie blokady na plik
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                # Odczyt obecnej zawartości
                data = json.loads(f.read() or '[]')
                # Dodanie nowego pasażera
                data.append(passenger)
                # Powrót na początek pliku i nadpisanie zawartości
                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            finally:
                # Zdjęcie blokady
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    except OSError as e:
        handle_system_error("Dodawanie pasażera", filename, e)
        raise
    except Exception as e:
        log(f"{timestamp()} - BŁĄD: Nie udało się dodać pasażera do {filename}: {str(e)}")
        raise

def timestamp() -> str:
    """Zwraca aktualny znacznik czasu w formacie HH:MM:SS"""
    return datetime.now().strftime('%H:%M:%S')

def log(message: str, output_file: str = LOGS_FILE, to_console: bool = True):
    """Logowanie wiadomości do pliku i/lub konsoli w celu zbierania statystyk"""
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

    if to_console:
        print(message)

