from time import time
from math import floor


# Konfiguracja generatora pasażerów
DANGEROUS_ITEMS_PROBABILITY = 0.01  # 1% chance
VIP_PROBABILITY = 0.05  # 5% chance
MIN_LUGGAGE_WEIGHT = 1.0  # kg
MAX_LUGGAGE_WEIGHT = 15.0  # kg
PASSENGER_GENERATION_MIN_DELAY = 0.75  # seconds
PASSENGER_GENERATION_MAX_DELAY = 1  # seconds


# Sćieżki do plików
ENTRANCE_FILE = "../data/entrance.json"
LUGGAGE_CHECKED_FILE = "../data/luggage_checked.json"
LUGGAGE_REJECTED_FILE = "../data/luggage_rejected.json"
LOGS_FILE = f"../logs/logs_{floor(time())}.txt"
LOGS_DIRECTORY = "../logs"
SECURITY_CHECKED_FILE = "../data/security_checked.json"
SECURITY_REJECTED_FILE = "../data/security_rejected.json"

AIRPORT_LUGGAGE_LIMIT = 12.5  # kg

# Konfiguracja kontroli pasażerów
SECURITY_CHECKPOINTS_COUNT = 3
MAX_PASSENGERS_PER_CHECKPOINT = 2
MAX_CONTROL_PASSES = 3 # max num of passes through security control

# Wiadmości wysyłane przez procesy
class MESSAGES:
    # Generator
    NEW_PASSENGER = 'Wygenerowano pasażera'
    # Luggage
    LUGGAGE_CHECK_BEGIN = 'Sprawdzam pasażera'
    LUGGAGE_CHECK_OK = 'przeszedł kontrolę bagażową'
    LUGGAGE_CHECK_REJECT = "odrzucony - za ciężki bagaż"
    # Security
    SECURITY_CONTROL_BEGIN = "rozpoczyna kontrolę bezpieczeństwa"
    SECURITY_CONTROL_OK = "przeszedł kontrolę bezpieczeństwa"
    SECURITY_CONTROL_REJECT = "odrzucony - znaleziono niebezpieczne przedmioty"

# Nazwy lokalizacji w procesach
class LOCATIONS:
    ENTRANCE = 'ENTRANCE'
    LUGGAGE = 'LUGGAGE'
    SECURITY = 'SECURITY'
    
