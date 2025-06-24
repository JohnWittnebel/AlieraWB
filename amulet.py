from card import Card
from cardGeneric import *

class Amulet(Card):
    def __init__(self, name, cost, allyFollowerTargets, enemyFollowerTargets, isCountdown, countdown):
        self.name = name
        self.cost = cost
        self.numAllyFollowerTargets = allyFollowerTargets
        self.numEnemyFollowerTargets = enemyFollowerTargets
        self.numChooseTargets = 0
        self.numTargets = self.numAllyFollowerTargets + self.numEnemyFollowerTargets
        self.isCountdown = isCountdown
        self.countdown = countdown
        self.isAttackable = False
        self.fanfareTargetFace = False
        self.targetOptional = False
        self.hasWard = 0
        self.hasBane = 0
        self.isEvolved = 0
        self.canAttack = 0
        self.canEvolve = 0
        self.maxEffPerTurn = 8
        self.currAttack = 0
        self.currHP = 7
        self.effActivations = 0
        self.traits = []
        self.isAmulet = True

        # Effect Arrays
        self.fanfareEffects = []
        self.LWEffects = []
        self.strikeEffects = []
        self.clashEffects = []
        self.onAllyEvoEffects = []
        self.onPlayEffects = []  # for when an ally follower is played
        self.onSummonEffects = []
        self.enemyTurnStartEffects = []
        self.turnEndEffects = []
        self.turnStartEffects = []
        self.selfPingEffects = []
        self.selfHealEffects = []

    def play(self, gameState, side, *args, **kwargs):
        genericPlay(self, gameState, side)
    
    def takeEffectDamage(self, gameState, damage):
        return

    # called to actually destroy, activate LW, etc.
    def destroy(self, gameState, *args, **kwargs):
        genericDestroy(self, gameState)

    # called when an effect attempts to destroy (bane, destroy follower, etc.). Might not actually
    # destroy if the target has protection
    def effectDestroy(self, gameState, *args, **kwargs):
        genericDestroy(self, gameState)
