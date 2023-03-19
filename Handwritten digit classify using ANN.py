import pygame
import sys
from pygame.locals import *
import numpy as np
from numpy import testing
from keras.models import load_model
import cv2
from numpy.lib.type_check import imag

windowsizex=1200
windowsizey=700
boundaryinc=5
white=(255,255,255)
black=(0,0,0)
red=(255,0,0)
imagesave=False
# initialze pygame
pygame.init()
font = pygame.font.SysFont('calibri', 25)
model=load_model("Handwritten digit classify using mnist dataset model (1).h5")
labels={0:"Zero",
        1:"One",
        2:"Two",
        3:"Three",
        4:"Four",
        5:"Five",
        6:"Six",
        7:"Seven",
        8:"Eight",
        9:"Nine"}


displaysurf=pygame.display.set_mode((windowsizex,windowsizey))
pygame.display.set_caption("Handwritten digit board")
iswriting=False
number_xcord=[]
number_ycord=[]
predic=True
imgcnt=1
while True:
    for event in pygame.event.get():
        if event.type==QUIT:
            pygame.quit()
            sys.exit()
        if event.type==MOUSEMOTION and iswriting:
            xcord,ycord=event.pos
            pygame.draw.circle(displaysurf,white,(xcord,ycord),4,0)
            number_xcord.append(xcord)
            number_ycord.append(ycord)
        if event.type == MOUSEBUTTONDOWN:
            iswriting=True
        if event.type==MOUSEBUTTONUP:
            iswriting=False
            number_xcord=sorted(number_xcord)
            number_ycord=sorted(number_ycord)
            rect_minx,rect_maxx=max(number_xcord[0]-boundaryinc,0),min(windowsizex,number_xcord[-1]+boundaryinc)
            rect_miny, rect_maxy = max(number_ycord[0] - boundaryinc, 0), min(windowsizey,
                                                                              number_ycord[-1] + boundaryinc)
            number_xcord=[]
            number_ycord=[]
            imgarr=np.array(pygame.PixelArray(displaysurf))[rect_minx:rect_maxx,rect_miny:rect_maxy].T.astype(np.float32)
            if imagesave:
                cv2.imwrite("img.png")
                imgcnt+=1
            if predic:
                image=cv2.resize(imgarr,(28,28))
                image=np.pad(image,(10,10),'constant',constant_values=0)
                image=cv2.resize(image,(28,28))/255

                label=str(labels[np.argmax(model.predict(image.reshape(1,28,28,1)))])
                textsurf=font.render(label, True,red)

                textrectobj=pygame.surface.Surface.get_rect(textsurf)
                textrectobj.left ,textrectobj.bottom=rect_minx,rect_maxy


                displaysurf.blit(textsurf,textrectobj)
            if event.type==KEYDOWN:
                if event.unicode=="n":
                    displaysurf.fill(black)
        pygame.display.update()