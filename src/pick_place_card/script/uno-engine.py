#!/usr/bin/env python
import random
import time
from naoqi_bridge_msgs.msg import SpeechWithFeedbackActionGoal,WordRecognized
import rospy

class NAOTalk:

    def __init__(self):

        rospy.init_node('nao_talk', anonymous=True)
        self.rate = rospy.Rate(1)
        self.speech_pub = rospy.Publisher("/speech_action/goal", SpeechWithFeedbackActionGoal, queue_size=10)
        self.talk_phrases = {
            'draw_cards': [
                "Looks like you've got an armful there!",
                "I need to draw a card, none of mine can be played",
                "Drawing cards, are we? I hope you find what you're looking for!"
            ],
            'uno_call': [
                "UNO! I'm just one card away from victory!",
                "Just between us, I've always been good at this part.",
                "UNO! Did I just say random that out loud?"
            ],
            'winning': [
                "And that's how it's done!",
                "Victory is mine! Better luck next time.",
                "I guess I'm just programmed to win."
            ],                                                                                             
            'losing': [
                "You got me this time!",
                "Well played! I'll get you in the next round.",
                "I'm letting you win, you know."
            ],
            'starter': [ 
                "Hello, let's play UNO! I hope you are ready for a challange",
                "Welcome to our UNO game. I am excited to see who will win",
                "Ready to start the game, Can someone shuffle the cards?"

            ],
            'last_card_action' : [
                "Last card cannot be an action card. Let me draw a card."
            ],
            'throw_card' : [
                "Hmm, Let me see which card to play",
                "I think this card will do nicely",
            ],


        }


    def run_speech(self, event_type):
            
            talk_line = random.choice(self.talk_phrases[event_type])
            
            # Construct the speech goal message
            talk_msg = SpeechWithFeedbackActionGoal()
            talk_msg.goal_id.id = str(rospy.Time.now().to_sec())
            talk_msg.goal.say = talk_line
            
            # Publish the trash talk line
            self.speech_pub.publish(talk_msg)
            rospy.sleep(10)

    def run_given_speech(self, input_speech):
            
            
            # Construct the speech goal message
            talk_msg = SpeechWithFeedbackActionGoal()
            talk_msg.goal_id.id = str(rospy.Time.now().to_sec())
            talk_msg.goal.say = input_speech
            
            # Publish the trash talk line
            self.speech_pub.publish(talk_msg)
            rospy.sleep(10)

    



color = ('RED','GREEN','BLUE','YELLOW',)
rank = ('0','1','2','3','4','5','6','7','8','9','Skip','Reverse','Draw2','Draw4','Wild')
ctype = {'0':'number','1':'number','2':'number','3':'number','4':'number','5':'number','6':'number',
            '7':'number','8':'number','9':'number','Skip':'action','Reverse':'action','Draw2':'action',
            'Draw4':'action_nocolor','Wild':'action_nocolor'}


class Card:

    def __init__(self, color, rank):
        self.rank = rank
        if ctype[rank] == 'number':
            self.color = color
            self.cardtype = 'number'
        elif ctype[rank] == 'action':
            self.color = color
            self.cardtype = 'action'
        else:
            self.color = None
            self.cardtype = 'action_nocolor'

    def __str__(self):
        if self.color == None:
            return self.rank
        else:
            return self.color + " " + self.rank
class Deck:
    def __init__(self):
        self.deck = []
        for clr in color:
            for ran in rank:
                if ctype[ran] != 'action_nocolor':
                    self.deck.append(Card(clr, ran))
                    self.deck.append(Card(clr, ran))
                else:
                    self.deck.append(Card(clr, ran))   

    def __str__(self):
        deck_comp = ''
        for card in self.deck:
            deck_comp += '\n' + card.__str__()
        return 'The deck has ' + deck_comp

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        return self.deck.pop()

class NAOHand:

    def __init__(self):
        self.cards = []
        self.cardsstr = []
        self.number_cards = 0
        self.action_cards = 0

    def add_card(self, card):
        self.cards.append(card)
        self.cardsstr.append(str(card))
        if card.cardtype == 'number':
            self.number_cards += 1
        else:
            self.action_cards += 1

    def remove_card(self, place):
        self.cardsstr.pop(place - 1)
        return self.cards.pop(place - 1)

    def cards_in_hand(self):
        for i in range(len(self.cardsstr)):
            print(' {}.{}'.format(i+1, self.cardsstr[i]))

    def single_card(self, place):
        return self.cards[place - 1]

    def no_of_cards(self):
        return len(self.cards)

#Funciton to randomly select who starts first
def choose_first():
    if random.randint(0,1)==0:
        return 'Player'
    else:
        return 'NAO'


#Function to check if the card thrown by NAO/Player is a valid card by comparing it with the top card
def single_card_check(top_card,card):
    if card.color==top_card.color or top_card.rank==card.rank or card.cardtype=='action_nocolor':
        return True
    else:
        return False

#To check if NAO has any valid card to throw
def full_hand_check(hand,top_card):
    for c in hand.cards:
        if c.color==top_card.color or c.rank == top_card.rank or c.cardtype=='action_nocolor':
            return hand.remove_card(hand.cardsstr.index(str(c))+1)
    else:
        return 'no card'

#To check if NAO wins
def win_check(hand):
    if len(hand.cards)==0:
        return True
    else:
        return False

#Function to check if last card is an action card (GAME MUST END WITH A NUMBER CARD)
def last_card_check(hand):
    for c in hand.cards:
        if c.cardtype!='number':
            return True
        else:
            return False


def main():
    nao_hand = NAOHand()
    top_card = None
    nao_talk = NAOTalk()
    player_hand = NAOHand()
    deck = Deck()
    # rospy.spin()

    while True:

        # NAO SPEECH 
        event_type = 'starter'
        nao_talk.run_speech(event_type)

        ###### Computer vision system integration here
        ### Let's say there is a function for detecting the cards
        #top_card = get_top_card()
        #new_cards = get_new_cards()
        ############
        #for card in new_cards:
            #nao_hand.add_card(card)
        

        deck.shuffle()

        for i in range(7):
            player_hand.add_card(deck.deal())
        for i in range(7):
            nao_hand.add_card(deck.deal())

        top_card = deck.deal()
        if top_card.cardtype != 'number':
            while top_card.cardtype != 'number':
                top_card = deck.deal()
            
        print('\nStarting Card is: {}'.format(top_card))
        time.sleep(1)

        # NAO SPEECH 
        say = str("Starting Card is" + str(top_card))
        nao_talk.run_given_speech(say)
        playing = True

        turn = choose_first()
        print(turn + ' will go first')
        #NAO SPEECH 
        say = str(str(turn) + "will go first")
        nao_talk.run_given_speech(say)


        while playing:

            if turn == 'Player':
                print('\nTop card is: ' + str(top_card))
                print('Your cards: ')
                player_hand.cards_in_hand()
                if player_hand.no_of_cards() == 1:
                    if last_card_check(player_hand):
                        print('Last card cannot be action card \nAdding one card from deck')
                        player_hand.add_card(deck.deal())
                        print('Your cards: ')
                        player_hand.cards_in_hand()
                choice = input("\nHit or Pull? (h/p): ")
                if choice == 'h':
                    pos = int(input('Enter index of card: '))
                    temp_card = player_hand.single_card(pos)
                    if single_card_check(top_card, temp_card):
                        if temp_card.cardtype == 'number':
                            top_card = player_hand.remove_card(pos)
                            turn = 'NAO'
                        else:
                            if temp_card.rank == 'Skip':
                                turn = 'Player'
                                top_card = player_hand.remove_card(pos)
                            elif temp_card.rank == 'Reverse':
                                turn = 'Player'
                                top_card = player_hand.remove_card(pos)
                            elif temp_card.rank == 'Draw2':
                                nao_hand.add_card(deck.deal())
                                nao_hand.add_card(deck.deal())
                                top_card = player_hand.remove_card(pos)
                                turn = 'Player'
                            elif temp_card.rank == 'Draw4':
                                for i in range(4):
                                    nao_hand.add_card(deck.deal())
                                top_card = player_hand.remove_card(pos)
                                draw4color = input('Change color to (enter in caps): ')
                                if draw4color != draw4color.upper():
                                    draw4color = draw4color.upper()
                                top_card.color = draw4color
                                turn = 'Player'
                            elif temp_card.rank == 'Wild':
                                top_card = player_hand.remove_card(pos)
                                wildcolor = input('Change color to (enter in caps): ')
                                if wildcolor != wildcolor.upper():
                                    wildcolor = wildcolor.upper()
                                top_card.color = wildcolor
                                turn = 'NAO'
                    else:
                        print('This card cannot be used')
                elif choice == 'p':
                    temp_card = deck.deal()
                    print('You got: ' + str(temp_card))
                    time.sleep(1)
                    if single_card_check(top_card, temp_card):
                        player_hand.add_card(temp_card)
                    else:
                        print('Cannot use this card')
                        player_hand.add_card(temp_card)
                        turn = 'NAO'
                if win_check(player_hand):
                    print('\nPLAYER WON!!')
                    playing = False
                    break
            
            if turn == 'NAO':
                if nao_hand.no_of_cards() == 1:
                    if last_card_check(nao_hand):
                        time.sleep(1)
                        print('Adding a card to NAO hand')
                        nao_hand.add_card(deck.deal())
                temp_card = full_hand_check(nao_hand, top_card)
                time.sleep(1)
                if temp_card != 'no card':
                    print('\nNAO throws:{}'.format(temp_card))
                    time.sleep(1)
                    if temp_card.cardtype == 'number':
                        top_card = temp_card
                        #NAO Speech
                        say = str(str(top_card) + "is on the top." )
                        nao_talk.run_given_speech(say)
                        turn = 'Player'
                    else:
                        if temp_card.rank == 'Skip':
                            turn = 'NAO'
                            top_card = temp_card
                        elif temp_card.rank == 'Reverse':
                            turn = 'NAO'
                            top_card = temp_card
                        elif temp_card.rank == 'Draw2':
                            player_hand.add_card(deck.deal())
                            player_hand.add_card(deck.deal())
                            top_card = temp_card
                            turn = 'NAO'
                        elif temp_card.rank == 'Draw4':
                            for i in range(4):
                                player_hand.add_card(deck.deal())
                            top_card = temp_card
                            draw4color = nao_hand.cards[0].color
                            print('Color changes to', draw4color)
                            top_card.color = draw4color
                            
                        elif temp_card.rank == 'Wild':
                            top_card = temp_card
                            wildcolor = nao_hand.cards[0].color
                            print("Color changes to", wildcolor)
                            top_card.color = wildcolor
                            turn = 'Player'
                else:
                    print('\nNAO wants to pull a card from deck')
                    time.sleep(1)
                    temp_card = deck.deal() #here change with the computer vision

                    if single_card_check(top_card, temp_card):
                        print('\nNAO has option to throw:{}'.format(temp_card))
                        time.sleep(1)
                        if temp_card.cardtype == 'number':
                            top_card = temp_card
                            turn = 'Player'
                        else:
                            if temp_card.rank == 'Skip':
                                turn = 'NAO'
                                top_card = temp_card
                            elif temp_card.rank == 'Reverse':
                                turn = 'NAO'
                                top_card = temp_card
                            elif temp_card.rank == 'Draw2':
                                player_hand.add_card(deck.deal())
                                player_hand.add_card(deck.deal())
                                top_card = temp_card
                                turn = 'NAO'
                            elif temp_card.rank == 'Draw4':
                                for i in range(4):
                                    player_hand.add_card(deck.deal())
                                top_card = temp_card
                                draw4color = nao_hand.cards[0].color
                                print('Color changes to', draw4color)
                                top_card.color = draw4color
                                turn = 'NAO'
                            elif temp_card.rank == 'Wild':
                                top_card = temp_card
                                wildcolor = nao_hand.cards[0].color
                                print('Color changes to', wildcolor)
                                top_card.color = wildcolor
                                turn = 'Player'
                    else:
                        print('NAO doesnt have a card')
                        time.sleep(1)
                        nao_hand.add_card(temp_card)
                        turn = 'Player'
                print('\nNAO has {} cards remaining'.format(nao_hand.no_of_cards()))
                time.sleep(1)
                if win_check(nao_hand):
                    print('\nNAO WON!!')
                    playing = False

        new_game = input('Would you like to play again? (y/n)')
        if new_game == 'y':
            continue
        else:
            print('\nThanks for playing!!')
            break    





if __name__ == '__main__':
	main()
     


        