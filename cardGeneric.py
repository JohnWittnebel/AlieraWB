# For generic card functions

def genericTakeDamage(mons, gameState, damage):
    if (mons.hasDivineShield):
        mons.hasDivineShield = 0
        return 0
    mons.currHP -= damage
    if (mons.currHP <= 0):
        mons.destroy(gameState)
    return damage

def genericDestroy(mons, gameState):
    gameState.queue.append(gameState.removeFollower(mons))
    if mons.side == 0:
        gameState.player1.shadows += 1
    else:
        gameState.player2.shadows += 1

    for func in mons.LWEffects:
        gameState.queue.append(func(gameState, mons.side))

def genericBanish(mons, gameState):
    gameState.queue.append(gameState.removeFollower(mons))

def genericEvolve(mons, gameState):
    if (mons.isEvolved):
        print("ERROR: monster is already evolved")
        return
        
    mons.currAttack += 2
    mons.maxAttack += 2
    mons.maxHP += 2
    mons.currHP += 2
    mons.name += "(E)"

    mons.canEvolve = 0
    mons.canSuperEvolve = 0
    mons.isEvolved = 1
    if (mons.hasAttacked == 0):
        mons.canAttack = 1
    if (mons.turnPlayed == gameState.currTurn) and (mons.hasStorm == 0):
        mons.canAttackFace = 0
    
    if (mons.autoEvolve != 1):
        gameState.activePlayer.canEvolve = 0
        gameState.activePlayer.canSuperEvolve = 0
    if (mons.freeEvolve != 1):
        gameState.activePlayer.currEvos -= 1
    gameState.queue.append(gameState.activateOnAllyEvoEffects(mons))

def genericSuperEvolve(mons, gameState):
    if (mons.isEvolved):
        print("ERROR: monster is already evolved")
        return
        
    mons.currAttack += 3
    mons.maxAttack += 3
    mons.maxHP += 3
    mons.currHP += 3
    mons.name += "(SE)"

    mons.canEvolve = 0
    mons.canSuperEvolve = 0
    mons.isEvolved = 0
    mons.isSuperEvolved = 1
    if (mons.hasAttacked == 0):
        mons.canAttack = 1
    if (mons.turnPlayed == gameState.currTurn) and (mons.hasStorm == 0):
        mons.canAttackFace = 0
    
    if (mons.autoEvolve != 1):
        gameState.activePlayer.canEvolve = 0
        gameState.activePlayer.canSuperEvolve = 0
    if (mons.freeEvolve != 1):
        gameState.activePlayer.currSuperEvos -= 1
    gameState.queue.append(gameState.activateOnAllySuperEvoEffects(mons))

def genericPlay(mons, gameState, currPlayer):
    mons.turnPlayed = gameState.currTurn
    mons.side = gameState.activePlayer.playerNum - 1
    gameState.board.fullBoard[currPlayer].append(mons)
    gameState.activePlayer.currPP -= mons.cost
    for ele in mons.fanfareEffects:
        ele(gameState)
    gameState.queue.append(gameState.activateOnSummonEffects(mons))

def genericSummon(mons, gameState, side):
    if (len(gameState.board.fullBoard[side]) < 5):
        mons.turnPlayed = gameState.currTurn
        mons.side = side
        gameState.board.fullBoard[side].append(mons)
        gameState.queue.append(gameState.activateOnSummonEffects(mons))

