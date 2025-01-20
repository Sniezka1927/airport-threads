from consts import MIN_LUGGAGE_WEIGHT, MAX_LUGGAGE_WEIGHT
from generator import generate_passenger
from cleanup import clear_files

def test_generate_multiple_passengers():
    passenger = generate_passenger()
    assert passenger.isVIP in [True, False]
    assert passenger.hasDangerousItems in [True, False]
    assert passenger.luggageWeight>= MIN_LUGGAGE_WEIGHT
    assert passenger.luggageWeight <= MAX_LUGGAGE_WEIGHT
    assert passenger.gender in ['M', 'F']
    assert passenger.id == 1

    passenger = generate_passenger()
    assert passenger.isVIP in [True, False]
    assert passenger.hasDangerousItems in [True, False]
    assert passenger.luggageWeight >= MIN_LUGGAGE_WEIGHT
    assert passenger.luggageWeight <= MAX_LUGGAGE_WEIGHT
    assert passenger.gender in ['M', 'F']
    assert passenger.id == 2

if __name__ == "__main__":
    clear_files(False)
    test_generate_multiple_passengers()
    print("OK")