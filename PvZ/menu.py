import pygame, sys, constants, drawable, buttons

class Game_Menu:

    def __init__(self, game = None, bg = None, but = None, fg = None, screen_color=(148, 85, 141)):
        if constants.dev_mode:
            print("menu.__init__: initing")
        if bg != None:
            self.game = game
            self.screen = game.screen
            self.screen_color = screen_color
            self.is_mouse_held = True
            self.bg_obj = bg
            self.buttons = []
            for i in bg+but+fg:
                x=i
                x.assign(self)
            for i in but:
                x=i
                self.buttons.append(x)
            self.fg_obj = fg

            self.buttons_above = []

    def initialize(self, scr):
        if constants.dev_mode:
            print("menu.initialize: initing test screen")
        self.game=None
        self.screen = scr
        self.screen_color = 148, 85, 141
        self.is_mouse_held = True
        self.bg_obj = []
        but = [buttons.Button("BTE", (500, 400, 80, 60), (512, 406, 16, 16), buttons.button_function_dupe)]
        self.buttons = []
        for i in but:
            i.assign(self)
            self.buttons.append(i)
        self.fg_obj = []
        self.buttons_above = []
        if constants.dev_mode:
            print("menu.initialize: finished initing test screen")

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.quit_game()

        self.screen.fill(self.screen_color)

        self.react_to_input()
        self.draw_all()

    def react_to_input(self):
        mouse_pos = pygame.mouse.get_pos()
        is_clicked = pygame.mouse.get_pressed()[0]
        self.handle_but_presses(mouse_pos, is_clicked)
    
    def handle_but_presses(self, mouse_pos, is_mouse_pressed):
        self.buttons_above.clear()
        for button in self.buttons:
            if button.point_in_rect(mouse_pos):
                button.seem_active()
                self.buttons_above.append(button)
            else:
                button.de_activate()
        if is_mouse_pressed:
            if (not self.is_mouse_held) and len(self.buttons_above) > 0:
                if constants.dev_mode:
                    print("activating ",self.buttons_above[0]," Their function is ",self.buttons_above[0].button_func)
                self.buttons_above[0].activate()
                self.is_mouse_held = True
        else:
            self.is_mouse_held = False

    def draw_all(self):
        for spr in self.bg_obj + self.buttons:
            spr.draw()
        for spr in self.fg_obj:
            if isinstance(spr,drawable.particle) and spr.alph <= 0:
                self.fg_obj.remove(spr)
            else:
                spr.draw()
                
    def quit_game(self):
        pygame.quit()
        sys.exit("Game Closed")


if __name__ == '__main__':
    pygame.init()
    scr = pygame.display.set_mode(constants.screen_size)
    g = Game_Menu()
    g.initialize(scr)

    while True:
        g.update()
