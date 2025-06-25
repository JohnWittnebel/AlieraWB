from deck import Deck
from constants import MAX_HAND_SIZE, DEFAULT_MAX_HP, DEFAULT_MAX_PP
from leaderEffect import *
import copy

# A Player has an associated deck, that is a Deck type
# A Player has a hand, and that is simply an array of Cards, we can specify a starting hand if we wish
# A Player has a PlayerNum, and that is 1 or 2 depending on if the player is first or second respectively
# A Player has a max number of Evos, this is 2 when first or 3 when second, but this can change with certain cards
# A Player has a current number of usable Evos
# A Player has leader effects, that will be used in a later version
# A Player has a maximum and current HP
# A Player has a maximum and current PP
# A Player has a field to indicate if they are able to evolve yet

class Player:
    def __init__(self, deck, playerNum):
        self.deck = deck
        self.maxEvos = 2
        self.currEvos = 2
        self.maxSuperEvos = 2
        self.currSuperEvos = 2
        self.playerNum = playerNum
        self.hand = []
        self.currHP = DEFAULT_MAX_HP
        self.maxHP = DEFAULT_MAX_HP
        self.currPP = DEFAULT_MAX_PP
        self.maxPP = DEFAULT_MAX_PP
        self.canEvolve = 0
        self.canCoin = 0
        self.canSuperEvolve = 0
        self.damageProtection = 0
        self.effectProtection = 0
        self.selfPings = 0
        self.selfPingsTurn = 0
        self.shadows = 0
        self.immune = False
        self.effectImmune = False
        self.leaderEffects = LeaderEffectManager()

    """
    def __deepcopy__(self, info):
        deckcopy = copy.deepcopy(self.deck)
        retVal = Player(deckcopy, self.maxEvos, self.currEvos, self.playerNum)
        retVal.hand = copy.deepcopy(self.hand)
        retVal.currHP = self.currHP
        retVal.maxHP = self.maxHP
        retVal.currPP = self.currPP
        retVal.maxPP = self.maxPP
        retVal.damageProtection = self.damageProtection
        retVal.canEvolve = self.canEvolve
        retVal.effectProtection = self.effectProtection
        retVal.selfPings = self.selfPings
        retVal.selfPingsTurn = self.selfPingsTurn
        retVal.immune = self.immune
        retVal.effectImmune = self.effectImmune
        retVal.leaderEffect = copy.deepcopy(self.leaderEffects)
        return retVal
    """

    def draw(self, count = 1):
        for _ in range(count):
            cardToAdd = self.deck.draw()
            # Hacky way to kill you when you draw reaper
            if (cardToAdd.name == "Reaper"):
                self.hand = []
                self.currHP = 0
                self.maxHP = 0
                self.maxPP = 0
                self.currPP = 0
            elif (len(self.hand) == MAX_HAND_SIZE):
                #print("Hand size full")
                return
            else:
                self.hand.append(cardToAdd)

    def drawCard(self, card):
        cardToDraw = self.deck.cards.pop(card)
        if (len(self.hand) == MAX_HAND_SIZE):
            return
        else:
            self.hand.append(cardToDraw)
    
    # Actual mulligan, draw without replacement, then insert cards and reshuffle
    def mulligan(self, mull1, mull2, mull3):
        numCards = mull1+mull2+mull3
        temp1 = None
        temp2 = None
        temp3 = None
        if (mull3 == 1):
            temp3 = self.hand.pop(2)
        if (mull2 == 1):
            temp2 = self.hand.pop(1)
        if (mull1 == 1):
            temp1 = self.hand.pop(0)

        self.deck.trueShuffle()
        self.draw(numCards)
        
        if (mull3 == 1):
            self.deck.cards.append(temp3)
        if (mull2 == 1):
            self.deck.cards.append(temp2)
        if (mull1 == 1):
            self.deck.cards.append(temp1)
        self.deck.trueShuffle()

    # Used to sample different mulligan results to estimate optimal mulligan strat
    def mulliganSample(self, mull1, mull2, mull3):
        numCards = mull1+mull2+mull3
        temp1 = None
        temp2 = None
        temp3 = None
        if (mull3 == 1):
            temp3 = self.hand.pop(2)
        if (mull2 == 1):
            temp2 = self.hand.pop(1)
        if (mull1 == 1):
            temp1 = self.hand.pop(0)

        self.deck.trueShuffle()
        self.draw(numCards)
        return [temp1, temp2, temp3]

    # Used in conjunction with mulliganSample to return the gameState to the original position
    def returnMulliganSample(self, mullArr):
        tempHand = []
        for i in range(3):
            if mullArr[i] != None:
                tempHand.append(mullArr[i])
            else:
                keptCard = self.hand.pop(0)
                tempHand.append(keptCard)
        for ele in self.hand:
            self.deck.cards.append(ele)
        self.hand = tempHand
        self.deck.trueShuffle()
       
    def printHand(self):
        count = 0
        printString = ""
        for item in self.hand:
            printString += str(item)
            printString += " [" + str(count) + "], "
            count += 1
        print(printString)

    def restoreHP(self, gameState, val):
        gameState.queue.append(gameState.activateHealEffects)
        if self.currHP + val <= self.maxHP:
            self.currHP += val
        else:
            self.currHP = self.maxHP 

    def takeCombatDamage(self, gameState, val):
        if not self.immune:
            self.currHP = self.currHP - max(0,val - self.damageProtection)
            if self.currHP <= 0:
                gameState.endgame((self.playerNum % 2) + 1)
            return max(0, val - self.damageProtection)
        if self.currHP <= 0:
            gameState.endgame((self.playerNum % 2) + 1)
        return 0

    def takeEffectDamage(self, gameState, val):
        if gameState.activePlayer == self:
            gameState.queue.append(gameState.activateSelfPingEffects)
            self.selfPings += 1
            self.selfPingsTurn += 1
        if not self.effectImmune and not self.immune:
            self.currHP = self.currHP - max(0,val - self.effectProtection)
        if self.currHP <= 0:
            gameState.endgame((self.playerNum % 2) + 1)
     
    def printHand(self):
        index = 0
        for ele in self.hand:
            print(str(index) + ": " + str(ele))
            index += 1
