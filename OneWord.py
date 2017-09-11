# Task 2
# Searches for a user-defined word on a board
# Extension: iterates through dictionary and
# prints all words present on the board

import BSBoggle, profile

def main():
    word = raw_input().upper()
    x = BSBoggle.game(raw_input())
    if x.find(word):
        print 'YES'
    else:
        print 'NO'
        
    input = ''
    while input not in ('y', 'n'):
        print 'Iterate through dictionary and print all words on board? y/n'
        input = raw_input()
        
    if input == 'n':
        return
    
    x.iterateOverDict()

main()