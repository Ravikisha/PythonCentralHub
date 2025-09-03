# Text-based Blackjack Game

import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def value(self):
        if self.rank in ['Jack', 'Queen', 'King']:
            return 10
        elif self.rank == 'Ace':
            return 11  # Will be handled in Hand class
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        self.cards = []
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal_card(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0
    
    def add_card(self, card):
        self.cards.append(card)
        self.value += card.value()
        
        # Track aces
        if card.rank == 'Ace':
            self.aces += 1
        
        # Adjust for aces
        self.adjust_for_ace()
    
    def adjust_for_ace(self):
        # If total value > 21 and we have aces, convert ace from 11 to 1
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1
    
    def __str__(self):
        hand_str = "Hand contains:\n"
        for card in self.cards:
            hand_str += f"  {card}\n"
        hand_str += f"Total value: {self.value}"
        return hand_str

class Chips:
    def __init__(self, total=100):
        self.total = total
        self.bet = 0
    
    def win_bet(self):
        self.total += self.bet
    
    def lose_bet(self):
        self.total -= self.bet

def take_bet(chips):
    while True:
        try:
            chips.bet = int(input(f"You have {chips.total} chips. How many would you like to bet? "))
        except ValueError:
            print("Sorry, please enter a valid number!")
        else:
            if chips.bet > chips.total:
                print(f"Sorry, you only have {chips.total} chips!")
            else:
                break

def hit(deck, hand):
    hand.add_card(deck.deal_card())

def hit_or_stand(deck, hand):
    global playing
    
    while True:
        choice = input("\nWould you like to Hit or Stand? Enter 'h' or 's': ").lower()
        
        if choice == 'h':
            hit(deck, hand)
        elif choice == 's':
            print("Player stands. Dealer is playing.")
            playing = False
        else:
            print("Sorry, please try again.")
            continue
        break

def show_some(player, dealer):
    print("\nDealer's Hand:")
    print(" <card hidden>")
    print(f" {dealer.cards[1]}")
    print(f"\nPlayer's Hand: {player.value}")
    for card in player.cards:
        print(f" {card}")

def show_all(player, dealer):
    print("\nDealer's Hand:", dealer.value)
    for card in dealer.cards:
        print(f" {card}")
    print(f"\nPlayer's Hand: {player.value}")
    for card in player.cards:
        print(f" {card}")

def player_busts(player, dealer, chips):
    print("Player busts! Dealer wins!")
    chips.lose_bet()

def player_wins(player, dealer, chips):
    print("Player wins!")
    chips.win_bet()

def dealer_busts(player, dealer, chips):
    print("Dealer busts! Player wins!")
    chips.win_bet()

def dealer_wins(player, dealer, chips):
    print("Dealer wins!")
    chips.lose_bet()

def push(player, dealer):
    print("Dealer and Player tie! It's a push.")

# Game Logic
def play_blackjack():
    global playing
    playing = True
    
    print("Welcome to BlackJack! Get as close to 21 as you can without going over!")
    print("Dealer hits until she reaches 17. Aces count as 1 or 11.")
    
    # Create & shuffle the deck, deal two cards to each player
    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand()
    
    player_hand.add_card(deck.deal_card())
    player_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    
    # Set up the Player's chips
    player_chips = Chips()
    
    # Prompt the Player for their bet
    take_bet(player_chips)
    
    # Show cards (but keep one dealer card hidden)
    show_some(player_hand, dealer_hand)
    
    while playing:  # recall this variable from our hit_or_stand function
        
        # Prompt for Player to Hit or Stand
        hit_or_stand(deck, player_hand)
        
        # Show cards (but keep one dealer card hidden)
        show_some(player_hand, dealer_hand)
        
        # If player's hand exceeds 21, run player_busts() and break out of loop
        if player_hand.value > 21:
            player_busts(player_hand, dealer_hand, player_chips)
            break
    
    # If Player hasn't busted, play Dealer's hand until Dealer reaches 17
    if player_hand.value <= 21:
        
        while dealer_hand.value < 17:
            hit(deck, dealer_hand)
        
        # Show all cards
        show_all(player_hand, dealer_hand)
        
        # Run different winning scenarios
        if dealer_hand.value > 21:
            dealer_busts(player_hand, dealer_hand, player_chips)
        
        elif dealer_hand.value > player_hand.value:
            dealer_wins(player_hand, dealer_hand, player_chips)
        
        elif dealer_hand.value < player_hand.value:
            player_wins(player_hand, dealer_hand, player_chips)
        
        else:
            push(player_hand, dealer_hand)
    
    # Inform Player of their chips total
    print(f"\nPlayer's winnings stand at {player_chips.total}")
    
    # Ask to play again
    new_game = input("Would you like to play another hand? Enter 'y' or 'n': ").lower()
    if new_game == 'y':
        playing = True
        play_blackjack()
    else:
        print("Thanks for playing!")

if __name__ == "__main__":
    play_blackjack()
