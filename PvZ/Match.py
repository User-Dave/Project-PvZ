import pygame, constants,  assets, drawable, buttons, menu, unitsPvZ, winscreen
import textgen

class MatchPvZ(menu.Game_Menu):
    MAX_SEED_PACKET = 5
    screen_colors = [(101,151,101),(151,101,151)]
    def __init__(self, game, randomseed = None):
        if randomseed == None:
            randomseed = constants.rn.randint(0,1000000)
        super().__init__(game=game, bg=[
            drawable.drawable(game.screen, "BetaField", constants.board_proportions)],
                         but=[#assets.make_zom_but((constants.board_proportions[0])+(constants.board_proportions[2])+10,
                              #                     constants.board_proportions[1]),
                              #assets.make_dev_but(1475, 0),
                                assets.make_end_turn_but(constants.display_proportions[0]-160,30),
                                assets.make_draw_packet_but(180,200)], fg=[])
        self.screen_color = self.screen_colors[0]
        self.board = [[],[],[],[]]
        for lane in range(len(self.board)):
            for i in range(10):
                to_add=buttons.Tile([lane, i], self.screen, self)
                self.board[lane].append(to_add)
                self.buttons.append(to_add)
        self.bg_obj.append(drawable.drawable(self.screen, "BgDispBeta", constants.display_proportions))
        self.game_state = [1, 0, 0,[0,0]]
        self.suns_images = [drawable.drawable(self.screen, "suns", [0,0,240,200]),
                            drawable.drawable(self.screen, "brainz", [0,0,240,200])]
        self.suns = [16,16]
        self.target_left_to_hit = 3
        self.fontSuns = textgen.font(size = [44,44])
        self.inventories = [[],
                            []]
        self.randomgen = constants.rn.Random(randomseed)
        self.decks_of_types = [[unitsPvZ.Peashooter,
                                unitsPvZ.Peashooter,
                                unitsPvZ.Wallnut,
                                unitsPvZ.Wallnut,
                                unitsPvZ.Sunflower,
                                unitsPvZ.Sunflower,
                                unitsPvZ.CherryBomb,
                                unitsPvZ.GoldenPea],
                               [unitsPvZ.BrowncoatZombie,
                                unitsPvZ.FlagZombie,
                                unitsPvZ.BucketheadZombie,
                                unitsPvZ.Grave,
                                unitsPvZ.Grave,
                                unitsPvZ.Imp,
                                unitsPvZ.Imp,
                                unitsPvZ.Imp]]
        self.shuffle_list(self.decks_of_types[0])
        self.shuffle_list(self.decks_of_types[1])
        for lane in range(len(self.board)):
            self.board[lane][0].spawn(unitsPvZ.Lawnmower(self,[lane,0]))
            self.board[lane][9].spawn(unitsPvZ.TargetZombie(self,[lane,9]))
        self.temp_buttons = []
        self.switch_turn()
        if constants.dev_mode:
            print("Match.Match_PvZ.__init__: Finished initing")

    def update(self):
        super().update()

        self.draw_disp()

    def draw_disp(self):
        if self.game_state[1] == 1:
            self.game_state[2][0].draw_d()
        elif self.game_state[1] in (4,5):
            self.game_state[3].draw_d()
        self.draw_munies(self.game_state[0])

    def draw_munies(self, team):
        self.suns_images[team].draw()
        text_surface = self.fontSuns.render(str(self.suns[team]))
        text_location = [120-(text_surface.get_width()//2),138]
        self.screen.blit(text_surface, (text_location[0], text_location[1]))


    def switch_game_state(self, action, info=None, extra=None):
        for i in self.temp_buttons:
            self.buttons.remove(i)
        self.temp_buttons.clear()
        if action==0: # Info = tile
            self.game_state[1] = 0
            self.game_state[2] = info
            self.game_state[3] = None
        elif action == 1: # Info = tile.plants+tile.zombies
            self.game_state[1] = 1
            self.game_state[2] = info
            cyc = buttons.Button(origin = "cycle_button", visual_rect = [constants.display_proportions[0]-105,
                                                                     constants.display_proportions[1] + constants.display_proportions[3]-65,
                                                                     100,
                                                                     60], 
                                 touch_rect = [constants.display_proportions[0] -101,
                                                                     constants.display_proportions[1] + constants.display_proportions[3]-61,
                                                                     92,
                                                                     52],
                                                                     button_function = buttons.button_function_cycle_unit_queue,
                                                                     screen = self.screen, menu = self)
            self.temp_buttons.append(cyc)
            self.buttons.append(cyc)
            if info[0].this_unit_team == self.game_state[0]:
                act = buttons.Button(origin = "activate_button", visual_rect = [constants.display_proportions[0] -105,
                                                                     constants.display_proportions[1] + constants.display_proportions[3]-65-65,
                                                                     100,
                                                                     60], 
                                 touch_rect = [constants.display_proportions[0] -101,
                                                                     constants.display_proportions[1] + constants.display_proportions[3]-61-65,
                                                                     92,
                                                                     52],
                                                                     button_function = buttons.button_function_activate_unit,
                                                                     screen = self.screen, menu = self)
                self.temp_buttons.append(act)
                self.buttons.append(act)
            self.game_state[3] = None
        elif action == 4:  # Info = unit_type, Extra = unit to display
            self.game_state[1] = 4
            self.game_state[2] = info
            self.game_state[3] = extra
        elif action == 5:
            if len(self.inventories[self.game_state[0]]) > self.MAX_SEED_PACKET-1:
                self.game_state[1] = 5
                self.game_state[2] = info
                self.game_state[3] = info(self, (-9,-9))
            else:
                self.create_new_seed_packet(info)

    
    def switch_turn(self):
        # Remove other team's seed packets and cool down
        for i in self.inventories[self.game_state[0]]:
            if i in self.buttons:
                self.buttons.remove(i)
                i.cooldown = max(0, i.cooldown-1)
        
        team_to_switch_to = 1-self.game_state[0]
        self.suns[team_to_switch_to] += 1
        # Add new team's seed packets
        for i in self.inventories[team_to_switch_to]:
            self.buttons.append(i)

        self.screen_color = self.screen_colors[team_to_switch_to]
        self.game_state[0] = team_to_switch_to
        # do turn start and turn end for all units
        for lane in range(len(self.board)):
            for col in range(10):
                for unit in self.board[lane][col].plants + self.board[lane][col].zombies:
                    if unit.this_unit_team == team_to_switch_to:
                        unit.react(unitsPvZ.reaction_worthy_unit_flags[2])
                    else:
                        unit.react(unitsPvZ.reaction_worthy_unit_flags[3])
        self.switch_game_state(0)
        pass

    def random_number_generator(self, low, high):
        x = self.randomgen.randint(low,high)
        return x
    
    def shuffle_list(self, lllst):
        self.randomgen.shuffle(lllst)
        return lllst
    
    def create_new_seed_packet(self, unit_type):
                diff_between_packets_y=140
                possible_ys = [200]
                for i in range(1,self.MAX_SEED_PACKET):
                    possible_ys.append(possible_ys[-1]+diff_between_packets_y)
                # search for the one y not yet used
                for i in self.inventories[self.game_state[0]]:
                    possible_ys.remove(i.visual_rect[1])
                newpacket = buttons.seed_packet(10,possible_ys[0], unit_type, self.screen, self)
                self.inventories[self.game_state[0]].append(newpacket)
                self.buttons.append(newpacket)
                self.switch_game_state(0)

    def win(self, unit_responsible=None, team = 0):
        self.game.displays[2] = MatchPvZ(self.game)
        self.game.displays[3] = winscreen.win_screen(game=self.game,
                  unit_responsible=unit_responsible, team = team)
        self.game.current_display = 3