import time
from multiprocessing import Process
from typing import List, Dict, Optional
from dataclasses import dataclass
from consts import (
    LUGGAGE_CHECKED_FILE,
    MAX_CONTROL_PASSES,
    SECURITY_CHECKED_FILE,
    SECURITY_REJECTED_FILE,
    MESSAGES,
    LOCATIONS,
    SECURITY_CHECKPOINTS_COUNT,
)
from utils import (
    ensure_files_exists,
    read_passengers,
    save_passengers,
    timestamp,
    append_passenger,
    log,
)


@dataclass
class CheckpointStation:
    id: int
    current_gender: Optional[str] = None
    passengers: List[Dict] = None

    def __post_init__(self):
        self.passengers = []

    def is_full(self) -> bool:
        """Sprawdza czy stacja jest pełna"""
        return len(self.passengers) >= 2

    def is_empty(self) -> bool:
        """Sprawdza czy stacja jest pusta"""
        return len(self.passengers) == 0

    def can_accept_passenger(self, passenger: Dict) -> bool:
        """Sprawdza czy stacja może przyjąć pasażera"""
        if self.is_full():
            return False
        if self.is_empty():
            return True
        return self.current_gender == passenger["gender"]

    def add_passenger(self, passenger: Dict) -> bool:
        """Dodaje pasażera do stacji"""
        if not self.can_accept_passenger(passenger):
            return False
        if self.is_empty():
            self.current_gender = passenger["gender"]
        self.passengers.append(passenger)
        return True

    def remove_passenger(self, passenger: Dict):
        """Usuwa pasażera ze stacji"""
        if passenger in self.passengers:
            self.passengers.remove(passenger)
            if self.is_empty():
                self.current_gender = None


class SecurityCheckpoint:
    def __init__(self, num_stations: int = SECURITY_CHECKPOINTS_COUNT):
        self.stations = [CheckpointStation(id=i) for i in range(num_stations)]
        # Przechowuje ID pasażerów z poprzedniej partii
        self.previous_batch_ids = set()

    def get_empty_stations(self) -> List[CheckpointStation]:
        # Zwraca dostępne stacje do kontroli bezpieczeństwa
        return [station for station in self.stations if station.is_empty()]

    def get_station_for_passenger(self, passenger: Dict) -> Optional[CheckpointStation]:
        # Selekcja stanowiska dla pasażerów w zależności od priorytetów
        if passenger["isVIP"]:
            for station in self.stations:
                if station.is_empty():
                    return station

        for station in self.stations:
            if not station.is_full() and station.current_gender == passenger["gender"]:
                return station

        for station in self.stations:
            if station.is_empty():
                return station

        return None

    def add_passenger(self, passenger: Dict) -> bool:
        """Sprawdza warunki płciowe i wolne miejsca na stacjach, dodaje pasażera do stacji"""
        station = self.get_station_for_passenger(passenger)
        if station and station.add_passenger(passenger):
            return True
        return False

    def process_stations(self) -> List[Dict]:
        """Przetwarza wszystkie stanowiska i zwraca listę przetworzonych pasażerów"""
        processed_passengers = []
        current_batch_ids = set()  # ID pasażerów w obecnej partii

        # Zbieramy ID wszystkich pasażerów w obecnej partii
        for station in self.stations:
            if not station.is_empty():
                for passenger in station.passengers:
                    current_batch_ids.add(passenger["id"])

        # Przetwarzamy stanowiska
        for station in self.stations:
            if not station.is_empty():
                station_passengers = list(station.passengers)

                for passenger in station_passengers:
                    if not passenger["isVIP"]:
                        # Sprawdzamy czy w poprzedniej partii był ktoś o większym ID i zwiększamy licznik przepuszczeń
                        higher_id_exists = any(
                            prev_id > passenger["id"]
                            for prev_id in self.previous_batch_ids
                        )
                        if higher_id_exists:
                            passenger["controlPassed"] = (
                                passenger.get("controlPassed", 0) + 1
                            )

                    processed_passengers.append(
                        {"passenger": passenger, "station_id": station.id}
                    )
                    station.remove_passenger(passenger)

        # Aktualizujemy ID poprzedniej partii
        self.previous_batch_ids = current_batch_ids
        return processed_passengers


def find_available_station(checkpoint, passenger):
    """Dopasowywuje stację do pasażera z zachowaniem priorytetów"""
    for station in checkpoint.stations:
        # Sprawdź czy stacja nie jest pełna
        if station.is_full():
            continue

        # Sprawdź czy stacja jest pusta lub obsługuje tę samą płeć
        if station.is_empty() or station.current_gender == passenger["gender"]:
            return station

    return None


def get_next_passengers(checkpoint: SecurityCheckpoint) -> List[Dict]:
    """Pobiera następnych pasażerów do kontroli z zachowaniem priorytetów:
    1. Pasażerowie którzy są na limitcie przepuszczeń (3)
    2. VIP-owie według płci
    3. Pozostali pasażerowie od góry listy
    """
    passengers = read_passengers(LUGGAGE_CHECKED_FILE)
    if not passengers:
        return []

    selected_passengers = []
    remaining_passengers = passengers.copy()

    # 1. Obsługa pasażerów z przekroczonym limitem
    exceeded_limit_passengers = [
        p
        for p in remaining_passengers
        if p.get("controlPassed", 0) >= MAX_CONTROL_PASSES
    ]

    for passenger in exceeded_limit_passengers:
        station = find_available_station(checkpoint, passenger)
        if station and checkpoint.add_passenger(passenger):
            selected_passengers.append(passenger)
            remaining_passengers.remove(passenger)

    # 2. Obsługa VIP-ów według płci
    vip_passengers = [p for p in remaining_passengers if p["isVIP"]]

    for vip in vip_passengers:
        station = find_available_station(checkpoint, vip)
        if station and checkpoint.add_passenger(vip):
            selected_passengers.append(vip)
            remaining_passengers.remove(vip)

    # 3. Obsługa pozostałych pasażerów w kolejności od góry
    regular_passengers = [
        p
        for p in remaining_passengers
        if not p["isVIP"] and p.get("controlPassed", 0) < MAX_CONTROL_PASSES
    ]

    for passenger in regular_passengers:
        station = find_available_station(checkpoint, passenger)
        if station and checkpoint.add_passenger(passenger):
            selected_passengers.append(passenger)
            remaining_passengers.remove(passenger)

    save_passengers(LUGGAGE_CHECKED_FILE, remaining_passengers)
    return selected_passengers


def process_passengers(checkpoint: SecurityCheckpoint):
    """Główna funkcja przetwarzająca pasażerów na stanowiskach kontroli bezpieczeństwa"""
    # Pobierz nowych pasażerów do pustych stanowisk
    if checkpoint.get_empty_stations():
        selected_passengers = get_next_passengers(checkpoint)
        for passenger in selected_passengers:
            log(
                f"{timestamp()} - {LOCATIONS.SECURITY}: "
                f"Pasażer ID={passenger['id']} {'(VIP) ' if passenger['isVIP'] else ''}"
                f"płeć={passenger['gender']} {MESSAGES.SECURITY_CONTROL_BEGIN}"
            )

    # Przetwórz pasażerów na wszystkich stanowiskach
    if any(not station.is_empty() for station in checkpoint.stations):
        time.sleep(2)  # Symulacja czasu kontroli
        processed = checkpoint.process_stations()

        for item in processed:
            passenger = item["passenger"]
            station_id = item["station_id"]

            # Sprawdź czy pasażer ma niebezpieczne przedmioty
            if passenger["hasDangerousItems"]:
                log(
                    f"{timestamp()} - {LOCATIONS.SECURITY}: Stanowisko {station_id}: Pasażer ID={passenger['id']} "
                    f"(przepuścił: {passenger.get('controlPassed', 0)} osób) {MESSAGES.SECURITY_CONTROL_REJECT}"
                )
                append_passenger(SECURITY_REJECTED_FILE, passenger)
            else:
                log(
                    f"{timestamp()} - {LOCATIONS.SECURITY}: Stanowisko {station_id}: Pasażer ID={passenger['id']} "
                    f"(przepuścił: {passenger.get('controlPassed', 0)} osób) {MESSAGES.SECURITY_CONTROL_OK}"
                )
                append_passenger(SECURITY_CHECKED_FILE, passenger)


def check_security_continuously():
    """Główna pętla kontroli bezpieczeństwa, sprawdza czy pliki istnieją i przetwarza pasażerów w nieskończoność"""
    ensure_files_exists([SECURITY_CHECKED_FILE, SECURITY_REJECTED_FILE])
    checkpoint = SecurityCheckpoint()

    while True:
        process_passengers(checkpoint)
        time.sleep(1)


if __name__ == "__main__":
    print("Uruchamianie kontroli bezpieczeństwa...")
    process = Process(target=check_security_continuously)
    process.start()

    try:
        process.join()
    except KeyboardInterrupt:
        print("\nZatrzymywanie kontroli bezpieczeństwa...")
        process.terminate()
        print("Kontrola zatrzymana.")
