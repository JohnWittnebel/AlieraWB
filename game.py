import os
from board import Board
from player import Player
from spell import Spell
from monster import Monster
from amulet import Amulet
from constants import *
from deck import Deck
import copy
import random
import sys

# A Game is the primary class that controls the flow of the game
# It has 2 players, a board, and keeps track of who is the current player and the current turn
# It has a winner field that will change to 1 or 2 depending on the winner of the game
# the winString returns the reason for winning (deckout, hp reached 0, etc.)

# training variables
TRAINING = 1

class Game:
    def __init__(self):
        # If we are initializing a board state without players already generated,
        # we need to generate the players and the decks that they will be using

        deck1 = Deck("deck1")
        deck2 = Deck("deck2")
        self.p1played = []
        self.p2played = []
        for _ in range(28):
            self.p1played.append(0)
            self.p2played.append(0)

        self.player1 = Player(deck1, 1)
        self.player2 = Player(deck2, 2)

        self.deterministic = 1
        self.gameNum = -1
        self.board = Board()
        self.activePlayer = self.player1
        self.currTurn = 1
        self.winner = 0
        self.error = 0
        self.winString = ""
        self.queue = []
    """
    def __deepcopy__(self, memo):
        # somehow this actually needs to be here, otherwise things happen like deepcopying the board
        # before a follower is summoned by an effect and then it doesnt get summoned
        self.clearQueue()
        cls = self.__class__
        result = cls.__new__(cls)
        result.p1played = self.p1played
        result.p2played = self.p2played
        result.player1 = copy.deepcopy(self.player1)
        result.player2 = copy.deepcopy(self.player2)
        result.board = copy.deepcopy(self.board)
        if (self.activePlayer == self.player1):
            result.activePlayer = result.player1
        else:
            result.activePlayer = result.player2
        result.currTurn = self.currTurn
        result.winner = self.winner
        result.error = self.error
        result.winString = self.winString
        # A new leaf node should never be created while there is still something in the queue, or something has gone
        # seriously wrong
        result.queue = []
        return result
    """
    def printGameState(self):
        os.system('clear')
        if (self.gameNum > -1):
            print("Game number: " + str(self.gameNum)) 
        if (self.activePlayer == self.player1):
            print("Active player: 1")
            print("HP: " + str(self.player2.currHP) + "/" + str(self.player2.maxHP))
            print("Cards: " + str(len(self.player2.hand)))
            print("PP: " + str(self.player2.currPP) + "/" + str(self.player2.maxPP))
            print("Evos: " + str(self.player2.currEvos))
            print("Super Evos: " + str(self.player2.currSuperEvos))
            print("Coin: " + str(self.player2.canCoin))
            print("Shadows: " + str(self.player2.shadows))
            print("")
            self.board.printBoard()
            print("")
            print("HP: " + str(self.player1.currHP) + "/" + str(self.player1.maxHP))
            print("PP: " + str(self.player1.currPP) + "/" + str(self.player1.maxPP))
            print("Evos: " + str(self.player1.currEvos))
            print("Super Evos: " + str(self.player1.currSuperEvos))
            print("Shadows: " + str(self.player1.shadows))
            print("Hand:")
            self.player1.printHand()
        else:
            print("Active player: 2")
            print("HP: " + str(self.player2.currHP) + "/" + str(self.player2.maxHP))
            print("Cards: " + str(len(self.player1.hand)))
            print("PP: " + str(self.player2.currPP) + "/" + str(self.player2.maxPP))
            print("Evos: " + str(self.player2.currEvos))
            print("Super Evos: " + str(self.player2.currSuperEvos))
            print("Shadows: " + str(self.player2.shadows))
            print("Coin: " + str(self.player2.canCoin))
            print("")
            self.board.printBoard()
            print("")
            print("HP: " + str(self.player1.currHP) + "/" + str(self.player1.maxHP))
            print("PP: " + str(self.player1.currPP) + "/" + str(self.player1.maxPP))
            print("Evos: " + str(self.player1.currEvos))
            print("Super Evos: " + str(self.player1.currSuperEvos))
            print("Shadows: " + str(self.player1.shadows))
            print("Hand:")
            self.player2.printHand()

    def initiateEvolve(self, allyMonsterIndex):
        if (not self.activePlayer.canEvolve):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                # Reset the standard output
                self.printGameState()
                print("ERROR: this player cannot evolve")
                sys.stdout = original_stdout 
            self.error = 1
            return
        
        if len(self.board.fullBoard[self.activePlayer.playerNum-1]) <= allyMonsterIndex[0]:
            print("ERROR: non-existant evo target")
            self.error = 1
            return
        evolveTarget = self.board.fullBoard[self.activePlayer.playerNum-1][allyMonsterIndex[0]]
            
        if ((self.activePlayer.currEvos == 0) and evolveTarget.freeEvolve == 0):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                # Reset the standard output
                self.printGameState()
                print("ERROR: not enough evolves")
                sys.stdout = original_stdout 
            self.error = 1
            return

        if evolveTarget.evoEnemyFollowerTargets > 0 and len(self.board.fullBoard[(self.activePlayer.playerNum+1) % 2]) > 0:
            evolveTarget.evolve(self, allyMonsterIndex[1:], self.activePlayer.playerNum % 2)
        else:
            evolveTarget.evolve(self)

    def initiateSuperEvolve(self, allyMonsterIndex):
        if (not self.activePlayer.canSuperEvolve):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                # Reset the standard output
                self.printGameState()
                print("ERROR: this player cannot super evolve")
                sys.stdout = original_stdout
            self.error = 1
            return
        
        if len(self.board.fullBoard[self.activePlayer.playerNum-1]) <= allyMonsterIndex[0]:
            print("ERROR: non-existant evo target")
            self.error = 1
            return
        evolveTarget = self.board.fullBoard[self.activePlayer.playerNum-1][allyMonsterIndex[0]]
            
        if ((self.activePlayer.currSuperEvos == 0) and evolveTarget.freeSuperEvolve == 0):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                # Reset the standard output
                self.printGameState()
                print("ERROR: not enough evolves")
                sys.stdout = original_stdout 
            self.error = 1
            return

        if evolveTarget.evoEnemyFollowerTargets > 0 and len(self.board.fullBoard[(self.activePlayer.playerNum+1) % 2]) > 0:
            evolveTarget.superEvolve(self, allyMonsterIndex[1:], self.activePlayer.playerNum % 2)
        else:
            evolveTarget.superEvolve(self)

    def initiateCoinAction(self):
        if self.activePlayer.canCoin == 0:
            print("ERROR: attempt to use coin illegally")
            return
        self.activePlayer.currPP += 1
        self.activePlayer.canCoin = 0

    def initiateAttack(self, allyMonster, enemyMonster):
    
        # First, figure out what side is attacking
        attackingPlayer = self.activePlayer.playerNum - 1
        defendingPlayer = self.activePlayer.playerNum % 2

        # VALID TARGETS CHECKING
        # Make sure that the allyMonster attacking a valid target, and that the enemyMonster is a valid target
        if (allyMonster > len(self.board.fullBoard[attackingPlayer]) - 1):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print(allyMonster, enemyMonster)
                print("ERROR: attempt to use a non-existent monster to attack")
                sys.stdout = original_stdout 
            self.error = 1
            return
        elif (allyMonster < 0):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print("ERROR: attempt to use a non-existent monster to attack")
                sys.stdout = original_stdout 
            self.error = 1
            return
        elif (enemyMonster > len(self.board.fullBoard[defendingPlayer]) - 1):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print("ERROR: attempt to attack a non-existent target")
                sys.stdout = original_stdout 
            self.error = 1
            return
        elif (enemyMonster < -1):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print(allyMonster, enemyMonster)
                print("ERROR: attempt to attack a non-existent target")
                sys.stdout = original_stdout 
            self.error = 1
            return
        elif (not self.board.fullBoard[attackingPlayer][allyMonster].canAttack):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print(allyMonster, enemyMonster)
                print("ERROR: attempt to attack with a monster that cannot attack")
                sys.stdout = original_stdout 
            self.error = 1
            return
        elif (enemyMonster == -1 and not self.board.fullBoard[attackingPlayer][allyMonster].canAttackFace):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print(allyMonster, enemyMonster)
                print("ERROR: this monster cannot attack face")
                sys.stdout = original_stdout 
            self.error = 1
            return

        # VALID TARGETS CHECKING FOR WARDS, this might need to become more general
        wardExists = 0
        for enem in self.board.fullBoard[defendingPlayer]:
            if enem.hasWard:
                wardExists = 1
        if wardExists and (enemyMonster == ENEMY_FACE or not self.board.fullBoard[defendingPlayer][enemyMonster].hasWard):
            with open('demo.txt', 'a') as f:
                original_stdout = sys.stdout
                sys.stdout = f
                self.printGameState()
                print("ERROR: attempt to attack through a ward")
                sys.stdout = original_stdout 
            self.error = 1
            return

        # Actual Fuction

        # Give summoning sickness to the monster that just attacked, do this here
        # because the monster might stop existing after attacking, and then we would apply
        # summoning sickness to a different monster (or out of index error)
        # TODO: put these into the followerStrike/leaderStrike functions
        self.board.fullBoard[attackingPlayer][allyMonster].canAttack = 0
        self.board.fullBoard[attackingPlayer][allyMonster].hasAttacked = 1

        # Face is being attacked
        if (enemyMonster == ENEMY_FACE):
            if (attackingPlayer == 0):
                self.board.player1side[allyMonster].leaderStrike(self, allyMonster)
            else:
                self.board.player2side[allyMonster].leaderStrike(self, allyMonster)

        # otherwise, we are attacking a monster, deal damage to each other
        else:
            attackingMonster = self.board.fullBoard[attackingPlayer][allyMonster]
            defMonster = self.board.fullBoard[defendingPlayer][enemyMonster]
            attackingMonster.followerStrike(self, allyMonster, attackingPlayer, defMonster, enemyMonster)
        self.clearQueue()

    def endgame(self, winner):
        if winner == 1:
            #input("The winner is player 1")
            self.winner = 1
        else:
            #input("The winner is player 2")
            self.winner = 2
        #print("Cause of win: " + self.winString)

    # Note that function might also become bloated with time, be careful!
    # For now, nothing has a battlecry, so just place it on the field
    # Once spells are implemented, have this split into 2 separate functions
    def playCard(self, action):
        # First, figure out what side is playing cards
        currPlayer = self.activePlayer.playerNum - 1

        if (action[1][0] >= len(self.activePlayer.hand)):
            print("ERROR: played card out of range")
            self.error = 1
            return

        card = self.activePlayer.hand[action[1][0]]
        if (currPlayer == 0):
            self.p1played[card.encoding] += 1
        else:
            self.p2played[card.encoding] += 1

        # Check if we are acceling
        if (isinstance(card, Monster) and self.activePlayer.currPP < card.cost and card.canAccel and self.activePlayer.currPP >= card.accelCost):
            accelerating = True
        else:
            accelerating = False

        # Check that board is not full
        if (len(self.board.fullBoard[currPlayer]) == MAX_BOARD_SIZE and (not isinstance(card,Spell)) and (not accelerating)):
            print("Attempted to play a follower when the board is full")
            self.error = 1
            return

        # Make sure that we have the PP to play the follower/spell
        if self.activePlayer.currPP < self.activePlayer.hand[action[1][0]].cost and not accelerating:
            print("Attempted to play a card that costs more than our current PP")
            self.error = 1
            return
        
        cardToPlay = self.activePlayer.hand.pop(action[1][0])
        if accelerating:
            cardToPlay = cardToPlay.accelCard

        if (cardToPlay.numTargets == 0):
            cardToPlay.play(self, currPlayer)
        elif (len(action[1]) == 1) and (cardToPlay.targetOptional):
            cardToPlay.play(self, currPlayer, [])
        elif (len(action[1]) == 1):
            print("ERROR: tried to play a non-optional target without a target")
            self.error = 1
            #TODO: in theory this can cause a bug with acceleration
            self.activePlayer.hand.append(cardToPlay)
            return
        else:
            cardToPlay.play(self, currPlayer, action[1][1:])

    def endTurn(self):
        self.activateTurnEndEffects(None)
        self.clearQueue()

        # Allow all followers to attack again
        for mons in self.board.player1side:
            mons.effActivations = 0
            if (not mons.isAmulet):
                mons.canAttack = 1
                mons.canAttackFace = 1
        for mons in self.board.player2side:
            mons.effActivations = 0
            if (not mons.isAmulet):
                mons.canAttack = 1
                mons.canAttackFace = 1

        # Change the current active player
        if (self.activePlayer == self.player1):
            self.activePlayer.selfPingsTurn = 0
            self.activePlayer = self.player2
        else:
            self.activePlayer.selfPingsTurn = 0
            self.activePlayer = self.player1
        
        # Change the turn number
        if (self.activePlayer == self.player1):
            self.currTurn += 1

        # Check if coin is activatable
        if (self.activePlayer == self.player2) and (self.currTurn == 1 or self.currTurn == 6):
            self.activePlayer.canCoin = 1
        
        self.startTurn()

    def startTurn(self):
        self.activateTurnStartEffects(None)
        self.clearQueue()
        self.activateEnemyTurnStartEffects()
        self.clearQueue()

        for mons in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            if (mons.isAmulet) and (mons.isCountdown):
                mons.countdown -= 1
                if mons.countdown == 0:
                    mons.destroy(self)

        # Increase max PP of the current player
        if (self.activePlayer.maxPP < MAX_EMPTY_PP):
          self.activePlayer.maxPP += 1

        # Set active player current PP equal to their new max
        self.activePlayer.currPP = self.activePlayer.maxPP
 
        # Set if the player has the ability to evolve or not on this turn
        if (self.activePlayer == self.player1 and self.currTurn >= PLAYER_1_EVO_TURN):
            self.activePlayer.canEvolve = 1
        elif (self.activePlayer == self.player2 and self.currTurn >= PLAYER_2_EVO_TURN):
            self.activePlayer.canEvolve = 1
        else:
            self.activePlayer.canEvolve = 0

        # Set if the player has the ability to evolve or not on this turn
        if (self.activePlayer == self.player1 and self.currTurn >= PLAYER_1_SUPER_EVO_TURN):
            self.activePlayer.canSuperEvolve = 1
        elif (self.activePlayer == self.player2 and self.currTurn >= PLAYER_2_SUPER_EVO_TURN):
            self.activePlayer.canSuperEvolve = 1
        else:
            self.activePlayer.canSuperEvolve = 0

        # In WB the player going second doesnt draw an additional card
        self.activePlayer.draw()

        # Current problem is that only the Game can signal to end itself but the player is the
        # class that draws cards. This means that the game will have to check with the player
        # after any draw instance. To fix this, we can create a draw method for the board that
        # draws for the active player and then checks for reaper, for now this is ok though.
        # TODO
        if self.activePlayer.hand == []:
            self.winString = "Decked out"
            if self.activePlayer == self.player1:
                self.endgame(2)
            else:
                self.endgame(1)


    #def mulligan(self, player):
    #    mull = player.mulliganSample(1,1,0)
    #    player.returnMulliganSample(mull)

    # this function will have the initial drawing and mulligan phase
    def gameStart(self):
        self.winner = 0
        self.player1.draw(3)
        self.player2.draw(3)
       
        if (len(self.player1.deck.cards) == 0):
            raise Exception("no cards in deck at start")
        
        #self.mulligan(self.player1)
        #self.mulligan(self.player2)

        #self.startTurn()

    # this function is mostly to deal with ward, but can be expanded to include other specific cards
    def attackableTargets(self):
        targets = []
        if self.activePlayer == self.player1:
            targetPlayer = 1
        else:
            targetPlayer = 0

        tempTargets = []
        # Ward check
        wards = []
        wardIndex = 0
        for follower in self.board.fullBoard[targetPlayer]:
            if follower.hasWard:
                wards.append(wardIndex)
            if follower.isAttackable:
                tempTargets.append(wardIndex)
            wardIndex += 1
  
        if wards == []:
            targets.append(-1)
            targets += tempTargets
        else:
            targets = wards

        return targets
  
    #TODO for disco and stuff
    #def getLegalTargets(self, card, currIndex):
        
    # Helper function for generating legal moves for playing cards
    def addLegalMovesForCard(self, card, moves, currIndex):
        allyBoard = self.activePlayer.playerNum - 1
        #legalTargets = self.getLegalTargets(card, currIndex)

        if (card.numTargets == 0):
            moves.append([PLAY_ACTION, [currIndex]])
            # For now we only support battlecries that have a single target
        if (card.fanfareTargetFace):
            moves.append([PLAY_ACTION, [currIndex, -1]])
        if (card.numEnemyFollowerTargets == 1):
            for targetIndex in range(len(self.board.fullBoard[(allyBoard+1) % 2])):
                if isinstance(self.board.fullBoard[(allyBoard+1) % 2][targetIndex], Monster):
                    moves.append([PLAY_ACTION, [currIndex, targetIndex]])
        elif (card.numAllyFollowerTargets == 1):
            if (card.targetOptional):
                moves.append([PLAY_ACTION, [currIndex]])
            for targetIndex in range(len(self.board.fullBoard[allyBoard])):
                if isinstance(self.board.fullBoard[allyBoard][targetIndex], Monster):
                    moves.append([PLAY_ACTION, [currIndex, targetIndex]])
        elif (card.numChooseTargets > 0):
            for targetIndex in range(card.numChooseTargets):
                moves.append([PLAY_ACTION, [currIndex, targetIndex]])

    def generateLegalMoves(self):
        self.clearQueue()
        moves = []

        allyBoard = self.activePlayer.playerNum - 1
        
        # Playing card from hand moves available
        currIndex = 0
        for card in self.activePlayer.hand:
            # Check for accel
            if (isinstance(card, Monster) and self.activePlayer.currPP < card.cost and card.canAccel and self.activePlayer.currPP >= card.accelCost):
                accelerating = True
            else:
                accelerating = False
             
            # We are accelerating
            if (accelerating):
                self.addLegalMovesForCard(card.accelCard, moves, currIndex)

            # Not acceling, but there is either room for the card, or it is a spell
            if self.activePlayer.currPP >= card.cost and (len(self.board.fullBoard[allyBoard]) < 5 or isinstance(card,Spell)):
                self.addLegalMovesForCard(card, moves, currIndex)

            currIndex += 1

        # Attacking moves available
        currIndex = 0
        possibleTargets = self.attackableTargets()
        for card in self.board.fullBoard[allyBoard]:
            if (card.canAttack):
                for attackable in possibleTargets:
                    if (attackable == -1) and not card.canAttackFace:
                        continue
                    moves.append([ATTACK_ACTION, [currIndex, attackable]])
            currIndex += 1

        # If we cant evolve, we are done
        #TODO: if we are out of evo points, do we still get SEV
        if not self.activePlayer.canEvolve:
            moves.append([PASS_ACTION])
            if self.activePlayer.canCoin == 1:
                moves.append([COIN_ACTION])
            return moves

        # Otherwise, Evolving follower moves available, find them
        currIndex = 0
        for card in self.board.fullBoard[allyBoard]:
            if card.canEvolve and ((self.activePlayer.currEvos > 0) or (card.freeEvolve)):
                # TODO: ally targeting at some point
                if card.evoEnemyFollowerTargets == 0:
                    moves.append([EVO_ACTION, [currIndex]])
                elif card.evoEnemyFace == 0 and len(self.board.fullBoard[(allyBoard+1) % 2]) == 0:
                    moves.append([EVO_ACTION, [currIndex]])
                else:
                    if card.evoEnemyFace == True:
                        moves.append([EVO_ACTION, [currIndex, -1]])
                    for targetIndex in range(len(self.board.fullBoard[(allyBoard+1) % 2])):
                        moves.append([EVO_ACTION, [currIndex, targetIndex]])
            currIndex += 1

        if self.activePlayer.canSuperEvolve:
            currIndex = 0
            for card in self.board.fullBoard[allyBoard]:
                if card.canSuperEvolve and ((self.activePlayer.currSuperEvos > 0) or (card.freeSuperEvolve)):
                    if card.superEvoEnemyFollowerTargets == 0:
                        moves.append([SUPER_EVO_ACTION, [currIndex]])
                    elif card.superEvoEnemyFace == 0 and len(self.board.fullBoard[(allyBoard+1) % 2]) == 0:
                        moves.append([SUPER_EVO_ACTION, [currIndex]])
                    else:
                        if card.superEvoEnemyFace == True:
                            moves.append([SUPER_EVO_ACTION, [currIndex, -1]])
                        for targetIndex in range(len(self.board.fullBoard[(allyBoard+1) % 2])):
                            moves.append([SUPER_EVO_ACTION, [currIndex, targetIndex]])
                currIndex += 1

        moves.append([PASS_ACTION])

        if self.activePlayer.canCoin == 1:
            moves.append([COIN_ACTION])

        return moves

    # Remove magic numbers from this, maybe implement action as a class. Find some better
    # implementation in any case
    def initiateAction(self, action):
        if action[0] == PASS_ACTION:
            self.endTurn()
        elif action[0] == PLAY_ACTION:
            self.playCard(action)
        elif action[0] == ATTACK_ACTION:
            self.initiateAttack(action[1][0], action[1][1])
        elif action[0] == EVO_ACTION:
            self.initiateEvolve(action[1])
        elif action[0] == SUPER_EVO_ACTION:
            self.initiateSuperEvolve(action[1])
        elif action[0] == COIN_ACTION:
            self.initiateCoinAction()
        else:
            print("ERROR: Invalid action:")
            input(action)
        return self.error

    # This is used for rollouts on a MCTS, but we dont actually do this with our AZ implementation
    def runToCompletion(self):
        while (self.winner == 0):
            moves = self.generateLegalMoves()
            selection = random.randrange(len(moves))
            #print(moves[selection])
            self.initiateAction(moves[selection])
        return self.winner

    def miniRollout(self):
        currPlayer = self.activePlayer.playerNum
        while (self.activePlayer.playerNum == currPlayer):
            moves = self.generateLegalMoves()
            selection = random.randrange(len(moves))
            self.initiateAction(moves[selection])

    def removeFollowerLambda(self, mons):
        for side in self.board.fullBoard:
            for item in side:
                if item == mons:
                    side.remove(mons)

    def removeFollower(self, mons):
        return lambda gameState: gameState.removeFollowerLambda(mons) 

    def activateOnPlayEffects(self, card):
        self.activePlayer.leaderEffects.activateOnPlayEffects(self, card)

    def activateOnSummonEffects(self, card):
        if card.side == 1:
            self.player1.leaderEffects.activateOnSummonEffects(self, card)
        else:
            self.player2.leaderEffects.activateOnSummonEffects(self, card)
        for item in self.board.fullBoard[card.side]:
            for eff in item.onSummonEffects:
                eff(self, card)

    def activateSelfPingEffects(self, nothing):
        self.activePlayer.leaderEffects.activateSelfPingEffects(self)
        for card in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            for eff in card.selfPingEffects:
                eff(card, self)

    def activateHealEffects(self, nothing):
        self.activePlayer.leaderEffects.activateHealEffects(self)
        for card in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            for eff in card.selfHealEffects:
                eff(self)
    
    def activateTurnEndEffects(self, placholder):
        #TODO this is a bandage, pls fix the castle interactions
        startPings = self.activePlayer.selfPings
        tempPings = self.activePlayer.selfPings
        self.activePlayer.leaderEffects.activateTurnEndEffects(self)
        for card in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            for eff in card.turnEndEffects:
                eff(self)
                if (startPings != self.activePlayer.selfPings):
                    tempPings += (self.activePlayer.selfPings - startPings)
                    self.activePlayer.selfPings = startPings
        self.activePlayer.selfPings = tempPings
    
    def activateTurnStartEffects(self, placholder):
        self.activePlayer.leaderEffects.activateTurnStartEffects(self)
        for card in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            for eff in card.turnStartEffects:
                eff(self)

    def activateEnemyTurnStartEffects(self):
        for card in self.board.fullBoard[self.activePlayer.playerNum % 2]:
            for eff in card.enemyTurnStartEffects:
                eff(self)

    def activateOnAllyEvoEffects(self, mons):
        # TODO: leader effects?
        for card in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            if (card != mons):
                for eff in card.onAllyEvoEffects:
                    eff(self)

    def activateOnAllySuperEvoEffects(self, mons):
        # TODO: leader effects?
        for card in self.board.fullBoard[self.activePlayer.playerNum - 1]:
            if (card != mons):
                for eff in card.onAllySuperEvoEffects:
                    eff(self)

    def clearQueue(self):
        queueIndex = 0
        while queueIndex < len(self.queue):
            if self.queue[queueIndex] != None:
                self.queue[queueIndex](self)
            queueIndex += 1
        self.queue = []

    # sorts the active player's hand and the monsters on board. Mostly used to handle transpositions that have
    # position differences but everything else is the same. WARNING: there are rare cases where board position actually does matter
    # so use with caution
    def sortGame(self):
        self.activePlayer.hand.sort(key=lambda x: x.encoding)
        self.board.fullBoard[0].sort(key=lambda x: 1000*x.encoding + 500*x.hasBane + 400*x.hasWard + 300*x.isEvolved + 200*x.canAttack + 10*x.currAttack + x.currHP)
        self.board.fullBoard[1].sort(key=lambda x: 1000*x.encoding + 500*x.hasBane + 400*x.hasWard + 300*x.isEvolved + 200*x.canAttack + 10*x.currAttack + x.currHP)

