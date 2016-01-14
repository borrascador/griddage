class Card:
   
    def __init__(self, suit=0, rank=1):
        self.suit = suit
        self.rank = rank

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



class Hand(Deck):

    def __init__(self, name=""):
        self.cards = []
        self.name = name

    def add_card(self, card):
        self.cards.append(card)

    def pop_card(self):
        if len(self.cards) > 0:
            return self.cards.pop()

    def __str__(self):
        s = "Hand " + self.name
        if self.is_empty():
            return s + " is empty\n"
        else:
            return s + " contains\n" + Deck.__str__(self)



class Game:
    
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.p1 = Hand('Anna')
        self.p2 = Hand('Jan')
        self.deck.deal([self.p1, self.p2])
        self.starter = self.deck.pop_card()
##        print self.p1
##        print self.p2
##        print self.starter

if __name__ == '__main__':
    game = Game()
