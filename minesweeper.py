import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # No mines
        if self.count == 0:
            return set()

        # All mines
        if self.count == len(self.cells):
            return self.cells

        # Else we donot know wheter a cell is a mine or not

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # All safe
        if self.count == 0:
            return self.cells

        # No safe
        if self.count == len(self.cells):
            return set()

        # Else we donot know wheter a cell is a mine or not

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # Cell in sentence
        if cell in self.cells:
            
            # Remove cell from cells
            self.cells.remove(cell)

            # Update count
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # Cell in sentence
        if cell in self.cells:

            # Removes cell from cells
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        # Mark as one of the moves made
        self.moves_made.add(cell)

        # Mark cell safe also in sentences
        self.mark_safe(cell)

        # New sentence in Knowledge base
        cells = set()

        # Cells around given cell
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update cells
                if 0 <= i < self.height and 0 <= j < self.width:

                    # Add cells not known mines or safes
                    if (i, j) not in self.mines:
                        if (i, j) not in self.safes:
                            cells.add((i, j))
                    
                    # -1 for each known mine around cell not added in cells
                    if (i, j) in self.mines:
                        count -= 1

        # Remove sentences with empty cells from knowledge
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

        # If new sentence is empty No modification is required
        # Check for sentence to be empty
        if len(cells) != 0:

            # Add new sentence in knowledge
            new_sentence = Sentence(cells, count)
            self.knowledge.append(new_sentence)

            # Subset method
            length = len(self.knowledge)

            for i in range(length):

                # Eliminating the case where a set is a subset of itself
                if self.knowledge[i].cells != cells:

                    # sentence in knowledge is subset of new sentence
                    if self.knowledge[i].cells.issubset(cells):

                        # Add derived sentence to knowledge
                        self.knowledge.append(Sentence(cells - self.knowledge[i].cells, count - self.knowledge[i].count))
                        
                        # new sentence(superset) no longer needed
                        if new_sentence in self.knowledge:
                            self.knowledge.remove(new_sentence)
                        
                    # new sentence is subset of sentence in knowledge
                    elif cells.issubset(self.knowledge[i].cells):

                        # Add derived sentence to knowledge
                        self.knowledge.append(Sentence(self.knowledge[i].cells - cells, self.knowledge[i].count - count))
                        
                        # sentence in knowledge(superset) no longer needed
                        self.knowledge.remove(self.knowledge[i])
                    
            # For each sentence in knowledge
            for sentence in self.knowledge:

                # If new cells can be safe
                if sentence.known_safes():

                    # Deep copy
                    x = set()
                    for z in sentence.known_safes():
                        x.add(z)
                    
                    # Mark each cell as safe
                    for cell in x:
                        self.mark_safe(cell)
                           
                # If new cells can be mines
                if sentence.known_mines():
                    # Deep copy
                    x = set()
                    for z in sentence.known_mines():
                        x.add(z)
                    
                    # Mark each cell as mine
                    for cell in x:
                        self.mark_mine(cell)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Return a cell from safes
        for x in self.safes:
            if x not in self.moves_made:
                return x

        # No safe move possible
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Set of all cells
        setall = set()
        for i in range(0, self.width):
            for j in range(0, self.height):
                setall.add((i, j))
        
        # Remove cells from setall
        setall -= self.moves_made
        setall -= self.safes
        setall -= self.mines

        # Now setall has all the cells that are not mines and not made move

        # If no move is possible
        if len(setall) == 0:
            return None

        # Make random move from setall
        return random.sample(setall, 1)[0]
