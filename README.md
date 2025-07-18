[![AI Assisted](https://img.shields.io/badge/AI-Assisted-blue?style=for-the-badge&logo=openai)](./AI_POLICY.md) [![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini-4285F4?style=for-the-badge&logo=google-gemini)](https://gemini.google.com/)

Poniżej znajduje się moja implementacja rozwiązania problemu [TennisDoublesPlanner](https://github.com/Kagroth/TennisDoublesPlanner).

# Planer Turnieju Tenisa Deblowego

To repozytorium zawiera zaawansowane rozwiązanie problemu planowania turnieju tenisa deblowego dla zmiennej liczby graczy (`n >= 4`), oparte na **Programowaniu w Oparciu o Ograniczenia (Constraint Programming - CP)** przy użyciu biblioteki **Google OR-Tools**. Celem jest wygenerowanie sprawiedliwego, zrównoważonego i wolnego od błędów harmonogramu.

## Problem: Wariant Problemu Społecznego Golfisty

Głównym wyzwaniem jest stworzenie harmonogramu dla `n` graczy na jednym korcie, przestrzegając kluczowych ograniczeń kombinatorycznych:

1.  **Unikalność Drużyn**: Każda para graczy może stworzyć drużynę **co najwyżej raz**.
2.  **Poprawność Meczu**: Każdy mecz musi składać się z 4 unikalnych graczy. Problem, w którym jeden gracz mógłby grać przeciwko sobie, został zidentyfikowany i wyeliminowany.
3.  **Sprawiedliwa Rotacja**: Liczba rozegranych meczów przez każdego uczestnika powinna być jak najbardziej wyrównana, aby zapewnić sprawiedliwy czas gry i odpoczynku.

Problem ten jest wariantem znanego w informatyce **Problemu Społecznego Golfisty (SGP)**, który należy do klasy problemów **NP-trudnych**. Oznacza to, że znalezienie optymalnego rozwiązania dla dużej liczby graczy jest obliczeniowo bardzo kosztowne.

## Rozwiązanie: Model CP-SAT z Google OR-Tools

Wykorzystano solver **CP-SAT** z biblioteki Google OR-Tools, który jest wyspecjalizowanym i wydajnym narzędziem do rozwiązywania problemów spełniania ograniczeń.

**Dlaczego CP-SAT?**
*   **Wydajność**: Jest znacznie szybszy niż tradycyjne solvery CP dla problemów, które można zamodelować za pomocą ograniczeń całkowitoliczbowych.
*   **Elastyczność**: Umożliwia deklaratywne definiowanie złożonych, logicznych ograniczeń.
*   **Gwarancja Poprawności**: Solver systematycznie przeszukuje przestrzeń rozwiązań, gwarantując znalezienie optymalnego (lub wykonalnego) harmonogramu, który spełnia wszystkie zdefiniowane warunki.

### Architektura Modelu

**1. Zmienne:**

*   `schedule[(p, m)]`: Zmienna binarna (0 lub 1) wskazująca, czy `gracz p` uczestniczy w `meczu m`.
*   `teams[(p1, p2, m)]`: Zmienna binarna wskazująca, czy `gracz p1` i `gracz p2` tworzą drużynę w `meczu m`. Definiowana tylko dla par `p1 < p2`, aby uniknąć duplikatów.

**2. Kluczowe Ograniczenia:**

*   **Liczba Graczy w Meczu**: Suma graczy (`schedule`) w każdym meczu musi wynosić dokładnie 4.
    ```python
    forall m: sum(schedule[(p, m)] for p in players) == 4
    ```
*   **Liczba Drużyn w Meczu**: Suma drużyn (`teams`) w każdym meczu musi wynosić dokładnie 2.
    ```python
    forall m: sum(teams[(p1, p2, m)] for p1 < p2) == 2
    ```
*   **Integralność Harmonogramu i Drużyn (Kluczowa Poprawka)**: Gracz jest w harmonogramie meczu **wtedy i tylko wtedy**, gdy jest częścią jednej z drużyn w tym meczu. To ograniczenie eliminuje błąd, w którym gracz mógłby grać przeciwko sobie.
    ```python
    forall m, p: schedule[(p, m)] == sum(teams[(min(p, p_o), max(p, p_o)), m] for p_o if p != p_o)
    ```
*   **Unikalność Drużyn (SGP)**: Każda para graczy może tworzyć drużynę co najwyżej raz w całym turnieju.
    ```python
    forall p1 < p2: sum(teams[(p1, p2, m)] for m in matches) <= 1
    ```
*   **Sprawiedliwa Rotacja**: Różnica między maksymalną a minimalną liczbą rozegranych meczów przez dowolnego gracza jest ograniczona do 1.
    ```python
    max(played_matches) - min(played_matches) <= 1
    ```

**3. Funkcja Celu:**

Celem jest maksymalizacja całkowitej liczby gier rozegranych w turnieju. W połączeniu z ograniczeniem sprawiedliwej rotacji, model dąży do stworzenia jak najpełniejszego i najbardziej sprawiedliwego harmonogramu.

```python
Maximize: sum(schedule[(p, m)] for p, m)
```

## Jak Uruchomić

1.  **Instalacja Zależności**:
    ```bash
    pip install ortools matplotlib networkx seaborn pandas
    ```
2.  **Uruchomienie Skryptu**:
    Uruchom skrypt `matches_cp.py`, podając liczbę graczy (`n`) jako argument.
    ```bash
    # Przykład dla 9 graczy
    python matches_cp.py 9
    ```

## Wyniki i Wizualizacja

Skrypt generuje:
*   **Szczegółowy Harmonogram Meczów** na konsoli.
*   **Tabelę Podsumowującą** z liczbą gier i odpoczynków dla każdego gracza.
*   **Wizualizacje Graficzne**:
    1.  **Graf Harmonogramu**: Pokazuje, kto z kim grał w poszczególnych meczach.
    2.  **Mapy Ciepła**: Ilustrują częstotliwość tworzenia par (partnerów) i grania przeciwko sobie (przeciwników).

Dzięki zastosowaniu modelu CP-SAT, rozwiązanie jest nie tylko wydajne, ale również weryfikowalnie poprawne, co zostało potwierdzone przez eliminację krytycznego błędu w logice harmonogramu.
