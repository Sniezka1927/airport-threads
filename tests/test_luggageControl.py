from dataclasses import asdict
from consts import MIN_LUGGAGE_WEIGHT, MAX_LUGGAGE_WEIGHT, AIRPORT_LUGGAGE_LIMIT
from generator import generate_passenger
from luggageControl import validate_passenger
from cleanup import clear_files
from utils import save_passengers, read_passengers
from consts import ENTRANCE_FILE, LUGGAGE_CHECKED_FILE, LUGGAGE_REJECTED_FILE


def test_check_passenger_with_correct_luggage_weight():
    clear_files(False)
    passenger = generate_passenger()
    assert passenger.isVIP in [True, False]
    assert passenger.hasDangerousItems in [True, False]
    assert passenger.luggageWeight >= MIN_LUGGAGE_WEIGHT
    assert passenger.luggageWeight <= MAX_LUGGAGE_WEIGHT
    assert passenger.gender in ['M', 'F']
    assert passenger.id == 1

    passenger.luggageWeight = AIRPORT_LUGGAGE_LIMIT - 1

    save_passengers(ENTRANCE_FILE, [asdict(passenger)])
    validate_passenger(asdict(passenger))

    passed_passengers = read_passengers(LUGGAGE_CHECKED_FILE)
    assert len(passed_passengers) == 1

    passed_passenger = passed_passengers[0]
    assert passed_passenger['id'] == passenger.id
    assert passed_passenger['luggageWeight'] == passenger.luggageWeight
    assert passed_passenger['isVIP'] == passenger.isVIP
    assert passed_passenger['hasDangerousItems'] == passenger.hasDangerousItems


def test_check_passenger_with_incorrect_luggage_weight():
    passenger = generate_passenger()
    assert passenger.isVIP in [True, False]
    assert passenger.hasDangerousItems in [True, False]
    assert passenger.luggageWeight >= MIN_LUGGAGE_WEIGHT
    assert passenger.luggageWeight <= MAX_LUGGAGE_WEIGHT
    assert passenger.gender in ['M', 'F']
    assert passenger.id == 2
    passenger.luggageWeight = AIRPORT_LUGGAGE_LIMIT + 0.001
    save_passengers(ENTRANCE_FILE, [asdict(passenger)])
    validate_passenger(asdict(passenger))

    passed_passengers = read_passengers(LUGGAGE_REJECTED_FILE)
    assert len(passed_passengers) == 1

    passed_passenger = passed_passengers[0]
    assert passed_passenger['id'] == passenger.id
    assert passed_passenger['luggageWeight'] == passenger.luggageWeight
    assert passed_passenger['isVIP'] == passenger.isVIP
    assert passed_passenger['hasDangerousItems'] == passenger.hasDangerousItems


if __name__ == "__main__":
    test_check_passenger_with_correct_luggage_weight()
    test_check_passenger_with_incorrect_luggage_weight()
    print("OK")