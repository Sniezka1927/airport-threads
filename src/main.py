import os
import time
import random
import sys
import signal
from baggage_check import baggage_check
from security_check import security_check
from generator import generate_passengers
from departure_lounge import departure_lounge
from dispatcher import dispatcher
from consts import SECURITY_STATIONS, child_processes, terminating


def signal_handler(signum, frame):
    global terminating
    if terminating:
        return
    terminating = True
    try:
        sys.stdout.write("\nReceived termination signal. Cleaning up...\n")
        sys.stdout.flush()
        for pid in child_processes:
            try:
                os.kill(pid, signal.SIGTERM)
            except (ProcessLookupError, OSError):
                continue
    except:
        pass
    finally:
        os._exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Utworzenie pipe'ów
    baggage_pipe_read, baggage_pipe_write = os.pipe()
    security_pipes = [os.pipe() for _ in range(SECURITY_STATIONS)]
    security_to_lounge_read, security_to_lounge_write = os.pipe()
    dispatcher_to_lounge_read, dispatcher_to_lounge_write = os.pipe()
    lounge_to_dispatcher_read, lounge_to_dispatcher_write = os.pipe()

    try:
        pid_baggage = os.fork()
        if pid_baggage == 0:
            os.close(baggage_pipe_write)
            write_pipes = [pipe[1] for pipe in security_pipes]
            for pipe in security_pipes:
                os.close(pipe[0])
            baggage_check(baggage_pipe_read, write_pipes)
            os._exit(0)
        else:
            child_processes.append(pid_baggage)

        security_processes = []
        for i in range(SECURITY_STATIONS):
            pid_security = os.fork()
            if pid_security == 0:
                os.close(baggage_pipe_read)
                os.close(baggage_pipe_write)
                for j, pipe in enumerate(security_pipes):
                    if j != i:
                        os.close(pipe[0])
                        os.close(pipe[1])
                security_check(i + 1, security_pipes[i][0], security_to_lounge_write)
                os._exit(0)
            else:
                security_processes.append(pid_security)
                child_processes.append(pid_security)

        pid_dispatcher = os.fork()
        if pid_dispatcher == 0:
            os.close(baggage_pipe_read)
            os.close(baggage_pipe_write)
            for pipe in security_pipes:
                os.close(pipe[0])
                os.close(pipe[1])
            os.close(security_to_lounge_read)
            os.close(security_to_lounge_write)
            dispatcher(dispatcher_to_lounge_write, lounge_to_dispatcher_read)
            os._exit(0)
        else:
            child_processes.append(pid_dispatcher)

        pid_departure = os.fork()
        if pid_departure == 0:
            os.close(baggage_pipe_read)
            os.close(baggage_pipe_write)
            for pipe in security_pipes:
                os.close(pipe[0])
                os.close(pipe[1])
            departure_lounge(
                security_to_lounge_read,
                dispatcher_to_lounge_read,
                lounge_to_dispatcher_write,
            )
            os._exit(0)
        else:
            child_processes.append(pid_departure)

        os.close(baggage_pipe_read)
        for pipe in security_pipes:
            os.close(pipe[0])
            os.close(pipe[1])
        os.close(security_to_lounge_read)
        os.close(dispatcher_to_lounge_read)
        os.close(dispatcher_to_lounge_write)
        os.close(lounge_to_dispatcher_read)
        os.close(lounge_to_dispatcher_write)

        generate_passengers(baggage_pipe_write)
        os.close(baggage_pipe_write)

        for pid in child_processes:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass
            except KeyboardInterrupt:
                signal_handler(signal.SIGINT, None)

        print("Symulacja zakończona.")

    except Exception as e:
        sys.stderr.write(f"Wystąpił błąd: {str(e)}\n")
        signal_handler(signal.SIGTERM, None)
