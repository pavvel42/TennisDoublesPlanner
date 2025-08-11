import itertools

def is_match_valid(config, match):
    """
    Sprawdza, czy mecz jest prawidłowy (4 różnych graczy).
    """
    return len(set(match[0]) | set(match[1])) == config.PLAYERS_PER_MATCH

def get_all_valid_matches(config):
    """
    Tworzy listę wszystkich możliwych, prawidłowych meczów dla danej konfiguracji.
    """
    teams = list(itertools.combinations(config.PLAYERS, 2))
    matches = list(itertools.combinations(teams, 2))
    return [m for m in matches if is_match_valid(config, m)]

def get_cost(individual, config):
    """
    Oblicza koszt (liczbę naruszeń zasad) dla danego harmonogramu.
    Im niższy koszt, tym lepszy harmonogram.
    """
    cost = 0
    player_counts = {player: 0 for player in config.PLAYERS}
    team_history = set()

    for match in individual:
        teams = (frozenset(match[0]), frozenset(match[1]))
        
        # Kara za powtórzenie drużyny
        if teams[0] in team_history or teams[1] in team_history:
            cost += 10 # Duża kara
        team_history.add(teams[0])
        team_history.add(teams[1])

        # Zliczenie wystąpień graczy
        for player in (set(match[0]) | set(match[1])):
            player_counts[player] += 1

    # Kara za niezgodność z docelową liczbą gier na gracza
    for player in config.PLAYERS:
        cost += abs(player_counts.get(player, 0) - config.TARGET_GAMES_PER_PLAYER)
        
    return cost

def get_player_counts(schedule, players):
    """
    Zlicza, ile razy każdy gracz wystąpił w danym harmonogramie.
    """
    player_counts = {player: 0 for player in players}
    for match in schedule:
        for player in (set(match[0]) | set(match[1])):
            player_counts[player] += 1
    return player_counts

def is_full_schedule_valid(schedule, config):
    """
    Sprawdza, czy pełny harmonogram jest prawidłowy pod względem wszystkich zasad.
    Używane do weryfikacji końcowego rozwiązania.
    """
    if len(schedule) != config.MATCHES_COUNT:
        return False # Harmonogram nie ma odpowiedniej liczby meczów

    player_counts = {player: 0 for player in config.PLAYERS}
    team_history = set()

    for match in schedule:
        teams = (frozenset(match[0]), frozenset(match[1]))
        
        # Sprawdzenie unikalności drużyn
        if teams[0] in team_history or teams[1] in team_history:
            return False
        team_history.add(teams[0])
        team_history.add(teams[1])

        # Zliczenie wystąpień graczy
        for player in (set(match[0]) | set(match[1])):
            player_counts[player] += 1

    # Sprawdzenie liczby meczów dla każdego gracza
    for player in config.PLAYERS:
        if player_counts.get(player, 0) != config.TARGET_GAMES_PER_PLAYER:
            return False
            
    return True
