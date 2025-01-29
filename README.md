# Raport z Projektu - Samolot z bagażami

## 1. Założenia projektowe

Projekt implementuje system symulujący działanie lotniska z następującymi głównymi komponentami:

- [Generator pasażerów](https://github.com/Sniezka1927/airport-threads/blob/master/src/generator.py#L88-L123):
  Proces, który w nieskończonej pętli generuje nowych pasażerów, nie przekraczając ustawionego limitu procesów określonego przez użytkownika.
- [Kontrola biletowo-bagażowa](https://github.com/Sniezka1927/airport-threads/blob/master/src/luggageControl.py#L61-L80):
  Pobiera wygenerowanych pasażerów i sprawdza ich bilety oraz bagaż pod kątem zgodności z kryteriami wagowymi lotniska. Po pozytywnej weryfikacji przydziela pasażerów do odpowiednich stanowisk kontroli bezpieczeństwa, wykorzystując algorytm Round Robin.
- [Kontrola bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L77-L138):
  Sprawdza pasażerów pod kątem posiadania niebezpiecznych przedmiotów. Po pozytywnej kontroli kieruje ich do hali odlotów. Kontrola odbywa się przy maksymalnie dwóch osobach na stanowisko, przy zachowaniu zasady tej samej płci. Pasażerowie mogą przepuścić maksymalnie trzy osoby w kolejce. System obsługuje także pasażerów VIP, którzy mają priorytet i mogą ominąć kolejkę.
- [System zarządzania bramkami (gates)](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L78-L126):
  Po otrzymaniu sygnału o gotowości samolotu kieruje pasażerów do odpowiedniej bramki i organizuje boarding.
- [Dyspozytor lotów](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L78-L126):
  Komunikuje się z bramkami oraz samolotem. Po sprawdzeniu odpowiedniej liczby pasażerów wydaje zgodę na rozpoczęcie boardingu, a następnie na start samolotu. W przypadku nadmiernego zatłoczenia lotniska może natychmiast zatrzymać pracę lotniska.
- [Proces obsługi samolotu](https://github.com/Sniezka1927/airport-threads/blob/master/src/airplane.py#L16-L88):
  Po zakończeniu boardingu i otrzymaniu zgody na start rozpoczyna lot. Po określonym czasie wraca na lotnisko, kończąc swój cykl operacyjny.

### 1.1 Główne wymagania funkcjonalne:

- [Odprawa biletowo-bagażowa z limitem wagowym](https://github.com/Sniezka1927/airport-threads/blob/master/src/luggageControl.py#L41-L58)
- [3 równoległe stanowiska kontroli bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L119-L121)
- [Maksymalnie 2 osoby tej samej płci na stanowisku](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L32-L39)
- [Limit 3 przepuszczeń w kolejce dla każdego pasażera](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L77-L116)
- [System obsługi VIP](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L77-L116)
- [Zarządzanie schodami pasażerskimi o ograniczonej pojemności](https://github.com/Sniezka1927/airport-threads/blob/master/src/gate.py#L63-L101)
- [Koordynacja oraz zarządzanie flotą samolotów przez dyspozytora](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L78-L126)

## 2. Implementacja wymagań obowiązkowych

### 2.1 Dokumentacja przypadków użycia

Projekt zawiera szczegółową dokumentację w postaci komentarzy w kodzie oraz struktury modułowej reprezentującej poszczególne komponenty systemu. Główne przypadki użycia są zaimplementowane w oddzielnych modułach:

- `./src/generator.py` - [generowanie pasażerów](https://github.com/Sniezka1927/airport-threads/blob/master/src/generator.py)
- `./src/luggageControl.py` - [kontrola bagażowa](https://github.com/Sniezka1927/airport-threads/blob/master/src/luggageControl.py)
- `./src/securityControl.py` - [kontrola bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py)
- `./src/gate.py` - [obsługa bramek](https://github.com/Sniezka1927/airport-threads/blob/master/src/gate.py)
- `./src/dispatcher.py` - [zarządzanie lotami](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py)
- `./src/airplane.py` - [obsługa samolotu](https://github.com/Sniezka1927/airport-threads/blob/master/src/airplane.py)
- `./src/consts.py` - [stałe oraz konfiguracja programów](https://github.com/Sniezka1927/airport-threads/blob/master/src/consts.py)

### 2.2 Walidacja danych

Walidacja została zaimplementowana w module `utils.py` w funkcji [validate_config()](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L218-L253)

### 2.3 Obsługa błędów

Obsługa błędów systemowych jest zaimplementowana w module `utils.py` w funkcji [handle_system_error()](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L29-L64)

### 2.4 Minimalne prawa dostępu

Projekt implementuje minimalne prawa dostępu dla tworzonych struktur:

- [Kolejek](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L15-L18)
- [Plików](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L72-L78)

## 3. Realizacja wymagań

a. Tworzenie i obsługa plików

- [Tworzenie pliku](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L69-L82)
- [Zapis do pliku](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L130-L150)
- [Odczyt z pliku](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L108-L127)
- [Unlink](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L172)

b. Tworzenie procesów

- [Fork](https://github.com/Sniezka1927/airport-threads/blob/master/src/main.py#L18)
- [Exit](https://github.com/Sniezka1927/airport-threads/blob/master/src/main.py#L25)
- [Wait](https://github.com/Sniezka1927/airport-threads/blob/master/src/main.py#L36)

c. Obsługa sygnałów

- [Obsługa KeyboardInterrupt](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L53-L54)
- [Kill](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L256-L274)

d. Synchronizacja procesów

- [Synchronizacja przez pliki](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L108-L172)

e. Kolejki komunikatów

- [Tworzenie kolejek](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L8-L36)
- [Dodawanie do kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L38-L110)
- [Pobieranie z kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L112-L185)

## 4. Problemy i rozwiązania

### 4.1 Synchronizacja dostępu do plików

Problem: Równoległy dostęp do plików przez różne procesy.
Rozwiązanie: Wykorzystanie mechanizmu `fcntl` do [blokowania](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L135) i [odblokowywania](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L142) plików

### 4.2 Koordynacja procesów

Problem: Koordynacja wielu procesów i przekazywanie sygnałów.
Rozwiązanie: Wykorzystanie kolejek komunikatów:

- [Tworzenie kolejek](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L8-L36)
- [Dodawanie do kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L38-L110)
- [Pobieranie z kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/queue_handler.py#L112-L185)
- [Synchronizacja przez pliki](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L108-L172)

## 5. Testy

### 5.1 Struktura testów

Projekt zawiera kompleksowy zestaw testów:

#### 1. Testy jednostkowe poszczególnych komponentów:

- `./tests/test_generator.py` - [testy generatora pasażerów](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_generator.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_generator.py#L6-L23): Wygenerowanie oraz sprawdzanie poprawności generowanych danych zgodnie z konfiguracją parametrów w module consts
- `./tests/test_luggageControl.py` - [testy kontroli bagażowej](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_luggageControl.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_luggageControl.py#L10-L33): Kontrola pasażera z prawidłową wagą bagażu. Test zakłada że w kolejce do kontroli bagażowej stoi jeden pasażer z prawidłowa wagą bagażu. Kontrola przebiega pomyślnie.
  - [TEST_2](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_luggageControl.py#L36-L54): Kontrola pasażera z nadwagą bagażu podręcznego. Test zakłada że w kolejce do kontroli bagażowej znajduję się jeden pasażer z nadwagą bagażową. Pasażer zostaje odrzucony.
- `./tests/test_securityControl.py` - [testy kontroli bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L29-L39): Kontrola pojedynczego pasażera bez niebezpiecznych przedmiotów. W kolejce do kontroli oczekuje jeden pasażer bez niebezpiecznych przedmiotów. Kontrola przebiega pomyślnie
  - [TEST_2](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L42-L52): Kontrola pasażera z niebezpiecznym przedmiotem. W kolejce do kontroli oczekuje jeden pasażer z niebezpiecznymi przedmiotami. Zostaje odrzucony.
  - [TEST_3](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L55-L71): Kontrola wielu pasażerów. Do każdego punktu kontroli bezpieczeństwa oczekuję po 2 mężczyzn bez niebezpiecznych przedmiotów. Są oni równocześnie kontrolowani po 2 osoby na każdym stanowisku. Przechodzą kontrole pomyślnie
  - [TEST_4](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L74-L91): Weryfikacja zasady zachowania płci na stanowisku. Do punktu 1 i 2 w kolejce oczekuję 2 mężczyzn, do punktu 3 oczekuje 1 mężczyzna i 1 kobieta w podanej kolejności. Początkowo kontrolowana jest para mężczyzn na stanowisku 1 i 2, oraz jeden mężczyzna na stanowisku 3. Po zakończeniu kontroli, kontrolowana jest oczekująca kobieta.
  - [TEST_5](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L94-L120): Weryfikacja przypuszczeń pasażerów w kolejce do pojedynczego punktu kontroli bezpieczeństwa ustawieni są w kolejności: M,F,M. Do kontroli zostaje przepuszczony 3 z kolei mężczyzna. Kontrolowana są pary w kolejności M,M oraz później F.
  - [TEST_6](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L94-L120): Weryfikacja obsługi VIP. Do pojedynczego punktu kontroli bezpieczeństwa ustawieni są M,M,F(pasażer VIP). Kontrola przebiega według schematu F (pasażer VIP pojedyńczo), i poźniej MM.
- `./tests/test_gate.py` - [testy systemu bramek](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py#L22-L40): Sprawdzenie odlotu samolotu przy idealnych warunkach. W hali odlotów oczekuje idealna liczba pasażerów do miejsc w samolocie. Pasażerowie nie przekraczając limitu pasażerów na schodach wsiadają do samolotu
  - [TEST_2](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py#L43-L61): Sprawdzenie odlotu samolotu przy braku pasażerów do zapełnienia samolotu. W hali odlotów oczekuje mniej pasażerów niż miejsc w samolocie. Pasażerowie wsiadają do samolotu przy wykorzystaniu schodów maksymalizując liczbę osób przy każdym użyciu schodów
  - [TEST_3](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py#L64-L81): Sprawdzenie odlotu samolotu przy nadmiarze pasażerów oczekujących na odlot. W hali odlotów oczekuje więcej pasażerów niż jest wolnych miejsc w samolocie Pasażerowie wsiadają do samolotu przy wykorzystaniu schodów nie przekraczając limitu miejsc w samolocie

### 5.2 Zakres testów

#### Testy jednostkowe

Każdy moduł ma dedykowany zestaw testów sprawdzających:

- Poprawność walidacji danych
- Obsługę skrajnych przypadków

## 6. Elementy wyróżniające projekt

- Zaawansowany system logowania i [statystyk](https://github.com/Sniezka1927/airport-threads/blob/master/src/stats.py):
- Moduł `stats.py` zbierający kompleksowe statystyki
- System logowania z timestampami
- Wielopoziomowa walidacja:

## 7. Wnioski

Projekt spełnia wszystkie wymagane funkcjonalności i implementuje zaawansowane mechanizmy synchronizacji i komunikacji między procesami. Szczególnie warte uwagi są:

1. Kompleksowa obsługa błędów i walidacja danych
2. Efektywna synchronizacja procesów
3. Modułowa struktura kodu
4. Rozbudowany system logowania i statystyk

Podczas implementacji szczególnie wymagające okazały się:

- Koordynacja wielu procesów
- Zapewnienie spójności danych przy równoległym dostępie

## 8. Włączenie symulacji

### 8.1 Wymagania

- Python 3.x

### 8.2 Uruchomienie

```bash
git clone git@github.com:Sniezka1927/airport-threads.git
cd airport-threads/src && python3 main.py
```

### 8.3 Zebranie statystyk

Pliki ze statystykami zostaną zapisane w katalogu `./stats/stats_{SIMULATE_START_TIMESTAMP}.json`

```bash
# Z katalogu src
python3 stats.py
```

### 8.4 Testowanie aplikacjii

Przed każdym uruchomieniem każdego testu należy się upewnić, że wszystkie pliki w `./data/*.txt` oraz `./tests/tmp/*` nie zawierają informacji o pasażerach.

```bash
# Z katalogu tests
pytest test_generator.py -s
pytest test_luggageControl.py -s
pytest test_securityControl.py -s
pytest test_gate.py -s
```
