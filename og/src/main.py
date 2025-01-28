import os
import time
import random
import sys
import signal

# Stałe
MAX_PASSENGERS = 30
VIP_PROBABILITY = 0.3
BAGGAGE_LIMIT = 2000
SECURITY_CHECK_PROBABILITY = 0.9
MESSAGE_SEPARATOR = "|||"
SECURITY_STATIONS = 3
MAX_PASSENGERS_PER_STATION = 2
MAX_SKIP = 3
STAIRS_CAPACITY = 5  # Pojemność schodów pasażerskich
FLIGHT_CAPACITY = 20  # Pojemność samolotu
FLIGHT_DEPARTURE_TIME = 30  # Czas odlotu samolotu w sekundach
NUM_PLANES = 3  # Liczba samolotów

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


class Passenger:
    def __init__(self, pid, is_vip, baggage_weight, gender):
        self.pid = pid
        self.is_vip = is_vip
        self.baggage_weight = baggage_weight
        self.gender = gender
        self.skipped = 0  # Licznik przepuszczonych osób

    def __str__(self):
        return f"Pasażer {self.pid} {'VIP' if self.is_vip else 'zwykły'} (płeć: {self.gender}, bagaż: {self.baggage_weight} kg)"


def safe_print(message):
    try:
        sys.stdout.write(message + "\n")
        sys.stdout.flush()
    except:
        pass


class DepartureLounge:
    def __init__(self):
        self.waiting_passengers = []
        self.stairs_queue = []
        self.stairs_capacity = STAIRS_CAPACITY
        self.flight_capacity = FLIGHT_CAPACITY
        self.current_flight_passengers = []
        self.departure_signal_received = False

    def add_passenger(self, passenger):
        self.waiting_passengers.append(passenger)
        safe_print(f"Hala odlotów: Dodano pasażera {passenger} do kolejki.")

    def board_passengers(self):
        while not self.departure_signal_received:
            if self.waiting_passengers:
                # Pasażerowie VIP mają pierwszeństwo
                vip_passengers = [p for p in self.waiting_passengers if p.is_vip]
                if vip_passengers:
                    passenger = vip_passengers[0]
                    self.waiting_passengers.remove(passenger)
                else:
                    passenger = self.waiting_passengers[0]
                    self.waiting_passengers.remove(passenger)

                if len(self.stairs_queue) < self.stairs_capacity:
                    self.stairs_queue.append(passenger)
                    safe_print(
                        f"Schody pasażerskie: Pasażer {passenger} wchodzi na schody."
                    )
                else:
                    safe_print(
                        f"Schody pasażerskie: Brak miejsca dla pasażera {passenger}. Oczekuje."
                    )

                if len(self.current_flight_passengers) < self.flight_capacity:
                    self.current_flight_passengers.append(passenger)
                    safe_print(f"Samolot: Pasażer {passenger} wszedł na pokład.")
                else:
                    safe_print(
                        f"Samolot: Brak miejsca dla pasażera {passenger}. Oczekuje."
                    )

            time.sleep(1)

    def depart_flight(self):
        safe_print("Samolot: Kapitan sprawdza schody pasażerskie.")
        while self.stairs_queue:
            time.sleep(1)  # Czekaj aż schody będą puste
        safe_print("Samolot: Schody pasażerskie są puste. Samolot odlatuje.")
        self.current_flight_passengers.clear()

    def receive_departure_signal(self):
        self.departure_signal_received = True
        safe_print(
            "Hala odlotów: Otrzymano sygnał odlotu. Pasażerowie nie mogą wsiadać."
        )


class Plane:
    def __init__(self, plane_id, baggage_limit):
        self.plane_id = plane_id
        self.baggage_limit = baggage_limit
        self.passengers = []
        self.departure_time = FLIGHT_DEPARTURE_TIME

    def board_passengers(self, passengers):
        self.passengers.extend(passengers)
        safe_print(f"Samolot {self.plane_id}: Pasażerowie wsiedli na pokład.")

    def depart(self):
        safe_print(f"Samolot {self.plane_id}: Odlatuje.")
        time.sleep(self.departure_time)
        safe_print(f"Samolot {self.plane_id}: Wrócił na lotnisko.")
        self.passengers.clear()


def departure_lounge_process(lounge, read_pipe):
    try:
        buffer = ""
        while True:
            data = os.read(read_pipe, 100).decode()
            if not data:
                break
            buffer += data
            while MESSAGE_SEPARATOR in buffer:
                message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                if message == "END":
                    return
                pid, is_vip, baggage_weight, gender = message.split("|")
                is_vip = is_vip == "True"
                baggage_weight = int(baggage_weight)
                passenger = Passenger(int(pid), is_vip, baggage_weight, gender)
                lounge.add_passenger(passenger)
    except KeyboardInterrupt:
        sys.exit(0)


def plane_process(plane, lounge):
    try:
        while not departure_signal_received:
            plane.board_passengers(lounge.current_flight_passengers)
            time.sleep(FLIGHT_DEPARTURE_TIME)
            plane.depart()
    except KeyboardInterrupt:
        sys.exit(0)


def dispatcher_process(lounge):
    try:
        time.sleep(FLIGHT_DEPARTURE_TIME // 2)
        safe_print("Dyspozytor: Wysyłam sygnał odlotu.")
        lounge.receive_departure_signal()
    except KeyboardInterrupt:
        sys.exit(0)


def baggage_check(read_pipe, write_pipes):
    try:
        buffer = ""
        next_station = 0
        while True:
            data = os.read(read_pipe, 100).decode()
            if not data:
                break
            buffer += data
            while MESSAGE_SEPARATOR in buffer:
                message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                if message == "END":
                    for pipe in write_pipes:
                        os.write(pipe, f"END{MESSAGE_SEPARATOR}".encode())
                    return
                pid, is_vip, baggage_weight, gender = message.split("|")
                is_vip = is_vip == "True"
                baggage_weight = int(baggage_weight)
                passenger = Passenger(int(pid), is_vip, baggage_weight, gender)
                safe_print(f"Kontrola biletowo-bagażowa: {passenger}")
                time.sleep(random.uniform(0.1, 0.3))

                if baggage_weight <= BAGGAGE_LIMIT:
                    safe_print(f"{passenger} przeszedł kontrolę bagażową.")
                    # Wysyłanie do kolejnego dostępnego stanowiska (round-robin)
                    os.write(
                        write_pipes[next_station],
                        f"{message}{MESSAGE_SEPARATOR}".encode(),
                    )
                    next_station = (next_station + 1) % SECURITY_STATIONS
                else:
                    safe_print(
                        f"{passenger} nie przeszedł kontroli bagażowej (za ciężki bagaż)."
                    )
    except KeyboardInterrupt:
        sys.exit(0)


class SecurityStation:
    def __init__(self, station_id):
        self.station_id = station_id
        self.current_passengers = []
        self.waiting_queue = []
        self.current_gender = None
        self.control_in_progress = False  # Flaga wskazująca czy trwa kontrola
        self.expect_more_passengers = True

    def can_add_passenger(self, passenger):
        if self.control_in_progress:
            return False
        if not self.current_passengers:
            return True
        return (
            len(self.current_passengers) < MAX_PASSENGERS_PER_STATION
            and self.current_gender == passenger.gender
        )

    def add_passenger(self, passenger):
        if not self.current_passengers:
            self.current_gender = passenger.gender
        self.current_passengers.append(passenger)
        safe_print(f"Stanowisko {self.station_id}: Dodano do kontroli: {passenger}")

    def remove_passenger(self, passenger):
        self.current_passengers.remove(passenger)
        if not self.current_passengers:
            self.current_gender = None

    def requires_skip(self, passenger):
        skip = self.waiting_queue[0].pid != passenger.pid
        if skip:
            self.waiting_queue[0].skipped += 1

    def control(self, passenger):
        status = False
        if random.random() < SECURITY_CHECK_PROBABILITY:
            safe_print(
                f"Stanowisko {self.station_id}: {passenger} przeszedł kontrolę bezpieczeństwa."
            )
            status = True
        else:
            safe_print(
                f"Stanowisko {self.station_id}: {passenger} nie przeszedł kontroli bezpieczeństwa."
            )
        self.remove_passenger(passenger)
        return status


def security_check(station_id, read_pipe, write_pipe):
    try:
        buffer = ""
        station = SecurityStation(station_id)

        while True:
            try:
                if station.expect_more_passengers:
                    data = os.read(read_pipe, 100).decode()

                    print("Data: ", data)
                    if data:
                        buffer += data
                        while MESSAGE_SEPARATOR in buffer:
                            message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                            if message == "END":
                                station.expect_more_passengers = False
                                continue

                            pid, is_vip, baggage_weight, gender = message.split("|")
                            passenger = Passenger(
                                int(pid), is_vip == "True", int(baggage_weight), gender
                            )

                            # Dodaj do kolejki oczekujących
                            station.waiting_queue.append(passenger)
                            safe_print(
                                f"Stanowisko {station_id}: Nowy pasażer w kolejce: {passenger}"
                            )
            except BlockingIOError:
                pass

            # Przetwarzanie kolejki
            if len(station.current_passengers) < MAX_PASSENGERS_PER_STATION:
                waiting_vips = [p for p in station.waiting_queue if p.is_vip]
                passengers_with_skip_limit = [
                    p for p in station.waiting_queue if p.skipped >= MAX_SKIP
                ]
                remaining_passengers = [
                    p
                    for p in station.waiting_queue
                    if p not in waiting_vips and p not in passengers_with_skip_limit
                ]

                for passenger in passengers_with_skip_limit:
                    if station.can_add_passenger(passenger):
                        station.add_passenger(passenger)
                        station.waiting_queue.remove(passenger)
                        if (
                            len(station.current_passengers)
                            >= MAX_PASSENGERS_PER_STATION
                        ):
                            break

                for passenger in waiting_vips:
                    if station.can_add_passenger(passenger):
                        station.requires_skip(passenger)
                        station.add_passenger(passenger)
                        station.waiting_queue.remove(passenger)
                        if (
                            len(station.current_passengers)
                            >= MAX_PASSENGERS_PER_STATION
                        ):
                            break

                for passenger in remaining_passengers:
                    if station.can_add_passenger(passenger):
                        station.requires_skip(passenger)
                        station.add_passenger(passenger)
                        station.waiting_queue.remove(passenger)
                        if (
                            len(station.current_passengers)
                            >= MAX_PASSENGERS_PER_STATION
                        ):
                            break

            # Obsługa aktualnie kontrolowanych pasażerów
            if station.current_passengers:
                # Jeśli jest tylko jeden pasażer, kontroluj go indywidualnie
                if len(station.current_passengers) == 1:
                    passenger = station.current_passengers[0]
                    safe_print(
                        f"Stanowisko {station_id}: Rozpoczęcie kontroli indywidualnej dla {passenger}"
                    )
                    time.sleep(1.0)  # Stały czas kontroli 1 sekunda

                    if station.control(passenger):
                        os.write(
                            write_pipe,
                            f"{passenger.pid}|{passenger.is_vip}|{passenger.baggage_weight}|{passenger.gender}{MESSAGE_SEPARATOR}".encode(),
                        )

                # Jeśli są dwie osoby, kontroluj je grupowo
                elif len(station.current_passengers) == MAX_PASSENGERS_PER_STATION:
                    safe_print(
                        f"Stanowisko {station_id}: Rozpoczęcie kontroli grupowej dla {len(station.current_passengers)} pasażerów"
                    )
                    time.sleep(1.0)  # Stały czas kontroli 1 sekunda

                    # Kontrola wszystkich pasażerów w grupie
                    for passenger in station.current_passengers[:]:
                        if station.control(passenger):
                            os.write(
                                write_pipe,
                                f"{passenger.pid}|{passenger.is_vip}|{passenger.baggage_weight}|{passenger.gender}{MESSAGE_SEPARATOR}".encode(),
                            )

    except KeyboardInterrupt:
        sys.exit(0)


def generate_passengers(write_pipe):
    try:
        for i in range(1, MAX_PASSENGERS + 1):
            time.sleep(0.2)
            is_vip = random.random() < VIP_PROBABILITY
            baggage_weight = random.randint(10, 30)
            gender = random.choice(["M", "F"])
            passenger = Passenger(i, is_vip, baggage_weight, gender)
            passenger_data = f"{i}|{is_vip}|{baggage_weight}|{gender}"
            os.write(write_pipe, f"{passenger_data}{MESSAGE_SEPARATOR}".encode())
            safe_print(f"Wygenerowano: {passenger}")
        os.write(write_pipe, f"END{MESSAGE_SEPARATOR}".encode())

        # Wait until all passengers have passed security check
        while passed_security_count < MAX_PASSENGERS:
            time.sleep(0.1)

        safe_print("Wszyscy pasażerowie przeszli kontrolę bezpieczeństwa.")
    except KeyboardInterrupt:
        os.write(write_pipe, f"END{MESSAGE_SEPARATOR}".encode())
        sys.exit(0)


def handle_approved_passengers(read_pipe):
    global passed_security_count
    try:
        buffer = ""
        while True:
            data = os.read(read_pipe, 100).decode()
            if not data:
                break
            buffer += data
            while MESSAGE_SEPARATOR in buffer:
                message, buffer = buffer.split(MESSAGE_SEPARATOR, 1)
                if message == "END":
                    return
                pid, is_vip, baggage_weight, gender = message.split("|")
                is_vip = is_vip == "True"
                baggage_weight = int(baggage_weight)
                passenger = Passenger(int(pid), is_vip, baggage_weight, gender)
                safe_print(
                    f"Pasażer {passenger} został dopuszczony do wejścia na pokład."
                )
                passed_security_count += 1
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    baggage_pipe_read, baggage_pipe_write = os.pipe()
    security_pipes = [os.pipe() for _ in range(SECURITY_STATIONS)]
    approved_pipe_read, approved_pipe_write = os.pipe()

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
                security_check(i + 1, security_pipes[i][0], approved_pipe_write)
                os.close(security_pipes[i][0])
                os.close(approved_pipe_write)
                sys.exit(0)
            else:
                security_processes.append(pid_security)
                child_processes.append(pid_security)

        # Fork approved passengers process
        pid_approved = os.fork()
        if pid_approved == 0:
            os.close(baggage_pipe_read)
            os.close(baggage_pipe_write)
            for pipe in security_pipes:
                os.close(pipe[0])
                os.close(pipe[1])
            os.close(approved_pipe_write)
            handle_approved_passengers(approved_pipe_read)
            os.close(approved_pipe_read)
            sys.exit(0)
        else:
            child_processes.append(pid_approved)

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

        safe_print("Symulacja zakończona.")

    except Exception as e:
        try:
            sys.stderr.write(f"Wystąpił błąd: {str(e)}\n")
            sys.stderr.flush()
        except:
            pass
        finally:
            signal_handler(signal.SIGTERM, None)
