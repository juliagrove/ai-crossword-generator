import json
import os
import random
from pathlib import Path

from .llm_service import clue_generator


class CrosswordService:
    """
    Builds a full crossword grid (letters + numbering + clue lists)
    from a dict of {word: clue} pairs.
    """

    def __init__(self, clue_generator):
        self._clue_generator = clue_generator

    def generate(self, category: str, num_words: int):
        """
        Public entrypoint: returns (grid, across_clues, down_clues)
        """
        if os.getenv("USE_SAMPLE_CROSSWORD_DATA", "false").lower() == "true":
            clues = self._load_sample_data()
        else:
            clues = self._clue_generator.generate(category, num_words)

        crossword_filled, words_placed = self._build_grid(clues)
        first_letters, across_clues, down_clues = self._build_clues(clues, words_placed)
        numbered_grid = self._add_numbers_to_grid(crossword_filled, first_letters)
        final_grid = self._simplify_grid(numbered_grid)

        return final_grid, across_clues, down_clues

    def _load_sample_data(self):
        """
        Instead of calling the API, use premade crosswords for testing
        """
        sample_path = (
            Path(__file__).resolve().parent.parent / "tests" / "large_sample.json"
        )
        with open(sample_path) as f:
            return json.load(f)

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
        crossword = [
            [
                {
                    "letter": "-",
                    "across_number": None,
                    "down_number": None,
                }
                for _ in range(grid_size)
            ]
            for _ in range(grid_size)
        ]
        # find the longest word to place first
        first_word = max(words, key=len)
        words.remove(first_word)

        # place the first word
        # tag all its cells with across_number = 1
        for offset, letter in enumerate(first_word):
            cell = crossword[mid_row][start_col + offset]
            cell["letter"] = letter
            cell["across_number"] = 1
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

        def letter_at(r, c):
            return grid[r][c]["letter"]
        # intersection letter must match or be empty
        if letter_at(row, col) not in (empty, word[letter_index]):
            return False

        if d == "h":
            start_c = col - letter_index
            end_c = start_c + len(word) - 1

            if start_c < 0 or end_c >= cols:
                return False

            # cell before first and after last must be empty or edge
            if start_c > 0 and letter_at(row, start_c - 1) != empty:
                return False
            if end_c < cols - 1 and letter_at(row, end_c + 1) != empty:
                return False

            # check each position
            for k, ch in enumerate(word):
                r, c = row, start_c + k
                existing = letter_at(r, c)

                if (r, c) == (row, col):
                    # intersection must match
                    if existing not in (empty, ch):
                        return False
                else:
                    # must be empty to place
                    if existing != empty:
                        return False
                    # no vertical neighbors
                    if r > 0 and letter_at(r - 1, c) != empty:
                        return False
                    if r < rows - 1 and letter_at(r + 1, c) != empty:
                        return False
            return True

        else:  # 'v'
            start_r = row - letter_index
            end_r = start_r + len(word) - 1

            if start_r < 0 or end_r >= rows:
                return False

            # cell before first and after last vertically must be empty or edge
            if start_r > 0 and letter_at(start_r - 1, col) != empty:
                return False
            if end_r < rows - 1 and letter_at(end_r + 1, col) != empty:
                return False

            for k, ch in enumerate(word):
                r, c = start_r + k, col
                existing = letter_at(r, c)

                if (r, c) == (row, col):
                    if existing not in (empty, ch):
                        return False
                else:
                    if existing != empty:
                        return False
                    # no horizontal neighbors
                    if c > 0 and letter_at(r, c - 1) != empty:
                        return False
                    if c < cols - 1 and letter_at(r, c + 1) != empty:
                        return False
            return True

    # Place letters on grid, assuming can_place is true
    def _place_letters(self, grid, word, row, col, d, letter_index, clue_number):
        if d == "h":
            start_c = col - letter_index
            for k, ch in enumerate(word):
                cell = grid[row][start_c + k]
                cell["letter"] = ch
                if cell.get("across_number") is None:
                    cell["across_number"] = clue_number
        else:  # 'v'
            start_r = row - letter_index
            for k, ch in enumerate(word):
                cell = grid[start_r + k][col]
                cell["letter"] = ch
                if cell.get("down_number") is None:
                    cell["down_number"] = clue_number
        return grid

    # Build crossword grid
    def _create_crossword(self, words, crossword):
        """
        Builds the crossword grid.

        crossword:
            {
                "letter": "-",
                "across_number": None,
                "down_number": None,
            }

        Returns:
            crossword (updated),
            kept_words: {
                word: {
                    "number": clue number,
                    "direction": "h" or "v",
                    "first_letter": (row, col),
                }
            }
        """
        kept_words = {}
        number = 1
        for word in words:
            direction = random.choice(["h", "v"])
            placed = False
            # check potential intersection
            for letter_index, letter in enumerate(word):
                if placed:
                    break
                for i, row in enumerate(crossword):
                    # Checks if the letter is in the row
                    if not any(cell["letter"] == letter for cell in row):
                        continue
                    # find the first column with this letter
                    j = next(
                        idx for idx, cell in enumerate(row) if cell["letter"] == letter
                    )
                    # check if word can be placed at this intersection
                    if not self._can_place(
                        crossword, word, i, j, direction, letter_index
                    ):
                        continue
                    number += 1
                    # place letters and tag clue number
                    self._place_letters(
                        crossword, word, i, j, direction, letter_index, number
                    )  # updates grid
                    # grid spot of the first letter, for tagging numbers
                    if direction == "v":
                        first_letter = (i - letter_index, j)
                    else:
                        first_letter = (i, j - letter_index)

                    # number += 1
                    # dictionary to only save words that were placed in the puzzle
                    kept_words[word] = {
                        "number": number,
                        "direction": direction,
                        "first_letter": first_letter,
                    }
                    placed = True
                    break
        return crossword, kept_words

    # append the number to indicies of lists that match the first letter of words
    def _add_numbers_to_grid(self, grid, number_coords):
        for number, (r, c) in number_coords.items():
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                cell = grid[r][c]
                existing = cell.get("label")
                if existing is None:
                    cell["label"] = str(number)
                # case when cell is the start letter of 2 words
                else:
                    existing_str = str(existing)
                    parts = {p.strip() for p in existing_str.split("/")}
                    if str(number) not in parts:
                        cell["label"] = existing_str + "/" + str(number)
        return grid

    # Removes exterior rows and columns if they're all "black squares"
    def _simplify_grid(self, grid):
        # remove all rows that are all '-'
        filtered_rows = [
            row for row in grid if not all(cell["letter"] == "-" for cell in row)
        ]

        # drop leading empty columns
        while filtered_rows and all(row[0]["letter"] == "-" for row in filtered_rows):
            filtered_rows = [row[1:] for row in filtered_rows]

        # drop trailing empty columns
        while filtered_rows and all(row[-1]["letter"] == "-" for row in filtered_rows):
            filtered_rows = [row[:-1] for row in filtered_rows]

        return filtered_rows


crossword_service = CrosswordService(clue_generator)
