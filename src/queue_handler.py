import os
import time
import errno
from utils import handle_system_error


class Queue:
    def __init__(self, queue_path):
        """Tworzy nowa kolejke. Jesli plik nie istnieje, zostanie utworzony."""
        self.queue_path = queue_path
        self.temp_path = f"{queue_path}.temp"

        try:
            if not os.path.exists(queue_path):
                try:
                    with open(queue_path, "a") as f:
                        pass
                    os.chmod(queue_path, 0o600)
                except OSError as e:
                    if e.errno == errno.ENOSPC:  # Brak miejsca na dysku
                        handle_system_error(
                            "initialization - no space left", queue_path, e
                        )
                    elif e.errno == errno.EMFILE:  # Za dużo otwartych plików
                        handle_system_error(
                            "initialization - too many open files", queue_path, e
                        )
                    else:
                        handle_system_error("initialization", queue_path, e)
                    raise
        except OSError as e:
            if e.errno == errno.EACCES:  # Brak uprawnień
                handle_system_error("initialization - permission denied", queue_path, e)
            else:
                handle_system_error("initialization", queue_path, e)
            raise

    def put(self, message, timeout=5):
        """
        Dodaje wiadomosc do kolejki. Akceptuje string lub tuple.
        Jesli message jest tuple, konwertuje je na string z separatorem ';'
        """
        # Konwersja tuple na string jeśli potrzebna
        if isinstance(message, tuple):
            message = ";".join(str(item) for item in message)

        start_time = time.time()
        lock_fd = None

        while True:
            try:
                # Próba dostania locka
                lock_fd = os.open(
                    f"{self.queue_path}.lock",
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )

                try:
                    # Przeczytanie istniejących wiadomości
                    messages = []
                    try:
                        with open(self.queue_path, "r") as f:
                            messages = f.readlines()
                    except OSError as e:
                        if e.errno != errno.ENOENT:  # Brak pliku
                            handle_system_error("reading", self.queue_path, e)
                            raise

                    # Dodanie nowej wiadomości
                    messages.append(message + "\n")

                    # Zapisa do pliku
                    try:
                        with open(self.temp_path, "w") as f:
                            f.writelines(messages)
                        os.chmod(self.temp_path, 0o600)
                    except OSError as e:
                        handle_system_error("writing", self.temp_path, e)
                        raise

                    # Rename pliku
                    try:
                        os.rename(self.temp_path, self.queue_path)
                    except OSError as e:
                        handle_system_error("renaming", self.temp_path, e)
                        raise

                    return True

                finally:
                    # Zwolnienie locka
                    if lock_fd is not None:
                        try:
                            os.close(lock_fd)
                            os.unlink(f"{self.queue_path}.lock")
                        except OSError as e:
                            handle_system_error("cleanup", f"{self.queue_path}.lock", e)

            except OSError as e:
                if e.errno != errno.EEXIST:
                    handle_system_error("lock creation", f"{self.queue_path}.lock", e)
                    raise

                # Sleep na odblokowanie locka jeżeli zajęty
                time.sleep(0.1)

                if timeout is not None:
                    if time.time() - start_time > timeout:
                        return False

    def get(self, timeout=5):
        """
        Odbiór wiadomości z kolejki.
        Jeśli wiadomość zawiera separator ';', zwraca tuple.
        W przeciwnym razie zwraca string.
        """
        start_time = time.time()
        lock_fd = None

        while True:
            try:
                lock_fd = os.open(
                    f"{self.queue_path}.lock",
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )

                try:
                    messages = []
                    try:
                        with open(self.queue_path, "r") as f:
                            messages = f.readlines()
                    except OSError as e:
                        if e.errno == errno.EIO:  # Obsługi błędu I/O
                            handle_system_error(
                                "reading due to I/O error", self.queue_path, e
                            )
                            raise
                        if e.errno != errno.ENOENT:
                            handle_system_error("reading", self.queue_path, e)
                            raise

                    if not messages:
                        raise Empty()

                    # Pierwsza wiadomość od góry
                    message = messages[0].rstrip("\n")
                    messages = messages[1:]
                    # Zapis pozostałych wiadomości
                    try:
                        with open(self.temp_path, "w") as f:
                            f.writelines(messages)
                        os.chmod(self.temp_path, 0o600)
                    except OSError as e:
                        handle_system_error("writing", self.temp_path, e)
                        raise
                    try:
                        os.rename(self.temp_path, self.queue_path)
                    except OSError as e:
                        handle_system_error("renaming", self.temp_path, e)
                        raise
                    # Konwersja na tuple jeśli zawiera separator
                    if ";" in message:
                        return tuple(message.split(";"))
                    return message

                finally:
                    if lock_fd is not None:
                        try:
                            os.close(lock_fd)
                            os.unlink(f"{self.queue_path}.lock")
                        except OSError as e:
                            handle_system_error("cleanup", f"{self.queue_path}.lock", e)

            except OSError as e:
                if e.errno != errno.EEXIST:
                    handle_system_error("lock creation", f"{self.queue_path}.lock", e)
                    raise

                time.sleep(0.1)

                if timeout is not None:
                    if time.time() - start_time > timeout:
                        return None


class Empty(Exception):
    """Exception kiedy kolejka jest pusta"""

    pass
