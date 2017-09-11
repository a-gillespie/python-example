import random, string, profile, math, sys
from os.path import exists

DEFAULT = 5
ALPHA_VAL = 65


class dictNode:
    """Create a new node structure for implementing a dictionary trie.
    
    Attributes:
      children ([dictNode]): Array of pointers to children, corresponds to A-Z.
      found (bool): Indicator that the word has been found and can be ignored.
      isWord (bool): Indicator that the node corresponds to a real word.
      parent (dictNode): Pointer to parent.
    """
    
    def __init__(self, parent, letter):
        """Class constructor.
        
        Args:
          parent (dictNode): Parent node.
          letter (char): Next letter in the word to be entered in the dictionary
            trie. Must be uppercase.
        """
        self.parent = parent
        self.children = [None] * 26
        self.isWord = False
        self.found = False
        if parent is not None:
            parent.children[ord(letter) - ALPHA_VAL] = self


class game:
    """Create a new game of boggle.
    
    Attributes:
      board ([[char]]): All letters on the board arranged [row][column].
      dict (dictNode): Root node of dictionary trie.
      found ([string]): Stores each word found on the board.
      score (int): Stores sum of score of words on board.
      size (int): Dimension of board.
      srange ([int]): Range (0,1,...,size), stored to reduce calls to range().
      visited ([[bool]]): Tracks which squares have been visited during crawl.
      visited_reset ([[bool]]): Stores initial state of self.visited for reset.
    """
    
    def __init__(self, board_in=None, dict_file=None):
        """Class constructor.
        
        Args:
          board_in (string|int, optional): User-defined string of uppercase
            characters representing the board, or an integer specifying the
            dimensions of the board.
          dict_file (string, optional): Filename of dictionary.
        """
        # handles input of a board string or board size to populate randomly
        board_in = str(board_in)
        if board_in.isdigit() or board_in == 'None':
            self.size = DEFAULT if board_in == 'None' else int(board_in)
            self.srange = range(self.size)
            self.board = self.generateBoard()
        # ensures custom boards are square
        elif math.sqrt(len(board_in)).is_integer() and board_in.isupper():
            self.size = int(math.sqrt(len(board_in)))
            self.srange = range(self.size)
            self.board = self.specifyBoard(board_in)
        else:
            sys.exit('User-defined boards must contain '
                     'a square number of letters.')
        
        # initialise vars for max score, array of found words and grid tracker
        self.score = 0
        self.found = []
        self.visited = []
        for i in self.srange:
            self.visited.append([False]*self.size)
        # remember this state to use later instead of repeating the above
        self.visited_reset = [x[:] for x in self.visited]
        
        # check for user specified dictionary file else use a default filename
        dict_file = dict_file if dict_file else 'dictionary.txt'
        if exists(dict_file):
            self.dict = self.makeTrie(dict_file)
        else:
            sys.exit("Dictionary file '%s' not found." % d) 
    
    def makeTrie(self, dictfile):
        """Return the root of a trie from the words in a dictionary file.
        
        The resulting data structure requires significantly more memory than an
        array but allows constant lookup time once initialised.
        
        Args:
          dictfile (string): Filename of dictionary.
        """
        root = dictNode(None, '')
        with open(dictfile) as d:
            for word in d:
                cur = root
                for letter in word.strip():
                    next = cur.children[ord(letter) - ALPHA_VAL]
                    if next is None:
                        next = dictNode(cur, letter)
                    cur = next
                cur.isWord = True
        return root
    
    def __str__(self):
        """Return a string representation of the board for print() behaviour."""
        tempstr = ''
        for row in self.board:
            tempstr += (''.join(row) + '\n')
        return tempstr
    
    def generateBoard(self):
        """Return a randomly generated board from a set of dice."""
        # check for dice file, convert it into a 2d array 'dice'[die][face]
        if exists('dice.txt'):
            with open('dice.txt') as f:
                dice = [die.strip() for die in f]
        else:
            sys.exit("Dice file 'dice.txt' not found.")
        # check that there are actually enough dice in the file
        if len(dice) < (self.size*self.size):
            sys.exit("Not enough dice in 'dice.txt' "
                     "to populate board of size %d." % self.size)
        
        # construct the board with random dice throws
        tempBoard = []
        for x in self.srange:
            row = []
            for y in self.srange:
                die = dice.pop(random.randrange(len(dice)))
                row.append(random.choice(die))
            tempBoard.append(row)
        self.found = []
        return tempBoard
    
    def specifyBoard(self, input):
        """Return a board of a specific letter configuration.
        
        Args:
          input (string): Sequence of uppercase letters representing the board.
        """
        tempBoard = []
        for i in range(self.size):
            tempBoard.append(input[i*self.size:(i+1)*self.size])
        self.found = []
        return tempBoard
    
    def resetVisited(self):
        """Set all bools in self.visited to False."""
        self.visited = [x[:] for x in self.visited_reset]
    
    def getValidStrings(self):
        """Initiate a crawl across the board to detect all legal strings.
        
        This function calls self.buildString() for each square on the board,
        from top-left to bottom-right. At the end of the call, self.found should
        be an array of all words able to be constructed on the board according
        to the rules of boggle, and self.score should be an integer equal to the
        maximum possible score for the board.
        """
        self.score = 0
        self.found = []
        for row in self.srange:
            for col in self.srange:
                self.resetVisited()
                s = ''
                self.buildString(s, row, col, self.dict)
    
    def buildString(self, letters, x, y, cur):
        if (x < 0 or x >= self.size or y < 0 or y >= self.size):
            return
        if self.visited[x][y]:
            return
        
        self.visited[x][y] = True
        letters += 'QU' if self.board[x][y] == 'Q' else self.board[x][y] # TODO: fix this
        
        next = cur.children[ord(self.board[x][y]) - ALPHA_VAL]
        if next:
            if next.isWord and not next.found:
                next.found = True
                self.found.append(letters)
                print letters
                l = len(letters)
                if l > 2:
                    self.awardPoints(l)

            for i in (-1,0,1):
                for j in (-1,0,1):
                    self.buildString(letters, x+i, y+j, next)
        
        self.visited[x][y] = False
    
    def awardPoints(self, l):
        if l<5:
            self.score += 1
        elif l==5:
            self.score += 2
        elif l==6:
            self.score += 3
        elif l==7:
            self.score += 5
        else:
            self.score += 11

            
def main():
    b = raw_input().upper()
    d = raw_input()
    x = game(b,d)
    x.getValidStrings()
    print ("Maximum score: %d" % x.score)
    
if __name__ == '__main__':
    main()