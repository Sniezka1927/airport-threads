from dataclasses import asdict
from queue_handler import Queue
from gate import handle_passengers
from generator import generate_passenger as _generate_passenger
from cleanup import clear_files
from utils import save_passengers, read_passengers
from consts import SECURITY_CHECKED_FILE, AIRPLANE_CAPACITY, STAIRS_FILE, TO_GATE_QUEUE
import threading
import time
import random


def generate_passengers(count: int) -> list[dict]:
    passengers = []
    for i in range(count):
        rnd_pid = random.randint(100000000, 999999999)
        passenger = _generate_passenger(rnd_pid)
        passengers.append(asdict(passenger))
    return passengers


def test_exact_passengers():
    queue = Queue(TO_GATE_QUEUE)
    passengers = generate_passengers(AIRPLANE_CAPACITY)
    save_passengers(SECURITY_CHECKED_FILE, passengers)
    queue.put(("airplane_ready", AIRPLANE_CAPACITY, 10000))

    thread = threading.Thread(target=handle_passengers, args=(queue,))
    thread.daemon = True
    thread.start()

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    assert len(read_passengers(STAIRS_FILE)) == 0
    assert len(read_passengers(SECURITY_CHECKED_FILE)) == 0
    print("\n")
    time.sleep(10)


def test_not_enough_passengers():
    queue = Queue(TO_GATE_QUEUE)
    passengers = generate_passengers(AIRPLANE_CAPACITY - 1)
    save_passengers(SECURITY_CHECKED_FILE, passengers)
    queue.put(("airplane_ready", AIRPLANE_CAPACITY, 10000))

    thread = threading.Thread(target=handle_passengers, args=(queue,))
    thread.daemon = True
    thread.start()

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    assert len(read_passengers(STAIRS_FILE)) == 0
    assert len(read_passengers(SECURITY_CHECKED_FILE)) == 0
    print("\n")
    time.sleep(10)


def test_too_much_passengers():
    queue = Queue(TO_GATE_QUEUE)
    passengers = generate_passengers(AIRPLANE_CAPACITY + 1)
    save_passengers(SECURITY_CHECKED_FILE, passengers)
    queue.put(("airplane_ready", AIRPLANE_CAPACITY, 10000))

    thread = threading.Thread(target=handle_passengers, args=(queue,))
    thread.daemon = True
    thread.start()

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    time.sleep(2)
    save_passengers(STAIRS_FILE, [])

    assert len(read_passengers(STAIRS_FILE)) == 0
    assert len(read_passengers(SECURITY_CHECKED_FILE)) == 1


# if __name__ == "__main__":
#     clear_files(False)
#     test_exact_passengers()
#     test_not_enough_passengers()
#     test_too_much_passengers()
#     print("OK")
#     clear_files(False)
