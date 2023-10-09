from PIL import Image
import pygame
import numpy as np
import getDataStars
import getDataSpecialObjects

 # change this variable to the path to an image and everything will work #
pathToImage = "testImgs/testImgNebula1.jpg"

image = Image.open(pathToImage)
hPixels, vPixels = image.size
image = np.array(image)
dataRGBColumn = []
for i in range(hPixels):
    avgRed = 0
    avgGreen = 0
    avgBlue = 0
    for j in range(vPixels):
        avgRed += image[j][i][0]
        avgGreen += image[j][i][1]
        avgBlue += image[j][i][2]
    avgRed = avgRed // vPixels
    avgGreen = avgGreen // vPixels
    avgBlue = avgBlue // vPixels
    dataRGBColumn.append((avgRed, avgGreen, avgBlue))

dataRGBColumn = dataRGBColumn
dataStars = getDataStars.getDataStars(pathToImage)
dataSpecialObjects = getDataSpecialObjects.getDataSpecialObjects(pathToImage)

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

image = pygame.image.load(pathToImage)
screen = pygame.display.set_mode((hPixels, vPixels))

audio = ["audio/bg0.wav", "audio/bg1.wav", "audio/bg2.wav", "audio/bg3.wav", "audio/bg4.wav"]

maxPitch = 4
instructions = [(0, 0)] # tuple where first item is at what column to initiate pitch and second item is what pitch
for i in range(1, hPixels):
    curBright = (dataRGBColumn[i][0] + dataRGBColumn[i][1] + dataRGBColumn[i][2]) / 3
    shiftedPitch = int((curBright / 255) * maxPitch)
    if shiftedPitch != instructions[-1][1]:
        instructions.append((i, shiftedPitch))

lineColour = (255, 255, 255)
lineThickness = 5
lineRowsStart = 0
lineRowsEnd = vPixels

chime = pygame.mixer.Sound("audio/chime.wav")
chime.set_volume(0.25)
special = pygame.mixer.Sound("audio/special.wav")
special.set_volume(1)

event = True
curColumn = 0
while event:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            event = False

    if instructions and instructions[0][0] == curColumn:
        bg = pygame.mixer.Sound(audio[instructions[0][1]])
        bg.set_volume(1)
        instructions.pop(0)
        bg.play(-1)

    for c in dataStars:
        if curColumn == c:
            chime.play()
    for cStart, cEnd in dataSpecialObjects:
        if cStart <= curColumn <= cEnd:
            special.play(-1)
            break
    else:
        special.fadeout(2000)

    screen.blit(image, (0, 0))
    pygame.draw.line(screen, lineColour, (curColumn, lineRowsStart), (curColumn, lineRowsEnd), lineThickness)
    pygame.display.update()

    curColumn += 1
    if curColumn >= hPixels:
        event = False
    # higher int value here will pass through image faster. lower int value will pass through slower #
    clock.tick(120)

pygame.mixer.music.stop()
pygame.quit()
