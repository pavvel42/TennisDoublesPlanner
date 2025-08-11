import random

# --- Pula dostępnych imion ---
AVAILABLE_NAMES = [
    "Adam", "Barbara", "Czesław", "Daria", "Eugeniusz", "Felicja", 
    "Grzegorz", "Hanna", "Igor", "Joanna", "Krzysztof", "Laura",
    "Marek", "Natalia", "Oskar", "Patrycja", "Robert", "Stanisław",
    "Tomasz", "Zofia"
]

class TennisConfiguration:
    """
    Klasa do dynamicznego generowania konfiguracji gry w tenisa 
    dla określonej liczby graczy (N).
    """
    def __init__(self, num_players):
        """
        Inicjalizuje konfigurację dla N graczy.

        :param num_players: Liczba graczy do wylosowania.
        """
        if num_players < 4:
            raise ValueError("Liczba graczy musi wynosić co najmniej 4.")

        self.N = num_players
        
        players_set = set()
        if num_players <= len(AVAILABLE_NAMES):
            players_set = set(random.sample(AVAILABLE_NAMES, self.N))
        else:
            players_set = set(AVAILABLE_NAMES)
            num_to_generate = num_players - len(AVAILABLE_NAMES)
            for i in range(num_to_generate):
                players_set.add(f"Player_{len(AVAILABLE_NAMES) + i + 1}")

        self.PLAYERS = players_set
        
        # Zgeneralizowane zasady gry
        self.MATCHES_COUNT = self.N
        self.PLAYERS_PER_MATCH = 4
        self.BENCH_SIZE = self.N - self.PLAYERS_PER_MATCH
        
        # Docelowa liczba gier i pauz dla każdego gracza
        # To jest cel optymalizacyjny, nie zawsze idealnie osiągalny
        if self.N == 4:
            self.TARGET_GAMES_PER_PLAYER = 3 # For 4 players, 3 games is more realistic
        elif self.N > 4:
            self.TARGET_GAMES_PER_PLAYER = self.N - 2 # More flexible for larger N
        else:
            self.TARGET_GAMES_PER_PLAYER = self.PLAYERS_PER_MATCH
        self.TARGET_RESTS_PER_PLAYER = self.BENCH_SIZE

    def __str__(self):
        """Zwraca czytelny opis konfiguracji."""
        return (
            f"--- Konfiguracja Gry ---\n"
            f"Liczba graczy (N): {self.N}\n"
            f"Gracze: {sorted(list(self.PLAYERS))}\n"
            f"Liczba meczów: {self.MATCHES_COUNT}\n"
            f"Graczy na ławce w meczu: {self.BENCH_SIZE}\n"
            f"Docelowa liczba gier na gracza: {self.TARGET_GAMES_PER_PLAYER}\n"
            f"------------------------"
        )

# Przykład użycia:
if __name__ == "__main__":
    # Ustaw liczbę graczy, dla której chcesz wygenerować konfigurację
    config = TennisConfiguration(num_players=6)
    print(config)

    config_10 = TennisConfiguration(num_players=10)
    print(config_10)

