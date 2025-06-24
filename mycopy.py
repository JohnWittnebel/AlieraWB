# this is replace deepcopy of a game, which is a very computationally expensive task
from game import Game
from player import Player
from deck import Deck
from card import Card
from board import Board
import copy

def trueCopy(iGame):
    # generate a new game
    retVal = Game(0)

    retVal.player1 = playerCopy(iGame.player1)
    retVal.player2 = playerCopy(iGame.player2)
    if iGame.activePlayer == iGame.player1:
        retVal.activePlayer = retVal.player1
    else:
        retVal.activePlayer = retVal.player2
    
    retVal.gameBoard = boardCopy(iGame.board)
    retVal.currTurn = iGame.currTurn
    retVal.winner = iGame.winner
    #retVal.update(player1copy, player2copy, activePlayer, gameBoard, currTurn, winner)
    return retVal


def boardCopy(iBoard):
    gameBoard = Board()
    for item in iBoard.fullBoard[0]:
        gameBoard.player1side.append(cardCopy(item))
    for item in iBoard.fullBoard[1]:
        gameBoard.player2side.append(cardCopy(item))
    gameBoard.fullBoard = [gameBoard.player1side, gameBoard.player2side]
    return gameBoard

def playerCopy(iPlayer):
    newDeck = deckCopy(iPlayer.deck)
    newPlayerMaxEvos = iPlayer.maxEvos
    newPlayerCurrEvos = iPlayer.currEvos
    newPlayerPlayerNum = iPlayer.playerNum

    newPlayer = Player(newDeck, newPlayerMaxEvos, newPlayerCurrEvos, newPlayerPlayerNum)
    newPlayer.hand = handCopy(iPlayer.hand)
    # TODO, this wont actually work once effects are implemeneted
    newPlayer.effects = iPlayer.effects
    newPlayer.currHP = iPlayer.currHP
    newPlayer.maxHP = iPlayer.maxHP
    newPlayer.currPP = iPlayer.currPP
    newPlayer.maxPP = iPlayer.maxPP
    newPlayer.canEvolve = iPlayer.canEvolve
    return newPlayer

def handCopy(iHand):
    retHand = []
    for item in iHand:
        retHand.append(cardCopy(item))
    return retHand

def deckCopy(iDeck):
    cards = []
    for item in iDeck.cards:
        cards.append(cardCopy(item))
    return Deck(cards)

def cardCopy(iCard):
    return copy.deepcopy(iCard)
