import pygame, Match, loader, random, constants, textgen

import drawable
num = 1
reaction_worthy_unit_flags=["BORN","DEATH",
                            "TURN START","TURN END",
                            "MOVE", "THROW",
                            "ACTIVATE","GET HIT"]
damage_types = ["NORMAL", "CRUSH", "FIRE"]
def_unit_font = textgen.font(size=[33,33])

class Unit:
    offsets = [constants.board_proportions[0]+20, constants.board_proportions[1]+20, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+80, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-120, # proportions (disp)
               74,58] # proportions (f)
    lengths_of_anim = [3,5] # field, disp
    this_unit_team = 1
    particle_colors=[(255,255,255)]
    CARD_COOLDOWN = 0
    def __init__(self, match, origin_pic_f, origin_pic_d, pos, stats, seedpacket = None, looppoint = 0):
        self.match = match
        self.pics_f = [loader.loader(origin_pic_f, self.lengths_of_anim[0], (self.offsets[8],self.offsets[9])),looppoint * self.lengths_of_anim[0],looppoint * self.lengths_of_anim[0]] # [imgs, index of current, index to return to in loop]
        self.pics_d = [loader.loader(origin_pic_d, self.lengths_of_anim[1], (self.offsets[6],self.offsets[7])),0] # [imgs, index of current]
        # self.board_drawer=drawable.drawable(self.match.screen, origin, visual_rect)
        # self.menu_drawer=drawable.drawable()
        self.pos = pos #[Row, Col]
        self.stats = stats
        self.individual_unit_offset = [random.randint(-20, 23), random.randint(-1, 1)]
        self.seed_packet = seedpacket
        self.vis_pos = [self.offsets[0] + self.individual_unit_offset[0] + self.offsets[2] * self.pos[1]
            , self.offsets[1] + self.individual_unit_offset[1] + self.offsets[3] * self.pos[0]]

        self.amount_of_activations = 0
        self.font = def_unit_font


        global num
        self.iter = str(num)
        num += 1
    
    def desc(self):
        s = ""
        if constants.dev_mode:
            s += str(self.iter) + " "
        s += "\n!"+str(self.stats[0]) # HP
        s += ":" + "#$"[self.this_unit_team] + str(self.stats[1]) # COST
        if self.this_unit_team == 1:
            s += "\n@" + str(self.stats[3]) # SPD
            s += ":%" + str(self.stats[4]) # DMG
        s += "\n^"+str(self.stats[2]) # COOLDOWN
        if self.CARD_COOLDOWN != 0:
            s += ":^(CARD)" + str(self.CARD_COOLDOWN) # COOLDOWN (CARD)
        return s

    def draw_f(self):
        goal = (self.offsets[0] + self.individual_unit_offset[0] + self.offsets[2] * self.pos[1],
                    self.offsets[1] + self.individual_unit_offset[1] + self.offsets[3] * self.pos[0])
        spd = 0.125 # 0<spd<1
        self.vis_pos = [self.vis_pos[0] + int(spd*(goal[0]-self.vis_pos[0])),
                        self.vis_pos[1] + int(spd*(goal[1]-self.vis_pos[1]))]
        self.match.screen.blit(self.pics_f[0].get(self.pics_f[1]),self.vis_pos)
        self.pics_f[1] = (self.pics_f[1] + 1)
        if self.pics_f[1] >= len(self.pics_f[0]):
            self.pics_f[1] = self.pics_f[2]
        pass

    def draw_d(self):
        self.match.screen.blit(self.pics_d[0].get(self.pics_d[1]), (self.offsets[4]
                                                                   , self.offsets[5]))
        self.pics_d[1] = (self.pics_d[1] + 1) % len(self.pics_d[0])
        self.draw_text()
    
    def draw_text(self):
        #text_surface = self.font.render(self.desc(), True, (0,0,0))
        text_surface = self.font.render(self.desc())
        text_location = [constants.display_proportions[0]+250, constants.display_proportions[1]+10]
        self.match.screen.blit(text_surface, (text_location[0], text_location[1]))
    
    def isItSpawnable(self, tile):
        # Return weather or not this unit is plantable here
        return self.stats[1] <= self.match.suns[self.this_unit_team]
    
    def born(self, flag, info): # REACTION TO 0
        if (info[0] == self):
            (info[1].plants, info[1].zombies)[self.this_unit_team].append(self)
            if self.seed_packet != None:
                self.seed_packet.cooldown += self.CARD_COOLDOWN

    def die(self, flag, info): # REACTION TO 1
        thisTile = self.match.board[self.pos[0]][self.pos[1]]
        (thisTile.plants,thisTile.zombies)[self.this_unit_team].remove(self)

    def react_to_start(self, flag, info): # REACTION TO 2
        if self.match.game_state[0] == self.this_unit_team:
            # restart abilites for use next turn
            self.amount_of_activations = 0
            # remove cooldown by 1
            self.stats[2] = max(self.stats[2]-1, 0)

    def react_to_end(self, flag, info): # REACTION TO 3
        pass

    def feel_movement(self, flag, info): # REACTION TO 4
        pass

    def feel_throwing(self, flag, info): # REACTION TO 5
        pass

    def activated(self, flag, info): # REACTION TO 6
        pass

    def create_particles(self, angle_range, angle_start, particles, spds = (8,13), drag = 0.9):
        for i in range(particles):
            x = self.vis_pos[0]+int(0.5*(self.pics_f[0].get(self.pics_f[1]).get_width()))
            y = self.vis_pos[1]+int(0.3*(self.pics_f[0].get(self.pics_f[1]).get_height()))
            angle = angle_start + int((i-(particles/2)) * (angle_range/particles))
            spd = self.match.random_number_generator(low=spds[0], high=spds[1])
            if self.match.game.to_draw_particles:
                self.match.fg_obj.append(drawable.particle(screen=self.match.screen, x=x,
                                                            y=y, color=self.particle_colors[0][:], angle=angle,
                                                            spd=spd,
                                                            time_to_die = 0.5, drag = drag))
            self.particle_colors.append(self.particle_colors.pop(0))

    def get_hit(self, flag, info): # REACTION TO 7
        angle_range = 80
        angle_start = (0,180)[self.this_unit_team]
        particles = 50
        self.create_particles(angle_range=angle_range,angle_start=angle_start,particles=particles)

        self.stats[0] -= info[1]
        if self.stats[0] <= 0:
            self.react(reaction_worthy_unit_flags[1], None)
    
    def react(self, flag, info=None):
        if constants.dev_mode:
            print(str(self),"REACTED TO",str(flag))
        (self.born, self.die, self.react_to_start, self.react_to_end,
         self.feel_movement, self.feel_throwing, self.activated, self.get_hit)[reaction_worthy_unit_flags.index(flag)](flag,info)
    
    def attack(self, targets, damage, damage_type):
            if constants.dev_mode:
                print("attack start")
            for i in targets:
                if constants.dev_mode:
                    print("attacking",str(i))
                i.react(reaction_worthy_unit_flags[7],[self, damage, damage_type])
                if constants.dev_mode:
                    print("attack go")
            if constants.dev_mode:
                print("attack end")


class TargetZombie(Unit):
    offsets = [constants.board_proportions[0]+25, constants.board_proportions[1]-50, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+5, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-10, # proportions (disp)
               80,120] # proportions (f)
    lengths_of_anim = [1,1]
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="target zombie",
                          origin_pic_d="target zombie", pos=pos, stats=[5,0,0,0,0], seedpacket=seedpacket)
    
    def get_hit(self, flag, info):
        super().get_hit(flag,info)
        if self.stats[0] <= 0:
            self.match.target_left_to_hit -= 1
            if self.match.target_left_to_hit == 0:
                self.match.win(info[0], 0)
        
    def activated(self, flag, info):
        self.get_hit(flag=reaction_worthy_unit_flags[1],info=[self, 999, damage_types[0]])
        self.match.switch_game_state(0)
        return super().activated(flag, info)

    def desc(self):
        s = "Target"
        s += super().desc()
        s += f"\nDESTROY {self.match.target_left_to_hit} MORE TO\nEND THE GAME."
        s += "\nABILITY:DESTROY THIS."
        return s

class Lawnmower(Unit):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-25, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+5, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-10, # proportions (disp)
               86,100] # proportions (f)
    lengths_of_anim = [7,12]
    this_unit_team = 0
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="lawmower",
                          origin_pic_d="lawmower", pos=pos, stats=[0,0,0,0,0], seedpacket=seedpacket)
    
    def die(self, flag, info):
        lane = self.pos[0]
        for i in self.match.board[lane][0:9]:
            i.zombies.clear()
        self.pos[1] = 9
    
    def activated(self, flag, info):
        self.get_hit(flag=reaction_worthy_unit_flags[1],info=[self, 999, damage_types[0]])
        super().activated(flag, info)
        self.match.switch_game_state(0)
    
    def draw_f(self):
        super().draw_f()
        if self.vis_pos[0] >= (constants.board_proportions[0] + constants.board_proportions[2]-(self.offsets[8]*2)):
            self.pos[1] = 0
            super().die(0,0)
    
    def desc(self):
        s = "Lawnmower"
        s += super().desc()
        s += "\nABILITY: DESTROY \nEVERYTHING IN LANE\nWITHOUT ACTIVATING\nDEATH/HIT ABILITIES."
        return s

class plant(Unit):
    this_unit_team = 0
    particle_colors = [(10,100,10)]
    def isItSpawnable(self, tile):
        return super().isItSpawnable(tile) and len(tile.plants) == 0 and tile.position[1] < 5 and tile.position[1] > 0
    
    def attack_forward(self, damage_amt, dmg_type = damage_types[0]):
        position = self.pos.copy()
        while len((self.match.board[position[0]][position[1]]).zombies) < 1 and position[1] < 9:
            position[1] += 1
        if len((self.match.board[position[0]][position[1]]).zombies) > 0:
            self.attack(targets=[(self.match.board[position[0]][position[1]]).zombies[0]], damage=damage_amt, damage_type=dmg_type)
    pass

class zombie(Unit):

    def draw_f(self): # Must check if its past the lawn, in that case, win.
        # Cannot use draw d for this because draw d is used for a bunch of other stuff like buying
        if self.pos[1] < 0:
            self.match.win(self, 1)
        else:
            return super().draw_f()

    def activated(self, flag, info): # Upon activation:
        if self.stats[2] == 0:
            self.move_forward(self.stats[3])
            curr_tile = self.match.board[self.pos[0]][self.pos[1]]
            if ( len(curr_tile.plants) > 0 ):
                self.attack([curr_tile.plants[0]], self.stats[4], damage_types[0])
            self.amount_of_activations += 1
            self.match.switch_game_state(0)
            self.stats[2] += 1
    
    def isItSpawnable(self, tile):
        return super().isItSpawnable(tile) and tile.position[1] > 4 and tile.position[1] < 9

    def move_forward(self, spd):
        if constants.dev_mode:
            print("moving forward",spd,"start")
        board = self.match.board
        pos = self.pos
        copos = pos.copy()
        movement_left = spd
        while movement_left > 0 and len(board[pos[0]][pos[1]].plants) == 0:
            if constants.dev_mode:
                print("moving forward",movement_left,"go")
            self.pos[1] -= 1
            if constants.dev_mode:
                print("self pos = ",self.pos)
            board[pos[0]][pos[1]+1].zombies.remove(self)
            board[pos[0]][pos[1]].zombies.append(self)
            for i in (board[pos[0]][pos[1]].plants + board[pos[0]][pos[1]].zombies + 
                        board[pos[0]][pos[1]+1].plants + board[pos[0]][pos[1]+1].zombies):
                i.react(reaction_worthy_unit_flags[4], [self, copos])
            movement_left -= 1
        if constants.dev_mode:
            print("moving forward end")


class Peashooter(plant):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-2, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+80, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-120, # proportions (disp)
               90,81] # proportions (f)
    lengths_of_anim=[5,6]
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="Peashooter",
                          origin_pic_d="Peashooter", pos=pos, stats=[2,3,1], seedpacket=seedpacket)
        if constants.dev_mode:
            print("Created Peashooter no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "Peashooter"
        s += super().desc()
        s += "\nABILITY:SHOOTS FIRST\nZOMBIE IN FRONT FOR\n1 DMG."
        return s
    
    def activated(self, flag, info):
        if self.stats[2] == 0:
            self.attack_forward(1)
            self.stats[2] += 1
            self.match.switch_game_state(0)

class GoldenPea(Peashooter):
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match, pos, seedpacket)
        self.stats[1] = 8
    def desc(self):
        s = "G.Peashooter"
        s += Unit.desc(self)
        s += "\nABILITY:SHOOTS FIRST\nZOMBIE IN FRONT FOR\n8 DMG."
        return s
    
    def activated(self, flag, info):
        if self.stats[2] == 0:
            self.attack_forward(8)
            self.stats[2] += 1
            self.match.switch_game_state(0)

class Sunflower(plant):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-30, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+10, # start x (disp), start y (disp),
               200,250, # proportions (disp)
               80,100] # proportions (f)
    lengths_of_anim=[5,6]
    HOW_MANY_TURNS = 3
    CARD_COOLDOWN=1
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="sunflower",
                          origin_pic_d="sunflower", pos=pos, stats=[1,2,self.HOW_MANY_TURNS-1], seedpacket=seedpacket, looppoint=8)
        if constants.dev_mode:
            print("Created Sunflower no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "Sunflower"
        s += super().desc()
        s += f"\nAUTO-GENERATES 1#\nEVERY {self.HOW_MANY_TURNS} TURNS."
        return s
    
    def react_to_start(self, flag, info):
        self.stats[2] -= 1
        if self.stats[2] <= 0:
            self.match.suns[0] +=1
            self.pics_f[1] = 0
            self.stats[2] = self.HOW_MANY_TURNS
    
class Wallnut(plant):
    offsets = [constants.board_proportions[0]+25, constants.board_proportions[1]+10, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+20,constants.display_proportions[1]+100, # start x (disp), start y (disp),
               160,170, # proportions (disp)
               64,68] # proportions (f)
    lengths_of_anim=[7,6]
    particle_colors = [(87, 49, 11),(190, 120, 32),(190, 120, 32)]
    CARD_COOLDOWN = 3
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="walnut",
                          origin_pic_d="walnut", pos=pos, stats=[4,2,0], seedpacket=seedpacket, looppoint=0)
        if constants.dev_mode:
            print("Created Wallnut no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "Wallnut"
        s += super().desc()
        return s

class CherryBomb(plant):
    offsets = [constants.board_proportions[0]+25, constants.board_proportions[1]+10, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+20,constants.display_proportions[1]+100, # start x (disp), start y (disp),
               160,170, # proportions (disp)
               64,68] # proportions (f)
    lengths_of_anim=[1,20]
    particle_colors = [(50,50,50),(192,192,192),(25,25,25),(100,100,100)]
    CARD_COOLDOWN = 6
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="cherrydesc",
                          origin_pic_d="cherrydesc", pos=pos, stats=[0,8,0], seedpacket=seedpacket, looppoint=0)
        self.dmg = 5
        if constants.dev_mode:
            print("Created Cherrybomb no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "Cherry Bomb"
        s += super().desc()
        s += f"\nINSTANT: DEALS {self.dmg} DMG\nIN A 3X3 AREA."
        return s
    
    def born(self, flag, info):
        self.create_particles(angle_range=360, angle_start=0, particles=150, spds = (8,20), drag = 0.92)
        pos = self.pos[:]
        targets = []
        for i in range(3):
            for j in range(3):
                y = pos[0] + (i-1)
                x = pos[1] + (j-1)
                if y < len(self.match.board) and x < len(self.match.board[0]) and y >= 0 and x >= 0:
                    targets += self.match.board[y][x].zombies
                    self.match.board[y][x].plants.append(CherryBomb.CherryKaboom(self.match,[y,x],None))
        self.attack(targets=targets,damage=self.dmg,damage_type=damage_types[2])
        super().born(flag, info)
        self.die(flag,info)
    
    class CherryKaboom(Unit):
        this_unit_team = 0
        offsets = [constants.board_proportions[0]+20, constants.board_proportions[1]-2, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+20,constants.display_proportions[1]+100, # start x (disp), start y (disp),
               160,170, # proportions (disp)
               80,80] # proportions (f)
        lengths_of_anim=[4,1]
        def __init__(self, match, pos, seedpacket=None):
            super().__init__(match=match, origin_pic_f="cherrybomb",
                            origin_pic_d="cherrybomb", pos=pos, stats=[0,0,0], seedpacket=seedpacket, looppoint=0)
        
        def desc(self):
            return "Explosion" + super().desc()
        
        def draw_f(self):
            super().draw_f()
            if self.pics_f[1] >= int(self.lengths_of_anim[0] * 5.5):
                self.match.board[self.pos[0]][self.pos[1]].plants.remove(self)
                self.match.switch_game_state(0)


class BrowncoatZombie(zombie):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-50, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+5, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-10, # proportions (disp)
               80,120] # proportions (f)
    lengths_of_anim = [5,10]
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="Browncoat",
                          origin_pic_d="BrowncoatDesc", pos=pos, stats=[1,1,1,1,1], seedpacket=seedpacket)
        if constants.dev_mode:
            print("Created browncoat no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "Browncoat"
        s += super().desc()
        return s

class Imp(zombie):
    offsets = [constants.board_proportions[0]+20, constants.board_proportions[1]-3, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+80, # start x (disp), start y (disp),
               180,216, # proportions (disp)
               60,72] # proportions (f)
    CARD_COOLDOWN = 2
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="imp",
                          origin_pic_d="imp", pos=pos, stats=[1,2,0,2,1], seedpacket=seedpacket)
        if constants.dev_mode:
            print("Created imp no.",self.iter,"in",str(self.pos))
    
    
    def desc(self):
        s = "Imp "
        s += super().desc()
        return s

class Grave(zombie):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-30, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+50, # start x (disp), start y (disp),
               192,192, # proportions (disp)
               96,96] # proportions (f)
    lengths_of_anim=[7,6]
    HOW_MANY_TURNS = 4
    CARD_COOLDOWN = 2
    particle_colors = [(60,60,69),(105,106,106),(212,92,189),(105,106,106),(89,86,82),(100,76,111),(212,92,189),(232,168,208)]
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="grave",
                          origin_pic_d="grave", pos=pos, stats=[3,2,self.HOW_MANY_TURNS-1,0,0], seedpacket=seedpacket, looppoint=12)
        if constants.dev_mode:
            print("Created grave no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "Grave"
        s += super().desc()
        s += f"\nAUTO-GENERATES 1$\nEVERY {self.HOW_MANY_TURNS} TURNS."
        s += "\nONLY 1 GRAVE/TILE."
        return s
    
    def react_to_start(self, flag, info):
        self.stats[2] -= 1
        if self.stats[2] <= 0:
            self.match.suns[1] +=1
            self.pics_f[1] = 0
            self.stats[2] = self.HOW_MANY_TURNS
    
    def activated(self, flag, info):
        return Unit.activated(self,flag,info)
    
    def isItSpawnable(self, tile):
        x = True
        z = [isinstance(zom,Grave) for zom in tile.zombies]
        return super().isItSpawnable(tile) and (z.count(True) < 1)

class FlagZombie(zombie):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-50, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+5, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-10, # proportions (disp)
               80,120] # proportions (f)
    lengths_of_anim = [4,5]
    SUNS_ADDED = (6,4) # Zombie, Plants
    CARD_COOLDOWN = 6
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="flag_zombie",
                          origin_pic_d="flag_zombie", pos=pos, stats=[2,0,0,1,1], seedpacket=seedpacket)
        if constants.dev_mode:
            print("Created FLAGZOMBIE no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "FLAG ZOMBIE"
        s += super().desc()
        s += f"\nADDS {self.SUNS_ADDED[0]}$ ON SPAWN.\nADDS {self.SUNS_ADDED[1]}# ON DEATH."
        s += "\nMUST MOVE EACH TURN."
        return s
    
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="flag_zombie",
                          origin_pic_d="flag_zombie", pos=pos, stats=[2,0,0,1,1], seedpacket=seedpacket)
    
    def born(self, flag, info):
        if (info[0] == self and self.isItSpawnable(info[1])):
            super().born(flag, info)
            self.match.suns[self.this_unit_team] += self.SUNS_ADDED[0]
    
    def die(self, flag, info):
        self.match.suns[1-self.this_unit_team] += self.SUNS_ADDED[1]
        return super().die(flag, info)
    
    def react_to_end(self, flag, info):
        if self.stats[2] == 0:
            self.move_forward(1)
        return super().react_to_end(flag, info)

class BucketheadZombie(zombie):
    offsets = [constants.board_proportions[0]+15, constants.board_proportions[1]-50, # Start x, Start y
               constants.board_proportions[2]/10, constants.board_proportions[3]/4, # size X of tile , size Y of one tile
               constants.display_proportions[0]+10,constants.display_proportions[1]+5, # start x (disp), start y (disp),
               constants.display_proportions[2]-750,constants.display_proportions[3]-10, # proportions (disp)
               80,120] # proportions (f)
    lengths_of_anim = [5,6]
    def __init__(self, match, pos, seedpacket=None):
        super().__init__(match=match, origin_pic_f="bucket",
                          origin_pic_d="bucket", pos=pos, stats=[5,4,1,1,1], seedpacket=seedpacket)
        if constants.dev_mode:
            print("Created buckethead no.",self.iter,"in",str(self.pos))
    
    def desc(self):
        s = "BUCKETHEAD"
        s += super().desc()
        s += "\nTURNS INTO BROWNCOAT\nZOMBIE ON DEATH."
        return s
    
    def die(self, flag, info):
        super().die(flag, info)
        x = BrowncoatZombie(self.match,self.pos[:],None)
        x.born(reaction_worthy_unit_flags[0],[x, self.match.board[self.pos[0]][self.pos[1]]])