"""Rock-Paper-Scissors, up to Lizard-Spock, with an AI that is worth beating.

The rules live in one dictionary rather than an `elif` ladder. That is not
tidiness for its own sake: adding Lizard and Spock takes the ladder from 3
branches to 10, and takes the dictionary from 3 lines to 5.

    python rockpaperscissors.py            # play; unattended it runs the demo
    python rockpaperscissors.py --demo     # AI vs. two scripted opponents
    python rockpaperscissors.py --test     # unit tests
"""

import collections
import random
import sys

# Each move maps to everything it beats. Three-move play uses the first
# entry of each list; the full five-move game uses both.
BEATS = {
    "ROCK":     ["SCISSORS", "LIZARD"],
    "PAPER":    ["ROCK", "SPOCK"],
    "SCISSORS": ["PAPER", "LIZARD"],
    "LIZARD":   ["PAPER", "SPOCK"],
    "SPOCK":    ["SCISSORS", "ROCK"],
}

CLASSIC = ["ROCK", "PAPER", "SCISSORS"]
options = CLASSIC                       # what an unqualified game uses


def winner(user: str, computer: str) -> str:
    """Who won: "user", "computer", or "tie"."""
    if user == computer:
        return "tie"
    return "user" if computer in BEATS[user] else "computer"


COUNTER = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK",
           "LIZARD": "ROCK", "SPOCK": "LIZARD"}

last_user_move = None


def ai_pick(moves=None) -> str:
    """Counter whatever the player threw last time.

    This is a cheap strategy and it works, because people repeat moves far
    more often than chance would. Against a genuinely random opponent it is
    worth nothing -- which the demo below measures rather than asserts.
    """
    moves = moves or options
    if last_user_move is None:
        return random.choice(moves)
    return COUNTER.get(last_user_move, random.choice(moves))


score = {"user": 0, "computer": 0, "tie": 0}


def ask(prompt, default=""):
    """Read a line, or fall back to `default` when nobody is there to type."""
    try:
        answer = input(prompt)
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default
    return answer.strip() or default


def play_round(user_choice=None, moves=None, smart=True) -> str:
    """One round: pick, compare, score. Returns the result."""
    global last_user_move
    moves = moves or options
    if user_choice is None:
        user_choice = ask(f"Choose {', '.join(m.title() for m in moves)}: ",
                          moves[0]).upper()
        while user_choice not in moves:
            user_choice = ask("Invalid input. Try again: ",
                              moves[0]).upper()
    computer_choice = ai_pick(moves) if smart else random.choice(moves)
    result = winner(user_choice, computer_choice)
    score[result] += 1
    verdict = {"tie": "It's a tie!", "user": "You win!",
               "computer": "You lose!"}[result]
    print(f"Computer chose {computer_choice}. {verdict}")
    print(f"Score -- You: {score['user']}  Computer: {score['computer']}  "
          f"Ties: {score['tie']}")
    last_user_move = user_choice
    return result


def play():
    """The interactive loop."""
    while True:
        play_round()
        if ask("Do you want to play again? (y/n): ", "n").lower() != "y":
            break
    print("Thanks for playing!")


def measure(strategy, rounds=30_000, smart=True) -> dict:
    """How often the counter-AI wins against a given player, over many rounds.

    `strategy` is a function taking the round number and returning a move.
    """
    global last_user_move
    last_user_move = None
    tally = collections.Counter()
    for i in range(rounds):
        user_choice = strategy(i)
        computer_choice = ai_pick(CLASSIC) if smart \
            else random.choice(CLASSIC)
        tally[winner(user_choice, computer_choice)] += 1
        last_user_move = user_choice
    return {key: tally[key] / rounds for key in ("user", "computer", "tie")}


def demo():
    """Measure the AI against a random player and a habitual one."""
    random.seed(20260809)
    print(f"{'opponent':34} {'AI wins':>8} {'player wins':>12} {'ties':>7}")
    print("-" * 64)
    cases = [
        ("uniformly random player",
         lambda i: random.choice(CLASSIC), True),
        ("player who repeats one move",
         lambda i: "ROCK", True),
        ("player cycling R-P-S",
         lambda i: CLASSIC[i % 3], True),
        ("random player, AI also random",
         lambda i: random.choice(CLASSIC), False),
    ]
    for label, strategy, smart in cases:
        rates = measure(strategy, smart=smart)
        print(f"{label:34} {rates['computer']:7.1%} {rates['user']:11.1%} "
              f"{rates['tie']:6.1%}")
    print("\nThe counter strategy is only worth anything against a player who")
    print("repeats. Against a random opponent it lands on the same 1/3 as")
    print("random play, because there is nothing left to predict.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestGame(unittest.TestCase):
            def test_rock_beats_scissors(self):
                self.assertEqual(winner("ROCK", "SCISSORS"), "user")

            def test_same_move_ties(self):
                for move in BEATS:
                    self.assertEqual(winner(move, move), "tie")

            def test_every_pairing_has_a_winner(self):
                for a in BEATS:
                    for b in BEATS:
                        result = winner(a, b)
                        if a == b:
                            continue
                        # Exactly one direction wins; the rules must not be
                        # symmetric or a move would beat what beats it.
                        self.assertNotEqual(result, winner(b, a))

            def test_each_move_beats_two_and_loses_to_two(self):
                for move in BEATS:
                    wins = sum(1 for other in BEATS
                               if other != move and winner(move, other)
                               == "user")
                    self.assertEqual(wins, 2)

        unittest.main(argv=sys.argv[:1], exit=False)
    elif "--demo" in sys.argv or not sys.stdin.isatty():
        demo()
    else:
        play()
