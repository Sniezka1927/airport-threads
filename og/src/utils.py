import multiprocessing
import time
import random

# Stałe
MAX_PASSENGERS = 10
VIP_PROBABILITY = 0.2  # 20% szans na VIP-a


# Klasa reprezentująca pasażera
class Passenger:
    def __init__(self, pid, is_vip):
        self.pid = pid
        self.is_vip = is_vip

    def __str__(self):
        return f"Pasażer {self.pid} {'VIP' if self.is_vip else 'zwykły'}"


# Funkcja kontroli biletowo-bagażowej
def baggage_check(passenger_queue, lock, pipe):
    while True:
        with lock:
            if not passenger_queue.empty():
                passenger = passenger_queue.get()
                print(f"Kontrola biletowo-bagażowa: {passenger}")
                # Symulacja czasu kontroli
                time.sleep(random.uniform(0.5, 1.5))
                # Wysyłanie informacji o zakończeniu kontroli
                pipe.send(f"{passenger} przeszedł kontrolę.")
            else:
                break


# Funkcja generująca pasażerów
def generate_passengers(passenger_queue, lock):
    for i in range(1, MAX_PASSENGERS + 1):
        time.sleep(1)  # Generowanie pasażera co 1 sekundę
        is_vip = random.random() < VIP_PROBABILITY
        passenger = Passenger(i, is_vip)
        with lock:
            if is_vip:
                # Pasażerowie VIP są dodawani na początek kolejki
                temp_queue = multiprocessing.Queue()
                temp_queue.put(passenger)
                while not passenger_queue.empty():
                    temp_queue.put(passenger_queue.get())
                while not temp_queue.empty():
                    passenger_queue.put(temp_queue.get())
            else:
                passenger_queue.put(passenger)
            print(f"Wygenerowano: {passenger}")


if __name__ == "__main__":
    # Inicjalizacja kolejki pasażerów, locka i pipe
    passenger_queue = multiprocessing.Queue()
    lock = multiprocessing.Lock()
    parent_conn, child_conn = multiprocessing.Pipe()

    # Proces generowania pasażerów
    passenger_process = multiprocessing.Process(
        target=generate_passengers, args=(passenger_queue, lock)
    )
    passenger_process.start()

    # Proces kontroli biletowo-bagażowej
    baggage_process = multiprocessing.Process(
        target=baggage_check, args=(passenger_queue, lock, child_conn)
    )
    baggage_process.start()

    # Oczekiwanie na zakończenie generowania pasażerów
    passenger_process.join()

    # Oczekiwanie na zakończenie kontroli biletowo-bagażowej
    baggage_process.join()

    # Odczytanie wyników z pipe
    while parent_conn.poll():
        print(parent_conn.recv())

    print("Wszyscy pasażerowie przeszli kontrolę.")
