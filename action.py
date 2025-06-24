# An Action is one of the following:

# -Playing a card (with targets if applicable)
# -Attacking with a follower (with target)
# -Evolving a follower (with target if applicable)
# -Ending turn

# The current implementation is a simple array of size 3:

# first index is:
# Play card: 1
# Initiate attack: 2
# Evolve follower: 3
# End turn: 4

# The second index is the indicator number for the card the current player is selecting

# The third index is an array of targets in order



