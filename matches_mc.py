
import itertools
import numpy as np

def are_equal(sol1: list, sol2: list) -> bool:
    """
    Check if two given solutions are the same
    """
    for i in range(len(sol1)):
        if sol1[i] == sol2[i]:
            continue
        else:
            return False
    
    return True

def shift_matchday(matchday: list) -> list:
    """
    Shift the matchday schedule by one in the left direction.
    E.g. (A, B, C, D, E) -> (B, C, D, E, A) 
    """
    new_matchday = list()
    for idx in range(1, len(matchday)):
        new_matchday.append(matchday[idx])
    new_matchday.append(matchday[0])
    
    return new_matchday

def get_all_shifts(matchday: list) -> list:
    """
    Create all possible shifts for given matchday schedule
    E.g. (A, B, C, D, E) ->
                            (B, C, D, E, A)
                            (C, D, E, A, B)
                            (D, E, A, B, C)
                            (E, A, B, C, D)
    """
    shifted_matchdays = list()
    shifted = shift_matchday(matchday)
    shifted_matchdays.append(shifted)

    for _ in range(3):
        shifted = shift_matchday(shifted)
        shifted_matchdays.append(shifted)
    
    return shifted_matchdays

def is_shfited(matchday1: list, matchday2: list) -> bool:
    """
    Test if matchday1 and matchday2 are same schedules.
    Comparison is performed for all possible schedule shifts.
    """
    shifts = get_all_shifts(matchday1)

    for s in shifts:
        if are_equal(s, matchday2):
            return True
    
    return False

def remove_shifted_matchdays(matchdays: list, solutions_indices: list) -> list:
    """
    Remove shifted matchdays.
    """
    shifted_counter = 0
    indices_to_remove = list()
    print("Solutions before shift removal: {}".format(len(solutions_indices)))
    for i in solutions_indices:
        for j in solutions_indices:
            if i >= j:
                continue
            if is_shfited(matchdays[i], matchdays[j]):
                if j not in indices_to_remove:
                    indices_to_remove.append(j)            
                    shifted_counter += 1

    print("{} shifted solutions removed".format(shifted_counter))
    
    for idx in indices_to_remove:
        solutions_indices.remove(idx)

    return solutions_indices

def init_proba_matrix(states: list, players: set) -> np.ndarray:
    """
    Create transition matrix of size nxn where n is the number of possible matches (states).
    """
    states_count = len(states)
    proba_matrix = np.zeros((states_count, states_count))

    for x in range(states_count):
        match = states[x]
        match_bench = get_bench(players, match)
        first_team, second_team = match[0], match[1]

        for y in range(states_count):
            if x == y:
                proba_matrix[x, y] = 0
                continue

            next_match = states[y]
            next_match_bench = get_bench(players, next_match)
            next_first_team, next_second_team = next_match[0], next_match[1]

            if first_team == next_first_team or first_team == next_second_team:
                proba_matrix[x, y] = 0 
                continue

            if second_team == next_first_team or second_team == next_second_team:
                proba_matrix[x, y] = 0 
                continue
            
            if not is_player_swap_valid(match_bench, next_match_bench):
                proba_matrix[x, y] = 0
                continue

            proba_matrix[x, y] = 1
    
    proba_matrix = to_stochastic_matrix(proba_matrix)

    return proba_matrix

def to_stochastic_matrix(matrix: np.ndarray) -> np.ndarray:
    """
    Transform matrix to stochastic form - every column and every row sum up to 1.
    """
    rows, _ = matrix.shape
    proba_matrix = np.zeros(matrix.shape)

    for x in range(rows):
        row_sum = np.sum(matrix[x, :])
        for y in range(rows):            
            if row_sum == 0:
                proba_matrix[x, y] = 0
                continue 
            proba_matrix[x, y] = matrix[x, y] / row_sum

    return proba_matrix

def generate_matchdays(available_matches, proba_matrix: np.ndarray, matches_count: int, samples_count: int) -> list:
    """
    Given probability transition matrix, generate "samples_count" trajectories of length "matches_count".
    The initial probability is given by uniform distribution over integers from 0 to len(available_matches).  
    """
    matchdays = list()

    av_matches_count = len(available_matches)

    for _ in range(samples_count):
        matchday = list()
        idx = np.random.randint(0, av_matches_count)

        for _ in range(matches_count):
            idx = np.random.default_rng().choice(av_matches_count, p=proba_matrix[idx, :])
            matchday.append(available_matches[idx])

        assert len(matchday) == matches_count, "Generated matches count: {}, should be {}".format(len(matchday), matches_count)
        matchdays.append(matchday)

    return matchdays

def get_cost(matchday: list, player_matches_count: int) -> tuple:
    """
    Calculate the cost of given matchday.
    Cost consists of 3 ordered components:
        - total player costs
        - matchday cost
        - sum of total player and matchday costs
    
    Total player cost is sum of individual player costs.
    Player cost equals absolute value of difference between player occurences in games and desired player occurences (4)
    Matchday cost equals number of repeated teams in schedule.
    """
    player_costs = dict()
    matchday_cost = 0
    team_history = list()

    for match in matchday:
        fst_team, snd_team = match[0], match[1]
        m_players = list(fst_team) + list(snd_team)
                
        for p in m_players:
            if p not in player_costs:
                player_costs[p] = 1
            else:
                player_costs[p] += 1

        for team in team_history:
            if fst_team == team:
                matchday_cost += 1
                    
            if snd_team == team:
                matchday_cost += 1
                
        team_history.append(fst_team)
        team_history.append(snd_team)
            
    total_player_costs = 0

    for key in player_costs.keys():
        total_player_costs += abs(player_costs[key] - player_matches_count)
    
    return total_player_costs, matchday_cost, total_player_costs + matchday_cost

def get_bench(players: set, match: tuple) -> set:
    """
    Returns the "bench" - the set of players that are resting in the given match.
    """
    fst_team, snd_team = match[0], match[1]
    match_players = list(fst_team) + list(snd_team)
    return players.difference(match_players)

def is_match_valid(players: set, match: tuple) -> bool:
    """
    Tests if match is valid. The match is valid when the number of distinct players in game equals 4, and
    symmetric difference of match players and bench equals the all players set.
    """
    fst_team, snd_team = match[0], match[1]
    match_players = set(fst_team).union(set(snd_team))

    if len(match_players) != 4:
        return False

    bench = get_bench(players, match)

    return players == match_players.symmetric_difference(bench)

def is_player_swap_valid(bench1, bench2):
    """
    Tests if player swap is valid. The intersection between two benches should be empty set.
    """
    common = bench1.intersection(bench2)

    return len(common) == 0

if __name__ == "__main__":
    players = set(["K", "P", "W", "T", "M"])
    bench_size = len(players) - 4
    
    matches_count = 5
    player_matches_count = 4
    
    # create possible teams
    teams = list(itertools.combinations(players, 2))
    # create possible matches - every match consists of 2 teams
    matches = list(itertools.combinations(teams, 2))

    print("Players size: ", len(players))
    print("Bench size: ", bench_size)

    available_matches = list()

    # filter all matches from invalid ones
    for m in matches:
        is_valid = is_match_valid(players, m)
        if is_valid:
            available_matches.append(m)

    proba_matrix = init_proba_matrix(available_matches, players)
    tmp_proba_matrix = np.copy(proba_matrix)

    solutions = list()
    solutions_count = 1000

    print("Generating {} matchdays".format(solutions_count))
    matchdays = generate_matchdays(available_matches, proba_matrix, matches_count, solutions_count)

    for m in matchdays:
        pc, mc, tc = get_cost(m, player_matches_count)
        solutions.append([m, pc, mc, tc])

    perfect_solutions = list()
    min_index = 0

    # find the best solutions
    for idx in range(1, len(solutions)):
        if solutions[idx][3] < solutions[min_index][3]:
            min_index = idx

        if solutions[idx][3] == 0:
            perfect_solutions.append(idx)

    print("Perfect solutions count: ", len(perfect_solutions))
    print("Best solutions: ", solutions[min_index])

    exit()