import pygame, constants
import assets
import menu
import Match, OnlineMatch, winscreen
import ClientProtocol
import drawable



class Game:
    def __init__(self,scr,server_ip = "0.0.0.0"):
        self.screen = scr
        self.displays = [
            menu.Game_Menu(self, [drawable.drawable(self.screen, "logo", [400,120,800,700])],
                            [assets.trans_start_but(50,300,1)], []),
            menu.Game_Menu(self,[],[#assets.dupe_BTE_but(700,400),
                                     assets.trans_start_but(0,0,2,"Local"),
                                     assets.trans_start_but(0,300,4,"Online"),
                                     assets.trans_start_but(1000,0,6,"Sets")],[]),
            Match.MatchPvZ(self),
            winscreen.win_screen(self),
            OnlineMatch.WaitingRoom(self,server_ip=server_ip),
            None,
            menu.Game_Menu(self,[drawable.drawable(None,"credits",[10,400,711,88]),
                                 drawable.drawable(None,"III",[10,550,850,80]),
                                 drawable.drawable(None,"YYY",[10,650,850,80]),
                                 drawable.drawable(None,"RRR",[10,750,1000,80])],[assets.particles_but(400,0),
                                    assets.make_dev_but(400,100),
                                     assets.trans_start_but(0,0,1)],[])
        ] # the different screens (#5 is an online match, starts not inited)
        self.current_display = 0
        self.frame = 0
        self.load_settings() # load in the settings


    def frame_advance(self):
        self.frame += 1
        if self.frame % 600 == 0 and constants.dev_mode: # print every 600 frames how long the program ran
            print("game.Game.frame_advance: ran " + str(self.frame) + " frames (" + str(self.frame/constants.frame_rate) + " Seconds)","\nalso, particles =",self.to_draw_particles)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.displays[self.current_display].quit_game() # use menu's quit_game function

        self.displays[self.current_display].update() # update the screen


        pygame.display.flip()
        pygame.time.Clock().tick(constants.frame_rate) # wait until the next frame

    def load_settings(self):
        tf = ["True","False"]
        f = ClientProtocol.open_file_with(__file__,"settings.txt","r")
        txt = f.read()
        particles = [True,False][tf.index(txt)]
        f.close()
        self.to_draw_particles = particles


if __name__ == '__main__':
    x = input("Server IP:")
    base_game = Game(assets.scr, x)

    while True:
        base_game.frame_advance()
