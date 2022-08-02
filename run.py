import sys
import json
from crossword_generator import Crossword
from utilities import draw_string, get_move_cursor_string, get_alternating_square_color
from constants import AnsiCommands, Colors, UniChars, Orientation, get_large_letter

TERMINAL_WIDTH = 80
TERMINAL_HEIGHT = 24
START_ROW = 2
START_COL = 2
LIGHT_GRAY = Colors.get_background_color(220, 220, 220)
MEDIUM_GRAY = Colors.get_background_color(180, 180, 180)
DARK_GRAY = Colors.get_background_color(40, 40, 40)
TEXT_COLOR = Colors.get_foreground_color(0, 0, 0)

def main():
    """Main entry point for the program"""
    word_length_map = {}
    with open('data/crossword_dictionary.json', 'r', encoding='utf-8') as file:
        word_dict = json.load(file)

        # Build a python dictionary with word lengths as keys, and lists of words of
        # that length as values. The dictionary is used to search for matching
        # partial words
        for word in word_dict.keys():
            word = word.replace('\n', '')
            length = len(word)
            if length in word_length_map:
                word_length_map[length].append(word)
            else:
                word_length_map[length] = []
                word_length_map[length].append(word)
    crossword = Crossword(14, 14, word_length_map, word_dict)

    begin_puzzle(crossword)

def begin_puzzle(crossword):
    """Allows the user to begin solving the puzzle"""
    display_crossword(crossword)
    displayed = 'crossword'

    while True:
        input_y_pos = TERMINAL_HEIGHT - 1
        sys.stdout.write(get_move_cursor_string(0, input_y_pos))
        sys.stdout.write(AnsiCommands.CLEAR_LINE)
        sys.stdout.flush()
        command = input('Enter a command : ')
        if command != '':
            # The user may be entering the solution to a clue, or
            # requesting a clue to be displayed
            result = parse_command(command, crossword)
            user_message = f"{AnsiCommands.CLEAR_LINE}{result}"
            draw_string(user_message, 0, TERMINAL_HEIGHT, [Colors.FOREGROUND_RED])
        else :
            # The user is toggling through the views
            if displayed == 'crossword':
                displayed = 'clues'
                display_clues(crossword)
            elif displayed == 'clues':
                displayed = 'crossword'
                display_crossword(crossword)
                highlight_single_clue(crossword)

def display_crossword(crossword):
    """Print the crossword to the screen"""
    sys.stdout.write(AnsiCommands.CLEAR_SCREEN)
    sys.stdout.write(AnsiCommands.CLEAR_BUFFER)
    sys.stdout.flush()
    
    # Print a view of the crossword with blank squares where a letter occurs
    # in the grid. This view, on the left, will show the clue indices and 
    # highlight the currently selected clue
    for i, row in enumerate(crossword.grid):
        sys.stdout.write(get_move_cursor_string(START_COL, START_ROW + i))
        sys.stdout.flush()
        for j, col in enumerate(row):
            if crossword.grid[i][j] == '_':
                sys.stdout.write(f"{DARK_GRAY}  {AnsiCommands.DEFAULT_COLOR}")
            else:
                char = crossword.grid[i][j].upper()
                color = get_alternating_square_color(i, j)
                output = f"{color}{TEXT_COLOR}  {AnsiCommands.DEFAULT_COLOR}"
                sys.stdout.write(output)
    sys.stdout.flush()

    # Print a second view of the crossword on the right. This view displays
    # the solutions entered by the user
    right_col = 6 + crossword.cols * 2
    for i, row in enumerate(crossword.user_guesses):
        sys.stdout.write(get_move_cursor_string(right_col, START_ROW + i))
        sys.stdout.flush()
        for j, col in enumerate(row):
            if crossword.user_guesses[i][j] == '_':
                sys.stdout.write(f"{DARK_GRAY}  {AnsiCommands.DEFAULT_COLOR}")
            else:
                user_guess = crossword.user_guesses[i][j]
                char = None
                if user_guess == '*':
                    char = '  '
                else:
                    char = get_large_letter(user_guess)
                color = get_alternating_square_color(i, j)
                output = f"{color}{TEXT_COLOR}{char}{AnsiCommands.DEFAULT_COLOR}"
                sys.stdout.write(output)
    sys.stdout.flush()

    # Print the clue indices on the starting square of each clue.
    sys.stdout.write(TEXT_COLOR)
    for clue in crossword.clues_across:
        first_digit = ''
        second_digit = ''
        if clue.index <= 9:
            first_digit = UniChars.superscript(clue.index)
        else:
            first_digit = f"{UniChars.superscript(int(clue.index / 10))}"
            second_digit = f"{UniChars.superscript(clue.index % 10)}"

        row = START_ROW + clue.start_row
        col = START_COL + clue.start_col
        sys.stdout.write(get_move_cursor_string((col - 1) * 2, row))
        color = get_alternating_square_color(row, col)
        sys.stdout.write(f"{color}")
        sys.stdout.write(f"{first_digit}{second_digit}")

    for clue in crossword.clues_down:
        first_digit = ''
        second_digit = ''
        if clue.index <= 9:
            first_digit = UniChars.superscript(clue.index)
        else:
            first_digit = f"{UniChars.superscript(int(clue.index / 10))}"
            second_digit = f"{UniChars.superscript(clue.index % 10)}"

        row = START_ROW + clue.start_row
        col = START_COL + clue.start_col
        sys.stdout.write(get_move_cursor_string((col - 1) * 2, row))
        color = get_alternating_square_color(row, col)
        sys.stdout.write(f"{color}")
        sys.stdout.write(f"{first_digit}{second_digit}")
    sys.stdout.write(AnsiCommands.DEFAULT_COLOR)
    sys.stdout.flush()

def display_clues(crossword):
    """Print the clues to the screen"""
    start_col = 1
    start_row = 2
    sys.stdout.write(AnsiCommands.CLEAR_SCREEN)
    sys.stdout.write(AnsiCommands.CLEAR_BUFFER)
    sys.stdout.write(get_move_cursor_string(start_col, start_row))
    sys.stdout.flush()
    sys.stdout.write(f"{AnsiCommands.BOLD}{Colors.FOREGROUND_WHITE}")
    for char in 'across':
        sys.stdout.write(get_large_letter(char))
    print()
    sys.stdout.write(f"{AnsiCommands.NORMAL}{AnsiCommands.DEFAULT_COLOR}")
    for clue in crossword.clues_across:
        print(f"({clue.index} {clue.orientation.value}) ({len(clue.string)}) {clue.definitions[0]}")
    print()
    sys.stdout.write(f"{AnsiCommands.BOLD}{Colors.FOREGROUND_WHITE}")
    for char in 'down':
        sys.stdout.write(get_large_letter(char))
    print()
    sys.stdout.write(f"{AnsiCommands.NORMAL}{AnsiCommands.DEFAULT_COLOR}")
    for clue in crossword.clues_down:
        print(f"({clue.index} {clue.orientation.value}) ({len(clue.string)}) {clue.definitions[0]}")
    print()

def highlight_single_clue(crossword):
    """Highlight the position of one clue on the crossword puzzle, and print
       that clue below the crossword"""
    clue = crossword.selected_clue
    x_coord = START_COL + clue.start_col * 2
    y_coord = START_ROW + clue.start_row
    back = Colors.BACKGROUND_ORANGE
    fore = Colors.FOREGROUND_WHITE
    draw_string("  ", x_coord, y_coord, [fore, back])
    first_digit = ''
    second_digit = ''
    if clue.index <= 9:
        first_digit = UniChars.superscript(clue.index)
    else:
        first_digit = UniChars.superscript(int(clue.index / 10))
        second_digit = UniChars.superscript(clue.index % 10)
    
    # Draw the clue index in superscript in the starting cell of the clue
    draw_string(
        f"{first_digit}{second_digit}",
        x_coord,
        y_coord,
        [back, fore])

    # Color the succeeding squares of the clue in ORANGE
    if clue.orientation == Orientation.HORIZONTAL:
        for offset in range(1, len(clue.string)):
            back = Colors.BACKGROUND_ORANGE
            draw_string("  ", x_coord + offset * 2, y_coord, [fore, back])
    elif clue.orientation == Orientation.VERTICAL:
        for offset in range(1, len(clue.string)):
            back = Colors.BACKGROUND_ORANGE
            draw_string("  ", x_coord, y_coord + offset, [back, fore])

    # Highlight the corresponding squares of the solution view
    right_view_offset = 6 + crossword.cols * 2
    x_coord = right_view_offset + clue.start_col * 2 
    if clue.orientation == Orientation.HORIZONTAL:
        for offset, char in enumerate(clue.string):
            back = Colors.BACKGROUND_ORANGE
            fore = Colors.FOREGROUND_WHITE
            guess_char = crossword.user_guesses[clue.start_row][clue.start_col + offset]
            char_to_display = "  " if guess_char == "*" else get_large_letter(guess_char)
            draw_string(char_to_display, x_coord + offset * 2, y_coord, [fore, back])
    elif clue.orientation == Orientation.VERTICAL:
        for offset, char in enumerate(clue.string):
            back = Colors.BACKGROUND_ORANGE
            fore = Colors.FOREGROUND_WHITE
            guess_char = crossword.user_guesses[clue.start_row + offset][clue.start_col]
            char_to_display = "  " if guess_char == "*" else get_large_letter(guess_char)
            draw_string(char_to_display, x_coord, y_coord + offset, [back, fore])
    
    # Print the clue text just below the views of the crossword puzzle
    sys.stdout.write(AnsiCommands.DEFAULT_COLOR)
    sys.stdout.write(AnsiCommands.BOLD)
    text_display_y = START_ROW + crossword.rows + 1
    sys.stdout.write(get_move_cursor_string(0, text_display_y))
    length = len(clue.string)
    orientation = clue.orientation.value
    string = (
        f"{Colors.FOREGROUND_ORANGE}{clue.index} {orientation} "
        f"{Colors.FOREGROUND_YELLOW}({length}) "
        f"{Colors.FOREGROUND_ORANGE}{clue.definitions[0]}")
    sys.stdout.write(string)
    sys.stdout.write(AnsiCommands.DEFAULT_COLOR)
    sys.stdout.flush()

def parse_command(command, crossword):
    """Parse a command entered by the user. This can be either a request
       to display a different clue, or a solution to the clue currently
       displayed"""
    elements = command.split(' ')
    if elements[0].isnumeric():
        index = int(elements[0])
        # Check if this is a valic reference to a clue, and if so, highlight
        # that clue
        if elements[1].lower() == 'd' or elements[1].lower() == 'down':
            if crossword.has_clue(index, Orientation.VERTICAL):
                new_clue = crossword.get_clue(index, Orientation.VERTICAL)
                display_crossword(crossword)
                crossword.selected_clue = new_clue
                highlight_single_clue(crossword)
                return f"Now showing {index} Down"
            else:
                return 'No clue matches that!'
        elif elements[1].lower() == 'a' or elements[1].lower() == 'across':
            if crossword.has_clue(index, Orientation.HORIZONTAL):
                new_clue = crossword.get_clue(index, Orientation.HORIZONTAL)
                display_crossword(crossword)
                crossword.selected_clue = new_clue
                highlight_single_clue(crossword)
                return f"Now displaying {index} Across"
            else:
                return 'No clue matches that!'
        else:
            return 'No such clue!'
    else:
        # Check if command is a valid solution to the current clue
        # First ensure the command consists entirely of letters
        if not command.isalpha():
            return 'Solutions can only contain letters!'

        # Next check if the command is the correct lenght
        if len(command) != len(crossword.selected_clue.string):
            return f"Wrong length! Length of solution should be {len(crossword.selected_clue.string)}"

        # Guess is correct length and consists only of letters. Enter it in the
        # crossword.user_guesses array and draw the crossword views again to
        # display the updated solution to the user
        word = elements[0].lower()
        clue = crossword.selected_clue
        for i, char in enumerate(word):
            if clue.orientation == Orientation.HORIZONTAL:
                crossword.user_guesses[clue.start_row][clue.start_col + i] = char
            else:
                crossword.user_guesses[clue.start_row + i][clue.start_col] = char
        display_crossword(crossword)
        return f"Entered your guess : {word}"
    return 'No match pattern'


if __name__ == '__main__':
    main()