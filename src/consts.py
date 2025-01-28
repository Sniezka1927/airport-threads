# Stałe
MAX_PASSENGERS = 30
VIP_PROBABILITY = 0.3
BAGGAGE_LIMIT = 2000
SECURITY_CHECK_PROBABILITY = 0.9
MESSAGE_SEPARATOR = "|||"
SECURITY_STATIONS = 3
MAX_PASSENGERS_PER_STATION = 2
MAX_SKIP = 3
FLIGHT_CAPACITY = 20  # Pojemność samolotu
FLIGHT_DEPARTURE_TIME = 5  # Czas odlotu samolotu w sekundach
DISPATCHER_INTERVAL = 10  # Czas między kolejnymi samolotami
MIN_PLANE_CAPACITY = 15  # Minimalna pojemność samolotu
MAX_PLANE_CAPACITY = 25  # Maksymalna pojemność samolotu

# Typy komunikatów
MSG_PLANE_READY = "PLANE_READY"  # Komunikat o gotowości samolotu
MSG_BOARDING_COMPLETE = "BOARDING_COMPLETE"  # Komunikat o zakończeniu boardingu
MSG_END = "END"  # Komunikat końcowy

# Global variables
child_processes = []
terminating = False
passed_security_count = 0
departure_signal_received = False
