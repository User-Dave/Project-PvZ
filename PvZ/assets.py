import pygame, sys, constants, ClientProtocol
pygame.init()
scr = pygame.display.set_mode(constants.screen_size)
import unitsPvZ


import buttons
def dupe_BTE_but(x,y):
    return buttons.Button("BTE", [x, y, 80, 60], [x+30, y+12, 16, 16],
                          buttons.button_function_dupe)
def trans_start_but(x,y,dest,og = "Start"):
    return buttons.Button(og+"BetaButton",[x,y,260,160],[x+10,y+10,240,130],
                          buttons.make_trans_function(dest))

def make_zom_but(x,y):
    w, h = 125, 80
    return buttons.Button("ZomBetaButton",[x,y,w,h],[x+10,y+10,w-20,h-20],
                          buttons.button_function_make_zom)
def make_dev_but(x,y, og = "DevBetaButton"):
    w, h = 125, 80
    return buttons.Button(og, [x, y, w, h], [x + 10, y + 10, w - 20, h - 20],
                          buttons.button_function_toggle_dev)

def make_seed_packet_but(x, y, utype):
    return buttons.seed_packet(x, y, utype)

def make_end_turn_but(x,y):
    w, h = 160, 100
    return buttons.TwoStateButton(x=x, y=y, w=w, h=h, origin1="PlantsToZoms", origin2="ZomsToPlants",
                                   button_function=buttons.button_function_end_turn, screen=None, menu=None)

def make_draw_packet_but(x,y):
    w, h = 100, 80
    return buttons.DrawButton(x, y, w, h, screen=None, menu=None)

def particles_but(x,y):
    w, h = 92, 92
    tf = ["True","False"]
    f = ClientProtocol.open_file_with(__file__,"settings.txt","r")
    txt = f.read()
    particles = [True,False][tf.index(txt)]
    f.close()
    if particles:
        return buttons.TwoStateButton(x=x, y=y, w=w, h=h, origin1="particle_button", origin2="particle_button1",
                                   button_function=buttons.button_function_change_settings, screen=None, menu=None)
    return buttons.TwoStateButton(x=x, y=y, w=w, h=h, origin1="particle_button1", origin2="particle_button",
                                   button_function=buttons.button_function_change_settings, screen=None, menu=None)