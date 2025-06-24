from monster import Monster
from deck import Deck
from game import Game
import math
import time
import shutil
import random
import numpy as np
import pickle
import copy
import torch
import cProfile
import os
from deckGen import newDeckPool
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool, TimeoutError, Lock, Process

import fnmatch
import sys
sys.path.insert(0, './AI/')
sys.path.insert(0, './cardArchive')
from transformer import Transformer
from bot import NeuralNetwork
from allmoves import ALLMOVES
from AZMCTS import AZMCTS
from AZMCTS import setCurrNN
from trainer import training
from AZMCTS import createGameStateVal

def singleGame(botGame, currPosSave = 0):
  x = Game()
  y = Transformer()
  x.player1.deck.trueShuffle()
  x.player2.deck.trueShuffle()
  x.gameStart()
  hashtable = {}

  x.gameNum = botGame[1]
  botGame = botGame[0]
  
  # mulligan phase
  if botGame == 0:
      index = 0
      for item in x.player1.hand:
          print(str(index) + ": " + str(item))
          index += 1
      mull1 = int(input("mulligan card 0? "))
      mull2 = int(input("mulligan card 1? "))
      mull3 = int(input("mulligan card 2? "))
      x.player1.mulligan(mull1,mull2,mull3)
      
      index = 0
      for item in x.player2.hand:
          print(str(index) + ": " + str(item))
          index += 1
      mull1 = int(input("mulligan card 0? "))
      mull2 = int(input("mulligan card 1? "))
      mull3 = int(input("mulligan card 2? "))
      x.player2.mulligan(mull1,mull2,mull3)
  else:
      totals = [[[0,0],[0,0]],[[0,0],[0,0]]]
      currMax = 0
      currMaxIndices = [0,0,0]
      for _ in range(10):
          for i in range(2):
              for j in range(2):
                  for k in range(2):

                      mull = x.player1.mulliganSample(i,j,k)
                      myTree = AZMCTS(x)
                      val = myTree.rootInit(hashtable)
                      totals[i][j][k] += val

                      if totals[i][j][k] > currMax:
                          currMax = totals[i][j][k]
                          currMaxIndices = [i,j,k]

                      x.player1.returnMulliganSample(mull)

      x.player1.mulligan(currMaxIndices[0], currMaxIndices[1], currMaxIndices[2])
      x.activePlayer = x.player2
      totals = [[[0,0],[0,0]],[[0,0],[0,0]]]
      currMax = 0
      currMaxIndices = [0,0,0]
      for _ in range(10):
          for i in range(2):
              for j in range(2):
                  for k in range(2):
                      mull = x.player2.mulliganSample(i,j,k)
                      myTree = AZMCTS(x)
                      #with lock:
                      val = myTree.rootInit(hashtable)
                      totals[i][j][k] += val
                      if totals[i][j][k] > currMax:
                          currMax = totals[i][j][k]
                          currMaxIndices = [i,j,k]
                      x.player2.returnMulliganSample(mull)
      x.player2.mulligan(currMaxIndices[0], currMaxIndices[1], currMaxIndices[2])
      x.activePlayer = x.player1
  

  # Turn 1 start
  x.startTurn()

  if (botGame == 1):
    botTurn = 1
  else:
    botTurn = 0

  x.sortGame()
  myTree = AZMCTS(x)
  
  ######
  #myTree.rootInit(hashtable)
  ######
  while (x.winner == 0):
    if (x.queue != []):
        x.clearQueue()

    x.queue = []
    x.printGameState()
    
    print("Input action:")
    print("1 = play card")
    print("2 = attack")
    print("3 = evolve")
    print("4 = end turn")

    if (botGame == 1):
        treehash = hash(createGameStateVal(myTree.gameState))
        currhash = hash(createGameStateVal(x))

        myTree.runSimulations(max(50, math.floor(math.log2(math.log2(len(myTree.moveArr)) + 0.01)*50)))
        myTree.printTree()
        if (treehash != currhash):
            print("ERROR: out of sync, aborting game")
            #print("OUT OF SYNC, PRINTING GAME STATE AND TREE GAME STATE:")
            #x.printGameState()
            #print(createGameStateVal(x))
            #myTree.gameState.printGameState()
            #print(createGameStateVal(myTree.gameState))
            x.error = 1
            break
            #raise Exception("AZMCTS out of sync with current game")

        
        multinomArr = []
        childArr = []
        for ele in myTree.moveArr:
            multinomArr.append(ele[2] / myTree.totalSims)
            childArr.append(ele[0])

        selectedMoveArr = np.random.multinomial(1, multinomArr)
        index = 0
        for ele in selectedMoveArr:
            if ele == 1:
                bestMove = childArr[index]
                break
            index += 1
        if (bestMove == [4] and botGame == 0):
            botTurn = 0

        bestChild = myTree.children[index]
        #myTree.cleanTreeExceptAction(bestMove)
        if not isinstance(bestChild, int):
            myTree = bestChild
            myTree.truePath = 1
        x.initiateAction(bestMove)
        x.clearQueue()
        x.sortGame()
    
    elif (botTurn == 1):
        model1 = NeuralNetwork().to("cpu")
        model1.load_state_dict(torch.load("./AI/botModels/currbot.bot"))
        myTree = AZMCTS(x)
        x.printGameState()
    
        moves = x.generateLegalMoves()

        myTree.rootInit(hashtable,"curr")
        
        myTree.runSimulations(max(50, math.floor(math.log2(math.log2(len(myTree.moveArr)) + 0.01)*50)))
        currIndex = 0
        maxIndex = 0
        maxSims = 0
        for i in range(len(moves)):
            if maxSims < myTree.moveArr[i][2]:
                maxIndex = currIndex
                maxSims = myTree.moveArr[i][2]
            currIndex += 1

        x.initiateAction(moves[maxIndex])

        if (moves[maxIndex] == [4]):
            botTurn = 0

    else:
        #mytest = model(torch.flatten(inputArr))
        #mytest = y.normalizedVector(mytest[0], x)
        #mymax = 0
        #maxIndex = 0
        #for currIndex in range(len(mytest)):
        #    if mytest[currIndex] > mymax:
        #        maxIndex = currIndex
        #        mymax = mytest[currIndex]
        #    currIndex += 1
        #print(mytest)
        #print(ALLMOVES[maxIndex])
        print(x.generateLegalMoves())
        uinput1 = input("")

        if (uinput1 == "1"):
            print("input card:")
            uinput2 = input("")
            uinput3 = input("target?\n")
            if (len(uinput2) > 0):
                uinput2 = int(uinput2)
                if (len(uinput3) > 0):
                    uinput3 = int(uinput3)
                    x.initiateAction([int(uinput1),[uinput2, uinput3]])
                else:
                    x.initiateAction([int(uinput1),[uinput2]])
        if (uinput1 == "2"):
            print("Select attacker:")
            uinput2 = input("")
            print("Select defender:")
            uinput3 = input("")
            if (len(uinput2) > 0) and (len(uinput3) > 0):
                x.initiateAttack(int(uinput2), int(uinput3))
        if (uinput1 == "3"):
            print("Select target")
            uinput2 = input("")
            uinput3 = input("target:\n")
            if (len(uinput2) > 0):
                if (len(uinput3) > 0):
                    x.initiateAction([int(uinput1), [int(uinput2), int(uinput3)]])
                else:
                    x.initiateAction([int(uinput1), [int(uinput2)]])
        if (uinput1 == "4"):
            print("Select target")
            uinput2 = input("")
            uinput3 = input("target:\n")
            if (len(uinput2) > 0):
                if (len(uinput3) > 0):
                    x.initiateAction([int(uinput1), [int(uinput2), int(uinput3)]])
                else:
                    x.initiateAction([int(uinput1), [int(uinput2)]])
        if (uinput1 == "5"):
            x.endTurn()
            #botTurn = 1
            continue
        if (uinput1 == "d"):
            myTree = AZMCTS(x)
            myTree.rootInit(hashtable)
            myTree.runSimulations(50)
            myTree.printTree()
            print(myTree.val)
            del(myTree)
            #input("")
        if (uinput1 == "6"):
            model1 = NeuralNetwork().to("cpu")
            model1.load_state_dict(torch.load("./AI/botModels/currbot.bot"))
            model1.eval()

            pos = y.gameDataToNN(x)
            pos = pos.unsqueeze(dim=0)
            _, valuation = model1(pos)
            print(valuation)
            z = copy.deepcopy(x)
            z.endTurn()
            while (z.activePlayer.playerNum != x.activePlayer.playerNum):
                newpos = y.gameDataToNN(z)
                newpos = newpos.unsqueeze(dim=0)
                distrib, val = model1(newpos)
                currMax = 0
                maxIndex = 0
                currIndex = 0
                for ele in distrib:
                    if ele[5] > currMax:
                        currMax = ele[5]
                        maxIndex = currIndex
                moves = z.generateLegalMoves()
                z.initiateAction(moves[maxIndex])
            newpos = y.gameDataToNN(z)
            newpos = newpos.unsqueeze(dim=0)
            distrib, val = model1(newpos)
            print(val)
            
            worstVal = 1.
            for _ in range(100):
                z = copy.deepcopy(x)
                z.endTurn()
                z.miniRollout()
                newpos = y.gameDataToNN(z)
                newpos = newpos.unsqueeze(dim=0)
                _, val = model1(newpos)
                if val < worstVal:
                    worstVal = val
            print(worstVal)

        if (uinput1 == "7"):
            x.sortGame()

            #myTree = AZMCTS(x)
            #myTree.rootInit(hashtable)
            #myTree.runSimulations(50)
            #myTree.printTree()
            #myTree.shuffleHandBoard()
            #myTree.printTree()
        if (uinput1 == "8"):
            print("Rig RNG for card")
            uinput2 = input("select card: ")
            uinput3 = input("rigged RNG: ")
            if (len(uinput2) > 0) and (len(uinput3) > 0):
                x.activePlayer.hand[int(uinput2)].riggedVal = int(uinput3)
        if (uinput1 == "9"):
            input2 = input("cheat how many cards? ")
            if (len(input2) > 0):
                for i in range(int(input2)):
                    print("Card at position " + str(i) + ":")
                    deckIndex = 0
                    for card in x.activePlayer.deck.cards:
                        print(str(deckIndex) + ": " + str(card))
                        deckIndex += 1
                    cheatedCard = input("")
                    if (len(cheatedCard) > 0):
                        swap = x.activePlayer.hand[i]
                        x.activePlayer.hand[i] = x.activePlayer.deck.cards[int(cheatedCard)]
                        x.activePlayer.deck.cards[int(cheatedCard)] = swap
        if (uinput1 == "sb"):
            input2 = input("spellboost what card index?")
            input3 = input("spellboost how many times?")

  
  if x.error == 0 and botGame == 1:
      with lock:
          currDir = len(os.listdir("./AI/trainingData")) - 1
          currPosSave = len(fnmatch.filter(os.listdir("./AI/trainingData/trainingDataSubfolder" + str(currDir)),'*.pickle'))
          currPosSave = myTree.head.recordResults(x.winner, currPosSave)
  return currPosSave, x.winner
  #return x.winner


def botGenerationTest(deck1, deck2, newmodel, gameNum):  
    x = Game()
    x.player1.deck = deck1
    x.player2.deck = deck2
    x.gameNum = gameNum
    x.sortGame()
    x.gameStart()
    x.startTurn()
    y = Transformer()
    hashtable1 = {}
    hashtable2 = {}

    p1Tree = AZMCTS(x)
    p2Tree = AZMCTS(x)

    if (newmodel == 1):
        p1Tree.rootInit(hashtable1, "new")
        p2Tree.rootInit(hashtable2, "curr")
    else:
        p1Tree.rootInit(hashtable2, "curr")
        p2Tree.rootInit(hashtable1, "new")

    while (x.winner == 0):
        if (x.queue != []):
            x.clearQueue()

        x.printGameState()
    
        print("Input action:")
        print("1 = play card")
        print("2 = attack")
        print("3 = evolve")
        print("4 = end turn")

        pos = y.gameDataToNN(x)
        z = pos.unsqueeze(dim=0)
        moves = x.generateLegalMoves()

        if (x.activePlayer.playerNum == 1):
            activeTree = p1Tree
            p1Tree.runSimulations(max(50, math.floor(math.log2(math.log2(len(p1Tree.moveArr)) + 0.01)*50)))
        else:
            activeTree = p2Tree
            p2Tree.runSimulations(max(50, math.floor(math.log2(math.log2(len(p2Tree.moveArr)) + 0.01)*50)))
        
        activeTree.printTree()

        currIndex = 0
        maxIndex = 0
        maxSims = 0
        for i in range(len(moves)):
            if (len(activeTree.moveArr) <= i):
                activeTree.printTree()
                x.printGameState()
                raise Exception("something went wrong, out of sync?")
            if maxSims < activeTree.moveArr[i][2]:
                maxIndex = currIndex
                maxSims = activeTree.moveArr[i][2]
            currIndex += 1

        bestMove = moves[maxIndex]

        # this is just so that if the inactive tree hasnt visited the node we are going to, it becomes an AZMCTS node
        if (activeTree == p1Tree):
            p2Tree.takeAction(maxIndex, maxIndex)
        else:
            p1Tree.takeAction(maxIndex, maxIndex)
        
        bestChild1 = p1Tree.children[maxIndex]
        bestChild2 = p2Tree.children[maxIndex]

        if (hash(createGameStateVal(p1Tree.gameState)) != hash(createGameStateVal(p2Tree.gameState))):
            p1Tree.printTree()
            p2Tree.printTree()
            raise Exception("P1 and P2 tree out of sync")
        
        #p1Tree.cleanTreeExceptAction(bestMove)
        #p2Tree.cleanTreeExceptAction(bestMove)

        if not isinstance(bestChild1, int):
            p1Tree = bestChild1
            p2Tree = bestChild2

        x.initiateAction(bestMove)
        x.clearQueue()
        x.sortGame()

    return x.winner

def init(lock_: Lock):
    global lock
    lock = lock_
    
def botGenerationTestInit(simulationNum): 
    result = [0,0]
        
    seed_file = open("./constantDecks/P1deck" + str(simulationNum) + ".seed", "rb")
    deckSeed = pickle.load(seed_file)
    seed_file.close()
    deck1 = Deck("deck1")
    random.seed(deckSeed)
    deck1.trueShuffle()
        
    seed_file = open("./constantDecks/P2deck" + str(simulationNum) + ".seed", "rb")
    deckSeed = pickle.load(seed_file)
    seed_file.close()
    deck2 = Deck("deck2")
    random.seed(deckSeed)
    deck2.trueShuffle()

    winner = botGenerationTest(deck1, deck2, 1, simulationNum)
    if winner == 1:
        result[0] += 1
    else:
        result[1] += 1

    seed_file = open("./constantDecks/P1deck" + str(simulationNum) + ".seed", "rb")
    deckSeed = pickle.load(seed_file)
    seed_file.close()
    deck1 = Deck("deck1")
    random.seed(deckSeed)
    deck1.trueShuffle()
        
    seed_file = open("./constantDecks/P2deck" + str(simulationNum) + ".seed", "rb")
    deckSeed = pickle.load(seed_file)
    seed_file.close()
    deck2 = Deck("deck2")
    random.seed(deckSeed)
    deck2.trueShuffle()
        
    winner2 = botGenerationTest(deck1, deck2, 2, simulationNum)
    if winner2 == 1:
        result[1] += 1
    else:
        result[0] += 1
    if (winner != winner2):
        with lock:
            f = open("diffMakers.txt", "a")
            if (winner == 1):
                f.write("Game: " + str(simulationNum) + ", double winner = new bot\n")
            else:
                f.write("Game: " + str(simulationNum) + ", double winner = old bot\n")
            f.close()

    return result[0]
    
generation = len(fnmatch.filter(os.listdir("./AI/botModels/botArchive"), '*.bot')) - 1
lock_ = Lock()

#currPosSave=0
winner = singleGame([0,1])
#print(winner)
#input("")

oldbotwins = 0
newbotwins = 0
currPosSave = 0
numFails = 0
learningRate = 0.02

def testprint(inputval):
    print(inputval)


if __name__ == "__main__":
    #for _ in range(1):
    with Pool(initializer=init, initargs=[lock_], processes=2) as exe:
        for pepega in range(1):
            start_time = time.time()
            startingPoint = currPosSave            
            if (pepega > -1) and (sys.argv[1] != 'train') and (sys.argv[1] != 'verify'):
                runs = []
                # if we are doing a fresh run
                if (pepega == 0):
                    for j in range(int(sys.argv[1])):
                        runs.append([1,j])
                        #singleGame([1,j])
                exe.map(singleGame, runs)

            if (len(sys.argv) > 2):
                break
        
            if (sys.argv[1] == 'train'):
                training(learningRate)
                break

            generation += 1

            newDeckPool(4)
            tests = []
            for j in range(4):
                tests.append(j)
            
            results = exe.map(botGenerationTestInit, tests)
            
            newbotwins = 0
            for item in results:
                newbotwins += item
            
            f = open("resultFile.txt", "a")
            f.write(str(newbotwins) + " v " + str(30-newbotwins) + "\n")
            f.close()
            """
            if newbotwins >= 50 and newbotwins < 52:
                newDeckPool(50)
                result2 = exe.map(botGenerationTestInit, tests)
                for item in results2:
                    newbotwins += item
                f = open("resultFile.txt", "a")
                f.write(str(newbotwins) + " v " + str(100-newbotswins) + "\n")
                f.close()
                if (newbotwins < 102):
                    numFails += 1
                    os.remove("./AI/botModels/nextbot.bot")
                    generation -= 1
                else:
                    shutil.copy("./AI/botModels/nextbot.bot", "./AI/botModels/botArchive/gen" + str(generation) + ".bot")
                    shutil.move("./AI/botModels/nextbot.bot", "./AI/botModels/currbot.bot")
            elif newbotwins < 50:
                numFails += 1
                os.remove("./AI/botModels/nextbot.bot")
                generation -= 1
            else:
                shutil.copy("./AI/botModels/nextbot.bot", "./AI/botModels/botArchive/gen" + str(generation) + ".bot")
                shutil.move("./AI/botModels/nextbot.bot", "./AI/botModels/currbot.bot")
        
            print("--- %s seconds ---" % (time.time() - start_time))
            """
