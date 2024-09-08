import random
import pygame, sys, constants, loader

import unitsPvZ

import drawable
import textgen

import ClientProtocol


class Button(drawable.drawable):
    def __init__(self, origin, visual_rect, touch_rect, button_function, screen=None, menu=None):
        super().__init__(screen, origin, visual_rect)
        self.touch_rect = touch_rect
        self.rect_color = self.dev_colors[0]
        self.menu = menu
        self.button_func = button_function

        self.de_activate()

    def de_activate(self):  # makes the button look visually inactive
        self.curr_img = self.load_image(0)
        self.rect_color = self.dev_colors[0]

    def seem_active(self):
        self.curr_img = self.load_image(len(self.graphics)-1)
        self.rect_color = self.dev_colors[1]

    def draw(self):
        super().draw()
        if constants.dev_mode:  # pygame.draw.rect(screen, otherstuff)
            pygame.draw.rect(self.screen, self.rect_color,
                             (self.touch_rect[0], self.touch_rect[1],
                              self.touch_rect[2], self.touch_rect[3]), 1)

    def assign(self, menu):
        self.screen = menu.screen
        self.menu = menu

    def point_in_rect(self, point):
        return pygame.Rect(self.touch_rect[0], self.touch_rect[1],
                           self.touch_rect[2], self.touch_rect[3]).collidepoint(point)

    def collide_with_rect(self, rect2):
        return pygame.Rect(self.touch_rect[0], self.touch_rect[1],
                           self.touch_rect[2], self.touch_rect[3]).colliderect(rect2)

    def activate(self):
        self.button_func(self)

    def copy(self):
        return Button(self.origin, self.visual_rect.copy(), self.touch_rect.copy(), self.button_func, self.screen,
                      self.menu)


class Tile(Button): # Child class of Button, with the ability to track units on it
    dev_colors = [(230, 20, 20), (20, 230, 20), (0, 0, 255)]

    def __init__(self, position, screen=None, menu=None):
        visual_rect = [constants.board_proportions[0] + (constants.board_proportions[2] / 10) * position[1],
                       constants.board_proportions[1] + (constants.board_proportions[3] / 4) * position[0],
                       constants.board_proportions[2] / 10,
                       constants.board_proportions[3] / 4]
        touch_rect = [visual_rect[0] + 3, visual_rect[1] + 3, visual_rect[2] - 6, visual_rect[3] - 6]
        visual_rect[1] += visual_rect[3] // 8
        visual_rect[3] -= visual_rect[3] // 4
        origin = "tileChooseBeta" # Name of the image directory in Sprites.
        button_function = but_func_choose_tile
        super().__init__(origin, visual_rect, touch_rect, button_function, screen, menu) # Utilizing parent method to init
        self.graphics = loader.loader(origin, copies=7, size=[visual_rect[2], visual_rect[3]])
        self.touch_rect = touch_rect
        self.rect_color = self.dev_colors[0]
        self.menu = menu
        self.button_func = button_function
        self.frame_anim = 0 # Updating new capabilty, fluid animation (multiple frames)
        self.plants = [] # Updating new capabilty, tracking units
        self.zombies = []
        self.position = position

        self.de_activate() # make button seem inactive (not hovered on)

    def seem_active(self):
        starting_frame = 7
        super().seem_active()
        if self.frame_anim == 0:
            self.frame_anim = starting_frame
            self.rect_color = self.dev_colors[1]
        else:
            self.frame_anim += 1
            if self.frame_anim >= len(self.graphics):
                self.frame_anim = starting_frame
        # if constants.dev_mode:
        #     print("buttons.Tile.seem_active: frame = ",self.frame_anim)
        self.curr_img = self.load_image(self.frame_anim)

    def de_activate(self):
        super().de_activate()
        self.frame_anim = 0
        self.curr_img = self.load_image(0)

    def draw(self):
        super().draw() # Draws the tile
        for i in self.zombies+self.plants: # For every unit on tile
            i.draw_f() # Draw it in the field

    def spawn(self, x):
        if x.isItSpawnable(self):
            self.menu.suns[x.this_unit_team] -= x.stats[1]
            x.react(unitsPvZ.reaction_worthy_unit_flags[0], [x,self])
            
        llst = self.plants+self.zombies
        if x in llst:
            llst.remove(x)
            for unit in llst:
                unit.react(unitsPvZ.reaction_worthy_unit_flags[0], [x, self])

class TwoStateButton(Button):
    def __init__(self, x, y, w, h, origin1, origin2, button_function, screen=None, menu=None):
        super().__init__(origin=origin1,
                          visual_rect=[x,y,w,h],
                            touch_rect=[x+5,y+5,w-10, h-10],
                              button_function=button_function,
                          screen=screen, menu=menu)
        self.other_state_graphics = loader.loader(origin2, copies=1, size=[self.visual_rect[2], self.visual_rect[3]])
        pass
    
    def swap_sprites(self):
        temp = self.graphics
        self.graphics = self.other_state_graphics
        self.other_state_graphics = temp
        
    
    def activate(self):
        self.swap_sprites()
        super().activate()

class DrawButton(Button):
    def __init__(self, x, y, w, h, screen=None, menu=None):
        super().__init__(origin="newPacketBut",
                          visual_rect=[x,y,w,h],
                            touch_rect=[x+5,y+5,w-10, h-10],
                              button_function=button_function_draw_packet,
                          screen=screen, menu=menu)
        pass
    
    def seem_active(self):
        self.curr_img = self.load_image(1+2*(self.menu != None and self.menu.game_state[1] == 5))
        self.rect_color = self.dev_colors[1]
    
    def de_activate(self):  # makes the button look visually inactive
        self.curr_img = self.load_image(0+2*(self.menu != None and self.menu.game_state[1] == 5))
        self.rect_color = self.dev_colors[0]


class seed_packet(Button):
    font = textgen.font([(70,70,220),(150,150,220)], [55,55])
    def __init__(self, x, y, unit_type, screen=None, menu=None):
        w,h = (156,104)
        visual_rect=[x,y,w,h]
        touch_rect=[x+5,y+5,w-10,h-10]
        self.display_unit = unit_type(match=menu, pos=(-4,-4), seedpacket = None)
        button_function = make_plant_function(unit_type)
        self.unit_type=unit_type
        origin = "seedpacket" + ("plants","zoms")[self.display_unit.this_unit_team]
        super().__init__(origin, visual_rect, touch_rect, button_function, screen, menu)
        self.suns = [None]
        self.cooldown = 0

        
    
    def draw(self):
        x,y,w,h =self.visual_rect
        super().draw()
        if self.suns == [None]:
            self.init_suns()
        # Draw the mini-unit
        self.screen.blit(self.display_unit_showcase_surface,
                         (self.showcase_pos[0],
                          self.showcase_pos[1]),
                          (0,0,self.showcase_pos[2],
                          self.showcase_pos[3]))

        if constants.dev_mode:  # pygame.draw.rect(screen, otherstuff)
            pygame.draw.rect(self.screen, self.dev_colors[2],
                             (self.showcase_pos[0], self.showcase_pos[1],
                              self.showcase_pos[2], self.showcase_pos[3]),2)
        
        # Draw the black overlay and cooldown
        if self.cooldown > 0:
            # Create a surface for the rectangle with alpha channel
            rect_surface = pygame.Surface((w, h), pygame.SRCALPHA)
            rect_surface.fill((*(0,0,0), min(225, 40*self.cooldown)))  # Fill with color and alpha
            self.screen.blit(rect_surface,
                         self.visual_rect)
            text_surface = self.font.render(str(self.cooldown))
            text_location = [x+(w//2)-(text_surface.get_width()//2),
                             y+(h//2)-(text_surface.get_height()//2)]
            self.screen.blit(text_surface, (text_location[0], text_location[1]))
        # Draw the suns
        for i in self.suns:
            i.draw()
    
    def init_suns(self): #This function exists because button assignment is wonky, 
        # the button doesn't get a screen/menu until after init,
        # so only on the first draw we initialize anything that requires the screen
        x,y,w,h = self.visual_rect

        self.display_unit = self.unit_type(match=self.menu, pos=(-5,-5), seedpacket = self)
        self.display_unit_showcase_surface = self.display_unit.pics_f[0].get(self.display_unit.pics_f[2])

        width_of_showcase, height_of_showcase = (
            min(w-30,self.display_unit_showcase_surface.get_width()),
            min(h-30,self.display_unit_showcase_surface.get_height())
        )
        self.showcase_pos = [x+(w//2)-(width_of_showcase//2),
                        y+h-15-min(h,height_of_showcase),
                        width_of_showcase,
                        height_of_showcase]
        
        self.suns.clear()
        sun_size = (44,44)
        sun_origin = "sun" + ("plants","zoms")[self.display_unit.this_unit_team]
        for i in range(self.display_unit.stats[1]):
            sun_visual_rect = [x-10+((i%6)*((sun_size[0]*0.6)//1)),
                               y+h-25+((i//6)*((sun_size[1]*0.55)//1)),
                          sun_size[0],sun_size[1]]
            sun = drawable.drawable(self.screen, sun_origin, sun_visual_rect)
            self.suns.append(sun)

    def activate(self):
        if self.cooldown == 0 or self.menu.game_state[1] == 5:
            super().activate()


def button_function_null(b):
    if constants.dev_mode:
        print("buttons.button_function_null: activated nothing")
    pass


def button_function_dupe(b): # Testing function, no longer used
    if constants.dev_mode:
        print("buttons.button_function_dupe: activated dupelicate")
    pic = b.copy()
    pic.button_func = button_function_null
    offset = (random.randint(-constants.screen_size[0] // 2, constants.screen_size[0] // 2),
              random.randint(-constants.screen_size[1] // 2, constants.screen_size[1] // 2))
    pic.touch_rect = [pic.touch_rect[0] + offset[0], pic.touch_rect[1] + offset[1],
                      pic.touch_rect[2], pic.touch_rect[3]]
    pic.transpose_by(offset[0], offset[1])
    b.menu.buttons.append(pic)


def make_trans_function(dest_scr): # screen transition function maker
    def button_function_trans_screen(b):
        if constants.dev_mode:
            print("buttons.button_function_trans_screen: activated transition to", dest_scr)
        b.menu.game.current_display = dest_scr

    return button_function_trans_screen


def button_function_make_zom(b): # Testing function, no longer used
    if constants.dev_mode:
        print("buttons.button_function_make_zom: activated ability")
    for i in range(10):
        x = [random.randint(0, 3), random.randint(1, 8)]
        if constants.dev_mode:
            print("buttons.button_function_make_zom: " + str(x))
        unitAdded = unitsPvZ.Unit(match=b.menu, origin_pic_f="LILBTE", origin_pic_d="BTE",
                                   pos=[x[0], x[1]], stats=[0,0,0])
        b.menu.board[x[0]][x[1]].spawn(unitAdded)


def button_function_toggle_dev(b):
    constants.dev_mode = not constants.dev_mode
    print("buttons.button_function_toggle_dev: toggled constants.dev_mode", constants.dev_mode)


def but_func_choose_tile(b):
    if constants.dev_mode:
        print("buttons.but_func_choose_tile: activated. gamestate before = "+str(b.menu.game_state))
    gamestate = b.menu.game_state.copy()
    if gamestate[1] in (0,1,2):
        z = (b.plants,b.zombies)
        if len(z[0]) != 0 or len(z[1]) != 0:
            b.menu.switch_game_state(1,( z[gamestate[0]] + z[1-gamestate[0]]))
        else:
            b.menu.switch_game_state(0)
    elif gamestate[1] == 4:
        b.spawn(gamestate[2](b.menu, b.position.copy(), gamestate[3].seed_packet))
        b.menu.switch_game_state(0)
    if constants.dev_mode:
        print("buttons.but_func_choose_tile: over. after = " + str(b.menu.game_state))


def make_plant_function(unit_type):
    if constants.dev_mode: 
        print("buttons.make_plant_function: activated with unit_type="+str(unit_type))
    def button_function_prepare_planting(b):
        if constants.dev_mode:
            print("buttons.button_function_prepare_planting: activated with unit_type="+str(unit_type))
        gamestate = b.menu.game_state.copy()
        if gamestate[1] in (0,1,4) and gamestate[2] != unit_type:
                b.menu.switch_game_state(4,unit_type, b.display_unit)
        elif gamestate[1] == 4 and gamestate[2] == unit_type:
            b.menu.switch_game_state(0)
        elif gamestate[1] == 5: # Replace this seed packet with the one that was bought
            b.menu.decks_of_types[b.display_unit.this_unit_team].append(unit_type)
            b.menu.inventories[b.display_unit.this_unit_team].remove(b)
            b.menu.buttons.remove(b)
            b.menu.switch_game_state(5,gamestate[2])
    return button_function_prepare_planting

def button_function_cycle_unit_queue(b):
    queue = b.menu.game_state[2]
    a = queue.pop(0)
    queue.append(a)
    b.menu.switch_game_state(1, queue)

def button_function_activate_unit(b):
    unit = b.menu.game_state[2][0]
    if constants.dev_mode:
        print("buttons.button_function_activate_unit: activated with unit =",str(unit))
    unit.react(unitsPvZ.reaction_worthy_unit_flags[6], None)

def button_function_end_turn(b):
    if constants.dev_mode:
        print("button_function_end_turn.activate")
    b.menu.switch_turn()

def button_function_draw_packet(b):
    if b.menu.game_state[1] != 5 and b.menu.suns[b.menu.game_state[0]] >= 2:
        b.menu.suns[b.menu.game_state[0]] -= 2
        type_o_pack = b.menu.decks_of_types[b.menu.game_state[0]].pop(0)
        b.menu.switch_game_state(5, type_o_pack)
    elif b.menu.game_state[1] == 5:
        b.menu.decks_of_types[b.menu.game_state[0]].append(b.menu.game_state[2])
        b.menu.switch_game_state(0)
    pass

def make_msg_function_waitingroom(text):
    sendable_text = str(len(text)).zfill(4)+"|"+text
    def button_function_send_msg(b):
        msg = ClientProtocol.encrypt(sendable_text,ClientProtocol.KEYS[0])
        print("button_function_send_msg: sending",msg)
        b.menu.tcp_conv.send(msg.encode())
    return button_function_send_msg

def button_function_change_settings(b):
    tf = ["True","False"]
    f = ClientProtocol.open_file_with(__file__,"settings.txt","r")
    txt = f.read()
    f.close()
    changed = tf[1-tf.index(txt)]
    f = ClientProtocol.open_file_with(__file__,"settings.txt","w")
    f.write(changed)
    f.flush()
    if constants.dev_mode:
        print(f"button_function_change_settings: changed particles to {changed}")
    f.close()
    b.menu.game.load_settings()


if __name__ == "__main__":
    print()
