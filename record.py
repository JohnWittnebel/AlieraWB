# This is for human vs AI play, where the AI takes many actions quickly
# and it is not clear what they actually did

class RecordAction():
    def __init__(self, gameState, action):
        self.action = action[0]
        self.target = 0
        if len(action) > 1:
            side = gameState.activePlayer.playerNum - 1
            if (action[1][0] == 1):
                self.name1 = gameState.activePlayer.hand[action[1][1]].name
                if (len(action[1]) > 1):
                    self.target = action[1][1]
            elif (action[1][0] == 2):
                self.name1 = gameState.board.fullBoard[side][action[1][1]].name
                self.ind1 = action[1][1]
                self.name2 = gameState.board.fullBoard[(side+1) % 2][action[1][2]].name
                self.target = action[1][2]
            elif (action[1][0] == 3):
                self.name1 = gameState.board.fullBoard[side][action[1][1]].name
        

    def __str__(self):
        if self.action == 4:
            return "PASS"
        elif self.action == 1:
            actionStr = "PLAY"
            if self.target:
                return "PLAY " + self.name1 + " with target at index " self.target
            else:
                return "PLAY " + self.name1
        elif self.action == 2:
            actionStr = "ATTACK"
            return "ATTACK " + self.name1 + " at index " + self.ind1 " -> " + self.name + " at index " + self.ind2
        elif self.action == 3:
            actionStr = "EVO"
            if self.target:
                return "EVOLVE " + self.name1 + " with target at index " self.target
            else:
                return "EVOLVE " + self.name1

