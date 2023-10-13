# IMPORTANT: Change path to csv file

csv_file = '19860118RANK.MAG.csv'



import csv

# Initialize empty lists for each column

speed = 0.1 # lower the faster, can go below 0

date = []
time = []
x = []
y = []
z = []
bg = ["bg+0.wav", "bg+1.wav", "bg+2.wav", "bg+3.wav", "bg+4.wav"]
import pygame.mixer
import time as time_module

# Initialize pygame mixer
pygame.mixer.init()

prev = "i"
now = "i"

chime_noise = pygame.mixer.Sound("new_chime.wav")
channel = pygame.mixer.Channel(0)


# Open the CSV file for reading
with open(csv_file, newline='') as csvfile:
    reader = csv.reader(csvfile)

    # Iterate through each row in the CSV file
    for row in reader:
        # Assuming a CSV file with 3 columns
        # date.append()
        # time.append(b)
        # x.append(c)
        # y.append(d)
        # z.append(e)
        #print(row)
        if len(row) != 0 and row[0][0].isdigit():
            t = row[1]
            time.append(float(t[0] + t[1]) + float(t[3] + t[4]) / 60 + float(t[6] + t[7]) / 3600)
            x.append(float(row[2]))
            y.append(float(row[3]))
            z.append(float(row[4]))

            # x -> pitch
            min_x = min(x) # low pitch 0
            if min_x == 0:
                min_x = 1
            max_x = max(x) # high pitch 4
            if max_x == 0:
                max_x = 1
            d = (max_x - min_x)
            if d == 0:
                d = 1
            rel = (float(row[2]) - min_x) / d
            ind = int(rel / 0.25)
            #print(ind)
            pygame.mixer.music.load(bg[ind])

            # y -> vol
            min_y = min(y)  # low pitch 0
            if min_y == 0:
                min_y = 1
            max_y = max(y)  # high pitch 4
            if max_y == 0:
                max_y = 1
            d = (max_y - min_y)
            if d == 0:
                d = 1
            rel = (float(row[2]) - min_y) / d
            rel *= 2
            pygame.mixer.music.set_volume(rel)

            # relative maximas of z: play high bing, relative minimas: play low bing
            if len(time) >= 2:
                if z[len(z) - 1] > z[len(z) - 2]:
                    now = "i"
                else:
                    now = "d"

                if prev != now:
                    # bing
                    #print("######################################")
                    #chime_noise.play()
                    channel.play(chime_noise)

                prev = now
            pygame.mixer.music.play(-1)
            time_module.sleep(speed)





