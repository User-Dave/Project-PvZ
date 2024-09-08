import pygame, math, loader, constants
class drawable:
    dev_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    def __init__(self, screen, origin, visual_rect):
        self.screen = screen
        self.origin = origin
        self.graphics = loader.loader(origin, size=[visual_rect[2],visual_rect[3]])
        self.visual_rect=visual_rect
        self.curr_img = self.load_image(0)

    def draw(self):
        self.screen.blit(self.curr_img,
                         (self.visual_rect[0],
                          self.visual_rect[1]))

        if constants.dev_mode:  # pygame.draw.rect(screen, otherstuff)
            pygame.draw.rect(self.screen, self.dev_colors[2],
                             (self.visual_rect[0], self.visual_rect[1],
                              self.visual_rect[2], self.visual_rect[3]),2)

    def load_image(self, number_from_loader):
        image = self.graphics.get(number_from_loader)
        if image is None:
            print(f"{self.__class__.__name__}.load_image: Error loading image for number {number_from_loader}")
        return image

    def transpose_by(self,x,y):
        for i in range(2):
            self.visual_rect[i] += (x,y)[i]

    def transpose_to(self,x,y):
        for i in range(2):
            self.visual_rect[i] = (x,y)[i]
    
    def assign(self, menu):
        self.screen = menu.screen
    

class particle(drawable):
    def __init__(self, screen, x, y, color, angle, spd, time_to_die = 1, drag = 0.5):
        vis_rect = [x,y,10,10]
        super().__init__(screen, origin="BTE", visual_rect=vis_rect)
        self.v = [int(math.cos(math.radians(angle)) * spd), int(math.sin(math.radians(angle)) * spd)]
        self.alph = 255
        self.color = color
        self.drag = drag
        self.curr_img = pygame.Surface((self.visual_rect[2], self.visual_rect[3]), pygame.SRCALPHA)
        self.curr_img.fill((*self.color, self.alph))  # Fill with color and alpha
        self.alph_decay = 255//(time_to_die*constants.frame_rate)
    
    def draw(self):
        super().draw()
        self.alph -= self.alph_decay
        self.transpose_by(self.v[0],self.v[1])
        for i in range(len(self.v)):
            self.v[i] = int(self.v[i]*self.drag)
        self.curr_img = pygame.Surface((self.visual_rect[2], self.visual_rect[3]), pygame.SRCALPHA)
        if self.alph > 0:
            try:
                self.curr_img.fill((*self.color, self.alph))  # Fill with color and alpha
            except Exception as e:
                print("tried filling with",str(self.color),"ran into",str(e))
