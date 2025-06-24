# This is owned by Player
class LeaderEffectManager():
    def __init__(self):
        self.onPlayEffects = []
        self.turnStartEffects = []
        self.turnEndEffects = []
        self.onSelfHealEffects = []
        self.onSelfPingEffects = []
        self.onCombatDamageEffects = []
        self.onEffectDamageEffects = []
        self.onSummonEffects = []
        
    def activateOnPlayEffects(self, gameState, card):
        for effect in self.onPlayEffects:
            effect(gameState, card)
    
    def activateSelfPingEffects(self, gameState):
        for effect in self.onSelfPingEffects:
            effect(gameState)
    
    def activateCombatDamageEffects(self, gameState):
        for effect in self.onCombatDamageEffects:
            effect(gameState)
    
    def activateEffectDamageEffects(self, gameState):
        for effect in self.onEffectDamageEffects:
            effect(gameState)

    def activateHealEffects(self, gameState):
        for effect in self.onSelfHealEffects:
            effect(gameState)

    def activateTurnEndEffects(self, gameState):
        for effect in self.turnEndEffects:
            effect(gameState)

    def activateTurnStartEffects(self, gameState):
        for effect in self.turnStartEffects:
            effect[0](gameState)
            effect[1] -= 1
            if (effect[1] == 0):
                self.turnStartEffects.remove(effect)

    def activateOnSummonEffects(self, gameState, card):
        for effect in self.onSummonEffects:
            effect(gameState, card)

