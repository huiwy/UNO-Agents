# implementation reference: https://github.com/bennuttall/uno
from random import shuffle, choice, randint
from itertools import product, repeat, chain
from threading import Thread
from time import sleep


from game import *
from agents import *
from utils import constants

agent_scope = {"require_action":False,
         "update_hand": True,
         "action": None,
         "invalid_action": False,
         "select_color":False,
         "selected_color":None}

num_players = 3


color_dic = {'r':0, 'y':1, 'g':2, 'b':3}

h = GUIAgent(agent_scope)
g = GreedyAgent()

game = UNO([h, g, g], "fin", False, False)

WIDTH = 1200
HEIGHT = 800

global_scope = {"human_hand": [], "sprite_hand":[], "end": False}

deck_img = Actor('back')
color_imgs = {card: Actor(card.lower()) for card in constants.COLORS}

def game_loop():
    while True:
        while True:
            action = game.get_action()
            t = game.apply_action(action)
            agent_scope["update_hand"] = True
            if t:
                break
        if game.current_win():
            winner = game.current_player
            global_scope["end"] = True
            return winner
        sleep(1)
        game.next_player()
        game.penalize()
        agent_scope["update_hand"] = True

game_loop_thread = Thread(target=game_loop)
game_loop_thread.start()

def draw_deck():
    deck_img.pos = (130, 70)
    deck_img.draw()
    current_card = game.previous_card
    if current_card != None:
        if current_card in ['r', 'g', 'b', 'y']:
            sprite = Actor(current_card)
            sprite.pos = (210, 70)
            sprite.draw()
        else:
            sprite = Actor(INT2CARD[current_card].lower())
            sprite.pos = (210, 70)
            sprite.draw()
    if agent_scope["select_color"]:
        for i, card in enumerate(color_imgs.values()):
            card.pos = (290+i*80, 70)
            card.draw()
    # elif current_card.color == 'black' and current_card.temp_color is not None:
    #     color_img = color_imgs[current_card.temp_color]
    #     color_img.pos = (290, 70)
#         color_img.draw()

def draw_players_hands():
    for p, hand in game.hands.items():

        color = 'red' if p == 0 else 'black'
        text = 'P{}'.format(p)
        screen.draw.text(text, (10, 300+p*130), fontsize=100, color=color)


        if p == 0:
            if agent_scope["update_hand"]:
                # agent_scope["update_hand"] = False
                global_scope["sprite_hand"] = []
                global_scope["human_hand"] = []
                for i, n in enumerate(hand):
                    for _ in range(n):
                        global_scope["human_hand"].append(INT2CARD[i].lower())
                for i, c in enumerate(global_scope["human_hand"]):
                    global_scope["sprite_hand"].append(Actor(c))
                    global_scope["sprite_hand"][-1].pos = (130+i*80, 330+p*130)
                    global_scope["sprite_hand"][-1].draw()
            else:
                for c in global_scope["sprite_hand"]:
                    c.draw()

        else:
            counter = 0
            for i, n in enumerate(hand):
                for _ in range(n):
                    sprite = Actor('back')
                    sprite.pos = (130+counter*80, 330+p*130)
                    sprite.draw()
                    counter += 1

def update():
    screen.clear()
    screen.fill((20, 90, 50))
    draw_deck()
    draw_players_hands()
    show_log()

def show_log():
    if not global_scope["end"]:
        if agent_scope["invalid_action"]:
            screen.draw.text('You cannot play that card', midbottom=(WIDTH/2, HEIGHT-50), fontsize=70, color='black')
        else:
            screen.draw.text('P{}\'s Turn'.format(game.current_player), midbottom=(WIDTH/2, HEIGHT-50), fontsize=70, color='black')
    else:
        screen.draw.text('P{} wins'.format(game.current_player), midbottom=(WIDTH/2, HEIGHT-50), fontsize=100, color='red')

def on_mouse_down(pos):
    if game.current_player == 0:
        for i, s in enumerate(global_scope["sprite_hand"]):
            if s.collidepoint(pos):
                agent_scope["action"] = CARD2INT[global_scope["human_hand"][i]]
                print('Selected card {}'.format(agent_scope["action"]))
                agent_scope["update_hand"] = True
        if deck_img.collidepoint(pos):
            agent_scope["action"] = 54
            print('Selected pick up')
        for color, card in color_imgs.items():
            if card.collidepoint(pos):
                agent_scope["select_color"] = False
                agent_scope["selected_color"] = color_dic[color]
