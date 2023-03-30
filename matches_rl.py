import itertools
import numpy as np
import matplotlib.pyplot as plt

np.set_printoptions(precision=4, linewidth=160)

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

def init_reward_matrix(players, available_matches):
    states_count = len(available_matches)

    reward_matrix = np.zeros((states_count, states_count))

    for x in range(states_count):
        match = available_matches[x]
        match_bench = get_bench(players, match)
        first_team, second_team = match[0], match[1]
        
        for y in range(states_count):
            if x == y:
                reward_matrix[x, y] -= 1

            next_match = available_matches[y]
            next_match_bench = get_bench(players, next_match)
            next_first_team, next_second_team = next_match[0], next_match[1]
            
            if first_team == next_first_team:
                reward_matrix[x, y] -= 1
            
            if first_team == next_second_team:
                reward_matrix[x, y] -= 1

            if second_team == next_first_team:
                reward_matrix[x, y] -= 1
            
            if second_team == next_second_team:
                reward_matrix[x, y] -= 1
            
            if is_player_swap_valid(match_bench, next_match_bench):
                reward_matrix[x, y] += 5
            else:
                reward_matrix[x, y] -= 1

    return reward_matrix

def get_cost(matchday, player_matches_count):
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

def get_max_q(q_matrix, idx):
    max_value = np.amax(q_matrix[idx, :])
    indices = np.where(q_matrix[idx, :] == max_value)[0]

    if len(indices) == 1:
        return indices[0]

    return indices[np.random.default_rng().integers(low=0, high=len(indices))]

def q_learning_step(q_matrix, state_idx, action_idx, reward):
    alfa = 0.2
    discount = 0.9
    q_max_idx = get_max_q(q_matrix, action_idx)
    q_max = q_matrix[action_idx, q_max_idx]
    delta = reward + discount * q_max - q_matrix[state_idx, action_idx]
    delta = delta * alfa
    q_matrix[state_idx, action_idx] = q_matrix[state_idx, action_idx] + delta

if __name__ == "__main__":
    players = set(["K", "P", "W", "T", "M"])
    bench_size = len(players) - 4
    counter = dict()

    matches_count = 5 # how many matches will be played
    player_matches_count = len(players) - 1 # how many matches every player has to play
    teams = list(itertools.combinations(players, 2))
    matches = list(itertools.combinations(teams, 2))

    print("Players size: ", len(players))
    print("Bench size: ", bench_size)

    print(matches[0])
    print(get_bench(players, matches[0]))

    available_matches = list()

    for m in matches:
        is_valid = is_match_valid(players, m)
        if is_valid:
            available_matches.append(m)

    print("Possible matches: ", len(matches))
    print("Valid matches:    ", len(available_matches))

    # available_matches = matches

    reward_matrix = init_reward_matrix(players, available_matches)
    transition_matrix = init_proba_matrix(available_matches, players)

    print("Reward matrix: ")
    print(reward_matrix)
    print()
    print("Transition matrix: ")
    print(transition_matrix)

    available_matches_count = len(available_matches)
    q_matrix = np.zeros((available_matches_count, available_matches_count))
    # q_matrix = np.random.default_rng().integers(low=-5, high=10, size=(available_matches_count, available_matches_count))
    # q_matrix = np.random.default_rng().random((available_matches_count, available_matches_count))
    print()
    print(q_matrix)

    # q_learning_step(q_matrix, 0, 2, 1)

    reward_history = list()
    epochs = 200
    horizon = 10

    # Q-learning loop
    for epoch in range(epochs):
        total_reward = 0
        current_state = np.random.default_rng().choice(available_matches_count)
        
        for h in range(horizon):
            next_state = None
            # explore vs exploit
            if np.random.default_rng().uniform(0, 1) >= 0.8:
                next_state = np.random.default_rng().choice(available_matches_count, p=transition_matrix[current_state, :])
            else:
                next_state = get_max_q(q_matrix, current_state)
            
            reward = reward_matrix[current_state, next_state]
            total_reward += reward

            q_learning_step(q_matrix, current_state, next_state, reward)

            current_state = next_state

        reward_history.append(total_reward)

    print()
    print(q_matrix)

    matchdays_count = 100
    matchdays = list()

    # Generate trajectories using Q-table
    for x in range(matchdays_count):
        current_state = np.random.default_rng().integers(low=0, high=available_matches_count)
        total_reward = 0
        trajectory = list()
        trajectory.append(current_state)

        for h in range(player_matches_count):
            next_state = get_max_q(q_matrix, current_state)
            trajectory.append(next_state)
            reward = reward_matrix[current_state, next_state]
            total_reward += reward

            current_state = next_state

        matchday = list()

        for idx in trajectory:
            matchday.append(available_matches[idx])

        matchdays.append(matchday)

    perfect_solutions = list()
    cost_counter = dict()
    min_cost = np.inf

    for m in matchdays:
        cost = get_cost(m, player_matches_count)
        if cost[2] < min_cost:
            min_cost = cost[2]

        if cost[2] not in cost_counter:
            cost_counter[cost[2]] = 1
        else:
            cost_counter[cost[2]] += 1

        if cost[2] == 0:
            perfect_solutions.append(m)
            print(m, cost)

    print(len(perfect_solutions))
    print(cost_counter)
    print("The best cost: {}".format(min_cost))
    plt.plot(reward_history)
    plt.show()