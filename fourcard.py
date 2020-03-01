import numpy as np

ALL_CARDS = ['{}{}'.format(c,n) for c in ('♠', '♣', '♥', '♦')
         for n in ('A',2,3,4,5,6,7,8,9,10,'J','Q','K')]

def PlayedJack(table, played_card):
    # Update table as a result
    choices = []
    choice = set()
    choice.add(played_card)

    # take non face cards
    for card in table:
        if card[1] not in ('J', 'Q', 'K'):
            choice.add(card)

    for card in table:
        # TODO does a Jack take off other jacks?
        if 'J' in card[1]:
            choice_n = set(choice)
            choice_n.add(card)
            choices.append(choice_n)

    # Check for no other jacks condition, but there were non-facecards.
    if len(choices) == 0 and len(choice) > 1:
        choices.append( choice )

    return choices

def PlayedRoyalty(table, played_card):
    # Update table as a result
    choices = []
    choice = set()
    choice.add(played_card)

    for card in table:
        # TODO does a Jack take off other jacks?
        if played_card[1] in card[1]:
            choice_n = set(choice)
            choice_n.add(card)
            choices.append(choice_n)

    return choices

def PlayedRegularCard(table, played_card):
    def card_sum( cards ):
        total = 0
        for card in cards:
            if card[1] == 'A':
                total += 1
            elif card[1] not in 'JQK':
                total += int(card[1:])
        return total

    def recursive_add( candidates, cards, choices ):
        print('Considering', candidates, cards, choices)
        total = card_sum(candidates)
        if total > 11:
            return
        elif total == 11:
            print('Found', candidates)
            choices.append(candidates)
            return
        elif len(cards) == 0:
            return

        for idx in range(len(cards)):
            new_cards = list(cards)
            new_candidates = list(candidates)
            new_candidates.append( new_cards.pop(idx) )
            recursive_add(new_candidates, new_cards, choices)

    choices = []
    candidates = [played_card]
    cards = sorted([card for card in table if card[1] not in 'JQK'])

    # Find all combinations of 11 that start with the played card
    recursive_add( candidates, cards, choices )

    # TODO here, error with unhashable type
    # Get rid of duplicates
    #unique_choices = set()
    #for choice in choices:
    #    unique_choices.add(list(choice))
    #choices = map(set, unique_choices)

    return choices

class GameState(object):
    def __init__(self):
        self.deck = list(np.random.permutation(ALL_CARDS))
        self.table = set()

        self.hands = [set(), set()]
        self.tricks = [set(), set()]

    def __str__(self):
        deck = 'Deck: ' + ' '.join(self.deck)
        table = 'Table: ' + ' '.join(sorted(self.table))
        hand1 = 'Hand1: ' + ' '.join(sorted(self.hands[0]))
        trick1 = 'Trick1: ' + ' '.join(sorted(self.tricks[0]))
        hand2 = 'Hand2: ' + ' '.join(sorted(self.hands[1]))
        trick2 = 'Trick2: ' + ' '.join(sorted(self.tricks[1]))
        return '{}\n{}\n{}\n{}\n{}\n{}'.format(deck, table, hand1, trick1, hand2,
                                       trick2)

    def deal(self, destination):
        for i in range(4):
            destination.add(self.deck.pop())

    def new_deal(self):
        self.deal( self.hands[0] )
        self.deal( self.hands[1] )

    def play(self, player, played_card):
        # Playing a card might require a choice on which cards to pull off.
        # So this function returns a list of choices of which one can be
        # chosen.

        # A played card definitely leaves the player's hand and ends up on the
        # table. It may come off.
        self.hands[player].discard(played_card)

        # Update table as a result
        choices = []
        if 'J' in played_card:
            choices.extend( PlayedJack( self.table, played_card ))
        if 'K' in played_card or 'Q' in played_card:
            choices.extend( PlayedRoyalty( self.table, played_card ))
        if played_card[1] not in 'JQK':
            choices.extend( PlayedRegularCard( self.table, played_card ))

        # Put it on the table after checking how it would interact with other
        # cards already there
        self.table.add(played_card)

        print("Choices:")
        for choice in choices:
            print(choice)
        return choices

    def apply_choice(self, player, choice):
        print('Applying', choice)
        self.tricks[player].update( choice )
        self.table.difference_update( self.tricks[player] )

        # TODO add logic for taking all cards
        # TODO add logic for last played card

    def score(self, player):
        total = 0
        trick = self.tricks[player]
        if '♦10' in trick:
            total += 3
        if '♣2' in trick:
            total += 2

        club_count = 0
        for card in trick:
            if '♣' in card:
                club_count += 1
        if club_count >= 7:
            total += 7

        for card in trick:
            if 'J' in card:
                total += 1
            if 'A' in card:
                total += 1

        # TODO add last card scoring

        return total

def main():
    pass

def get_played_card(state, player):
    print('Table: ' + ' '.join(sorted(list(state.table))))
    cards = sorted(list(state.hands[player]))
    print('Player {}, choose:'.format(player))
    for i in range(len(cards)):
        print('{}: {}'.format(i, cards[i]))

    print('> ', end='')
    index = int(input())
    if(index < 0):
        return 'quit'

    played_card = cards[index]
    print('...playing {}'.format(played_card))
    return played_card

def play_round( state, start_player ):
    player = start_player

    while (len(state.hands[0]) > 0) or (len(state.hands[1]) > 0):
        print(state)

        print('\nPlayer {} turn'.format(player))
        played_card = get_played_card(state, player)
        if played_card == 'quit':
            break

        choices = state.play(player, played_card)

        if len(choices) > 0:
            index = 0
            if len(choices) > 1:
                print('Which choice?')
                for idx in range(len(choices)):
                    print('{}: {}'.format(idx, choices[idx]))

                print('> ', end='')
                index = int(input())
                if(index < 0):
                    break

            state.apply_choice( player, choices[index] )
        else:
            print('All cards stayed on table')

        # Switch to next player, but switch back if they don't have cards
        player = (player+1)%2
        if len(state.hands[player]) == 0:
            player = (player+1)%2

if __name__ == "__main__":
    state = GameState()

    # Initialize the board
    state.deal( state.table )

    # Play out the deck
    while len(state.deck) > 0:
        state.new_deal()
        play_round( state, 0 )
    print()
    print('Player 1 score:', state.score(0))
    print('Player 2 score:', state.score(1))
