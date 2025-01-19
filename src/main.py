import time
from multiprocessing import Process, Queue
from gate import process_passengers
from dispatcher import Dispatcher
from generator import generate_continuously
from luggageControl import check_luggage_continuously
from securityControl import check_security_continuously
from cleanup import clear_files
from utils import validate_config


def main():
    clear_files()
    validate_config()

    dispatcher = Dispatcher()
    generator_process = Process(target=generate_continuously)
    luggage_control_process = Process(target=check_luggage_continuously, args=(dispatcher.luggage_queue,))
    security_control_process = Process(target=check_security_continuously)
    dispatcher_process = Process(target=dispatcher.dispatcher_loop)
    gate_process = Process(target=process_passengers, args=(dispatcher.gate_queue,))

    try:
        dispatcher_process.start()
        gate_process.start()
        generator_process.start()
        luggage_control_process.start()
        security_control_process.start()
        # Czekanie na zakończenie procesów
        dispatcher_process.join()
        gate_process.join()
        generator_process.join()
        luggage_control_process.join()
        security_control_process.join()

    except KeyboardInterrupt:
        print("\nOtrzymano sygnał zakończenia...")
        # Kończenie procesów
        if generator_process.is_alive():
            print("Kończenie procesu generatora...")
            generator_process.terminate()

        if luggage_control_process.is_alive():
            print("Kończenie procesu kontroli bagażowej...")
            luggage_control_process.terminate()

        if security_control_process.is_alive():
            print("Kończenie procesu kontroli bezpieczeństwa...")
            security_control_process.terminate()

        # Zakończ wszystkie procesy samolotów
        dispatcher.terminate_all_processes()

        if dispatcher_process.is_alive():
            print("Kończenie procesu dyspozytora...")
            dispatcher_process.terminate()

        if gate_process.is_alive():
            print("Kończenie procesu gate'ów...")
            gate_process.terminate()

        # Kończenie procesów
        generator_process.join()
        luggage_control_process.join()
        security_control_process.join()
        dispatcher_process.join()
        gate_process.join()

        print("Wszystkie procesy zostały zakończone.")


if __name__ == "__main__":
    main()