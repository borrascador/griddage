class Card:
    def __init__(self, suit=0, rank=1):
        self.suit = suit
        self.rank = rank
        if suit != None and rank != None:
            self.source = 'cards/s{}r{}.png'.format(self.suit, self.rank)
        else:
            self.source = 'cards/back1.png'

    def __str__(self):
        return 's{}r{}'.format(self.suit, self.rank)



class Deck:

    def __init__(self):
        self.cards = []
        for suit in range(4):
            for rank in range(1,14):
                self.cards.append(Card(suit, rank))

    def __str__(self):
        s = ''
        for i in range(len(self.cards)):
            s = s + ' '*i + str(self.cards[i]) + '\n'
        return s

    def shuffle(self):
        import random
        nCards = len(self.cards)
        for i in range(nCards):
            j = random.randrange(i, nCards)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def pop_card(self):
        return self.cards.pop()

    def is_empty(self):
        return (len(self.cards) == 0)

    def deal(self, hands, nCards=24):
        nHands = len(hands)
        for i in range(nCards):
            if self.is_empty(): break    # break if out of cards
            card = self.pop_card()       # take the top card
            hand = hands[i % nHands]     # whose turn is next?
            hand.add_card(card)          # add the card to the hand
