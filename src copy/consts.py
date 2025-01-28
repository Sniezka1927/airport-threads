# Stałe
MAX_PASSENGERS = 30
VIP_PROBABILITY = 0.3
BAGGAGE_LIMIT = 2000
SECURITY_CHECK_PROBABILITY = 0.9
MESSAGE_SEPARATOR = "|||"
SECURITY_STATIONS = 3
MAX_PASSENGERS_PER_STATION = 2
MAX_SKIP = 3
STAIRS_CAPACITY = 5  # Pojemność schodów pasażerskich
FLIGHT_CAPACITY = 20  # Pojemność samolotu
FLIGHT_DEPARTURE_TIME = 30  # Czas odlotu samolotu w sekundach
NUM_PLANES = 1  # Liczba samolotów

# Global variable to track child processes
child_processes = []
terminating = False

# Global variable to track the number of passengers who passed security check
passed_security_count = 0
planes = []
departure_signal_received = False
