import holdem_calc

def calculate_win_rate(player_hand_str, board_str):
    """
    Calculates the probability of winning against 1 random opponent.
    player_hand_str: e.g., ["As", "Ks"]
    board_str: e.g., ["Ad", "2s", "5h"]
    """
    if not player_hand_str or len(player_hand_str) < 2:
        return 0.0

    # calculate(board, exact, num_sims, input_file, hole_cards, verbose)
    # We set 'exact' to False for speed on the Raspberry Pi
    results = holdem_calc.calculate(
        board=board_str if board_str else None,
        exact=False,
        num_sims=5000,
        input_file=None,
        hole_cards=player_hand_str,
        verbose=False
    )
    
    # holdem_calc returns a list of result objects; we take the first player
    if results:
        return results[0] * 100 # Returns winning percentage
    return 0.0