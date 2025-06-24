import random
import copy
import sys
import pickle
sys.path.insert(0, './cardArchive/')
from cardsSimple import *

class Deck:
    def __init__(self, deckname):
        self.deckName = deckname
        self.cards = []
        if (deckname != ""):
           self.deckFromFile()
    """
    def __deepcopy__(self, info):
        retVal = Deck("")
        retVal.cards = copy.deepcopy(self.cards)
        return retVal
    """
    # This is between games so that the deck is different
    def trueShuffle(self):
        random.shuffle(self.cards)

    def shuffle(self):
        # For training purposes, we use a seed so that MCTS works
        seed = 0
        if (len(self.cards) >= 5):
            for i in range(5):
                seed += self.cards[i].encoding
        else:
            seed = 123
        random.Random(seed).shuffle(self.cards)

    # This actually draws from the end of the deck, important to note
    def draw(self):
        if len(self.cards) > 0:
            cardDrawn = self.cards.pop()
            return cardDrawn
        else:
            return Reaper()

    # This is pretty dumb, but will work for now
    def __str__(self):
        for item in self.cards:
            print(item)
        return ""
    
    # For when the deck needs to be reset in between games
    # This is deprecated and no longer used probably, delete soon
    def refresh(self):
        self.deckFromFile()

    def deckFromFile(self):
        self.cards = []
        deck_file = open("./" + self.deckName + ".deck", "rb")
        deckData = pickle.load(deck_file)
        deck_file.close()

        for ele in deckData:
            if (len(ele) > 1):
                for _ in range(ele[1]):
                    self.cards.append(ele[0]())
            else:
                self.cards.append(ele[0]())

