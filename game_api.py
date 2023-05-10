import pyscreeze
import time
from pynput.mouse import Button, Controller
from retry import retry

GAME_UPPER_LEFT_X = 1250
GAME_UPPER_LEFT_Y = 95

CARD_WIDTH = 362
CARD_HEIGHT = 72

COLUMN_1_X_THRESHOLD = 1285
COLUMN_2_X_THRESHOLD = 1655
COLUMN_3_X_THRESHOLD = 2025
COLUMN_4_X_THRESHOLD = 2025

CARD_IMAGES = {
    "a":    ("ref/a.png",   0.9),
    "2":    ("ref/2.png",   0.9),
    "3":    ("ref/3.png",   0.9),
    "4":    ("ref/4.png",   0.9),
    "5":    ("ref/5.png",   0.9),
    "6":    ("ref/6.png",   0.9),
    "7":    ("ref/7.png",   0.9),
    "8":    ("ref/8.png",   0.9),
    "9":    ("ref/9.png",   0.9),
    "10":   ("ref/10.png",  0.9),
    "j":    ("ref/j.png",   0.9),
    "q":    ("ref/q.png",   0.93),
    "k":    ("ref/k.png",   0.9)
}

NEXT_STACK_REF_IMAGE = "ref/next_stack.png"
NEW_GAME_REF_IMAGE = "ref/new_game.png"

class FoundCard:
    def __init__(self, name, upper_left_y_coord):
        self.name = name
        self.upper_left_y_coord = upper_left_y_coord

    def __lt__(self, other):
        return isinstance(other, FoundCard) and self.upper_left_y_coord < other.upper_left_y_coord

    def __hash__(self):
        return hash(self.name, self.upper_left_y_coord)

    def __eq__(self, other):
        return isinstance(other, FoundCard) and self.__hash__() == other.__hash__()

class GameApi:
    def __init__(self):
        self.stacks = []
        self.mouse = Controller()
        self.__focus_game_window()
        # Try to start a new game if we're on the window. This can also be run from the initial dealt screen.
        try:
            self.new_game()
        except:
            pass
        self.__populate_game_state()

    def __populate_game_state(self):
        game_image = pyscreeze.screenshot()

        cards = [[], [], [], []]
        for name, value in CARD_IMAGES.items():
            for result in self.__find_cards_by_image(value[0], game_image, value[1]):
                column_index = 0
                if result[0] > COLUMN_3_X_THRESHOLD:
                    column_index = 3
                elif result[0] > COLUMN_2_X_THRESHOLD:
                    column_index = 2
                elif result[0] > COLUMN_1_X_THRESHOLD:
                    column_index = 1
                cards[column_index].append(FoundCard(name, result[1]))

        for card_stack in cards:
            sorted_cards = sorted(card_stack)
            for x in sorted_cards:
                print(x.name + " " + str(x.upper_left_y_coord))
            self.stacks.append([x.name for x in sorted_cards])

        print("Found card stacks:")
        print(self.stacks)

    '''
    Returns a list of (upper left x coordinate, upper left y coordinate)
    '''
    def __find_cards_by_image(self, search_image, game_image, confidence_level, cards_to_find=4, depth=0):
        # Don't search for too long.
        if depth >= 15:
            raise Exception("Can't determine cards")

        results = []
        for found_card_pos in pyscreeze.locateAll(search_image, game_image, grayscale=True, confidence=confidence_level):
            skip = False
            if found_card_pos[0] > 2240:
                continue
            if found_card_pos[1] > 1020:
                continue
            for existing_card_pos in results:
                if self.__overlaps(found_card_pos, existing_card_pos):
                    skip = True
                    break
            if not skip:
                results.append((found_card_pos[0], found_card_pos[1]))

        '''
        If we find too many cards, increase the confidence level.
        If we don't find enough, decrease it.
        '''
        if len(results) > cards_to_find:
            return self.__find_cards_by_image(search_image, game_image, confidence_level + 0.005, cards_to_find, depth + 1)

        if len(results) < cards_to_find:
            return self.__find_cards_by_image(search_image, game_image, confidence_level - 0.005, cards_to_find, depth + 1)

        return results

    def __overlaps(self, found_card_pos, existing_card_pos):
        if (abs(found_card_pos[0] - existing_card_pos[0]) <= 5 and
            abs(found_card_pos[1] - existing_card_pos[1]) <= 5):
            return True
        return False

    def __click_on(self, position_tuple):
        self.mouse.position = position_tuple
        time.sleep(0.05)
        self.mouse.press(Button.left)
        time.sleep(0.05)
        self.mouse.release(Button.left)
        time.sleep(0.05)

    def __focus_game_window(self):
        self.__click_on((200, 200))


    '''
    Card tuple consists of (stack index, card index).
    '''
    def click_card(self, card_tuple):
        stack_num = card_tuple[0]
        card_num = card_tuple[1]
        x_pos = GAME_UPPER_LEFT_X + stack_num * CARD_WIDTH
        y_pos = GAME_UPPER_LEFT_Y + card_num * CARD_HEIGHT
        self.__click_on((x_pos, y_pos))
        time.sleep(0.25)

    @retry(tries=3, delay=0.5)
    def click_next_stack(self):
        location = pyscreeze.locateCenterOnScreen(NEXT_STACK_REF_IMAGE, grayscale=True, confidence=0.9)
        if not location:
            raise Exception("Can't find \"Next Stack\" button")
        self.__click_on(location)
        time.sleep(0.25)

    @retry(tries=3, delay=0.5)
    def new_game(self):
        location = pyscreeze.locateCenterOnScreen(NEW_GAME_REF_IMAGE, grayscale=True, confidence=0.9)
        if not location:
            raise Exception("Can't find \"New Game\" button")
        self.__click_on(location)
        time.sleep(5)
