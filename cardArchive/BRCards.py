from monster import Monster
from spell import Spell
from cardGeneric import *
from constants import *

import sys
sys.path.insert(0, '..')

class Reaper(Monster):
    def __init__(self):
        monsterName = "Reaper"
        cost = 0
        monsterAttack = 0
        monsterMaxHP = 0
        monsterCurrHP = 0
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)

class DeathDragon(Monster):
    def __init__(self):
        monsterName = "Death Dragon"
        cost = 4
        monsterAttack = 4
        monsterMaxHP = 4
        monsterCurrHP = 4
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = DeathDragonVal

def dealFaceDamage(val):
    return lambda gameState, side: gameState.player1.takeEffectDamage(gameState, val) if side == 0 \
    else gameState.player2.takeEffectDamage(gameState, val)

def healFace(val):
    return lambda gameState: gameState.activePlayer.restoreHP(gameState, val)

class Maiden(Monster):
    def __init__(self):  
        monsterName = "Maiden (W)"
        cost = 1
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)

        self.hasWard = 1
        self.evoEnemyFollowerTargets = 1
        self.evoEnemyFace = True
        self.encoding = MaidenVal
        self.LWEffects.append(dealFaceDamage(2))
        self.selfPingEffects.append(healFace(1))
        
    def evolve(self, gameState, target, targetSide, *args, **kwargs):
        genericEvolve(self, gameState)
        self.maxHP -= 1
        self.currHP -= 1
        self.currAttack -= 1
        
        if (target[0] == -1) and targetSide == 1:
            gameState.player2.takeEffectDamage(gameState, 3)
        elif (target[0] == -1) and targetSide == 0:
            gameState.player1.takeEffectDamage(gameState, 3)
        else:
            enemyPlayer = gameState.activePlayer.playerNum % 2
            if (len(gameState.board.fullBoard[enemyPlayer]) > target[0]):
                gameState.board.fullBoard[enemyPlayer][target[0]].takeEffectDamage(gameState, 3)

class Goliath(Monster):
  def __init__(self):
    monsterName = "Goliath"
    cost = 4
    monsterAttack = 3
    monsterMaxHP = 4
    monsterCurrHP = 4
    Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
    self.encoding = GoliathVal

class Mercenary(Monster):
  def __init__(self):
    monsterName = "Mercenary"
    cost = 3
    monsterAttack = 3
    monsterMaxHP = 2
    monsterCurrHP = 2
    Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
    self.encoding = MercVal

class Goblin(Monster):
  def __init__(self):
    monsterName = "Goblin"
    cost = 1
    monsterAttack = 1
    monsterMaxHP = 2
    monsterCurrHP = 2
    Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
    self.encoding = GoblinVal

def givePlusOne(gameState, card):
    if (isinstance(card, Monster)):
        card.currAttack += 1
        card.currHP += 1
        card.maxHP += 1

def selfPing(val):
    return lambda gameState, side: gameState.activePlayer.takeEffectDamage(gameState, val)

class Fighter(Monster):
    def __init__(self):
        monsterName = "Fighter"
        cost = 2
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = FighterVal

        self.strikeEffects.append(selfPing(1))
        self.strikeEffects.append(selfPing(1))

    # Giving leader effect
    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        if (givePlusOne not in gameState.activePlayer.leaderEffects.onSummonEffects):
            gameState.activePlayer.leaderEffects.onSummonEffects.append(givePlusOne)

    # Remove leader effect when this follower leaves play
    def destroy(self, gameState):
        currPlayer = None
        for ele in gameState.board.fullBoard[0]:
            if ele == self:
                currPlayer = gameState.player1
        if currPlayer == None:
            currPlayer = gameState.player2
        currPlayer.leaderEffects.onSummonEffects = list(filter(lambda a: a != givePlusOne,currPlayer.leaderEffects.onSummonEffects))
        genericDestroy(self, gameState) 

class DragonBreath(Spell):
    def __init__(self):
        spellName = "Dragon's breath"
        spellCost = 2
        allyFollowerTargets = 0
        enemyFollowerTargets = 1
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = GoliathVal
        
    def play(self, gameState, currSide, targets):
        damage = 2
        enemySide = (currSide + 1) % 2
        targetIndex = targets[0]
        gameState.board.fullBoard[enemySide][targetIndex].takeEffectDamage(gameState, damage)
        gameState.activePlayer.draw(2)
        gameState.activePlayer.currPP -= self.cost
        return
