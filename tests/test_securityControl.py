from dataclasses import asdict
from generator import generate_passenger as _generate_passenger
from cleanup import clear_files
from securityControl import SecurityCheckpoint, process_passengers
from luggageControl import get_file_name
from utils import save_passengers, read_passengers
from consts import LUGGAGE_CHECKED_FILE, SECURITY_CHECKED_FILE, SECURITY_REJECTED_FILE
import random


def generate_passengers(
    count: int, male_count: int = 0, with_items: bool = False, is_vip: bool = False
) -> list[dict]:
    passengers = []
    for i in range(count):
        rnd_pid = random.randint(100000000, 999999999)
        passenger = _generate_passenger(rnd_pid)
        passenger.hasDangerousItems = with_items
        passenger.isVIP = is_vip
        if i < male_count:
            passenger.gender = "M"
        else:
            passenger.gender = "F"

        passengers.append(asdict(passenger))
    return passengers


def test_single_passenger():
    clear_files(False)
    passengers = generate_passengers(1, 0, False)
    checkpoint = SecurityCheckpoint()
    save_passengers(get_file_name(0), passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 1
    assert len(rejected_passengers) == 0


def test_single_passenger_with_dangerous_items():
    clear_files(False)
    passengers = generate_passengers(1, 0, True)
    checkpoint = SecurityCheckpoint()
    save_passengers(get_file_name(0), passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 0
    assert len(rejected_passengers) == 1


def test_multiple_passengers():
    clear_files(False)
    checkpoint = SecurityCheckpoint()

    for station in checkpoint.stations:
        passengers = generate_passengers(2, 2)
        save_passengers(station.file_name, passengers)

    process_passengers(checkpoint)

    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)

    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 6
    assert len(rejected_passengers) == 0


def test_gender_control():
    clear_files(False)
    checkpoint = SecurityCheckpoint()

    for station in checkpoint.stations:
        passengers = generate_passengers(2, 2 if station.station_id != 2 else 1)
        save_passengers(station.file_name, passengers)

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 5
    assert len(rejected_passengers) == 0

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 6


def test_passing_passengers():
    clear_files(False)
    checkpoint = SecurityCheckpoint()

    initial_passengers = generate_passengers(2, 1)
    additional_male = generate_passengers(1, 1)
    passengers = initial_passengers + additional_male
    save_passengers(get_file_name(0), passengers)

    process_passengers(checkpoint)

    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 2
    assert len(rejected_passengers) == 0

    remaining_passengers = read_passengers(get_file_name(0))
    assert len(remaining_passengers) == 1
    assert remaining_passengers[0]["gender"] == "F"
    assert remaining_passengers[0]["controlPassed"] == 1

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 3
    assert passed_passengers[-1]["gender"] == "F"
    assert passed_passengers[-1]["controlPassed"] == 1


def test_vip_pass():
    clear_files(False)

    initial_passengers = generate_passengers(2, 2)
    additional_female_vip = generate_passengers(1, 0, False, True)
    passengers = initial_passengers + additional_female_vip
    checkpoint = SecurityCheckpoint()
    save_passengers(get_file_name(0), passengers)

    process_passengers(checkpoint)

    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 1
    assert len(rejected_passengers) == 0

    remaining_passengers = read_passengers(get_file_name(0))
    assert len(remaining_passengers) == 2
    assert remaining_passengers[0]["gender"] == "M"
    assert remaining_passengers[1]["gender"] == "M"

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 3


if __name__ == "__main__":
    test_single_passenger()
    test_single_passenger_with_dangerous_items()
    test_multiple_passengers()
    test_gender_control()
    test_passing_passengers()
    test_vip_pass()
    print("OK")
