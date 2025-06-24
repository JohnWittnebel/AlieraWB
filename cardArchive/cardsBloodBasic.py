import sys
sys.path.insert(0, '..')

from monster import Monster
from spell import Spell
from cardGeneric import *
from constants import *

class Nightmare(Monster):
    def __init__(self):
        monsterName = "Nightmare"
        cost = 2
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = NightmareVal

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
        self.encoding = MaidenVal
        
    def evolve(self, gameState, target, targetSide, *args, **kwargs):
        genericEvolve(self, gameState)
        self.monsterMaxHP -= 1
        self.monsterCurrHP -= 1
        self.monsterCurrAttack -= 1
            
        enemyPlayer = gameState.activePlayer.playerNum % 2
        if (len(gameState.board.fullBoard[enemyPlayer]) > target[0]):
            gameState.board.fullBoard[enemyPlayer][target[0]].takeEffectDamage(gameState, 3, target[0], targetSide)
    
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

class Fighter(Monster):
  def __init__(self):
    monsterName = "Fighter"
    cost = 2
    monsterAttack = 2
    monsterMaxHP = 2
    monsterCurrHP = 2
    Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
    self.encoding = FighterVal

class DragonBreath(Spell):
    def __init__(self):
        spellName = "Dragon's breath"
        spellCost = 1
        allyFollowerTargets = 0
        enemyFollowerTargets = 1
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = 2
        
    def play(self, gameState, currSide, targets):
        damage = 2
        enemySide = (currSide + 1) % 2
        targetIndex = targets[0]
        gameState.board.fullBoard[enemySide][targetIndex].takeEffectDamage(gameState, damage, targetIndex, enemySide)
        gameState.activePlayer.currPP -= self.cost
        return
