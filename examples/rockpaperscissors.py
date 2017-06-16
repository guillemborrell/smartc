from smartc.contract.builder import node, Attribute, visualize, gather, Contract
from collections import defaultdict

# Set all attributes.
bets_player1 = [Attribute('player1_try{}'.format(i), str) for i in range(5)]
bets_player2 = [Attribute('player2_try{}'.format(i), str) for i in range(5)]


def game_winner(player1, player2, scoreboard):
    """
    Determine the winner of the game

    :param player1: 'rock', 'paper' or 'scissors'
    :param player2: 'rock', 'paper' or 'scissors'
    :param scoreboard: Scoreboard dictionary
    :return: True if player1 wins, False if player2 wins
    """
    if player1 == 'rock':
        if player2 == 'scissors':
            scoreboard['player1'] += 1
        if player2 == 'paper':
            scoreboard['player2'] += 1

    if player1 == 'paper':
        if player2 == 'rock':
            scoreboard['player1'] += 1
        if player2 == 'scissors':
            scoreboard['player2'] += 1

    if player1 == 'scissors':
        if player2 == 'paper':
            scoreboard['player1'] += 1
        if player2 == 'rock':
            scoreboard['player2'] += 1

    return scoreboard


@node
def firstgame(player1, player2):
    scoreboard = defaultdict(int)
    return game_winner(player1, player2, scoreboard)


@node
def game(player1, player2, scoreboard):
    return game_winner(player1, player2, scoreboard)

@node
def winner(message):
    print(message)
    return True

def select_winner(*scoreboards):
    message = None
    
    for scoreboard in scoreboards:
        if scoreboard is not None:
            if scoreboard['player1'] == 3:
                message = 'Player1 is the winner'

            elif scoreboard['player2'] == 3:
                message = 'Player2 is the winner'

    return message


scoreboard1 = firstgame(bets_player1[0], bets_player2[0])
scoreboard2 = game(bets_player1[1], bets_player2[1], scoreboard1)
scoreboard3 = game(bets_player1[2], bets_player2[2], scoreboard2)
scoreboard4 = game(bets_player1[3], bets_player2[3], scoreboard3)
scoreboard5 = game(bets_player1[4], bets_player2[4], scoreboard4)
got_winner = gather(scoreboard3, scoreboard4, scoreboard5, condition=select_winner)
notify_winner = winner(got_winner)

contract = Contract(winner)
print(contract.graph)

contract.set('player1_try0', 'rock')
contract.set('player2_try0', 'paper')
contract.set('player1_try1', 'rock')
contract.set('player2_try1', 'paper')
contract.set('player1_try2', 'rock')
contract.set('player2_try2', 'scissors')
contract.set('player1_try3', 'rock')
contract.set('player2_try3', 'paper')

contract.visualize()
