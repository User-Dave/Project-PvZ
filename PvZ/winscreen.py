import pygame, constants,  assets, drawable, buttons, menu, unitsPvZ, textgen

class win_screen(menu.Game_Menu):
    def __init__(self, game=None,
                  unit_responsible=None, team = 0):
        if unit_responsible==None:
            unit_responsible=unitsPvZ.Unit(match=self, origin_pic_f="LILBTE", origin_pic_d="BTE",
                                                  pos=[0, 0], stats=[6.66,6.66,6.66,6.66,6.66])
        super().__init__(game, bg=[], but=[assets.trans_start_but(x=640,y=500,dest=1)], fg=[])
        self.unit = unit_responsible
        self.font = self.font = textgen.font(size=[66,66])
        self.team = team

    def update(self):
        super().update()

        self.draw_unit()
    
    def draw_unit(self):
        self.unit.draw_d()

        text_surface = self.font.render("The "+("plants", "zombies")[self.team]+" win!")
        text_location = [250,700]
        self.screen.blit(text_surface, (text_location[0], text_location[1]))
