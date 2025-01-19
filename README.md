# Raport z Projektu - System Obsługi Lotniska

## 1. Założenia projektowe

Projekt implementuje system symulujący działanie lotniska z następującymi głównymi komponentami:

- [Generator pasażerów](https://github.com/Sniezka1927/airport-threads/blob/master/src/generator.py#L52-L65)
- [Kontrola biletowo-bagażowa](https://github.com/Sniezka1927/airport-threads/blob/master/src/luggageControl.py#L39-L54)
- [Kontrola bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L194-L221)
- [System zarządzania bramkami (gates)](https://github.com/Sniezka1927/airport-threads/blob/master/src/gate.py#L28-L78)
- [Dyspozytor lotów](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L38-L77)
- [Proces obsługi samolotu](https://github.com/Sniezka1927/airport-threads/blob/master/src/airplane.py#L7-L55)

### 1.1 Główne wymagania funkcjonalne:

- [Odprawa biletowo-bagażowa z limitem wagowym](https://github.com/Sniezka1927/airport-threads/blob/master/src/luggageControl.py#L31-L37)
- [3 równoległe stanowiska kontroli bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L58-L62)
- [Maksymalnie 2 osoby tej samej płci na stanowisku](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L135)
- [Limit 3 przepuszczeń w kolejce dla każdego pasażera](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L154-L158)
- [System obsługi VIP](https://github.com/Sniezka1927/airport-threads/blob/master/src/securityControl.py#L166-L176)
- [Zarządzanie schodami pasażerskimi o ograniczonej pojemności](https://github.com/Sniezka1927/airport-threads/blob/master/src/gate.py#L47-L78)
- [Koordynacja odlotów przez dyspozytora](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L63-L68)
- [Zarządzanie flotą samolotów](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L47-L70)

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

Walidacja została zaimplementowana w module `utils.py` w funkcji [validate_config()](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L169-L186):

### 2.3 Obsługa błędów

Obsługa błędów systemowych jest zaimplementowana w module `utils.py` w funkcji [handle_system_error()](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L15-L36):

### 2.4 Minimalne prawa dostępu

Projekt implementuje minimalne prawa dostępu dla tworzonych struktur:

- [Kolejek](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L27-L31)
- [Plików](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L42-L46)

## 3. Realizacja wymagań

### a. Tworzenie i obsługa plików

- [Tworzenie pliku](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L39-L54)
- [Zapis do pliku](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L79-L96)
- [Odczyt z pliku](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L56-L77)

### b. Tworzenie procesów

- [Tworzenie](https://github.com/Sniezka1927/airport-threads/blob/master/src/main.py#L17-L21)

### c. Obsługa sygnałów

- [Obsługa przerwania](https://github.com/Sniezka1927/airport-threads/blob/master/src/main.py#L36-L69)

### d. Synchronizacja procesów

- [Synchronizacja przez pliki](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L59-L70)

### e. Kolejki komunikatów

- [Tworzenie kolejek](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L22-L24)
- [Dodawanie do kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L63)
- [Pobieranie z kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/gate.py#L32)

### f. Pamięć współdzielona

- [Tworzenie pamięci współdzielonej](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L36)
- [Modyfikacja pamięci współdzielonej](https://github.com/Sniezka1927/airport-threads/blob/master/src/airplane.py#L49-L50)

## 4. Problemy i rozwiązania

### 4.1 Synchronizacja dostępu do plików

Problem: Równoległy dostęp do plików przez różne procesy.
Rozwiązanie: Wykorzystanie mechanizmu `fcntl` do [blokowania](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L62) i [odblokowywania](https://github.com/Sniezka1927/airport-threads/blob/master/src/utils.py#L70) plików:

### 4.2 Koordynacja procesów

Problem: Koordynacja wielu procesów i przekazywanie sygnałów.
Rozwiązanie: Wykorzystanie kolejek komunikatów:

- [Tworzenie kolejek](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L22-L24)
- [Dodawanie do kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/dispatcher.py#L63)
- [Pobieranie z kolejki](https://github.com/Sniezka1927/airport-threads/blob/master/src/gate.py#L32)

## 5. Testy

### 5.1 Struktura testów

Projekt zawiera kompleksowy zestaw testów podzielony na dwie główne kategorie:

#### 1. Testy jednostkowe poszczególnych komponentów:

- `./tests/test_generator.py` - [testy generatora pasażerów](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_generator.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_generator.py#L5-L20): Wygenerowanie oraz sprawdzanie poprawności generowanych danych
- `./tests/test_luggageControl.py` - [testy kontroli bagażowej](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_luggageControl.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_luggageControl.py#L10-L29): Kontrola pasażera z prawidłową wagą bagażu
  - [TEST_2](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_luggageControl.py#L32-L51): Kontrola pasażera z nadwagą bagażu podręcznego
- `./tests/test_securityControl.py` - [testy kontroli bezpieczeństwa](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L24-L32): Kontrola pojedyńczego pasażera bez niebezpiecznych przedmiotów
  - [TEST_2](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L34-L42): Kontrola pasażera z niebezpiecznym przedmiotem
  - [TEST_3](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L44-L52): Kontrola wielu pasażerów
  - [TEST_4](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L54-L66): Weryfikacja zasady zachowania płci na stanowisku
  - [TEST_5](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L69-L89): Weryfikacja przepuszczeń pasażerów
  - [TEST_6](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_securityControl.py#L91-L110): Weryfikacja obsługi VIP
- `./tests/test_gate.py` - [testy systemu bramek](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py#L19-L36): Sprawdzenie odlotu samolotu przy idealnych warunkach
  - [TEST_2](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py#L40-L57): Sprawdzenie odlotu samolotu przy braku pasażerów do zapełnienia samolotu
  - [TEST_3](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_gate.py#L60-L77): Sprawdzenie odlotu samolotu przy nadmiarze pasażerów oczekujących na odlot

#### 2. Test end-to-end:

- `./tests/test_e2e.py` - [test integracyjny sprawdzający przepływ pasażerów przez cały system](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_e2e.py)
  - [TEST_1](https://github.com/Sniezka1927/airport-threads/blob/master/tests/test_e2e.py#L41-L105): Przepływ pasażerów przez cały system lotniskowy. Sprawdzenie wydajnościowe kontroli bagażowej oraz bezpieczeństwa. Synchronizacja wielu odlotów oraz powrót samolotów na lotnisko.

### 5.2 Zakres testów

#### Testy jednostkowe

Każdy moduł ma dedykowany zestaw testów sprawdzających:

- Poprawność walidacji danych
- Obsługę skrajnych przypadków

#### Test end-to-end

Test `./tests/test_e2e.py` weryfikuje:

- Pełny przepływ pasażera przez system
- Integrację wszystkich komponentów
- Poprawność synchronizacji procesów

## 6. Elementy wyróżniające projekt

### 1. Zaawansowany system logowania i [statystyk](https://github.com/Sniezka1927/airport-threads/blob/master/src/stats.py):

- Moduł `stats.py` zbierający kompleksowe statystyki
- System logowania z timestampami
- Testy end-to-end

### 2. Wielopoziomowa walidacja:

- Walidacja konfiguracji
- Sprawdzanie limitów
- Obsługa błędów systemowych

## 7. Wnioski

Projekt spełnia wszystkie wymagane funkcjonalności i implementuje zaawansowane mechanizmy synchronizacji i komunikacji między procesami. Szczególnie warte uwagi są:

1. Kompleksowa obsługa błędów i walidacja danych
2. Efektywna synchronizacja procesów
3. Modułowa struktura kodu
4. Rozbudowany system logowania i statystyk

Podczas implementacji szczególnie wymagające okazały się:

- Koordynacja wielu procesów
- Zapewnienie spójności danych przy równoległym dostępie
- Implementacja systemu priorytetów dla pasażerów (limitu przepuszczeń)
