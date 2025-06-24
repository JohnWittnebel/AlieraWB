# This class will determine what action to take, and keep track of winrates/games

# Each node has a gamestate, number of games ran, and winrate from that node

from allmoves import ALLMOVES
from multiset import FrozenMultiset as fms
import random
import copy
import math
import pickle
import torch
import os
from transformer import Transformer
from bot import NeuralNetwork
from mycopy import trueCopy
import _pickle as cPickle

import sys
#sys.path.insert(0, './botModels/')
sys.path.insert(0, './..')
from amulet import Amulet

def setCurrNN(mct, currOrNew = "curr"):
    mct.currNN = NeuralNetwork()
    if (currOrNew == "new"):
        dire = "./AI/botModels/nextbot.bot"
    else:
        dire = "./AI/botModels/currbot.bot"
    temp1 = torch.load(dire, map_location=torch.device('cpu'))
    mct.currNN.load_state_dict(temp1)
    mct.currNN.eval()

def moveCmp(item):
    #print(item)
    if (item[0][0] == 4):
        return 100000
    val1 = 100*item[0][0]
    val1 += 10*item[0][1][0]
    if (len(item[0][1]) > 1):
        val1 += (item[0][1][1] + 2)
    return val1

class AZMCTS():
    def __init__(self, gameState, head=None):
        self.gameState = gameState
        self.moveArr = []
        self.totalSims = 0
        self.exploreParam = 1.4
        self.head = head
        self.mask = 0
        self.currNN = 0
        self.transformer = 0
        self.val = 0
        self.truePath = 0
        self.hashtable = {}
        moves = gameState.generateLegalMoves()

        self.children = []

        rollIndex = 0
        # each element of moveArr is [move, childIndex, timesTaken, totalValue, meanValue, moveProb (according to NN),
        #                             move indices (for training)]
        for ele in moves:
            #FOR V2
            if ele[0] == 4:
                self.moveArr.append([ele,rollIndex, 0, 0., 0., 1/max(1,len(moves)-1)])
            else:
                self.moveArr.append([ele, rollIndex, 0, 0., 0., 0.])
            self.children.append(0)
            rollIndex += 1
    
    # the moveProbs are generated when the node is created during tree descent, but this doesnt occur for the root
    # so we do it manually here
    def rootInit(self, hashtable, new = "curr"):
        self.transformer = Transformer()
        nnInput = self.transformer.gameDataToNN(self.gameState)
        nnInput = nnInput.unsqueeze(dim=0)

        setCurrNN(self, new)
        logits = self.currNN(nnInput)[0]
        val = self.currNN(nnInput)[1]
        self.val = val
        self.head = self
        self.hashtable = hashtable
        self.truePath = 1
        #for ele in self.moveArr:
        #    ele[4] += val/4
        #print(logits)

        probabilitiesNN, mask = self.transformer.normalizedVector(logits[0], self.gameState)

        #print(mask)
        self.mask = mask
        self.setProbabilities(probabilitiesNN)

        return val

    def runSimulations(self, simulations):        
        for _ in range(simulations):
            self.descendTree()
        #self.shuffleHandBoard()

    def descendTree(self):
        self.totalSims += 1

        # dont need to select action if game is over
        if self.gameState.winner != 0:
            if self.gameState.winner == self.gameState.activePlayer.playerNum:
                return 1
            else:
                return -1
        actionIndex = self.selectAction()
        #input(self.printTree())
        updateValue = self.takeAction(actionIndex, self.moveArr[actionIndex][1])
        # if the previous action was a pass, then we invert the valuation
        if self.moveArr[actionIndex][0][0] == 4:
            updateValue = -1 * updateValue

        # update the action info
        self.moveArr[actionIndex][2] += 1
        self.moveArr[actionIndex][3] += updateValue
        self.moveArr[actionIndex][4] = self.moveArr[actionIndex][3] / self.moveArr[actionIndex][2]
        return updateValue

    def selectAction(self):
        if (len(self.moveArr) == 1): #or (self.totalSims == 0):
            return 0
        currMaxIndex = 0
        currMax = -1
        currActionIndex = 0
        for ele in self.moveArr:
            currVal = ele[4] + (self.exploreParam * ele[5] * (math.sqrt(float(self.totalSims)) / (1 + float(ele[2]))))
            if currMax < currVal:
                currMax = currVal
                currMaxIndex = currActionIndex
            currActionIndex += 1
            #input("")
        return currMaxIndex

    def takeAction(self, actionIndex, childIndex):
        # We are at a leaf node, time to create a new leaf then climb, unless we are already at a game end state
        if self.gameState.winner != 0:
            if self.gameState.winner == self.gameState.activePlayer.playerNum:
                return 1
            else:
                return -1

        if (self.children[childIndex] == 0):
            #z = cPickle.loads(cPickle.dumps(self.gameState, -1))
            z = copy.deepcopy(self.gameState)
            z.initiateAction(self.moveArr[actionIndex][0])
            z.clearQueue()
            z.sortGame()
            gameStateVal = createGameStateVal(z)
            hashval = hash(gameStateVal)
            if hashval in self.hashtable:
                if z.winner != 0:
                    if z.winner == z.activePlayer.playerNum:
                        return 1
                    else:
                        return -1
                #print("PEPEGA")
                self.children[childIndex] = self.hashtable[hashval]
                #TODO: the below line is for debugging purposes. The bug atm is that even though we end up in symmetric
                #      positions, our hand order (and thus legal moves that generated at the time of creation of AZMCTS)
                #      may not be the same. Consider playing maestro -> vampy or vampy -> maestro for ex.
                #self.children[childIndex].gameState = z
                #print("PEPEGA")
                #self.hashtable[hashval].printTree()
                return self.hashtable[hashval].descendTree()
                
            newAZMCTS = AZMCTS(z, self.head)
            self.children[childIndex] = newAZMCTS
            self.children[childIndex].hashtable = self.hashtable
            self.children[childIndex].currNN = self.currNN
            self.children[childIndex].transformer = self.transformer
            #self.children[childIndex].gameState.printGameState()
  
            # game has ended
            if self.children[childIndex].gameState.winner != 0:
                if self.children[childIndex].gameState.winner == self.children[childIndex].gameState.activePlayer.playerNum:
                    return 1
                else:
                    return -1
            # game is still in progress, return NN eval
            nnInput = self.transformer.gameDataToNN(self.gameState)
            nnInput = nnInput.unsqueeze(dim=0)
            self.hashtable[hashval] = newAZMCTS 
        
            logits = self.currNN(nnInput)
            logitsProb = logits[0][0]
            logitsValuation = logits[1][0]
            #for ele in self.children[childIndex].moveArr:
            #    ele[4] += logitsValuation/4

            probabilitiesNN, mask = self.transformer.normalizedVector(logitsProb, self.children[childIndex].gameState)
            self.children[childIndex].mask = mask
            self.children[childIndex].setProbabilities(probabilitiesNN)
            self.val = logitsValuation
            return logitsValuation

        return self.children[actionIndex].descendTree()
      
    def printTree(self):
        for ele in self.moveArr:
            bonusExploreParam = self.exploreParam * 0.01 * math.sqrt(1+float(self.totalSims)) / (1+float(ele[2]))
            currVal = ele[4] + (self.exploreParam * ele[5] * (math.sqrt(1 + float(self.totalSims)) / (1 + float(ele[2]))))
            currVal += bonusExploreParam
            print(ele)
            print(currVal)
            print(self.totalSims)

    def setProbabilities(self, probabilities):
        #this happens in V2 when pass action is the only action
        #if (len(probabilities) == 0):
        #    return
        currIndex = 0
        for ele in self.moveArr:
            if (ele[0] == [4]):
                continue
            ele[5] = probabilities[currIndex]
            currIndex += 1
        #moveInd = 0
        #allMoveInd = 0
        #while (moveInd < len(self.moveArr)):
        #    if ALLMOVES[allMoveInd] == self.moveArr[moveInd][0]:
        #        self.moveArr[moveInd][5] = probabilities[allMoveInd]
        #        moveInd += 1
        #    allMoveInd += 1

        if (self.moveArr[len(self.moveArr) - 1] == 0):
            print("ERROR")
            self.printTree()
            input(probabilities)

    def recordResults(self, result, posnum):
        self.gameState.clearQueue()
        for _ in range(10):
            self.shuffleHandBoard()

            _, mask = self.transformer.normalizedVector(0, self.gameState)
            MCTSRes = []
            for ele in self.moveArr:
                # commented out for V2
                # MCTSRes.append(float(ele[2]) / max(1., float(self.totalSims)))
                MCTSRes.append(float(ele[2]) / max(1., float(self.totalSims - self.moveArr[len(self.moveArr)-1][2])))

            if (result == self.gameState.activePlayer.playerNum):
                gameResult = 1
            else:
                gameResult = -1
            condensedResult = [self.transformer.gameDataToNN(self.gameState), MCTSRes, self.mask, gameResult]
            currDir = len(os.listdir("./AI/trainingData")) - 1

            with open("./AI/trainingData/trainingDataSubfolder" + str(currDir) + "/pos" + str(posnum) + ".pickle", "wb") as f:
                pickle.dump(condensedResult, f)
            posnum += 1
        
        for child in self.children:
            if child != None and isinstance(child,AZMCTS) and child.truePath == 1 and child.gameState.winner == 0:
                return child.recordResults(result, posnum)

    # shuffles hand and board positions to eliminate biases, changes mask and mcts array accordingly
    def shuffleHandBoard(self):
        handShuffle = list(range(len(self.gameState.activePlayer.hand)))
        random.shuffle(handShuffle)
        boardShuffle1 = list(range(len(self.gameState.board.fullBoard[0])))
        boardShuffle2 = list(range(len(self.gameState.board.fullBoard[1])))
        random.shuffle(boardShuffle1)
        random.shuffle(boardShuffle2)

        for action in self.moveArr:
            if (action[0][0] == 1):
                if (len(handShuffle) <= action[0][1][0]):
                    print(handShuffle)
                    print(action)
                    print(":)")
                    continue
                action[0][1][0] = handShuffle[action[0][1][0]]
            if (action[0][0] == 2) or (action[0][0] == 3):
                if (self.gameState.activePlayer.playerNum == 1):
                    action[0][1][0] = boardShuffle1[action[0][1][0]]
                else:
                    action[0][1][0] = boardShuffle2[action[0][1][0]]

        newHand = []
        for handIndex in range(len(self.gameState.activePlayer.hand)):
            for i in range(len(self.gameState.activePlayer.hand)):
                if (handShuffle[i] == handIndex):
                    newHand.append(self.gameState.activePlayer.hand[i])

        newBoardp1 = []
        for boardIndex in range(len(self.gameState.board.fullBoard[0])):
            for i in range(len(self.gameState.board.fullBoard[0])):
                if (boardShuffle1[i] == boardIndex):
                    newBoardp1.append(self.gameState.board.fullBoard[0][i])
        
        newBoardp2 = []
        for boardIndex in range(len(self.gameState.board.fullBoard[1])):
            for i in range(len(self.gameState.board.fullBoard[1])):
                if (boardShuffle2[i] == boardIndex):
                    newBoardp2.append(self.gameState.board.fullBoard[1][i])
        
        self.gameState.board.player1side = newBoardp1
        self.gameState.board.player2side = newBoardp2
        self.gameState.board.updateFullBoard()
        self.gameState.activePlayer.hand = newHand
        self.moveArr.sort(key=moveCmp)

    def cleanTreeExceptAction(self, action):
        for move in self.moveArr:
            if move[0] != action:
                if (self.children[move[1]] != 0):
                    self.children[move[1]].cleanTree()
                    self.children[move[1]] = None

    def cleanTree(self):
        for child in self.children:
            if child != 0:
                child.cleanTree()
                child = None

def createGameStateVal(gameState):
    board1 = []
    board2 = []
    currPlayer = gameState.activePlayer
    if (currPlayer.playerNum == 1):
        enemyPlayer = gameState.player2
    else:
        enemyPlayer = gameState.player1
    for ele in gameState.board.fullBoard[0]:
        if (isinstance(ele, Amulet)):
            board1.append((ele.encoding, ele.countdown))
        else:
            board1.append((ele.encoding, ele.currHP, ele.currAttack, ele.hasBane, ele.canAttack, ele.hasWard))
    for ele in gameState.board.fullBoard[1]:
        if (isinstance(ele,Amulet)):
            board2.append((ele.encoding, ele.countdown))
        else:
            board2.append((ele.encoding, ele.currHP, ele.currAttack, ele.hasBane, ele.canAttack, ele.hasWard))

    activedeck = []
    for ele in gameState.activePlayer.deck.cards:
        activedeck.append(ele.encoding)
    for ele in enemyPlayer.deck.cards:
        activedeck.append(ele.encoding)
    index = 0
    for ele in gameState.activePlayer.hand:
        activedeck.append((ele.encoding, index))
        index += 1
    index = 0
    for ele in enemyPlayer.hand:
        activedeck.append((ele.encoding, index))
        index += 1



    board1 = fms(board1)
    board2 = fms(board2)
    activedeck = tuple(activedeck)

    return (currPlayer.currHP, enemyPlayer.currHP, len(currPlayer.hand), len(enemyPlayer.hand), enemyPlayer.currEvos, currPlayer.currEvos, currPlayer.currPP, board1, board2, 3*gameState.currTurn+currPlayer.playerNum, activedeck, len(currPlayer.leaderEffects.turnEndEffects), len(enemyPlayer.leaderEffects.turnEndEffects))
