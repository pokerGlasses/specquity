"""
odds.py — Poker odds engine.

Pre-flop / Flop / Turn:
  - Win probability (Monte Carlo vs random opponent)
  - Current hand strength
  - Probability of making each hand type by the river (exhaustive combos)

River (all 5 community cards dealt):
  - Win probability only (hand is final, no more cards to come)
"""

import random
import logging
from itertools import combinations
from treys import Card, Evaluator, Deck

from config import MC_ITERATIONS

log = logging.getLogger(__name__)

evaluator = Evaluator()

CLASS_NAMES = {
    1: "Straight Flush", 2: "Four of a Kind", 3: "Full House",
    4: "Flush", 5: "Straight", 6: "Three of a Kind",
    7: "Two Pair", 8: "Pair", 9: "High Card",
}


def _normalize(card_str: str) -> str:
    """
    Convert Roboflow labels (e.g. '9C', 'QD', '10H') to Treys format ('9c', 'Qd', 'Th').
    """
    s = card_str.strip()
    if s.startswith("10"):
        s = "T" + s[2:]
    rank = s[:-1].upper()
    suit = s[-1].lower()
    return rank + suit


def calculate_odds(player_cards: list[str], community_cards: list[str]) -> dict:
    """
    Returns:
      - win_probability:  float
      - hand_strength:    str   (current made hand, or "Pre-Flop")
      - hand_odds:        dict  (hand name → % chance by river; empty on river)
    """
    player_norm = [_normalize(c) for c in player_cards]
    community_norm = [_normalize(c) for c in community_cards]

    log.info(f"Normalized cards — hand: {player_norm}, board: {community_norm}")

    my_hand = [Card.new(c) for c in player_norm]
    board = [Card.new(c) for c in community_norm]

    full_deck = Deck().cards
    seen = my_hand + board
    remaining_deck = [c for c in full_deck if c not in seen]

    cards_to_deal = 5 - len(board)

    # ── Current hand strength ────────────────────────────
    if len(board) >= 3:
        current_score = evaluator.evaluate(board, my_hand)
        current_class = evaluator.get_rank_class(current_score)
        hand_strength = CLASS_NAMES.get(current_class, "Unknown")
    else:
        hand_strength = "Pre-Flop"

    # ── Win probability (Monte Carlo) ────────────────────
    wins = 0
    ties = 0

    for _ in range(MC_ITERATIONS):
        deck_copy = list(remaining_deck)
        random.shuffle(deck_copy)

        opp_hand = deck_copy[:2]
        new_community = deck_copy[2: 2 + cards_to_deal]
        full_board = board + new_community

        my_score = evaluator.evaluate(full_board, my_hand)
        opp_score = evaluator.evaluate(full_board, opp_hand)

        if my_score < opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1

    win_prob = round(((wins + (ties / 2)) / MC_ITERATIONS) * 100, 1)

    # ── Hand type probabilities (exhaustive, skip on river) ──
    hand_odds = {}

    if cards_to_deal > 0:
        hand_counts = {i: 0 for i in range(1, 10)}
        possible_runouts = list(combinations(remaining_deck, cards_to_deal))
        total_scenarios = len(possible_runouts)

        for runout in possible_runouts:
            final_board = board + list(runout)
            score = evaluator.evaluate(final_board, my_hand)
            hand_class = evaluator.get_rank_class(score)
            hand_counts[hand_class] += 1

        for rank_class, count in sorted(hand_counts.items()):
            if count > 0:
                prob = round((count / total_scenarios) * 100, 2)
                hand_odds[CLASS_NAMES[rank_class]] = prob

    log.info(f"Win: {win_prob}%  |  Strength: {hand_strength}  |  Odds: {hand_odds}")

    return {
        "win_probability": win_prob,
        "hand_strength": hand_strength,
        "hand_odds": hand_odds,
    }