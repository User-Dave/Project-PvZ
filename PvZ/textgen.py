import constants, pygame, loader


DEF_COLORS = [(106, 190, 48, 255),(153, 229, 80, 255)]
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "0123456789" + "-+:/\\.,()<!@#$%^"
class font:
    def __init__(self, colors = DEF_COLORS[:] , size = [11,11]):
        # colors: interable(tuple(int*3)*2)
        # size: tuple(int*2)
        self.dir = loader.loader("fontext",1,size[:])
        self.__size = size
        if colors != DEF_COLORS[:]:
            for i in range(len(self.dir)):
                letter = self.dir.get(i)
                w,h = letter.get_size()
                for x in range(w):
                    for y in range(h):
                        for i in range(2):
                            if tuple(letter.get_at((x,y))) == DEF_COLORS[i]:
                                letter.set_at((x, y),colors[i])

    def render(self,text):
        LETTER_MARGIN = 1
        LINE_MARGIN = self.__size[1] // 4
        text = text.upper()
        lines = text.split("\n")
        # if constants.dev_mode: print("font: rendering",text, lines)
        height = max(self.__size[1] * len(lines) + LINE_MARGIN * (len(lines)-1) ,1)
        width = max([(self.__size[0] * len(line) + LETTER_MARGIN * (len(line)-1)) for line in lines])
        # if constants.dev_mode: print("font: width=",width)
        width = max(width, 1)
        # if constants.dev_mode: print("font: Height,width=",height,width)
        rendered_surface = pygame.surface.Surface((width, height), pygame.SRCALPHA, 32)
        y=0
        for line in lines:
            x = 0
            for i in line:
                if i in ALPHABET:
                    letter = self.dir.get(ALPHABET.index(i))
                    rendered_surface.blit(letter, (x,y))
                    x += self.__size[0] + LETTER_MARGIN
                elif i == " ":
                    x += self.__size[0]
                # else:
                    # if constants.dev_mode: print("ELSE",i)
            y += self.__size[1] + LINE_MARGIN
        return rendered_surface.convert_alpha()