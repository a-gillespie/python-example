import random, string, profile, math, sys
from os.path import exists

DEFAULT_BOARD_SIZE = 5

class game:
    
    def __init__(self, board_in=None, dict_f=None):
        
        # generates a random a board of default size if not passed arg1
        # if arg1 is a number, generates a random board of that size
        # if arg1 is an encoded board, generates that board
        board_in = str(board_in)
        if board_in.isdigit() or board_in == 'None' or not board_in:
            self.size = DEFAULT_BOARD_SIZE if board_in == 'None' or not board_in else int(board_in)
            self.srange = range(self.size)
            self.board = self.generateBoard()
        elif math.sqrt(len(board_in)).is_integer() and board_in.isupper():
            self.size = int(math.sqrt(len(board_in)))
            self.srange = range(self.size)
            self.board = self.specifyBoard(board_in)
        else:
            sys.exit('User-defined boards must contain a square number of letters.')
        
        self.score = 0 # stores max potential score
        
        self.found = [] # stores words found by allValidStrings() binary search
        
        self.visited = [] # tracks which letters have already been looked at during crawls
        for i in self.srange:
            self.visited.append([False]*self.size)
        self.visited_reset = [x[:] for x in self.visited]
        
        # retrieve dictionary from file specified in arg2
        # defaults to 'dictionary.txt' if not passed arg2
        d = dict_f if dict_f else 'dictionary.txt'
        if exists(d):
            with open(d) as f:
                self.dict = [word.strip() for word in f]
            self.dictlen = len(self.dict)
        else:
            sys.exit("Dictionary file '%s' not found." % d) 
    
    
    # defines simple print behaviour
    def __str__(self):
        
        tempstr = ''
        for row in self.board:
            tempstr += (''.join(row) + '\n')
        
        return tempstr
    
    
    # generates a board using randomly selected dice
    def generateBoard(self):
        
        # checks for dice file, converts into a 2d array dice[die][face]
        if exists('dice.txt'):
            with open('dice.txt') as f:
                dice = [die.strip() for die in f]
        else:
            sys.exit("Dice file 'dice.txt' not found.") # error message if no dice file
        if len(dice) < (self.size*self.size):
            sys.exit("Not enough dice in 'dice.txt' to populate board of size %d." % self.size)
        
        tempBoard = []
        
        # iterate through rows, construct board using random die throws
        for x in self.srange:
            row = []
            for y in self.srange:
                die = dice.pop(random.randrange(len(dice)))
                row.append(random.choice(die))
            tempBoard.append(row)     
        
        return tempBoard
        
    
    # handles construction of user-defined boards
    def specifyBoard(self, input):
        
        tempBoard = []
        
        for i in range(self.size):
            tempBoard.append(input[i*self.size:(i+1)*self.size])
        
        return tempBoard
    
    
    # clears tracker var
    def resetVisited(self):
        
        self.visited = [x[:] for x in self.visited_reset]
        # for x in self.srange:
            # for y in self.srange:
                # self.visited[x][y] = False
    
    
    # returns true iff word can be found on the board
    def find(self, word):
        
        if len(word) < 2:
            return False
        
        # performs recursive search starting from each letter
        for row in self.srange:
            for col in self.srange:
                self.resetVisited()
                if self.search(word, row, col):
                    return True
        return False
    
    
    # recursive function to crawl through board. returns true iff
    # all letters are exhausted
    # avoids off-board coordinates and previously visited letters
    def search(self, letters, x, y):
        
        if len(letters) == 0: # word has been found
            return True
        
        if (x < 0 or x >= self.size or y < 0 or y >= self.size): # ignore invalid coords
            return False 
        if self.visited[x][y]: # ignore previously visited letters
            return False
        if self.board[x][y] == 'Q': # treat instances of Q as QU
            if letters[:2] != 'QU':
                return False
            else:
                letters = letters[1:] # skip ahead one letter because of QU
        elif self.board[x][y] != letters[0]: # check for match at head
            return False
        
        self.visited[x][y] = True # update tracker var
        
        # look at all adjacent tiles
        for i in (-1,0,1):
            for j in (-1,0,1):
                if self.search(letters[1:], x+i, y+j):
                    return True
        
        # may need to look at this letter again from a different path
        self.visited[x][y] = False
        return False
    
    
    def iterateOverDict(self):
        
        found = 0
        for word in self.dict:
            if self.find(word):
                found +=1
                print word
        #print found
    
    
    # constructs strings from the letters on the board
    # and saves them in an array if they appear in the dictionary
    # dictionary is searched via binary search
    def allValidStrings(self):
        
        self.score = 0
        self.found = []
        for row in self.srange:
            for col in self.srange:
                self.resetVisited()
                s = ''
                self.buildString(s, row, col)
    
    
    # similar to search(), recursion ends when string is no
    # longer a prefix of any word in dict - IMPORTANT!
    def buildString(self, letters, x, y):
        
        if (x < 0 or x >= self.size or y < 0 or y >= self.size):
            return
        if self.visited[x][y]:
            return
        
        self.visited[x][y] = True
        letters += 'QU' if self.board[x][y] == 'Q' else self.board[x][y] # expands Q tiles to QU
        
        # perform binary search on the dictionary for the word, award points if
        # word is found and more than 2 letters long
        match, prefix = self.binarySearch(letters)
        if match and letters not in self.found:
            self.found.append(letters)
            print letters
            l = len(letters)
            if l > 2:
                self.awardPoints(l)
        
        # only continue the recursion if we know the current string is a prefix
        # of any words in the dictionary - prevents generating large amounts of
        # strings which we know won't be found
        if prefix:
            for i in (-1,0,1):
                for j in (-1,0,1):
                    self.buildString(letters, x+i, y+j)
        
        self.visited[x][y] = False
    
    
    # binary search for a given string in the dict array
    # returns a pair of bools for match/prefix found
    def binarySearch(self, letters):
        
        left = 0
        right = self.dictlen
        match = False
        prefix = False
        l = len(letters)
        
        while left <= right and not match:
            mid = (left + right)/2
            if not prefix:
                if self.dict[mid][:l] == letters:
                    prefix = True
            if self.dict[mid] == letters:
                match = True
            elif self.dict[mid] > letters:
                right = mid-1
            else:
                left = mid+1
        
        return(match, prefix)
        
    
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
    x.allValidStrings()
    print ("Words found: %d" % len(x.found))
    print ("Maximum score: %d" % x.score)
    
if __name__ == '__main__':
    main()