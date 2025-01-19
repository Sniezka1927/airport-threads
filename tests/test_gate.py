from dataclasses import asdict
from multiprocessing import Queue
from src.gate import handle_passengers
from src.generator import generate_passenger as _generate_passenger
from src.cleanup import clear_files
from src.utils import save_passengers, read_passengers
from src.consts import  SECURITY_CHECKED_FILE, AIRPLANE_CAPACITY, STAIRS_FILE
import threading
import time

def generate_passengers(count: int) -> list[dict]:
    passengers = []
    for i in range(count):
        passenger = _generate_passenger()
        passengers.append(asdict(passenger))
    return passengers


def test_exact_passengers():
    queue = Queue()
    passengers = generate_passengers(AIRPLANE_CAPACITY)
    save_passengers(SECURITY_CHECKED_FILE, passengers)
    queue.put(("airplane_ready", AIRPLANE_CAPACITY, 1000))

    thread = threading.Thread(target=handle_passengers, args=(queue,))
    thread.daemon = True
    thread.start()

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    assert len(read_passengers(STAIRS_FILE)) == 0
    assert len(read_passengers(SECURITY_CHECKED_FILE)) == 0



def test_not_enough_passengers():
    queue = Queue()
    passengers = generate_passengers(AIRPLANE_CAPACITY - 1)
    save_passengers(SECURITY_CHECKED_FILE, passengers)
    queue.put(("airplane_ready", AIRPLANE_CAPACITY, 1000))

    thread = threading.Thread(target=handle_passengers, args=(queue,))
    thread.daemon = True
    thread.start()

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    assert len(read_passengers(STAIRS_FILE)) == 0
    assert len(read_passengers(SECURITY_CHECKED_FILE)) == 0


def test_too_much_passengers():
    queue = Queue()
    passengers = generate_passengers(AIRPLANE_CAPACITY + 1)
    save_passengers(SECURITY_CHECKED_FILE, passengers)
    queue.put(("airplane_ready", AIRPLANE_CAPACITY, 1000))

    thread = threading.Thread(target=handle_passengers, args=(queue,))
    thread.daemon = True
    thread.start()

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    assert len(read_passengers(STAIRS_FILE)) == 0
    assert len(read_passengers(SECURITY_CHECKED_FILE)) == 1


if __name__ == "__main__":
    clear_files(False)
    test_exact_passengers()
    test_not_enough_passengers()
    test_too_much_passengers()
    print("OK")