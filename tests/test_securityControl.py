from dataclasses import asdict
from generator import generate_passenger as _generate_passenger
from cleanup import clear_files
from securityControl import SecurityCheckpoint, process_passengers
from utils import save_passengers, read_passengers
from consts import  LUGGAGE_CHECKED_FILE, SECURITY_CHECKED_FILE, SECURITY_REJECTED_FILE


def generate_passengers(count: int, male_count: int = 0, with_items: bool = False, is_vip: bool = False) -> list[dict]:
    passengers = []
    for i in range(count):
        passenger = _generate_passenger()
        passenger.hasDangerousItems = with_items
        passenger.isVIP = is_vip
        if i < male_count:
            passenger.gender = 'M'
        else:
            passenger.gender = 'F'

        passengers.append(asdict(passenger))
    return passengers


def test_single_passenger():
    passengers = generate_passengers(1, 0,False)
    checkpoint = SecurityCheckpoint()
    save_passengers(LUGGAGE_CHECKED_FILE, passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 1
    assert len(rejected_passengers) == 0

def test_single_passenger_with_dangerous_items():
    passengers = generate_passengers(1, 0,True)
    checkpoint = SecurityCheckpoint()
    save_passengers(LUGGAGE_CHECKED_FILE, passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 1
    assert len(rejected_passengers) == 1

def test_multiple_passengers():
    passengers = generate_passengers(6, 6)
    checkpoint = SecurityCheckpoint()
    save_passengers(LUGGAGE_CHECKED_FILE, passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 7
    assert len(rejected_passengers) == 1

def test_gender_control():
    passengers = generate_passengers(6, 5)
    checkpoint = SecurityCheckpoint()
    save_passengers(LUGGAGE_CHECKED_FILE, passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 12
    assert len(rejected_passengers) == 1

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 13


def test_passing_passengers():
    initial_passengers = generate_passengers(6, 5)
    additional_male = generate_passengers(1, 1)
    passengers = initial_passengers + additional_male
    checkpoint = SecurityCheckpoint()
    save_passengers(LUGGAGE_CHECKED_FILE, passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 19
    assert len(rejected_passengers) == 1

    remaining_passengers = read_passengers(LUGGAGE_CHECKED_FILE)
    assert len(remaining_passengers) == 1
    assert remaining_passengers[0]['gender'] == 'F'

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 20
    assert passed_passengers[-1]['gender'] == 'F'
    assert passed_passengers[-1]['controlPassed'] == 1

def test_vip_pass():
    initial_passengers = generate_passengers(6, 6)
    additional_female_vip = generate_passengers(1, 0, False, True)
    passengers = initial_passengers + additional_female_vip
    checkpoint = SecurityCheckpoint()
    save_passengers(LUGGAGE_CHECKED_FILE, passengers)
    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    rejected_passengers = read_passengers(SECURITY_REJECTED_FILE)
    assert len(passed_passengers) == 25
    assert len(rejected_passengers) == 1

    remaining_passengers = read_passengers(LUGGAGE_CHECKED_FILE)
    assert len(remaining_passengers) == 2
    assert remaining_passengers[0]['gender'] == 'M'
    assert remaining_passengers[1]['gender'] == 'M'

    process_passengers(checkpoint)
    passed_passengers = read_passengers(SECURITY_CHECKED_FILE)
    assert len(passed_passengers) == 27

if __name__ == "__main__":
    clear_files(False)
    test_single_passenger()
    test_single_passenger_with_dangerous_items()
    test_multiple_passengers()
    test_gender_control()
    test_passing_passengers()
    test_vip_pass()
    print("OK")