import copy
from game_api import GameApi
from queue import PriorityQueue

USE_SAMPLE = False
TIMES_TO_SOLVE = 10
# Some games are really hard to win.
STATES_SEARCH_LIMIT = 1000000

# Cheated card represented by negative equivalents, e.g. -6 is a cheated 6
CARD_TO_NUMBER = {
    "a": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "j": 11,
    "q": 12,
    "k": 13
}
NUMBER_TO_CARD = {v: k for k, v in CARD_TO_NUMBER.items()}

SAMPLE_STACKS = [['a', '2', '9', 'j', '6', 'a', '5', '5', '9', '3', '8', 'k', '4'],
                 ['7', '8', '2', '3', 'j', 'a', '10', 'q', '5', '7', 'q', '8', '7'],
                 ['j', '9', 'a', '10', '2', '6', '7', '4', '6', 'k', 'q', '4', '6'],
                 ['q', '10', 'k', 'k', '3', '2', '4', 'j', '9', '10', '5', '8', '3']]

'''
A move is a tuple of (stack index, card index)
The card index is not really needed, only used to determine the correct place to click the mouse.
A move of (-1, -1) indicates the hand is reset ("Next Stack" button is clicked) which automatically
is added when there are no legal moves
'''
class GameState:
    def __init__(self, stacks, score = 0, current_hand = [], moves_taken = []):
        self.stacks = stacks
        self.score = score
        self.current_hand = current_hand
        self.moves_taken = moves_taken

    def __str__(self):
        text = "Stacks:\n"
        text += '\n'.join(' '.join(map(str, x)) for x in self.stacks)
        text += '\n'
        text += 'Current Hand:\n'
        text += str(self.current_hand)
        text += '\n'
        text += 'Score: '
        text += str(self.score)
        return text

    def __lt__(self, other):
        return isinstance(other, GameState) and self.get_score_for_queue() < other.get_score_for_queue()

    def __hash__(self):
        return hash((str(self.stacks), str(self.current_hand), self.score))

    def __eq__(self, other):
        return isinstance(other, GameState) and self.__hash__() == other.__hash__()

    def get_score_for_queue(self):
        return -1 * self.score

    '''
    - 2 points if first card is a Jack
    - 2 points if the hand total value is 15
    - 2 points if the hand total value is 31
    - 2 points for a set of 2 of a kind
    - 6 points for a set of 3 of a kind
    - 12 points for a set of 4 of a kind
    - 3 points for a run of 3 cards in any order
    - 4 points for a run of 4 cards in any order
    - 5 points for a run of 5 cards in any order
    - 6 points for a run of 6 cards in any order
    - 7 points for a run of 7 cards in any order
    '''
    def score_latest_card_in_hand(self, hand):
        latest_card_score = 0

        if len(hand) == 1:
            if hand[0] == 11:
                return 2
            return 0

        total_value = self.sum_card_values(hand)

        if total_value == 15 or total_value == 31:
            latest_card_score += 2

        if len(hand) >= 7:
            if self.check_consecutive(hand[-7:]):
                latest_card_score += 7
                return latest_card_score

        if len(hand) >= 6:
            if self.check_consecutive(hand[-6:]):
                latest_card_score += 6
                return latest_card_score

        if len(hand) >= 5:
            if self.check_consecutive(hand[-5:]):
                latest_card_score += 5
                return latest_card_score

        if len(hand) >= 4:
            if hand[-4] == hand[-3] == hand[-2] == hand[-1]:
                latest_card_score += 12
                return latest_card_score
            if self.check_consecutive(hand[-4:]):
                latest_card_score += 4
                return latest_card_score

        if len(hand) >= 3:
            if hand[-3] == hand[-2] == hand[-1]:
                latest_card_score += 6
                return latest_card_score
            if self.check_consecutive(hand[-3:]):
                latest_card_score += 3
                return latest_card_score

        if len(hand) >= 2:
            if hand[-2] == hand[-1]:
                latest_card_score += 2

        return latest_card_score

    def check_consecutive(self, cards):
        if len(cards) != len(set(cards)):
            return False
        min_val = min(cards)
        count = len(cards)

        target_sum = count * (count + 1) / 2 + (min_val - 1) * count
        if target_sum == sum(cards):
            return True
        return False

    def sum_card_values(self, cards):
        total = 0
        for value in cards:
            if value > 10:
                total += 10
            else:
                total += value
        return total

    def is_won(self):
        if self.score >= 61:
            return True
        return False

    def is_lost(self):
        for stack in self.stacks:
            if stack:
                return False
        if self.score < 61:
            return True
        return False

    '''
    The current hand value cannot exceed 31.
    We are required to reset if there are no legal moves, and cannot reset otherwise.
    '''
    def find_legal_moves(self):
        legal_moves = []

        current_hand_sum = self.sum_card_values(self.current_hand)
        for index, stack in enumerate(self.stacks):
            if not stack:
                continue

            current_card_in_stack = stack[-1]

            if current_card_in_stack > 10:
                current_card_in_stack = 10

            if current_hand_sum + current_card_in_stack <= 31:
                legal_moves.append((index, len(stack) - 1))

        if not legal_moves:
            legal_moves.append((-1, -1))

        return legal_moves

    '''
    Get the resulting state if we were to apply a move onto this current state.
    '''
    def get_move_end_state(self, move):
        new_stacks = copy.deepcopy(self.stacks)
        new_current_hand = []
        new_moves = copy.deepcopy(self.moves_taken)
        new_score = self.score

        if move[0] == -1 and move[1] == -1:
            pass
        else:
            new_current_hand = copy.deepcopy(self.current_hand)
            new_current_hand.append(new_stacks[move[0]][-1])
            new_stacks[move[0]] = new_stacks[move[0]][:-1]

            new_score += self.score_latest_card_in_hand(new_current_hand)

        new_game_state = GameState(new_stacks, new_score, new_current_hand, new_moves)
        new_game_state.moves_taken.append(move)

        return new_game_state


class Solver:
    def __init__(self, initial_state):
        self.initial_state = initial_state

    def solve(self, states_search_limit=STATES_SEARCH_LIMIT, accept_losing_state=False):
        move_list = []

        print("Initial game state:")
        print(self.initial_state)
        print()

        visited = set()
        queue = PriorityQueue()
        states_checked = 0
        target_state = None
        is_winning = False
        highest_scoring_state = self.initial_state

        queue.put(self.initial_state)

        # Traverse the state space and search for a target state.
        while not queue.empty() and not target_state:
            current_state = queue.get()

            if current_state in visited:
                continue

            states_checked += 1
            if states_checked >= STATES_SEARCH_LIMIT:
                print("Reached states search limit!")
                break

            print("Currently checking state with score: " + str(current_state.get_score_for_queue() * -1) + " (searched " + str(states_checked) + " states)")

            if current_state < highest_scoring_state:
                highest_scoring_state = current_state

            visited.add(current_state)

            legal_moves = current_state.find_legal_moves()

            for move in legal_moves:
                move_end_state = current_state.get_move_end_state(move)

                if move_end_state.is_won():
                    target_state = move_end_state
                    is_winning = True
                    break

                if move_end_state.is_lost():
                    if accept_losing_state:
                        target_state = move_end_state
                        is_winning = False
                        break
                    continue

                queue.put(move_end_state)

        print()
        print("States searched: " + str(states_checked))

        if not target_state:
            print("No target state found!")
            if accept_losing_state:
                return None, is_winning
            return highest_scoring_state, is_winning
        else:
            print("Target state found!")
            return target_state, is_winning

def main():

    print("Will solve " + str(TIMES_TO_SOLVE) + " times.")

    games_lost = 0

    for x in range(TIMES_TO_SOLVE):

        while True:
            print(str(TIMES_TO_SOLVE - x) + " more times to go.")
            stacks = SAMPLE_STACKS
            if not USE_SAMPLE:
                game_api = GameApi()
                stacks = game_api.stacks

            stacks = card_stacks_to_num_stacks(stacks)
            game_state = GameState(stacks)
            solver = Solver(game_state)

            final_state, is_winning = solver.solve()
            print()

            if not is_winning:
                print("Highest scoring state:")
                print(final_state)
                print()
                print("Finding end state to reset the game...")
                lose_solver = Solver(final_state)
                # The highest score state is most likely very close to a losing state (or is a losing state), so we shouldn't need to search far.
                final_state, is_winning = lose_solver.solve(states_search_limit=100, accept_losing_state=True)
                if not final_state:
                    raise Exception("Unable to find losing state to reset the game")

            print("Moves taken:")
            current_state = game_state
            for move in final_state.moves_taken:
                if move[0] == -1 and move[1] == -1:
                    print("-- NEXT STACK --")
                    if not USE_SAMPLE:
                        game_api.click_next_stack()
                else:
                    print(str(move) + "\t-- Column " + str(move[0] + 1))
                    if not USE_SAMPLE:
                        game_api.click_card(move)

            if not USE_SAMPLE and x != TIMES_TO_SOLVE - 1:
                print("Starting new game...")
                game_api.new_game()

            if is_winning:
                break
            else:
                games_lost += 1

    print("Games won: " + str(TIMES_TO_SOLVE))
    print("Games lost: " + str(games_lost))
    print("Done!")

def card_stacks_to_num_stacks(stacks):
    return [[CARD_TO_NUMBER[x] for x in y] for y in stacks]

def num_stacks_to_card_stacks(self):
    return [[NUMBER_TO_CARD[x] for x in y] for y in stacks]

if __name__ == "__main__":
    main()

