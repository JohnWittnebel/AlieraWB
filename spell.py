from card import Card
from cardGeneric import *

class Spell(Card):
    def __init__(self, name, cost, allyFollowerTargets, enemyFollowerTargets):
        self.name = name
        self.cost = cost
        self.numAllyFollowerTargets = allyFollowerTargets
        self.numEnemyFollowerTargets = enemyFollowerTargets
        self.numTargets = self.numAllyFollowerTargets + self.numEnemyFollowerTargets
        self.fanfareTargetFace = False
        self.targetOptional = False
        self.isAmulet = False
        self.traits = []
        self.numChooseTargets = 0
        
        # For assist
        self.rigRNG = False
        self.riggedVal = 0

    def play(self, gameState, side, *args, **kwargs):
        # spells dont really have a default action, so just do nothing
        return
