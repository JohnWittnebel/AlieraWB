from card import Card
from cardGeneric import *

class Monster(Card):
    def __init__(self, cost, monsterAttack, monsterMaxHP, currHP, monsterName):
        self.cost = cost
        self.currAttack = monsterAttack
        self.maxAttack = monsterAttack
        self.maxHP = monsterMaxHP
        self.currHP = currHP

        # For assist
        self.rigRNG = False
        self.riggedVal = 0

        # These are various properties that a monster can have, maybe make this a bit more elegant
        self.canEvolve = 1
        self.canSuperEvolve = 1
        self.isEvolved = 0
        self.isSuperEvolved = 0
        self.autoEvolve = 0
        self.hasStorm = 0
        self.hasRush = 0
        self.hasBane = 0
        self.canAttack = 0
        self.hasWard = 0
        self.hasDrain = 0
        self.hasAttacked = 0
        self.turnPlayed = 0
        self.canAttackFace = 1
        self.freeEvolve = 0
        self.isAttackable = True
        self.isAmulet = False
        self.side = -1

        self.maxEffPerTurn = 8
        self.effActivations = 0

        #Enhance/accel
        self.canEnhance = False
        self.canAccel = False
        self.accelCost = 0
        self.accelCard = None

        # Effect Arrays
        self.fanfareEffects = []
        self.LWEffects = []
        self.followerStrikeEffects = []
        self.strikeEffects = []
        self.clashEffects = []
        self.onAllyEvoEffects = []
        self.onSummonEffects = [] # for when an ally follower is summoned (not played)
        self.turnEndEffects = []
        self.turnStartEffects = []
        self.enemyTurnStartEffects = []
        self.selfPingEffects = []
        self.selfHealEffects = []

        self.traits = []
        
        # Battlecry targets
        self.numTargets = 0
        self.targetOptional = False
        self.numEnemyFollowerTargets = 0
        self.numAllyFollowerTargets = 0
        self.numChooseTargets = 0
        self.chooseCards = []
        self.fanfareTargetFace = False

        # Evo targets
        self.evoEnemyFollowerTargets = 0
        self.superEvoEnemyFollowerTargets = 0
        self.evoAllyFollowerTargets = 0
        self.superEvoAllyFollowerTargets = 0
        self.evoEnemyFace = False
        self.evoAllyFace = False
        self.superEvoEnemyFace = False
        self.superEvoAllyFace = False

        Card.__init__(self, cost, monsterName)

    #@abstractmethod
    def play(self, board, currPlayer, *args, **kwargs):
        genericPlay(self, board, currPlayer)
  
    #@abstractmethod
    def takeCombatDamage(self, gameState, damage):
        damageTaken = genericTakeDamage(self, gameState, damage)
        return damageTaken

    def takeEffectDamage(self, gameState, damage):
        damageTaken = genericTakeDamage(self, gameState, damage)
    
    #@classmethod
    def evolve(self, gameState, *args, **kwargs):
        genericEvolve(self, gameState)
    
    def superEvolve(self, gameState, *args, **kwargs):
        genericSuperEvolve(self, gameState)

    # called to actually destroy, activate LW, etc.
    def destroy(self, gameState, *args, **kwargs):
        genericDestroy(self, gameState)

    # called when an effect attempts to destroy (bane, destroy follower, etc.). Might not actually
    # destroy if the target has protection
    def effectDestroy(self, gameState, *args, **kwargs):
        genericDestroy(self, gameState)

    def leaderStrike(self, gameState, myIndex, *args, **kwargs):
        self.hasAttacked = 1
        if gameState.activePlayer.playerNum == 1:
            damagePlayer = gameState.player2
            myPlayer = gameState.player1
        else:
            damagePlayer = gameState.player1
            myPlayer = gameState.player2

        for func in self.strikeEffects:
            func(gameState, myIndex)

        gameState.clearQueue()
        damageDealt = damagePlayer.takeCombatDamage(gameState, self.currAttack)
        if self.hasDrain == 1:
            myPlayer.restoreHP(gameState, damageDealt)

    def followerStrike(self, gameState, allyIndex, activeSide, enemyMonster, enemyIndex, *args, **kwargs):
        self.hasAttacked = 1
        #TODO: these should actually just queue instead of activating. Its ok for now tho I think
        for func in self.strikeEffects:
            func(gameState, allyIndex)
        for func in self.clashEffects:
            func(gameState, activeSide, enemyMonster)
        for func in self.followerStrikeEffects:
            func(gameState, activeSide, enemyMonster)
        for func in enemyMonster.clashEffects:
            func(gameState, (activeSide+1)%2, self)
        gameState.clearQueue()
        if (enemyMonster.currHP > 0):
            combatDamageToTake = enemyMonster.currAttack
            damageDealt = enemyMonster.takeCombatDamage(gameState, self.currAttack)
            if self.isSuperEvolved == False:
                damageTaken = self.takeCombatDamage(gameState, combatDamageToTake)
            if self.hasDrain == 1:
                if activeSide == 0:
                    gameState.player1.restoreHP(gameState, damageDealt)
                else:
                    gameState.player2.restoreHP(gameState, damageDealt)
            if self.hasBane:
                enemyMonster.effectDestroy(gameState)
            if enemyMonster.hasBane and self.isSuperEvolved == False:
                self.effectDestroy(gameState)
