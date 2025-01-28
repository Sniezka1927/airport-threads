import os

from consts import (
    ENTRANCE_FILE,
    LUGGAGE_CHECKED_FILE,
    LUGGAGE_REJECTED_FILE,
    SECURITY_CHECKED_FILE,
    SECURITY_REJECTED_FILE,
    STAIRS_FILE,
    FROM_AIRPLANE_QUEUE,
    FROM_GATE_QUEUE,
    FROM_LUGGAGE_QUEUE,
    TO_AIRPLANE_QUEUE,
    TO_GATE_QUEUE,
    TO_LUGGAGE_QUEUE,
)


def ensure_directory_exists():
    """Upewnij się, że katalog data istnieje"""
    os.makedirs("../data", exist_ok=True)


def clear_files(logs: bool = True):
    """Wyczyść wszystkie pliki systemu"""
    # Lista wszystkich plików do wyczyszczenia
    files = [
        ENTRANCE_FILE,
        LUGGAGE_CHECKED_FILE,
        LUGGAGE_REJECTED_FILE,
        SECURITY_CHECKED_FILE,
        SECURITY_REJECTED_FILE,
        STAIRS_FILE,
    ]

    # Kolejki
    queues = [
        FROM_AIRPLANE_QUEUE,
        FROM_GATE_QUEUE,
        FROM_LUGGAGE_QUEUE,
        TO_AIRPLANE_QUEUE,
        TO_GATE_QUEUE,
        TO_LUGGAGE_QUEUE,
    ]

    # Upewnij się, że katalog istnieje
    ensure_directory_exists()

    for file_path in files:
        try:
            # Stwórz lub wyczyść plik
            with open(file_path, "w") as f:
                f.write("")
            if logs:
                print(f"Wyczyszczono plik: {file_path}")
        except Exception as e:
            print(f"Błąd podczas czyszczenia pliku {file_path}: {e}")

    for file_path in queues:
        try:
            # Stwórz lub wyczyść plik
            with open(file_path, "w") as f:
                f.write("")
            if logs:
                print(f"Wyczyszczono plik: {file_path}")
        except Exception as e:
            print(f"Błąd podczas czyszczenia pliku {file_path}: {e}")


if __name__ == "__main__":
    print("Rozpoczynam czyszczenie plików...")
    clear_files()
    print("Zakończono czyszczenie plików.")
