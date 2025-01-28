import os
import time
import random
import sys
import signal
from baggage_check import baggage_check
from security_check import security_check
from generator import generate_passengers
from consts import SECURITY_STATIONS

# Global variable to track child processes
child_processes = []
terminating = False

# Global variable to track the number of passengers who passed security check
passed_security_count = 0
child_processes = []
terminating = False
passed_security_count = 0
planes = []
departure_signal_received = False


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

    baggage_pipe_read, baggage_pipe_write = os.pipe()
    security_pipes = [os.pipe() for _ in range(SECURITY_STATIONS)]
    approved_pipe_read, approved_pipe_write = os.pipe()
    departure_pipe_read, departure_pipe_write = os.pipe()

    try:
        # Fork baggage check process
        pid_baggage = os.fork()
        if pid_baggage == 0:
            os.close(baggage_pipe_write)
            write_pipes = [pipe[1] for pipe in security_pipes]
            for pipe in security_pipes:
                os.close(pipe[0])
            os.close(approved_pipe_read)
            os.close(approved_pipe_write)
            baggage_check(baggage_pipe_read, write_pipes)
            os.close(baggage_pipe_read)
            for pipe in write_pipes:
                os.close(pipe)
            sys.exit(0)
        else:
            child_processes.append(pid_baggage)

        # Fork security check processes
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
                os.close(approved_pipe_read)
                security_check(i + 1, security_pipes[i][0], departure_pipe_write)
                os.close(security_pipes[i][0])
                os.close(departure_pipe_write)
                sys.exit(0)
            else:
                security_processes.append(pid_security)
                child_processes.append(pid_security)

        # Parent process - generate passengers
        os.close(baggage_pipe_read)
        for pipe in security_pipes:
            os.close(pipe[0])
            os.close(pipe[1])
        os.close(approved_pipe_read)
        os.close(approved_pipe_write)
        generate_passengers(baggage_pipe_write)
        os.close(baggage_pipe_write)

        # Wait for child processes to finish
        for pid in child_processes:
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass
            except KeyboardInterrupt:
                signal_handler(signal.SIGINT, None)

        print("Symulacja zakończona.")

    except Exception as e:
        try:
            sys.stderr.write(f"Wystąpił błąd: {str(e)}\n")
            sys.stderr.flush()
        except:
            pass
        finally:
            signal_handler(signal.SIGTERM, None)
