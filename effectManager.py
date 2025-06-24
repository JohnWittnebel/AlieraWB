class MonsterEffectManager():
    def __init__(self):
        self.onPlayEffects = []
        self.turnStartEffects = []
        self.turnEndEffects = []
        self.onSelfPingEffects = []
        self.onSelfHealEffects = []
        
    def activateOnPlayEffects(self, gameState, card):
        for effect in self.onPlayEffects:
            effect(gameState, card)
  
    def activateSelfPingEffects(self, gameState):
        for effect in self.onSelfPingEffects:
            effect(gameState)
