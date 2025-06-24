# A Card is a superclass of Monster and Spell and Amulet
# A very generic class to encapsulate all card types

class Card:
  def __init__(self, cost, name):
    self.cost = cost
    self.name = name

  def __str__(self):
    return self.name
