import random

from .llm_service import clue_generator


class CrosswordService:
    """
    Builds a full crossword grid (letters + numbering + clue lists)
    from a dict of {word: clue} pairs.
    """

    def __init__(self, clue_generator):
        self._clue_generator = clue_generator

    def generate(self, category: str, num_words: int, use_fixture: bool = False):
        """
        Public entrypoint: returns (grid, across_clues, down_clues)
        """
        clues = self._clue_generator.generate(category, num_words)

        crossword_filled, words_placed = self._build_grid(clues)
        first_letters, across_clues, down_clues = self._build_clues(clues, words_placed)
        numbered_grid = self._add_numbers_to_grid(crossword_filled, first_letters)
        final_grid = self._simplify_grid(numbered_grid)

        return final_grid, across_clues, down_clues

    def _build_clues(self, clues, words_placed):
        # add clues to words dict
        for word in clues:
            if word in words_placed:
                words_placed[word]["clue"] = clues[word]

        across_clues = []
        down_clues = []

        for word, info in words_placed.items():
            entry = {"word": word, "number": info["number"], "clue": info["clue"]}
            if info["direction"] == "h":
                across_clues.append(entry)
            elif info["direction"] == "v":
                down_clues.append(entry)

        first_letters = {
            info["number"]: info["first_letter"] for info in words_placed.values()
        }
        return first_letters, across_clues, down_clues

    def _build_grid(self, clues):
        words = list(clues.keys())
        grid_size = max(len(word) for word in words) + 20  # padding for intersections
        mid_row = grid_size // 2
        start_col = grid_size // 2

        # initialize grid
        crossword = [["-" for _ in range(grid_size)] for _ in range(grid_size)]
        # find the longest word to place first
        first_word = max(words, key=len)
        words.remove(first_word)

        # place the first word
        for i, letter in enumerate(first_word):
            crossword[mid_row][start_col + i] = letter

        crossword_filled, words_placed = self._create_crossword(words, crossword)

        # adds first word to start of the word dict
        words_placed = {
            first_word: {
                "number": 1,
                "direction": "h",
                "first_letter": (mid_row, start_col),
            },
            **words_placed,
        }
        return crossword_filled, words_placed

    # Checks if words can be placed at given cell
    def _can_place(self, grid, word, row, col, d, letter_index, empty="-"):
        rows = len(grid)
        cols = len(grid[0])

        # intersection letter must match or be empty
        if grid[row][col] not in (empty, word[letter_index]):
            return False

        if d == "h":
            start_c = col - letter_index
            end_c = start_c + len(word) - 1

            if start_c < 0 or end_c >= cols:
                return False

            # cell before first and after last must be empty or edge
            if start_c > 0 and grid[row][start_c - 1] != empty:
                return False
            if end_c < cols - 1 and grid[row][end_c + 1] != empty:
                return False

            # check each position
            for k, ch in enumerate(word):
                r, c = row, start_c + k
                existing = grid[r][c]

                if (r, c) == (row, col):
                    # intersection must match
                    if existing not in (empty, ch):
                        return False
                else:
                    # must be empty to place
                    if existing != empty:
                        return False
                    # no vertical neighbors
                    if r > 0 and grid[r - 1][c] != empty:
                        return False
                    if r < rows - 1 and grid[r + 1][c] != empty:
                        return False
            return True

        else:  # 'v'
            start_r = row - letter_index
            end_r = start_r + len(word) - 1

            if start_r < 0 or end_r >= rows:
                return False

            # cell before first and after last vertically must be empty or edge
            if start_r > 0 and grid[start_r - 1][col] != empty:
                return False
            if end_r < rows - 1 and grid[end_r + 1][col] != empty:
                return False

            for k, ch in enumerate(word):
                r, c = start_r + k, col
                existing = grid[r][c]

                if (r, c) == (row, col):
                    if existing not in (empty, ch):
                        return False
                else:
                    if existing != empty:
                        return False
                    # no horizontal neighbors
                    if c > 0 and grid[r][c - 1] != empty:
                        return False
                    if c < cols - 1 and grid[r][c + 1] != empty:
                        return False
            return True

    # Place letters on grid, assuming can_place is true
    def _place_letters(self, grid, word, row, col, d, letter_index):
        if d == "h":
            start_c = col - letter_index
            for k, ch in enumerate(word):
                grid[row][start_c + k] = ch
        else:  # 'v'
            start_r = row - letter_index
            for k, ch in enumerate(word):
                grid[start_r + k][col] = ch

        return grid

    # Build crossword grid
    def _create_crossword(self, words, crossword):
        kept_words = {}
        number = 1
        for word in words:
            direction = random.choice(["h", "v"])
            for letter_index, letter in enumerate(word):
                for i, row in enumerate(crossword):
                    # Checks if the letter is present and that it can fit in the grid
                    if letter in row and self._can_place(
                        crossword, word, i, row.index(letter), direction, letter_index
                    ):
                        j = row.index(letter)
                        loc = (i, j)
                        self._place_letters(
                            crossword, word, i, j, direction, letter_index
                        )  # updates grid
                        # grid spot of the first letter, for tagging numbers
                        if direction == "v":
                            first_letter = loc[0] - letter_index, loc[1]
                        else:
                            first_letter = loc[0], loc[1] - letter_index

                        number += 1
                        # dictionary to only save words that were placed in the puzzle
                        kept_words[word] = {
                            "number": number,
                            "direction": direction,
                            "first_letter": first_letter,
                        }
                        break  # Stop after finding the first matching letter that CAN PLACE
                else:
                    continue
                break
        return crossword, kept_words

    # append the number to indicies of lists that match the first letter of words
    def _add_numbers_to_grid(self, grid, number_coords):
        for number, (r, c) in number_coords.items():
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                current_value = str(grid[r][c])
                grid[r][c] = f"{number} {current_value}"  # number is string
        return grid

    # Removes exterior rows and columns if they're all "black squares"
    def _simplify_grid(self, grid):
        # remove all rows that are all '-'
        filtered_rows = [row for row in grid if not all(cell == "-" for cell in row)]

        # check if the first or last element of all lists are '-' then drop that element (aka column)
        while filtered_rows and all(row[0] == "-" for row in filtered_rows):
            filtered_rows = [row[1:] for row in filtered_rows]

        while filtered_rows and all(row[-1] == "-" for row in filtered_rows):
            filtered_rows = [row[:-1] for row in filtered_rows]

        return filtered_rows


crossword_service = CrosswordService(clue_generator)
