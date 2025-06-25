import sys
sys.path.insert(0, './cardArchive/')


import pickle
from deck import Deck
from cardsSimple import *
from abyssCards import *

deck1 = [[Tank, 3],
         [BellRinger, 3],
         [HarmonicWolf, 3],
         [HowlingScream, 3],
         [Vampy, 3],
         [Maestro, 3],
         [VampireQueenCastle, 3],
         [RagingCommander, 3],
         [Veight, 3],
         [Garodeth, 3],
         [Lunelle, 2],
         [Drummer, 3],
         [HowlingDemon, 3],
         [Rhapsody, 2]]

with open("deck2.deck", "wb") as f:
    pickle.dump(deck1, f)
