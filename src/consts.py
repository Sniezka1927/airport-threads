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
LOGS_FILE = f"../logs/logs_{floor(time())}.txt"
LOGS_DIRECTORY = "../logs"

# Wiadmości wysyłane przez procesy
class MESSAGES:
    # Generator
    NEW_PASSENGER = 'Wygenerowano pasażera'
# Nazwy lokalizacji w procesach
class LOCATIONS:
    ENTRANCE = 'ENTRANCE'
