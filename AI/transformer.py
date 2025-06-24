# The transformer is a liason between the NN and the Game class
# it takes the output of the NN and interprets it for the Game,
# and takes the game state and condenses it into a digestible form
# for the NN

# This is where a lot of the modification is going to have to be between matchups

#TODO, get this from constants file
MAX_HAND_SIZE = 9
MAX_BOARD_SIZE = 5

import torch
from torch.masked import masked_tensor
from torch import nn
import numpy as np
from allmoves import ALLMOVES
from bot import onodes

def int_to_bits(x, bits=None, dtype=torch.int8):
    assert not(x.is_floating_point() or x.is_complex()), "x isn't an integer type"
    if bits is None: bits = x.element_size()
    mask = 2**torch.arange(bits-1,-1,-1).to(x.device, x.dtype)
    return x.unsqueeze(-1).bitwise_and(mask).ne(0).to(dtype=dtype)

#a = torch.tensor([[20,20,8,8],[3,4,8,3],[16,pow(2,4)+3,0,0]])
#print(int_to_bits(a, bits=5, dtype=torch.float))

class Transformer:
    def __init__(self):
        return

    # Current stack, see input.txt for details
    
    # From the game state, create an input to the NN
    def gameDataToNN(self, gameState):

        # TODO: maybe make this less bad
        if (gameState.activePlayer.playerNum == 1):
            currPlayer = gameState.player1
            enemyPlayer = gameState.player2
            allyBoard = gameState.board.fullBoard[0]
            enemyBoard = gameState.board.fullBoard[1]
        else:
            #NOTE: we are setting allyboard to p1 board now that we are transitioning to the oracle idea,
            #      so that the AI has a coherent idea of how passing effects the board
            currPlayer = gameState.player2
            enemyPlayer = gameState.player1
            allyBoard = gameState.board.fullBoard[0]
            enemyBoard = gameState.board.fullBoard[1]

        generatedData = []

        # Layer 1, basic data
        currLayer = []
        currLayer.append(currPlayer.currHP)
        currLayer.append(enemyPlayer.currHP)
        currLayer.append(currPlayer.currPP)
        currLayer.append(currPlayer.maxPP)
        currLayer.append(enemyPlayer.maxPP)
        #currLayer.append(0) #turn number, implement later
        currLayer.append(currPlayer.canEvolve)
        currLayer.append(len(enemyPlayer.hand))
        generatedData.append(currLayer)

        # Layer 2, basic data
        currLayer = []
        currLayer.append(currPlayer.selfPings)
        currLayer.append(enemyPlayer.selfPings)
        currLayer.append(currPlayer.selfPingsTurn)
        currLayer.append(len(currPlayer.leaderEffects.turnStartEffects))
        currLayer.append(len(enemyPlayer.leaderEffects.turnStartEffects))
        currLayer.append(currPlayer.currEvos)
        currLayer.append(enemyPlayer.currEvos)
        generatedData.append(currLayer)

        # Layer 3, basic data
        currLayer = []
        currLayer.append(len(currPlayer.deck.cards))
        currLayer.append(len(enemyPlayer.deck.cards))
        currLayer.append(0)
        currLayer.append(0)
        currLayer.append(0)
        currLayer.append(0)
        currLayer.append(0)
        generatedData.append(currLayer)

        # Layers 4-12, hand contents
        for loopIndex in range(MAX_HAND_SIZE):
            currLayer = [0,0,0,0,0,0,0]
            if loopIndex < len(currPlayer.hand):
                currLayer[currPlayer.hand[loopIndex].encoding // 7] = pow(2, (currPlayer.hand[loopIndex].encoding % 7))
            generatedData.append(currLayer)
        
        # Layers 13-16, in-hand P1 contents:
        currLayer = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
        for loopIndex in range(len(gameState.player1.hand)):
            #This is where we need a random variable for when P2 plays
            currLayer[gameState.player1.hand[loopIndex].encoding // 7][gameState.player1.hand[loopIndex].encoding % 7] += 1
        generatedData += currLayer

        # Layer 17-20, in-hand P2 contents:
        currLayer = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
        for loopIndex in range(len(gameState.player2.hand)):
            #This is where we need a random variable for when P1 plays
            currLayer[gameState.player2.hand[loopIndex].encoding // 7][gameState.player2.hand[loopIndex].encoding % 7] += 1
        generatedData += currLayer

        # Layer 21-40, the next 10 cards in each deck
        for loopIndex in range(10):
            currLayer = [0,0,0,0,0,0,0]
            if (len(gameState.player1.deck.cards) > loopIndex):
                nextCard = gameState.player1.deck.cards[len(gameState.player1.deck.cards) - 1 - loopIndex]
                currLayer[nextCard.encoding // 7] += pow(2,nextCard.encoding % 7)
            generatedData.append(currLayer)
        
        for loopIndex in range(10):
            currLayer = [0,0,0,0,0,0,0]
            if (len(gameState.player2.deck.cards) > loopIndex):
                nextCard = gameState.player2.deck.cards[len(gameState.player2.deck.cards) - 1 - loopIndex]
                currLayer[nextCard.encoding // 7] += pow(2,nextCard.encoding % 7)
            generatedData.append(currLayer)

        # Layers 41-48, played contents, note that this is always in order P1 then P2, not active player, inactive player
        # TODO: this can be done a LOT better
        for i in range(4):
            currLayer = [0,0,0,0,0,0,0]
            for loopIndex in range(len(currLayer)):
                currLayer[loopIndex] = pow(2,gameState.p1played[i*len(currLayer) + loopIndex])
            generatedData.append(currLayer)
        
        for i in range(4):
            currLayer = [0,0,0,0,0,0,0]
            for loopIndex in range(len(currLayer)):
                currLayer[loopIndex] = pow(2,gameState.p2played[i*len(currLayer) + loopIndex])
            generatedData.append(currLayer)    
  
        # Layers 49-58, board contents
        for loopIndex in range(MAX_BOARD_SIZE):
            currLayer = [0,0,0,0,0,0,0]
            if loopIndex < len(allyBoard):
                currMon = allyBoard[loopIndex]
                currMonEncIndex = currMon.encoding // 7
                currLayer[currMonEncIndex] = pow(2, (currMon.encoding % 7))
                if (not currMon.isAmulet):
                    currLayer[4] = currMon.currAttack
                    currLayer[5] = currMon.currHP
                    currLayer[6] = 8*currMon.canAttackFace + 4*currMon.isEvolved + 2*currMon.hasWard + currMon.canAttack
                    currLayer[6] += 32*currMon.hasBane + 16*currMon.hasDrain
                else:
                    currLayer[5] = 32*currMon.countdown
            generatedData.append(currLayer)
        
        for loopIndex in range(MAX_BOARD_SIZE):
            currLayer = [0,0,0,0,0,0,0]
            if loopIndex < len(enemyBoard):
                currMon = enemyBoard[loopIndex]
                currMonEncIndex = currMon.encoding // 7
                currLayer[currMonEncIndex] = pow(2, (currMon.encoding % 7))
                if (not currMon.isAmulet):
                    currLayer[4] = currMon.currAttack
                    currLayer[5] = currMon.currHP
                    currLayer[6] = 8*currMon.canAttackFace + 4*currMon.isEvolved + 2*currMon.hasWard + currMon.canAttack
                    currLayer[6] += 32*currMon.hasBane + 16*currMon.hasDrain
                else:
                    currLayer[5] = 32*currMon.countdown
            generatedData.append(currLayer)

        # Layer 59, player turn
        if currPlayer.playerNum == 1:
            currLayer = [127,127,127,127,127,127,127]
        else:
            currLayer = [0,0,0,0,0,0,0]
        generatedData.append(currLayer)
       
        #return generatedData
        return int_to_bits(torch.tensor(generatedData), bits=7, dtype=torch.float32)

    # The NN output is defined by 46 outputs, 45 being move probabilities and the last being the valuation.
    # first 9: play associated card
    # then next 30: attack
    # then next 30: evolve
    # then last 1: pass
    # We need to determine which moves are legal, and normalize the probabilities of the legal moves
    # Plan: get the game to generate all legal moves, create a binary tensor representing legal/illegal, element-wise product
    #       with NNoutput tensor, then normalize
    def normalizedVector(self, NNoutput, gameState):
        legalBinaryMask = torch.zeros(onodes-1, dtype=bool)
        legalMoves = gameState.generateLegalMoves()
        for move in legalMoves:
            if move[0] == 4:
                #V2
                legalBinaryMask[onodes-2] = False
                #legalBinaryMask[onodes-2] = True
            if move[0] == 1:
                if (len(move[1]) == 1):
                    legalBinaryMask[7*move[1][0]] = True
                else:
                    legalBinaryMask[7*move[1][0] + move[1][1] + 2] = True
            elif move[0] == 2:
                legalBinaryMask[64 + 6*move[1][0] + move[1][1]] = True
            elif move[0] == 3:
                if (len(move[1]) == 1):                    
                    legalBinaryMask[93 + 7*move[1][0]] = True
                else:
                    legalBinaryMask[93 + 7*move[1][0] + move[1][1] + 2] = True

        # crummy hack for shuffling the data being recorded
        if (isinstance(NNoutput,torch.Tensor)):
            legalMasked = NNoutput[legalBinaryMask]
            legalMoveProbs = nn.Softmax(dim=0)(legalMasked)
        else:
            legalMoveProbs = 0
        #print(legalMoveProbs)
        #binaryTensor = torch.Tensor(legalBinaryArray)
        #legalMoveProbs = legalBinaryArray * NNoutput
        
        #totalWeight = 0
        #for ele in legalMoveProbs:
        #    totalWeight += ele
        #for ind in range(len(legalMoveProbs)):
        #    legalMoveProbs[ind] /= totalWeight
        return legalMoveProbs, legalBinaryMask

