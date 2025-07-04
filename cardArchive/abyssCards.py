from monster import Monster
from spell import Spell
from amulet import Amulet
from cardGeneric import *
from constants import *
import random

import sys
sys.path.insert(0, '..')

##### TOKENS

class GhostAmulet(Amulet):
    def __init__(self):
        name = "GhostAmulet"
        cost = 3
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        isCountdown = False
        countdown = -1
        Amulet.__init__(self, name, cost, allyFollowerTargets, enemyFollowerTargets, isCountdown, countdown)
        self.encoding = GhostAmuletVal

        self.canEngage = 1
        
        

class ForestBat(Monster):
    def __init__(self):
        monsterName = "Forest Bat"
        cost = 1
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1

        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = BatVal
        self.hasDrain = 1

class Ghost(Monster):
    def __init__(self):
        monsterName = "Ghost"
        cost = 1
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1

        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = GhostVal
        self.hasStorm = 1
        self.canAttack = 1
        self.turnEndEffects.append(banishSelf(self))

    def destroy(self, gameState):
        self.banish(gameState)
        

class Skeleton(Monster):
    def __init__(self):
        monsterName = "Skeleton"
        cost = 0
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1

        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = SkeletonVal

class Mimi(Monster):
    def __init__(self):
        monsterName = "Mimi"
        cost = 1
        monsterAttack = 2
        monsterMaxHP = 1
        monsterCurrHP = 1

        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = MimiVal
        self.hasRush = 1
        self.canAttack = 1
        self.canAttackFace = 0
        self.LWEffects.append(enemyPing(2))

class Coco(Monster):
    def __init__(self):
        monsterName = "Coco"
        cost = 1
        monsterAttack = 1
        monsterMaxHP = 2
        monsterCurrHP = 2

        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = CocoVal
        self.hasRush = 1
        self.canAttack = 1
        self.canAttackFace = 0
        self.LWEffects.append(healFace(2))

class GiftForBloodKin(Spell):
    def __init__(self):
        spellName = "Gift"
        spellCost = 0
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = GiftVal
        
    def play(self, gameState, currSide):
        selfPing(1)(gameState)
        enemyPing(1)(gameState, currSide)
        genericSummon(ForestBat(), gameState, currSide)
        genericSummon(ForestBat(), gameState, (currSide + 1) % 2)

class ReaperDeathslash(Spell):
    def __init__(self):
        spellName = "Reaper Deathslash"
        spellCost = 1
        allyFollowerTargets = 1
        enemyFollowerTargets = 1
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = ReaperDeathslashVal

    def play(self, gameState, currSide, targets):
        gameState.board.fullBoard[currSide][targets[0]].effectDestroy(gameState)
        gameState.board.fullBoard[(currSide + 1) % 2][targets[1]].effectDestroy(gameState)


class Ceres(Monster):
    def __init__(self):
        monsterName = "Ceres"
        cost = 4
        monsterAttack = 1
        monsterMaxHP = 4
        monsterCurrHP = 4

        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = CeresVal
        self.hasBane = 1

        self.turnEndEffects.append(healFaceActive(2))
   
    def superEvolve(self, gameState):
        self.turnEndEffects[0] = healFaceActive(4)
        self.turnEndEffects.append(divineShield(self))
        genericSuperEvolve(self, gameState)
    

class SummonBloodKin(Spell):
    def __init__(self):
        spellName = "Summon BK"
        spellCost = 2
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = BloodkinVal
        
    def play(self, gameState, currSide):
        gameState.activePlayer.currPP -= self.cost
        genericSummon(ForestBat(), gameState, currSide)
        genericSummon(ForestBat(), gameState, currSide)

class CatMaids(Monster):
    def __init__(self):
        monsterName = "Cat Maids"
        cost = 2
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = MaidCatVal
        self.targetOptional = True
        self.numTargets = 1
        self.numAllyFollowerTargets = 1
        self.LWEffects.append(healFace(2))
    
    def play(self, gameState, currSide, targets):
        genericPlay(self, gameState, currSide)
        if (len(targets) > 0):
            if gameState.board.fullBoard[currSide][targets[0]].name == "Trill":
                gameState.board.fullBoard[currSide][targets[0]].freeEvolve = 1
                gameState.board.fullBoard[currSide][targets[0]].autoEvolve = 1
                gameState.board.fullBoard[currSide][targets[0]].evolve(gameState)
            
class DemonSong(Spell):
    def __init__(self):
        spellName = "Demon Song"
        spellCost = 3
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = DemonSongVal
        
    def play(self, gameState, currSide):
        gameState.activePlayer.currPP -= self.cost
        TrillExists = 0
        for ele in gameState.board.fullBoard[currSide]:
            if isinstance(ele, Trill):
                TrillExists = 1
                break
        if TrillExists == 1:
            AoEEnemy3(gameState)
        else:
            AoEEnemy2(gameState)

class Trill(Monster):
    def __init__(self):
        monsterName = "Trill"
        cost = 0
        monsterAttack = 3
        monsterMaxHP = 3
        monsterCurrHP = 3
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = TrillVal 
        self.numTargets = 2
        self.numChooseTargets = 2
    
    def play(self, gameState, currSide, targets):
        genericPlay(self, gameState, currSide)
        if targets[0] == 0:
            gameState.activePlayer.hand.append(CatMaids())
        else:
            gameState.activePlayer.hand.append(DemonSong())

def divaStrikeEffect(gameState, index):
    selfPing(1)(gameState)
    enemyPing(1)(gameState, gameState.activePlayer.playerNum - 1)
    selfPing(1)(gameState)
    enemyPing(1)(gameState, gameState.activePlayer.playerNum - 1)
    selfPing(1)(gameState)
    enemyPing(1)(gameState, gameState.activePlayer.playerNum - 1)
    gameState.activePlayer.restoreHP(gameState, 5) 

class Diva(Monster):
    def __init__(self):
        monsterName = "Diva"
        cost = 0
        monsterAttack = 3
        monsterMaxHP = 3
        monsterCurrHP = 3
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = DivaVal
    
    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        if (gameState.activePlayer.selfPings >= 7):
            self.freeEvolve = 1
            self.autoEvolve = 1
            self.evolve(gameState)
    
    def evolve(self, gameState):
        self.strikeEffects.append(divaStrikeEffect)
        genericEvolve(self, gameState)

def liberteEffect(gameState):
    enemyPing(1)(gameState, gameState.activePlayer.playerNum - 1)
    gameState.activePlayer.restoreHP(gameState, 2)

# TODO: FIX THIS IF YOU WANT TO IMPLEMENT SWORD!!!!
class Liberte(Monster):
    def __init__(self):
        monsterName = "Liberte"
        cost = 2
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = LiberteVal
        self.onAllyEvoEffects.append(liberteEffect)

class StormWolf(Monster):
    def __init__(self):
        monsterName = "Storm Wolf"
        cost = 3
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = StormWolfVal
        self.hasStorm = 1
        self.canAttack = 1
        self.canAttackFace = 1

class Orchestration(Spell):
    def __init__(self):
        spellName = "Orchestration"
        spellCost = 0
        allyFollowerTargets = 1
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = OrchVal
        
    def play(self, gameState, currSide, targets):
        mons = gameState.board.fullBoard[currSide][targets[0]]
        mons.maxHP += 1
        mons.currHP += 1
        mons.currAttack += 1
        if mons.hasAttacked == 0:
            mons.canAttack = 1
        if (mons.turnPlayed == gameState.currTurn) and (mons.hasStorm == 0):
            mons.canAttackFace = 0
        gameState.activePlayer.draw(1)

##### EFFECT FUNCTIONS

def banishSelf(mons):
    return lambda gameState: mons.banish(gameState)

def healFace(val):
    return lambda gameState, side: gameState.player1.restoreHP(gameState, val) if side == 0 \
    else gameState.player2.restoreHP(gameState, val)

def healFaceActive(val):
    return lambda gameState: gameState.player1.restoreHP(gameState, val) if gameState.activePlayer.playerNum == 1 \
    else gameState.player2.restoreHP(gameState, val)

def divineShield(mons):
    return lambda gameState: mons.applyDivineShield()

def selfPing(val):
    return lambda gameState: gameState.activePlayer.takeEffectDamage(gameState, val)

def enemyPing(val):
    return lambda gameState, side: gameState.player2.takeEffectDamage(gameState, val) if side == 0 \
    else gameState.player1.takeEffectDamage(gameState, val)

def summonBat():
    x = ForestBat()
    return lambda gameState: genericSummon(x, gameState, gameState.activePlayer.playerNum-1)

def draw(val):
    return lambda gameState: gameState.activePlayer.draw(val)

def givePlus1Bats(gameState):
    if gameState.activePlayer.playerNum == 1:
        otherPlayer = gameState.player2
    else:
        otherPlayer = gameState.player1
    if otherPlayer.selfPings >= 7:
        for card in gameState.board.fullBoard[otherPlayer.playerNum - 1]:
            if isinstance(card,ForestBat):
                card.maxHP += 1
                card.currHP += 1
                card.currAttack += 1

def drawCondemn(gameState):
    index = 0
    for card in gameState.activePlayer.deck.cards:
        if len(card.traits) > 0 and card.traits[0] == "condemn":
            cardToDraw = gameState.activePlayer.deck.cards.pop(index)
            gameState.activePlayer.deck.shuffle()
            if (len(gameState.activePlayer.hand) < 9):
                gameState.activePlayer.hand.append(cardToDraw)
            break
        index += 1

def AoEEnemy(placeholder, gameState):
    for card in gameState.board.fullBoard[gameState.activePlayer.playerNum % 2]:
        card.takeEffectDamage(gameState, 1)

def AoEEnemy2(gameState):
    for card in gameState.board.fullBoard[gameState.activePlayer.playerNum % 2]:
        card.takeEffectDamage(gameState, 2)

def AoEEnemy3(gameState):
    for card in gameState.board.fullBoard[gameState.activePlayer.playerNum % 2]:
        card.takeEffectDamage(gameState, 3)

def AoEEnemy5(gameState):
    for card in gameState.board.fullBoard[gameState.activePlayer.playerNum % 2]:
        card.takeEffectDamage(gameState, 5)

##### MAIN DECK MONSTERS

class BellRinger(Monster):
    def __init__(self):
        monsterName = "Bell Ringer (W)"
        cost = 2
        monsterAttack = 0
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = BellRingerVal

        def evolve(self, gameState):
            genericEvolve(self, gameState)
            gameState.activePlayer.draw(1)
            gameState.clearQueue()
        
        self.hasWard = 1
        self.LWEffects.append(LWDraw(1))

class Mummy(Monster):
    def __init__(self):
        monsterName = "Mummy"
        cost = 2
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = MummyVal

        def play(self, gameState, currSide):
            if gameState.activePlayer.shadows >= 4:
                self.hasStorm = 1
                gameState.activePlayer.shadows -= 4

class Veight(Monster):
    def __init__(self):
        monsterName = "Veight"
        cost = 4
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = VeightVal

        self.evoEnemyFollowerTargets = 1
        self.superEvoEnemyFollowerTargets = 1
        self.enemyTurnStartEffects.append(givePlus1Bats)
    
    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        selfPing(1)(gameState)
        genericSummon(ForestBat(), gameState, currSide)
        gameState.activePlayer.draw(1)
        selfPing(1)(gameState)
        genericSummon(ForestBat(), gameState, currSide)
        gameState.activePlayer.draw(1)


    def evolve(self, gameState, target, *args, **kwargs):
        genericEvolve(self, gameState)
            
        enemyPlayer = gameState.activePlayer.playerNum % 2
        if (len(target) > 0) and (len(gameState.board.fullBoard[enemyPlayer]) > target[0]):
            gameState.board.fullBoard[enemyPlayer][target[0]].takeEffectDamage(gameState, 4)
        
        if (len(gameState.board.fullBoard[gameState.activePlayer.playerNum - 1]) == 5):
            return

        amuletSummoned = False
        deckIndex = 0
        for ele in gameState.activePlayer.deck.cards:
            if amuletSummoned:
                break
            if ele.isAmulet:
                cardToSummon = gameState.activePlayer.deck.cards.pop(deckIndex)
                genericSummon(cardToSummon, gameState, gameState.activePlayer.playerNum-1)
                amuletSummoned = True
            deckIndex += 1

#TODO: max 8 times
class RagingCommander(Monster):
    def __init__(self):
        monsterName = "Raging Comm"
        cost = 3
        monsterAttack = 3
        monsterMaxHP = 1
        monsterCurrHP = 1
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = RCVal
        self.traits.append("condemn")

        self.selfPingEffects.append(AoEEnemy)
        self.fanfareEffects.append(selfPing(1))
        self.fanfareEffects.append(drawCondemn)

    def evolve(self, gameState):
        genericEvolve(self, gameState)
        gameState.activePlayer.takeEffectDamage(gameState, 1)
        drawCondemn(gameState)
        if (gameState.activePlayer.currPP < gameState.activePlayer.maxPP):
            gameState.activePlayer.currPP += 1


class DrummerAccel(Spell):
    def __init__(self):
        spellName = "Drummer Accel"
        spellCost = 2
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = DrummerVal
        
    def play(self, gameState, currSide):
        genericSummon(Drummer(), gameState, currSide)
        selfPing(1)(gameState)
        genericSummon(Drummer(), gameState, currSide)
        selfPing(1)(gameState)
        gameState.activePlayer.currPP -= self.cost
        return

class Drummer(Monster):
    def __init__(self):
        monsterName = "Drummer (W)"
        cost = 5
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = DrummerVal

        self.hasWard = 1
        self.canAccel = True
        self.accelCost = 2
        self.accelCard = DrummerAccel()
        self.LWEffects.append(healFace(1))

    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        for _ in range(4):
            x = Drummer()
            genericSummon(x, gameState, currSide)
        if gameState.activePlayer.selfPings >= 7:
            self.freeEvolve = 1
            self.autoEvolve = 1
            self.evolve(gameState)
    
    # TODO: this is a bit scuffed and doesnt work with silence and probably work work with other protections
    def takeCombatDamage(self, gameState, damage):
        if self.isEvolved and damage > 2:
            return genericTakeDamage(self, gameState, 2)
        else:
            return genericTakeDamage(self, gameState, damage)

    def takeEffectDamage(self, gameState, damage):
        if self.isEvolved and damage > 2:
            return genericTakeDamage(self, gameState, 2)
        else:
            return genericTakeDamage(self, gameState, damage)
    
    def evolve(self, gameState):
        self.LWEffects = [healFace(2)]
        genericEvolve(self, gameState)

def vampyEffect(gameState, card):
    if card.name == "Forest Bat":
        card.hasBane = 1
        card.hasStorm = 1
        card.canAttack = 1
        if (card.side == 0):
            gameState.player2.takeEffectDamage(gameState, 1)
        else:
            gameState.player1.takeEffectDamage(gameState, 1)

class Vampy(Monster):
    def __init__(self):
        monsterName = "Vampy"
        cost = 2
        monsterAttack = 2
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = VampyVal

    # TODO: fanfareify + special venge
    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        if (len(gameState.activePlayer.hand) < 9):
            gameState.activePlayer.hand.append(GiftForBloodKin())
        if (gameState.activePlayer.selfPings >= 7) or (gameState.activePlayer.currHP <= 10):
            self.freeEvolve = 1
            if (len(gameState.activePlayer.hand) < 9):
                gameState.activePlayer.hand.append(SummonBloodKin())
    
    def evolve(self, gameState):
        self.onSummonEffects.append(vampyEffect)
        genericEvolve(self, gameState)
    
    def superEvolve(self, gameState):
        self.onSummonEffects.append(vampyEffect)
        genericSuperEvolve(self, gameState)
        
class HowlingDemon(Monster):
    def __init__(self):
        monsterName = "Howling Demon"
        cost = 5
        monsterAttack = 5
        monsterMaxHP = 5
        monsterCurrHP = 5
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = HowlingDemonVal
        self.fanfareEffects.append(AoEEnemy5)
        
    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        if (gameState.activePlayer.selfPings < 7):
            gameState.activePlayer.takeEffectDamage(gameState, 3)
        else:
            self.freeEvolve = 1
            self.autoEvolve = 1
            self.evolve(gameState) 

    def evolve(self, gameState):
        self.hasStorm = 1
        self.hasDrain = 1
        genericEvolve(self, gameState)
        self.maxHP -= 2
        self.currHP -= 2
        self.currAttack -= 2

def GaroEvoCon(card, gameState):
    if gameState.activePlayer.selfPingsTurn >= 4:
        for ele in gameState.board.fullBoard[gameState.activePlayer.playerNum-1]:
            if ele.name == "Garodeth":
                ele.freeEvolve = 1
                ele.autoEvolve = 1
                ele.evolve(gameState)
                ele.selfPingEffects = []

class Garodeth(Monster):
    def __init__(self):
        monsterName = "Garodeth"
        cost = 4
        monsterAttack = 4
        monsterMaxHP = 4
        monsterCurrHP = 4
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = GarodethVal
        self.numTargets = 1
        self.numEnemyFollowerTargets = 1
        self.fanfareTargetFace = True
        self.canEvolve = 0
        self.traits.append("condemn")
        self.selfPingEffects.append(GaroEvoCon)
    
    def play(self, gameState, currSide, targets):
        genericPlay(self, gameState, currSide)
        selfPing(1)(gameState)
        if (targets[0] == -1):
            if (currSide == 0):
                gameState.player2.takeEffectDamage(gameState, 3)
            else:
                gameState.player1.takeEffectDamage(gameState, 3)
        else:
            gameState.board.fullBoard[(currSide+1) % 2][targets[0]].takeEffectDamage(gameState, 3)

    def evolve(self, gameState):
        self.hasStorm = 1
        genericEvolve(self, gameState)
        self.maxHP += 2
        self.currHP += 2
        self.currAttack += 2

def flauBuff(gameState, index):
    if gameState.activePlayer.selfPings >= 7:
        gameState.board.fullBoard[gameState.activePlayer.playerNum - 1][index].currAttack += 2

class Flautist(Monster):
    def __init__(self):
        monsterName = "Flautist"
        cost = 1
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = FlautistVal
        self.strikeEffects.append(flauBuff)
        self.fanfareEffects.append(selfPing(1))
        self.hasDrain = 1
        self.hasRush = 1
        self.canAttack = 1
        self.canAttackFace = 0

def tankHeal(card, gameState):
    if (card.effActivations < card.maxEffPerTurn):
        gameState.activePlayer.restoreHP(gameState, 1)
        card.effActivations += 1

class Tank(Monster):
    def __init__(self):
        monsterName = "Tank"
        cost = 1
        monsterAttack = 0
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = TankVal
        self.hasWard = 1
        self.traits.append("condemn")
        self.selfPingEffects.append(tankHeal)
        self.fanfareEffects.append(selfPing(1))

def LWDraw(val):
    return lambda gameState, side: gameState.player1.draw(val) if side == 0 \
    else gameState.player2.draw(val)

class HarmonicWolf(Monster):
    def __init__(self):
        monsterName = "Harmonic Wolf"
        cost = 1
        monsterAttack = 1
        monsterMaxHP = 2
        monsterCurrHP = 2
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = HarmonicVal
        self.fanfareEffects.append(selfPing(1))
        self.LWEffects.append(LWDraw(1))

def maestroLeaderEff(gameState):
    gameState.activePlayer.takeEffectDamage(gameState, 1)
    gameState.activePlayer.draw(1)

class Maestro(Monster):
    def __init__(self):
        monsterName = "Maestro"
        cost = 2
        monsterAttack = 1
        monsterMaxHP = 1
        monsterCurrHP = 1
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = MaestroVal

    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        if (gameState.activePlayer.selfPings < 7):
            gameState.activePlayer.takeEffectDamage(gameState, 1)
            gameState.activePlayer.draw(1)
        elif (len(gameState.activePlayer.hand) < 9):
            gameState.activePlayer.hand.append(Orchestration())
    
    def destroy(self, gameState):
        if (self.side == 0):
            gameState.player1.leaderEffects.turnStartEffects.append([maestroLeaderEff, 1])
        else:
            gameState.player2.leaderEffects.turnStartEffects.append([maestroLeaderEff, 1])
        genericDestroy(self, gameState)

def lunelleStrike(gameState, index):
    AoEEnemy(None,gameState)
    selfPing(1)(gameState)
    enemyPing(1)(gameState, gameState.activePlayer.playerNum - 1)
    AoEEnemy(None,gameState)
    selfPing(1)(gameState)
    enemyPing(1)(gameState, gameState.activePlayer.playerNum - 1)

class Lunelle(Monster):
    def __init__(self):
        monsterName = "Lunelle"
        cost = 4
        monsterAttack = 3
        monsterMaxHP = 3
        monsterCurrHP = 3
        Monster.__init__(self, cost, monsterAttack, monsterMaxHP, monsterCurrHP, monsterName)
        self.encoding = LunelleVal

    def play(self, gameState, currSide):
        genericPlay(self, gameState, currSide)
        genericSummon(Liberte(), gameState, currSide)
        if (gameState.activePlayer.currPP >= 3):
            gameState.activePlayer.currPP -= 3
            genericSummon(StormWolf(), gameState, currSide)
            if (gameState.activePlayer.selfPings >= 7):
                for ele in gameState.board.fullBoard[currSide]:
                    if isinstance(ele,Monster) and ele.isEvolved == 0:
                        ele.freeEvolve = 1
                        ele.autoEvolve = 1
                        #TODO: obviously this might be a problem in the future, figure out a better method
                        if (ele.name == "Veight"):
                            genericEvolve(ele, gameState)
                        else:
                            ele.evolve(gameState)

    def evolve(self, gameState):
        genericEvolve(self, gameState)
        self.strikeEffects.append(lunelleStrike)

##### MAIN DECK AMULETS
def castleEff(gameState):
    if gameState.activePlayer.selfPings >= 7:
        gameState.activePlayer.restoreHP(gameState, 3)
    else:
        gameState.activePlayer.takeEffectDamage(gameState, 1)

def summonBatWithWard(card, gameState):
    if (card.effActivations < card.maxEffPerTurn):
        newBat = ForestBat()
        newBat.hasWard = 1
        genericSummon(newBat, gameState, gameState.activePlayer.playerNum - 1)
        card.effActivations += 1

class VampireQueenCastle(Amulet):
    def __init__(self):
        name = "Castle"
        cost = 2
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        isCountdown = True
        countdown = 2
        Amulet.__init__(self, name, cost, allyFollowerTargets, enemyFollowerTargets, isCountdown, countdown)
        self.encoding = CastleVal
        self.turnEndEffects.append(castleEff)
        self.selfPingEffects.append(summonBatWithWard)
        self.maxEffPerTurn = 1


###### MAIN DECK SPELLS
class HowlingScream(Spell):
    def __init__(self):
        spellName = "Scream"
        spellCost = 1
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = ScreamVal
        
    def play(self, gameState, currSide):
        gameState.activePlayer.currPP -= self.cost
        selfPing(1)(gameState)
        #TODO: make this a general RNG method
        availTargets = []
        currIndex = 0
        for item in gameState.board.fullBoard[(currSide+1) % 2]:
            if not item.isAmulet:
                availTargets.append(currIndex)
            currIndex += 1
        if (len(availTargets) > 0):
            if self.rigRNG:
                gameState.board.fullBoard[(currSide+1) % 2][self.riggedVal].takeEffectDamage(gameState, 1)
            else:
                myseed = 1223234
                if (len(gameState.activePlayer.deck.cards) >= 5):
                    for ind in range(5):
                        myseed += (1234 * gameState.activePlayer.deck.cards[len(gameState.activePlayer.deck.cards) - 1 - ind].encoding)
                random.seed(myseed)
                randomTarget = random.choice(availTargets)
                gameState.board.fullBoard[gameState.activePlayer.playerNum % 2][randomTarget].takeEffectDamage(gameState, 1)
        gameState.activePlayer.draw(1)

class Rhapsody(Spell):
    def __init__(self):
        spellName = "Rhapsody"
        spellCost = 5
        allyFollowerTargets = 0
        enemyFollowerTargets = 0
        Spell.__init__(self, spellName, spellCost, allyFollowerTargets, enemyFollowerTargets)
        self.encoding = RhapsodyVal

    def play(self, gameState, currSide):
        gameState.activePlayer.currPP -= self.cost
        if (len(gameState.activePlayer.hand) < 9):
            gameState.activePlayer.hand.append(Trill())
        if (len(gameState.activePlayer.hand) < 9):
            gameState.activePlayer.hand.append(Diva())
