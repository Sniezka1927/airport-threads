import os
import time
import random
import sys
from consts import (
    MAX_PASSENGERS,
    VIP_PROBABILITY,
    MESSAGE_SEPARATOR,
    passed_security_count,
)


class Passenger:
    def __init__(self, pid, is_vip, baggage_weight, gender):
        self.pid = pid
        self.is_vip = is_vip
        self.baggage_weight = baggage_weight
        self.gender = gender
        self.skipped = 0  # Licznik przepuszczonych osób

    def __str__(self):
        return f"Pasażer {self.pid} {'VIP' if self.is_vip else 'zwykły'} (płeć: {self.gender}, bagaż: {self.baggage_weight} kg)"


def generate_passengers(write_pipe):
    try:
        for i in range(1, MAX_PASSENGERS + 1):
            time.sleep(0.2)
            is_vip = random.random() < VIP_PROBABILITY
            baggage_weight = random.randint(10, 30)
            gender = random.choice(["M", "F"])
            passenger = Passenger(i, is_vip, baggage_weight, gender)
            passenger_data = f"{i}|{is_vip}|{baggage_weight}|{gender}"
            os.write(write_pipe, f"{passenger_data}{MESSAGE_SEPARATOR}".encode())
            print(f"Wygenerowano: {passenger}")
        os.write(write_pipe, f"END{MESSAGE_SEPARATOR}".encode())

        # Wait until all passengers have passed security check
        while passed_security_count < MAX_PASSENGERS:
            time.sleep(0.1)

        print("Wszyscy pasażerowie przeszli kontrolę bezpieczeństwa.")
    except KeyboardInterrupt:
        os.write(write_pipe, f"END{MESSAGE_SEPARATOR}".encode())
        sys.exit(0)
