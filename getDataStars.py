import numpy as np
from PIL import Image
def getDataStars(pathToImage):
    colImage = Image.open(pathToImage)
    hPixels, vPixels = colImage.size
    threshold = 100 # value needs to be calibrated
    bwImage = colImage.point(lambda x: 0 if x < threshold else 255)
    bwImagePixels = np.array(bwImage)
    colImagePixels = np.array(colImage)
    d = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    vis = [[False for _ in range(hPixels)] for _ in range(vPixels)]
    numStars = 0
    sizeStars = []
    locOnePixelStars = []
    avgRGBStars = []
    for i in range(vPixels):
        for j in range(hPixels):
            if vis[i][j] or bwImagePixels[i][j][0] != 255:
                continue
            vis[i][j] = True
            stack = [(i, j)]
            sizeStars.append(0)
            avgRGBStars.append([0, 0, 0])
            while stack:
                curR, curC = stack.pop()
                for rd, cd in d:
                    nextR, nextC = curR  +rd, curC + cd
                    if nextR < 0 or nextR >= vPixels or nextC < 0 or nextC >= hPixels:
                        continue
                    if vis[nextR][nextC]:
                        continue
                    if bwImagePixels[nextR][nextC][0] != 255:
                        continue
                    vis[nextR][nextC] = True
                    sizeStars[-1] += 1
                    stack.append((nextR, nextC))
                    avgRGBStars[-1][0] += colImagePixels[nextR][nextC][0]
                    avgRGBStars[-1][1] += colImagePixels[nextR][nextC][1]
                    avgRGBStars[-1][2] += colImagePixels[nextR][nextC][2]
            if 100 < sizeStars[-1] < 10000: # these two variables need to be calibrated
                numStars += 1
                locOnePixelStars.append((i, j))
                avgRGBStars[-1][0] = avgRGBStars[-1][0] // sizeStars[-1]
                avgRGBStars[-1][1] = avgRGBStars[-1][1] // sizeStars[-1]
                avgRGBStars[-1][2] = avgRGBStars[-1][2] // sizeStars[-1]
            else:
                sizeStars.pop()
                avgRGBStars.pop()
    dataStars = {}
    for i in range(numStars):
        dataStars[locOnePixelStars[i][1]] = [sizeStars[i], avgRGBStars[i]]
    return dataStars
