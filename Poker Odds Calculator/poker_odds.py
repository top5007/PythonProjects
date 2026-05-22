# Required: pip install treys
#
# Terminal-based Texas Hold'em equity calculator.
# Run:  python poker_equity.py

import random
import sys
from itertools import combinations

from treys import Card, Deck, Evaluator


VALID_RANKS = {"2", "3", "4", "5", "6",
               "7", "8", "9", "10", "J", "Q", "K", "A"}
VALID_SUITS = {"d", "c", "s", "h"}

MC_ITERATIONS = 10000


# ---------- Input parsing & prompts ----------

def parse_card(text):
    """Parse user input like 'Ah', '10s', 'Kd' into a treys card int."""
    s = text.strip()
    if len(s) < 2 or len(s) > 3:
        raise ValueError(
            f"invalid card '{text}' (expected e.g. 'Ah', '10s', 'Kd')")

    suit = s[-1].lower()
    rank = s[:-1].upper()

    if rank not in VALID_RANKS:
        raise ValueError(
            f"invalid rank '{rank}' (use 2-10, J, Q, K, A)"
        )
    if suit not in VALID_SUITS:
        raise ValueError(f"invalid suit '{suit}' (use d, c, s, h)")

    treys_rank = "T" if rank == "10" else rank
    return Card.new(treys_rank + suit)


def prompt_card(prompt_text, used_cards):
    while True:
        try:
            raw = input(prompt_text)
        except EOFError:
            raise
        try:
            card = parse_card(raw)
        except ValueError as e:
            print(f"  Error: {e}. Try again.")
            continue
        if card in used_cards:
            print(
                f"  Error: card '{raw.strip()}' has already been used. Try again.")
            continue
        return card


def prompt_yes_no(prompt_text):
    while True:
        s = input(prompt_text).strip().lower()
        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False
        print("  Please answer 'y' or 'n'.")


def prompt_player_count():
    while True:
        s = input("How many players? (2-9): ").strip()
        try:
            n = int(s)
        except ValueError:
            print("  Error: please enter an integer between 2 and 9.")
            continue
        if 2 <= n <= 9:
            return n
        print("  Error: number of players must be between 2 and 9.")


# ---------- Equity calculation ----------

def _tally(player_hands, board, evaluator, wins, ties):
    scores = [evaluator.evaluate(board, hand) for hand in player_hands]
    best = min(scores)  # lower is better in treys
    winners = [i for i, s in enumerate(scores) if s == best]
    if len(winners) == 1:
        wins[winners[0]] += 1
    else:
        for w in winners:
            ties[w] += 1


def calculate_equity_monte_carlo(player_hands, community, iterations=MC_ITERATIONS):
    evaluator = Evaluator()
    n = len(player_hands)
    wins = [0] * n
    ties = [0] * n

    used = set()
    for hand in player_hands:
        used.update(hand)
    used.update(community)
    remaining = [c for c in Deck.GetFullDeck() if c not in used]
    cards_needed = 5 - len(community)

    for _ in range(iterations):
        sampled = random.sample(remaining, cards_needed)
        _tally(player_hands, community + sampled, evaluator, wins, ties)

    return [(wins[i] / iterations * 100, ties[i] / iterations * 100) for i in range(n)]


def calculate_equity_enumeration(player_hands, community):
    evaluator = Evaluator()
    n = len(player_hands)
    wins = [0] * n
    ties = [0] * n

    used = set()
    for hand in player_hands:
        used.update(hand)
    used.update(community)
    remaining = [c for c in Deck.GetFullDeck() if c not in used]
    cards_needed = 5 - len(community)

    total = 0
    # combinations(_, 0) yields one empty tuple, so river (0 unknowns) works naturally.
    for combo in combinations(remaining, cards_needed):
        _tally(player_hands, community + list(combo), evaluator, wins, ties)
        total += 1

    return [(wins[i] / total * 100, ties[i] / total * 100) for i in range(n)]


# ---------- Output ----------

def print_equity(stage_name, equity):
    print(f"\n--- {stage_name} Odds ---")
    print("{")
    for i, (win, tie) in enumerate(equity):
        print(f"  Player {i + 1} Win: {round(win, 2)},")
        print(f"  Player {i + 1} Tie: {round(tie, 2)},")
    print("}")


def show_hole_cards(player_hands):
    print("\nDealt hole cards:")
    for i, hand in enumerate(player_hands):
        pretty = " ".join(Card.int_to_pretty_str(c) for c in hand)
        print(f"  Player {i + 1}: {pretty}")


def show_board(community):
    if not community:
        return
    pretty = " ".join(Card.int_to_pretty_str(c) for c in community)
    print(f"Board: {pretty}")


# ---------- Main flow ----------

def main():
    print("♣️ ♦️ === Texas Hold'em Equity Calculator === ❤️ ♠️")
    print("Card format: rank + suit (lowercase).  Examples: Ah, 10s, Kd, 7c")

    num_players = prompt_player_count()

    used_cards = set()
    player_hands = []
    for p in range(1, num_players + 1):
        c1 = prompt_card(f"Player {p} - Enter card 1: ", used_cards)
        used_cards.add(c1)
        c2 = prompt_card(f"Player {p} - Enter card 2: ", used_cards)
        used_cards.add(c2)
        player_hands.append([c1, c2])

    show_hole_cards(player_hands)

    community = []

    # Pre-flop (auto)
    print(
        f"\nCalculating pre-flop equity ({MC_ITERATIONS} Monte Carlo iterations)...")
    equity = calculate_equity_monte_carlo(player_hands, community)
    print_equity("Pre-Flop", equity)

    # Flop
    if not prompt_yes_no("\nContinue to flop? (y/n): "):
        return
    for i in range(1, 4):
        c = prompt_card(f"Enter flop card {i}: ", used_cards)
        used_cards.add(c)
        community.append(c)
    show_board(community)
    print(
        f"\nCalculating flop equity ({MC_ITERATIONS} Monte Carlo iterations)...")
    equity = calculate_equity_monte_carlo(player_hands, community)
    print_equity("Flop", equity)

    # Turn
    if not prompt_yes_no("\nShow turn card? (y/n): "):
        return
    c = prompt_card("Enter turn card: ", used_cards)
    used_cards.add(c)
    community.append(c)
    show_board(community)
    print("\nCalculating turn equity (full enumeration)...")
    equity = calculate_equity_enumeration(player_hands, community)
    print_equity("Turn", equity)

    # River
    if not prompt_yes_no("\nShow river card? (y/n): "):
        return
    c = prompt_card("Enter river card: ", used_cards)
    used_cards.add(c)
    community.append(c)
    show_board(community)
    print("\nCalculating river equity (full enumeration)...")
    equity = calculate_equity_enumeration(player_hands, community)
    print_equity("River", equity)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        sys.exit(0)
