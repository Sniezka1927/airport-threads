import os
import signal
from gate import process_passengers
from dispatcher import Dispatcher
from generator import generate_continuously
from luggageControl import check_luggage_continuously
from securityControl import check_security_continuously
from cleanup import clear_files
from utils import validate_config
from stats import Statistics


class ProcessManager:
    def __init__(self):
        self.child_pids = []

    def fork_process(self, target_function, args=()):
        pid = os.fork()
        if pid == 0:
            try:
                if args:
                    target_function(*args)
                else:
                    target_function()
                os._exit(0)
            except KeyboardInterrupt:
                os._exit(0)
        else:
            self.child_pids.append(pid)
            return pid

    def terminate_all(self):
        for pid in self.child_pids:
            try:
                os.kill(pid, signal.SIGTERM)
                os.waitpid(pid, 0)
            except OSError:
                pass
        self.child_pids = []


def main():
    clear_files()
    validate_config()

    process_manager = ProcessManager()
    dispatcher = Dispatcher()

    try:
        # Start procesów
        process_manager.fork_process(dispatcher.dispatcher_loop)
        process_manager.fork_process(process_passengers, (dispatcher.to_gate_queue,))
        process_manager.fork_process(generate_continuously)
        process_manager.fork_process(
            check_luggage_continuously, (dispatcher.to_luggage_queue,)
        )
        process_manager.fork_process(check_security_continuously)

        # Oczekiwania na ich zakończenie
        while True:
            try:
                pid, status = os.waitpid(-1, 0)
                if pid > 0:
                    process_manager.child_pids.remove(pid)
                if not process_manager.child_pids:
                    break
            except OSError:
                break
            except KeyboardInterrupt:
                raise

    except KeyboardInterrupt:
        print("\nOtrzymano sygnał zakończenia...")

    finally:
        print("Kończenie wszystkich procesów...")
        # Kończenie procesu dispatcher'a
        dispatcher.terminate_all_processes()
        # Kończenie głownych porcesów
        process_manager.terminate_all()
        print("Wszystkie procesy zostały zakończone.")

        # Collect statystyk
        stats = Statistics()
        stats.collect()
        stats.save()


if __name__ == "__main__":
    main()
