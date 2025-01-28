import os
import time
import random
import sys
import signal
from consts import BAGGAGE_LIMIT, MESSAGE_SEPARATOR, SECURITY_STATIONS
from generator import Passenger


def baggage_check(read_pipe, write_pipes):
    try:
        buffer = ""
        next_station = 0
        while True:
            data = os.read(read_pipe, 100).decode()
            if not data:
                break
            buffer += data
            while MESSAGE_SEPARATOR in buffer:
                message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                if message == "END":
                    for pipe in write_pipes:
                        os.write(pipe, f"END{MESSAGE_SEPARATOR}".encode())
                    return
                pid, is_vip, baggage_weight, gender = message.split("|")
                is_vip = is_vip == "True"
                baggage_weight = int(baggage_weight)
                passenger = Passenger(int(pid), is_vip, baggage_weight, gender)
                print(f"Kontrola biletowo-bagażowa: {passenger}")
                time.sleep(random.uniform(0.1, 0.3))

                if baggage_weight <= BAGGAGE_LIMIT:
                    print(f"{passenger} przeszedł kontrolę bagażową.")
                    # Wysyłanie do kolejnego dostępnego stanowiska (round-robin)
                    os.write(
                        write_pipes[next_station],
                        f"{message}{MESSAGE_SEPARATOR}".encode(),
                    )
                    next_station = (next_station + 1) % SECURITY_STATIONS
                else:
                    print(
                        f"{passenger} nie przeszedł kontroli bagażowej (za ciężki bagaż)."
                    )
    except KeyboardInterrupt:
        sys.exit(0)
