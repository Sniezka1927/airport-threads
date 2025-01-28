from time import time
from math import floor

# Konfiguracja lotniska
AIRPORT_LUGGAGE_LIMIT = 12.5  # kg
AIRPORT_AIRPLANES_COUNT = 5

# Konfiguracja generatora pasażerów
DANGEROUS_ITEMS_PROBABILITY = 0.01  # 1% chance
VIP_PROBABILITY = 0.05  # 5% chance
MIN_LUGGAGE_WEIGHT = 1.0  # kg
MAX_LUGGAGE_WEIGHT = 15.0  # kg

# Konfiguracja schodów
STAIRS_CAPACITY = 10

# Konfiguracja samolotu
AIRPLANE_CAPACITY = 20
MIN_AIRPLANE_LUGGAGE_CAPACITY = 1000  # kg
MAX_AIRPLANE_LUGGAGE_CAPACITY = 2000  # kg

# -------------------- DO NOT EDIT BELOW THIS LINE --------------------


# Konfiguracja generatora pasażerów
PASSENGER_GENERATION_MIN_DELAY = 0.5  # seconds
PASSENGER_GENERATION_MAX_DELAY = 1  # seconds

# Konfiguracja kontroli pasażerów
SECURITY_CHECKPOINTS_COUNT = 3
MAX_PASSENGERS_PER_CHECKPOINT = 2
MAX_CONTROL_PASSES = 3

# Konfiguracja samolotów
FLIGHT_DURATION = 30  # seconds
MAX_PASSENGERS_FOR_SHUTDOWN = 2000
MIN_PASSENGERS_TO_BOARD = AIRPLANE_CAPACITY
TOTAL_PASSENGER_CHECKS = 30

# Sćieżki do plików
ENTRANCE_FILE = "../data/entrance.json"
LUGGAGE_CHECKED_FILE = "../data/luggage_checked.json"
LUGGAGE_REJECTED_FILE = "../data/luggage_rejected.json"
SECURITY_CHECKED_FILE = "../data/security_checked.json"
SECURITY_REJECTED_FILE = "../data/security_rejected.json"
STAIRS_FILE = "../data/stairs.json"
LOGS_FILE = f"../logs/logs_{floor(time())}.txt"
LOGS_DIRECTORY = "../logs"
STATS_DIRECTORY = "../stats"

# Sćieżki do kolejek
TO_GATE_QUEUE = "./tmp/to_gate_queue"
FROM_GATE_QUEUE = "./tmp/from_gate_queue"
TO_AIRPLANE_QUEUE = "./tmp/to_airplane_queue"
FROM_AIRPLANE_QUEUE = "./tmp/from_airplane_queue"
TO_LUGGAGE_QUEUE = "./tmp/to_luggage_queue"
FROM_LUGGAGE_QUEUE = "./tmp/from_luggage_queue"


# Wiadmości wysyłane przez procesy
class MESSAGES:
    # Generator
    NEW_PASSENGER = "Wygenerowano pasażera"
    # Luggage
    LUGGAGE_CHECK_BEGIN = "Sprawdzam pasażera"
    LUGGAGE_CHECK_OK = "przeszedł kontrolę bagażową"
    LUGGAGE_CHECK_REJECT = "odrzucony - za ciężki bagaż"
    # Security
    SECURITY_CONTROL_BEGIN = "rozpoczyna kontrolę bezpieczeństwa"
    SECURITY_CONTROL_OK = "przeszedł kontrolę bezpieczeństwa"
    SECURITY_CONTROL_REJECT = "odrzucony - znaleziono niebezpieczne przedmioty"
    # Gate
    RECEIVED_AIRPLANE_READY = "Otrzymano sygnał o gotowości samolotu"
    MOVING_PASSENGERS = "pasażerów na schody"
    GATE_READY = "Oczekiwanie na sygnał od dyspozytora"
    # Dispatcher
    AIRPLANE_READY = "Nowy odlot"
    OVERPOPULATE = "Przeludnienie na lotnisku, zamykanie"
    # Airplane
    PASSENGERS_BOARDED = "pasażerów wsiadło na pokład"
    BOARDING_COMPLETED = "Boarding skończony"
    FLIGHT_START = "startuje"
    FLIGHT_ENDED = "lot zakończony"
    AIRPLANE_RETURNED = "Powrócił na lotnisko"


# Nazwy lokalizacji w procesach
class LOCATIONS:
    ENTRANCE = "ENTRANCE"
    LUGGAGE = "LUGGAGE"
    SECURITY = "SECURITY"
    GATE = "GATE"
    DISPATCHER = "DISPATCHER"
    AIRPLANE = "AIRPLANE"
