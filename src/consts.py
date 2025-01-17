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


AIRPORT_LUGGAGE_LIMIT = 12.5  # kg

# Wiadmości wysyłane przez procesy
class MESSAGES:
    # Generator
    NEW_PASSENGER = 'Wygenerowano pasażera'
    # Luggage
    LUGGAGE_CHECK_BEGIN = 'Sprawdzam pasażera'
    LUGGAGE_CHECK_OK = 'przeszedł kontrolę bagażową'
    LUGGAGE_CHECK_REJECT = "odrzucony - za ciężki bagaż"
# Nazwy lokalizacji w procesach
class LOCATIONS:
    ENTRANCE = 'ENTRANCE'
    LUGGAGE = 'LUGGAGE'
    
