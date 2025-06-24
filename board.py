from constants import MAX_BOARD_SIZE
from amulet import Amulet
import copy

# A Board has 2 sides, one for each player
# On a side there is an ordered array of cards
# the maximum number of cards on each side is 5

class Board:
  def __init__(self):
    self.player1side = []
    self.player2side = []
    self.maxSize = MAX_BOARD_SIZE
    self.fullBoard = [self.player1side, self.player2side]

  """
  def __deepcopy__(self, info):
    retVal = Board()
    retVal.player1side = copy.deepcopy(self.player1side)
    retVal.player2side = copy.deepcopy(self.player2side)
    retVal.fullBoard = [retVal.player1side, retVal.player2side]
    return retVal
  """

  def printBoard(self):
    playerSideString = ""
    count = 0

    # TODO: change this so that each monster/amulet has its own print function at some point
    for item in self.player2side:
      if isinstance(item,Amulet):
          playerSideString += item.name + "[" + str(item.countdown) + "], "
      else:
        if item.canAttack:
          attackStr = "[X]"
        else:
          attackStr = "[ ]"
        playerSideString += item.name + " (" + str(item.currAttack) + "/" + str(item.currHP) + ") " + attackStr + " [" + str(count) + "], " 
      count += 1
    print(playerSideString)
    playerSideString = ""
    count = 0
    for item in self.player1side:
      if isinstance(item,Amulet):
          playerSideString += item.name + "[" + str(item.countdown) + "], "
      else:
        if item.canAttack:
          attackStr = "[X]"
        else:
          attackStr = "[ ]"
        playerSideString += item.name + " (" + str(item.currAttack) + "/" + str(item.currHP) + ") " + attackStr + " [" + str(count) + "], "
      count += 1
    print(playerSideString)
 
  def updateFullBoard(self):
    self.fullBoard = [self.player1side, self.player2side]
