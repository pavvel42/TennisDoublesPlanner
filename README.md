[![AI Assisted](https://img.shields.io/badge/AI-Assisted-blue?style=for-the-badge&logo=openai)](./AI_POLICY.md) [![Built with Gemini](https://img.shields.io/badge/Built%20with-Gemini-4285F4?style=for-the-badge&logo=google-gemini)](https://gemini.google.com/)

Poniżej znajduje się moja implementacja rozwiązania problemu [TennisDoublesPlanner](https://github.com/Kagroth/TennisDoublesPlanner).

# Planer Turnieju Tenisa Deblowego

To repozytorium zawiera zaawansowane rozwiązanie problemu planowania turnieju tenisa deblowego dla zmiennej liczby graczy (`n >= 4`), oparte na **Programowaniu w Oparciu o Ograniczenia (Constraint Programming - CP)** przy użyciu biblioteki **Google OR-Tools**. Celem jest wygenerowanie sprawiedliwego, zrównoważonego i wolnego od błędów harmonogramu.

---

## Problem: Wariant Problemu Społecznego Golfisty

Głównym wyzwaniem jest stworzenie harmonogramu dla `n` graczy na jednym korcie. Problem ten jest wariantem znanego w informatyce **Problemu Społecznego Golfisty (SGP)**, który należy do klasy problemów **NP-trudnych**. Oznacza to, że złożoność obliczeniowa rośnie wykładniczo wraz z liczbą graczy.

Liczba sposobów na wybranie 4 graczy do jednego meczu z puli `n` graczy jest określona przez współczynnik dwumianowy:
```math
C(n, 4) = \frac{n!}{4!(n-4)!} = \frac{n(n-1)(n-2)(n-3)}{24}
```
Dla `n=20` graczy, istnieje $`C(20, 4) = 4845`$ możliwych kombinacji czteroosobowych grup, co ilustruje skalę problemu. Model musi przeszukać tę przestrzeń, spełniając jednocześnie kluczowe ograniczenia kombinatoryczne.

### Kluczowe Ograniczenia
1.  **Unikalność Drużyn**: Każda para graczy może stworzyć drużynę **co najwyżej raz**.
2.  **Poprawność Meczu**: Każdy mecz musi składać się z 4 unikalnych graczy.
3.  **Sprawiedliwa Rotacja**: Liczba rozegranych meczów przez każdego uczestnika powinna być jak najbardziej wyrównana.

---

## Rozwiązanie: Model CP-SAT z Google OR-Tools

Wykorzystano solver **CP-SAT** z biblioteki Google OR-Tools, który jest wyspecjalizowanym i wydajnym narzędziem do rozwiązywania problemów spełniania ograniczeń.

**Dlaczego CP-SAT?**
*   **Wydajność**: Jest znacznie szybszy niż tradycyjne solvery CP dla problemów, które można zamodelować za pomocą ograniczeń całkowitoliczbowych.
*   **Elastyczność**: Umożliwia deklaratywne definiowanie złożonych, logicznych ograniczeń.
*   **Gwarancja Poprawności**: Solver systematycznie przeszukuje przestrzeń rozwiązań, gwarantując znalezienie optymalnego (lub wykonalnego) harmonogramu.

### Dynamiczne Zarządzanie Graczami
W celu zapewnienia maksymalnej elastyczności, skrypt został wyposażony w mechanizm dynamicznego zarządzania graczami:
*   Dostępna jest predefiniowana lista 20 unikalnych imion.
*   W przypadku żądania większej liczby graczy (`n > 20`), system automatycznie generuje unikalne identyfikatory dla dodatkowych uczestników (np. `Player_21`, `Player_22`), eliminując w ten sposób górny limit liczby graczy.

### Architektura Modelu Matematycznego

Niech $`P = {1, 2, ..., n}`$ będzie zbiorem graczy, a $`M`$ zbiorem potencjalnych meczów.

**1. Zmienne Decyzyjne:**

*   $`x_{pm} \in {0, 1}`$: Zmienna binarna przyjmująca wartość 1, jeśli gracz $`p \in P`$ uczestniczy w meczu $`m \in M`$, w przeciwnym razie 0.
*   $`y_{p_1 p_2 m} \in {0, 1}`$: Zmienna binarna przyjmująca wartość 1, jeśli gracze $`p_1, p_2 \in P`$ (gdzie $`p_1 < p_2`$) tworzą drużynę w meczu $`m \in M`$, w przeciwnym razie 0.

**2. Ograniczenia Modelu:**

*   **Liczba Graczy w Meczu**: W każdym meczu musi brać udział dokładnie 4 graczy.
    ```math
    \forall m \in M: \sum_{p \in P} x_{pm} = 4
    ```
*   **Liczba Drużyn w Meczu**: W każdym meczu muszą być dokładnie 2 drużyny.
    ```math
    \forall m \in M: \sum_{p_1, p_2 \in P, p_1 < p_2} y_{p_1 p_2 m} = 2
    ```
*   **Integralność Harmonogramu i Drużyn**: Gracz uczestniczy w meczu wtedy i tylko wtedy, gdy jest częścią jednej z drużyn w tym meczu.
    ```math
    \forall p \in P, \forall m \in M: x_{pm} = \sum_{p' \in P, p' \neq p} y_{\min(p, p'), \max(p, p') m}
    ```
*   **Unikalność Drużyn (Warunek SGP)**: Każda para graczy może tworzyć drużynę co najwyżej raz.
    ```math
    \forall p_1, p_2 \in P, p_1 < p_2: \sum_{m \in M} y_{p_1 p_2 m} \leq 1
    ```
*   **Sprawiedliwa Rotacja**: Różnica między maksymalną a minimalną liczbą rozegranych meczów przez dowolnego gracza jest ograniczona do 1. Niech \( G_p = \sum_{m \in M} x_{pm} \) będzie liczbą gier gracza \(p\).
    ```math
    \max_{p \in P}(G_p) - \min_{p \in P}(G_p) \leq 1
    ```

**3. Funkcja Celu:**

Celem jest maksymalizacja całkowitej liczby gier rozegranych w turnieju, co prowadzi do jak najpełniejszego harmonogramu.
```math
\text{maximize} \sum_{p \in P} \sum_{m \in M} x_{pm}
```

---

## Jak Uruchomić

1.  **Instalacja Zależności**:
    ```bash
    pip install ortools matplotlib networkx seaborn pandas
    ```
2.  **Uruchomienie Skryptu**:
    Uruchom skrypt `matches_cp.py`, podając liczbę graczy (`n`) jako argument.
    ```bash
    # Przykład dla 12 graczy
    python matches_cp.py 12
    
    # Przykład dla 22 graczy (z automatycznie generowanymi nazwami)
    python matches_cp.py 22
    ```

---

## Wyniki i Wizualizacja

Skrypt generuje:
*   **Szczegółowy Harmonogram Meczów** na konsoli.
*   **Tabelę Podsumowującą** z liczbą gier i odpoczynków dla każdego gracza.
*   **Wizualizacje Graficzne**:
    1.  **Graf Harmonogramu**: Pokazuje, kto z kim grał w poszczególnych meczach.
    2.  **Mapy Ciepła**: Ilustrują częstotliwość tworzenia par (partnerów) i grania przeciwko sobie (przeciwników).
