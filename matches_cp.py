from ortools.sat.python import cp_model
from visualizer import visualize_schedule, visualize_frequency_matrices
import time
from tennis_config import TennisConfiguration
from collections import defaultdict

def solve_tennis_problem(n):
    model = cp_model.CpModel()

    config = TennisConfiguration(num_players=n)
    num_players = config.N
    player_names = sorted(list(config.PLAYERS))
    player_map = {i: player_names[i] for i in range(num_players)}

    max_matches = num_players * (num_players - 1) // 4
    players = range(num_players)
    matches = range(max_matches)

    # Variables.
    # schedule[p][m] is 1 if player p plays in match m.
    schedule = {}
    for p in players:
        for m in matches:
            schedule[(p, m)] = model.NewBoolVar(f'schedule_p{p}_m{m}')

    # Constraints.

    # Each match has 4 players.
    for m in matches:
        model.Add(sum(schedule[(p, m)] for p in players) == 4)

    # Fair rotation of players on the bench.
    played_matches = [model.NewIntVar(0, max_matches, f'played_matches_p{p}') for p in players]
    for p in players:
        model.Add(played_matches[p] == sum(schedule[(p, m)] for m in matches))

    min_played = model.NewIntVar(0, max_matches, 'min_played')
    max_played = model.NewIntVar(0, max_matches, 'max_played')
    model.AddMinEquality(min_played, played_matches)
    model.AddMaxEquality(max_played, played_matches)
    model.Add(max_played - min_played <= 1) # All players play e.g. 3 or 4 matches

    # Maximize the number of matches played.
    # Also, minimize the variance in games played per player.
    total_games_played = sum(schedule[(p,m)] for p in players for m in matches)
    model.Maximize(total_games_played)

    # Calculate variance (or sum of absolute differences from mean) for fairness
    # This is tricky with CP, so we'll use a simpler approach: minimize max_played - min_played
    # which is already there. For more fine-grained control, we'd need to add more variables
    # and constraints to model the sum of absolute differences or squares.
    # For now, the max_played - min_played <= 1 constraint combined with maximizing total games
    # should lead to a reasonably fair distribution.


    # We need to model teams and opponents.
    # Let's create team variables.
    teams = {}
    for m in matches:
        for p1 in players:
            for p2 in players:
                if p1 < p2:
                    teams[(p1, p2, m)] = model.NewBoolVar(f'team_p{p1}_p{p2}_m{m}')

    # A player is in a match if and only if they are in a team for that match.
    # This ensures that the 4 players in the schedule are the same 4 players in the teams.
    for m in matches:
        for p in players:
            is_in_team = sum(teams.get((min(p, p_other), max(p, p_other), m), 0) for p_other in players if p != p_other)
            model.Add(schedule[(p, m)] == is_in_team)

    # Each match has two teams.
    for m in matches:
        model.Add(sum(teams[(p1, p2, m)] for p1 in players for p2 in players if p1 < p2) == 2)

    # No two players team up more than once.
    for p1 in players:
        for p2 in players:
            if p1 < p2:
                model.Add(sum(teams[(p1, p2, m)] for m in matches) <= 1)

    # Solve and print solution.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f'Solution for {num_players} players found in {solver.WallTime()} seconds:')
        schedule_result = []
        player_match_counts = {name: 0 for name in player_names}
        player_rest_counts = {name: 0 for name in player_names}

        partner_counts = defaultdict(lambda: defaultdict(int))
        opponent_counts = defaultdict(lambda: defaultdict(int))

        for m in matches:
            playing_indices = []
            for p in players:
                if solver.Value(schedule[(p, m)]):
                    playing_indices.append(p)
            
            if len(playing_indices) == 4:
                # Determine teams for display
                team_1_indices = []
                team_2_indices = []
                
                # Find the two teams in the current match
                found_teams_indices = []
                for p1_idx in playing_indices:
                    for p2_idx in playing_indices:
                        if p1_idx < p2_idx and solver.Value(teams[(p1_idx, p2_idx, m)]):
                            found_teams_indices.append((p1_idx, p2_idx))
                
                if len(found_teams_indices) == 2:
                    team_1_indices = found_teams_indices[0]
                    team_2_indices = found_teams_indices[1]

                    team_1_names = (player_map[team_1_indices[0]], player_map[team_1_indices[1]])
                    team_2_names = (player_map[team_2_indices[0]], player_map[team_2_indices[1]])

                    print(f'Match {m + 1}: {team_1_names[0]} & {team_1_names[1]} vs {team_2_names[0]} & {team_2_names[1]}')
                    schedule_result.append((team_1_names, team_2_names))

                    # Update player match counts
                    for p_idx in playing_indices:
                        player_match_counts[player_map[p_idx]] += 1

                    # Update partner counts
                    partner_counts[team_1_names[0]][team_1_names[1]] += 1
                    partner_counts[team_1_names[1]][team_1_names[0]] += 1
                    partner_counts[team_2_names[0]][team_2_names[1]] += 1
                    partner_counts[team_2_names[1]][team_2_names[0]] += 1

                    # Update opponent counts
                    for p1_name in team_1_names:
                        for p2_name in team_2_names:
                            opponent_counts[p1_name][p2_name] += 1
                            opponent_counts[p2_name][p1_name] += 1

                else:
                    print(f'Match {m + 1}: Could not determine teams for players {playing_indices}')
            else:
                print(f'Match {m + 1}: Not enough players for a match: {playing_indices}')

            # Update rest counts
            for p_idx in players:
                if p_idx not in playing_indices:
                    player_rest_counts[player_map[p_idx]] += 1

        print("\n--- Podsumowanie Graczy ---")
        print("| Gracz          | Mecze | Odpoczynki |\n|----------------|-------|------------|")
        for player_name in player_names:
            matches_played = player_match_counts.get(player_name, 0)
            rests_taken = player_rest_counts.get(player_name, 0)
            print(f"| {player_name:<14} | {matches_played:<5} | {rests_taken:<10} |")
        print("----------------------------")

        # Convert defaultdict to regular dict for visualization
        final_partner_counts = {name: dict(partner_counts[name]) for name in player_names}
        final_opponent_counts = {name: dict(opponent_counts[name]) for name in player_names}

        with open('results_cp.txt', 'a') as f:
            f.write(f'n={num_players}, time={solver.WallTime()}\n')
        visualize_schedule(schedule_result, player_map)
        visualize_frequency_matrices(player_names, final_partner_counts, final_opponent_counts)
    else:
        print('No solution found.')

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
            solve_tennis_problem(n)
        except ValueError:
            print("Please provide a valid number of players.")
    else:
        # Example for 5 players
        solve_tennis_problem(5)
