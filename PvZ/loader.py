import constants
import pygame
import os


class loader:

    def __init__(self, dirname, copies=1, size=None):
        # dirname - the name of the folder in Sprites
        self.__pics = []
        self.__origindirectory = os.getcwd()
        self.__directory = os.getcwd()
        while not (self.__directory.endswith(constants.project_name)):
            self.__directory = self.__directory[:len(self.__directory) - 2]
        self.__directory += "\\Sprites" + "\\" + dirname
        # Changing directory
        os.chdir(self.__directory)
        to_pass=os.listdir()[:]
        for i in to_pass:
            if i[:-4].isnumeric() and len(i[:-4])<2:
                to_pass.remove(i)
                to_pass.append("0"+i)
        to_pass.sort()
        for i in to_pass:
            X=(pygame.image.load(str(i)).convert_alpha())
            if size != None: # dealing with the default value, if it's changed than stretch the image
                X = pygame.transform.scale(X,
                                      size)
            for i in range(copies): # adding copies of the image to __pics
                self.__pics.append(X)
        os.chdir(self.__origindirectory)

    def __str__(self):
        return "============================\nsprite loader details: \npics = " + str(self.__pics) + "\n============================"
    
    def get(self, i):
        if i >= 0 and i < len(self.__pics): return self.__pics[i]
        else:
            print("wanted to load photo number: " + str(i) + " in "+self.__directory)
            return None

    def __len__(self):
        return len(self.__pics)
