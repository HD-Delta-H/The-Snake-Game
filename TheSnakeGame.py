import pygame
import sys
import time
import random
import pickle
import os
pygame.init()
# global
import urllib.request

#image
def_powerup = pygame.transform.scale(
    pygame.image.load(r'images\powerups\Default.PNG'),
    (70, int(70 * 149 / 129)))


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        # print('Internet is on')
        return True
    except:
        return False


internet = connect()

if internet:
    import operator
    from typing import final
    from faunadb import query as q
    from faunadb.objects import Ref
    from faunadb.client import FaunaClient
    import re

    client = FaunaClient(
        secret="fnAEalXja4AAScBNFQW0lxRWEg-VZEhs-thXkrb6",
        # secret = "fnAEcMKAPvAAR5LqwD05oCTtvuIWTdsSHyuOu7AE",
        domain="db.us.fauna.com",
        # NOTE: Use the correct domain for your database's Region Group.
        port=443,
        scheme="https")

ndataset = 10


def sortedLeaderboardList(index, collection):
    indexes = client.query(q.paginate(q.match(q.index(index))))

    data = [indexes['data']]  # list of ref ids
    # print(indexes['data'])

    result = re.findall('\d+',
                        str(data))  # to find all the numbers in the list
    # print(result)

    fData = []

    for i in result:
        user_details = client.query(q.get(q.ref(q.collection(collection), i)))
        details = user_details['data']
        # print(details)
        tempData = [
            details['name'], details['score'], details['time'],
            1 / float(details['time']),
            int(user_details['ref'].id())
        ]
        # print(tempData)
        fData.append(tempData)

    finalData = sorted(fData, key=operator.itemgetter(1, 3), reverse=True)
    # print(finalData)

    return finalData


def pullOBJ():
    indexes = client.query(q.paginate(q.match(q.index('missionsindex'))))

    result = re.findall('\d+',
                        str([indexes['data']]))  # to find all the numbers in the list

    dataDict = {}

    details = client.query(q.get(q.ref(q.collection("dailymissions"), result[0])))['data']

    dataDict['mission'] = details['mission']
    dataDict['offer1'] = details['offer1']
    dataDict['offer2'] = details['offer2']
    dataDict['time'] = details['time']
    dataDict['day'] = details['day']
        
    return dataDict


def pushDictData(collection, data):
    client.query(q.create(q.collection(collection), {'data': data}))
   

def countDocs(collection):
    count = client.query(q.count(q.documents(q.collection(collection))))

    return count


def deleteDoc(collection, refid):
    client.query(q.delete(q.ref(q.collection(collection), refid)))


def sameScoreTimes(data, score):
    lTimes = []

    for i in data:
        if i[1] == score:
            lTimes.append(i[2])

    return lTimes


def bigGameVar():
    global data, sortedData
    names = []
    for i in sortedData:
        names.append(i[0])

    if data['name'] not in names:
        bigGame = False
        # print('Name not on leaderboard, BiGame set to False')
    elif os.path.exists("bigGame.dat"):
        with open('bigGame.dat', 'rb') as file:
            bigData = pickle.load(file)
        bigGame = bigData['bigGame']
        # print(f"In file, bigGame: {bigGame}")
    else:
        bigGame = False

    # writeBigGame(data['name'], bigGame)
    return bigGame


def writeBigGame(name, bigGameP):
    global bigGame
    bigGame = bigGameP
    bigData = {'name': name, 'bigGame': bigGameP}
    with open('bigGame.dat', 'wb') as file:
        pickle.dump(bigData, file)
    print(f'BigGame for {name} set to {bigGameP}')


def pushData(name, score, time, bigGameP):
    global Pop, PopT, data, fromsettings
    sortedData1 = sortedLeaderboardList(index='testindex',
                                        collection='testcollection')

    # for i in sortedData1:
    #     print(i)

    lScores = []
    lnames = []

    for i in sortedData1:
        lScores.append(i[1])
        lnames.append(i[0])

    # print(lScores)

    count = countDocs(collection='testcollection')

    dataDict = {'name': name, 'score': score, 'time': time}

    sending = False

    lTimes = sameScoreTimes(data=sortedData1, score=min(lScores))

    if count < ndataset:
        print(
            'Sending data to leaderboard as there\'s less than 10 players on it'
        )
        sending = True
    elif score > min(lScores):
        sending = True
        if bigGameP == False:
            print(
                'Sending data to leaderboard as you beat player(s) to deserve it'
            )
        if lScores.count(min(lScores)) == 1:
            for i in sortedData1:
                if i[1] == min(lScores):
                    if bigGameP == False:
                        deleteDoc(collection='testcollection', refid=i[4])
                        print(f'{i[0]}\'s name removed from the Leaderboard')
    elif score == min(lScores):
        print(
            'Sending data to leaderboard as you scored the same as the lowest person on leaderboard but in fewer time'
        )
        if time < max(lTimes):
            sending = True
            for i in sortedData1:
                if i[2] == max(lTimes):
                    if bigGameP == False:
                        deleteDoc(collection='testcollection', refid=i[4])
                        print(f'{i[0]}\'s name removed from the Leaderboard')

    if (sending):
        if (bigGameP):
            for i in sortedData1:
                if name == i[0]:
                    if score > i[1]:
                        deleteDoc(collection='testcollection', refid=i[4])
                        pushDictData(collection='testcollection',
                                     data=dataDict)
                        print("Your data on Leaderboard updated successfully!")
                        writeBigGame(data['name'], True)
                    elif score == i[1]:
                        if time < i[2]:
                            deleteDoc(collection='testcollection', refid=i[4])
                            pushDictData(collection='testcollection',
                                         data=dataDict)
                            print(
                                "Your data on Leaderboard updated successfully!"
                            )
                            writeBigGame(data['name'], True)
        else:
            if name in lnames:
                print(
                    'A player already thrives on the leaderboard with this name. Kindly follow the promts to change name or to not send the data to servers.'
                )
                return True
                # send data with changed name
                # writeBigGame(True)
            else:
                pushDictData(collection='testcollection', data=dataDict)
                print("Data sent successfully!")
                writeBigGame(data['name'], True)
    else:
        print("Data not sent since conditions are not met")


# pulling data
def pullingSortedData():
    try:
        data = sortedLeaderboardList(index='testindex',
                                     collection='testcollection')
        file = open("sortedData.dat", "wb")
        pickle.dump(data, file)
        file.close()
        print('data pulled')
        return data
    except:
        try:
            file = open("sortedData.dat", "rb")
            data = pickle.load(file)
            print('data taken from file')
            file.close()
            return data
        except:
            data = []
            print('data can\'t be pulled and file is empty or non-existent')
            return data


def saveGameDataForLater(name, score, time):
    try:
        fileR = open('savedData.dat', "rb")
        data = pickle.load(fileR)
        if data['score'] < score:
            fileW = open('savedData.dat', 'wb')
            pickle.dump(data, fileW)
        elif data['score'] == score:
            if data['time'] > time:
                fileW = open('savedData.dat', 'wb')
                pickle.dump(data, fileW)
        fileR.close()
    except:
        file = open('savedData.dat', 'wb')
        data = {'name': name, 'score': score, 'time': time}
        pickle.dump(data, file)
        file.close()


def maintain10onleaderboard():
    global sortedData
    toDelete = []
    revData = sortedData.copy()
    revData.reverse()

    if len(sortedData) > 10:
        n = len(sortedData) - 10
        print('n : ', n)
        for i in range(n):
            print('added: ', revData[i])
            toDelete.append(revData[i])

    if len(toDelete) >= 1:
        for i in toDelete:
            deleteDoc(collection='testcollection', refid=i[4])
            print(
                f'{i[0]}\'s name removed from Leaderboard as it doesn\'t qualify to show up there anymore.'
            )

        print('Leaderboard bought down to 10 players')


def pullCheaterlistData(index, collection):
    indexes = client.query(q.paginate(q.match(q.index(index))))

    data = [indexes['data']]  # list of ref ids
    # print(indexes['data'])

    result = re.findall('\d+',
                        str(data))  # to find all the numbers in the list

    fData = []

    for i in result:
        user_details = client.query(q.get(q.ref(q.collection(collection), i)))
        details = user_details['data']
        fData.append(details['name'])

    return fData


def cheaterlistData():
    try:
        data = pullCheaterlistData(index='cheaterindex',
                                   collection='cheaterlist')
        file = open("cheaterlist.dat", "wb")
        pickle.dump(data, file)
        file.close()
        print('data pulled')
        return data
    except:
        try:
            file = open("cheaterlist.dat", "rb")
            data = pickle.load(file)
            print('data taken from file')
            file.close()
            return data
        except:
            data = []
            print(
                'Cheaterlist data can\'t be pulled and file is empty or non-existent'
            )
            return data


def update_obj():
    with open('daily.dat', 'wb') as file:
        pickle.dump(obj, file)

sortedData = pullingSortedData()
# print(sortedData)
maintain10onleaderboard()


s = time.time()
day = int(((s + 19800) / 3600) // 24)
with open('daily.dat', 'rb') as file:
    dail = pickle.load(file)
    if dail['day'] < day:
        obj = pullOBJ()
        update_obj()

if internet and os.path.exists("savedData.dat"):
    try:
        fileR = open('savedData.dat', "rb")
        data = pickle.load(fileR)
        bigGame = bigGameVar()
        pushData(name=data['name'],
                 score=data['score'],
                 time=data['time'],
                 bigGame=bigGame)
        fileR.close()
        os.remove("savedData.dat")
        print('Saved data from previous games sent')
    except:
        print(
            "Saved data from previous games couldn't be sent due to an unexpected error"
        )

# line pygame.draw.line(SCREEN, BLUE, (100,200), (300,450),5) #screen, color, starting point, ending point, width
# rect pygame.draw.rect(SCREEN, BLUE, (390,390,50,25)) #screen, color, (starting_x, starting_y, width,height)
# circle pygame.draw.circle(SCREEN, BLUE, (150,150), 75) #screen, color, (center_x, center_y), radius)
# polygon pygame.draw.polygon(SCREEN, BLUE, ((25,75),(76,125),(250,375),(390,25),(60,540))) #screen, color, (coordinates of polygon(consecutive))
# image pygame.image.load("space-invaders.png")


def readSettings():
    try:
        with open('userSettings.dat', 'rb') as file:
            setData = pickle.load(file)
        return setData
    except:
        setData = {
            'volume': 80,
            'music': True,
            'sound': True,
            'arrow': True,
            'fauna': True
        }
        with open('userSettings.dat', 'wb') as file:
            pickle.dump(setData, file)
        return setData


def updateSettings(setData):
    with open('userSettings.dat', 'wb') as file:
        pickle.dump(setData, file)
    # print('Settings Updated')


userSettings = readSettings()

#constants
LENGTH = 454
PIXEL = 15
SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH), pygame.RESIZABLE)

CLOCK = pygame.time.Clock()
rate = 8
coin_2, point_2 = False, False
sensitivity=0
#colours
LIGHTBROWN = '#AD9157'
DARKBROWN = '#4F3119'
BLACKBROWN = '#11110F'
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
RED = (255, 0, 0)
ORANGE = (255, 120, 0)
VOILET = (100, 0, 100)
PINK = (255, 0, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 255, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
A = "".join([chr(x) for x in range(65, 91)])
ALPHA = A + A.lower() + '_' + ''.join([str(x) for x in range(10)])
cheaterImage = pygame.image.load(r'images\cheater.png')
sideSnake = pygame.image.load(r'images\side-snake.png')
frontSnake = pygame.image.load(r'images\front-snake.png')
bgMusic = pygame.mixer.music.load(r'audios\bgmusic.mp3')
speedupMusic = pygame.mixer.Sound(r'audios\speedup.wav')
buttonSound = pygame.mixer.Sound(r'audios\button.wav')
appleMusic = pygame.mixer.Sound(r'audios\apple.wav')
bombMusic = pygame.mixer.Sound(r'audios\bomb.wav')
speeddownMusic = pygame.mixer.Sound(r'audios\speeddown.wav')
gameOverSound = pygame.mixer.Sound(r'audios\gameOver.wav')

#[[name,score,timeplayed,1_time,ref_id]]


#user data
def newUser_init():
    global Cursor, Text_Val, iterrr
    iterrr = 0
    Cursor = False
    Text_Val = ''


fromsetting = False
try:
    file = open('userData.dat', 'rb')
    data = pickle.load(file)
    non_cheater = True
except pickle.UnpicklingError:
    user = 'Cheater'
    non_cheater = False
    try:
        with open('bigGame.dat', 'rb') as file:
            bigData = pickle.load(file)
        dictData = {'name': bigData['name']}
        pushDictData(collection='cheaterlist', data=dictData)
    except:
        pass
    print('YOU CHEATED!')
if non_cheater:
    if data['name'] == '' or data['name'] == None:
        user = 'NewUser'
        print('Redirecting to New User')
        newUser_init()
    else:
        user = 'Home'
    file.close()


def show(msg, color, x, y, size):
    score_show = pygame.font.Font("freesansbold.ttf",
                                  size).render(msg, True, color)
    SCREEN.blit(score_show, (x, y))


selected_items = [False, False, False, False, False, False]

Pop = False
I = 0
iterr = 0

def update_data():
    with open('userData.dat', 'wb') as file:
        pickle.dump(data, file)


def daily():
    global obj
    mission_list = [['points', 20, 200], ['up', 20, 100], ['down', 20, 100],
                    ['apple', 50, 250], ['speed', 0, 11]]
    items_dict = {
        "More Ice Apples": 12,
        "More Green Apples": 12,
        "High Vel": 8,
        "Low Vel": 8,
        "Fewer Bombs": 15,
        "Teleport": 40,
    }
    s = time.time()
    day = int(((s + 19800) / 3600) // 24)
    with open('daily.dat', 'rb') as file:
        dail = pickle.load(file)
        if dail['day'] < day:
            mis = random.choice(mission_list)
            val = random.randint(mis[1], mis[2])
            disp_v = val * (50 if mis[0] == 'points' else
                            (2 if mis[0] == 'speed' else 1))
            rat_cal = (abs(
                (6 - val) / (6 - mis[2])) if mis[0] == 'speed' else val /
                       mis[2])
            rat = float(f"{rat_cal:.2f}")
            reward = (('5' if val < 0.4 else
                       ('30' if val > 0.8 else '10')) + '-' + random.choice(
                           ('C', 'P')),
                      int(rat *
                          (15 if mis[0] in ('up', 'down', 'speed') else 30)))
            it = random.choice(list(items_dict.keys()))
            obj = {
                'mission': [
                    mis[0], disp_v, reward,
                    (f"0/{disp_v}" if mis[0] in ('apple', 'up',
                                                 'down') else False), False
                ],
                'offer1': (it, items_dict[it] * random.randint(25, 75) / 100,
                           items_dict[it]),
                'offer2':
                '',
                'time':
                s,
                'day':
                day
            }
            update_obj()
            pushDictData(collection = 'dailymissions', data = obj)
        else:
            obj = dail


def button(text,
           x,
           y,
           width,
           height,
           bg_color=WHITE,
           x_offset=10,
           text_size=10,
           text_col=BLACK,
           hover_col=BLUE,
           hover_width=2):
    global buttonSound,sensitivity
    pos = pygame.mouse.get_pos()
    if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
            1] <= y + height:
        pygame.draw.rect(SCREEN, hover_col,
                         (x - hover_width, y - hover_width,
                          width + hover_width * 2, height + hover_width * 2))
        if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
            sensitivity=time.time()
            if userSettings['sound']:
                buttonSound.play(loops=0)
            return True
    pygame.draw.rect(SCREEN, bg_color, (x, y, width, height))
    show(text, text_col, x + x_offset,
         (y + (height - text_size) // 2 if height > text_size else height),
         text_size)


def screen_animation(decreaser=False, r=25, color=BLACK, timer=0.01):
    global I, iterr

    if iterr == 0:
        I = r if decreaser else 0
        stopper = False
    stopper = True if I > r else (True if I < 0 else False)
    if stopper:
        iterr = 0
        return True
    s = pygame.Surface((LENGTH, LENGTH))
    s.set_alpha((I * 255 // r + 255 % r))
    I -= 1 if decreaser else -1
    iterr += 1
    time.sleep(timer)
    s.fill(color)
    SCREEN.blit(s, (0, 0))
    return False


def home_params():
    pass
    # global i, decreaser, done
    # i = 0
    # done = False
    # decreaser = False


breaker = False

# reBigGame = False
    
def home():
    global i, decreaser, done, user, start, breaker, frontSnake
    bigGame = bigGameVar()
    LENGTH = pygame.display.get_surface().get_width()
    HEIGHT = pygame.display.get_surface().get_height()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, HEIGHT - 60))
    usualWidth, margin = 120, 65

    show('playing as ', LIGHTBROWN, 20, 16, 16)
    show(data['name'].upper() + '.', WHITE, 110, 9, 24)
    show(data['coin'] + ' coins', WHITE, 275, 9, 24)
    user = 'Settings' if button('Settings',
                                LENGTH - 154,
                                5,
                                100,
                                30,
                                LIGHTBROWN,
                                x_offset=10,
                                text_col=DARKBROWN,
                                text_size=16,
                                hover_col=BLACKBROWN,
                                hover_width=1) else user
    
    if bigGame:
        pygame.draw.rect(SCREEN, RED, (LENGTH - 30, 10, 10, 20))

    scaledFrontSnake = pygame.transform.scale(
        frontSnake, (int(250 * HEIGHT / 400), int(250 * HEIGHT / 400)))
    frontSnakeSize = scaledFrontSnake.get_size()

    scaledSideSnake = pygame.transform.scale(
        sideSnake, (int(250 * HEIGHT / 454), int(250 * HEIGHT / 454)))
    sideSnakeSize = scaledSideSnake.get_size()

    flippedScaledSideSnake = pygame.transform.flip(scaledSideSnake, True,
                                                   False)
    scaledSideSnake.set_alpha(55), flippedScaledSideSnake.set_alpha(55)

    SCREEN.blit(
        scaledSideSnake,
        (margin + (usualWidth * LENGTH / 554 - sideSnakeSize[0]) / 2, 40 +
         (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2 + frontSnakeSize[1] / 4))
    SCREEN.blit(
        flippedScaledSideSnake,
        (LENGTH -
         (margin +
          (usualWidth * LENGTH / 554) / 2 + sideSnakeSize[0] / 2 + 15), 40 +
         (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2 + frontSnakeSize[1] / 4))

    user = 'Arsenal' if button('Play Game',
                               (LENGTH - (170 * LENGTH / 554)) / 2,
                               265 * HEIGHT / 454,
                               170 * LENGTH / 554,
                               55 * HEIGHT / 454,
                               DARKBROWN,
                               x_offset=30 + (10**(LENGTH / 554)) / 5,
                               text_col=WHITE,
                               text_size=int(24 * LENGTH / 700),
                               hover_col=BLACKBROWN,
                               hover_width=1) else user
    SCREEN.blit(scaledFrontSnake,
                ((LENGTH - frontSnakeSize[0]) / 2, 30 +
                 (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2))

    newUser = button('New User',
                     margin,
                     380 * HEIGHT / 454,
                     usualWidth * LENGTH / 554,
                     30 * HEIGHT / 454,
                     DARKBROWN,
                     x_offset=20 + (10**(LENGTH / 554)) / 3,
                     text_col=WHITE,
                     text_size=16,
                     hover_col=BLACKBROWN,
                     hover_width=1)
    if newUser:
        newUser_init()
        user = 'NewUser'

    user = 'LeaderBoard' if button('LeaderBoard',
                                   margin,
                                   300 * HEIGHT / 454,
                                   usualWidth * LENGTH / 554,
                                   30 * HEIGHT / 454,
                                   DARKBROWN,
                                   x_offset=7 + (10**(LENGTH / 554)) / 3,
                                   text_col=WHITE,
                                   text_size=16,
                                   hover_col=BLACKBROWN,
                                   hover_width=1) else user
    if button('Missions',
              margin,
              340 * HEIGHT / 454,
              usualWidth * LENGTH / 554,
              30 * HEIGHT / 454,
              DARKBROWN,
              x_offset=20 + (10**(LENGTH / 554)) / 3,
              text_col=WHITE,
              text_size=16,
              hover_col=BLACKBROWN,
              hover_width=1):
        user = 'Missions'
        daily()
    user = 'MarketPlace' if button('Shop',
                                   LENGTH -
                                   (margin + usualWidth * LENGTH / 554),
                                   300 * HEIGHT / 454,
                                   usualWidth * LENGTH / 554,
                                   30 * HEIGHT / 454,
                                   DARKBROWN,
                                   x_offset=35 + (10**(LENGTH / 554)) / 3,
                                   text_col=WHITE,
                                   text_size=16,
                                   hover_col=BLACKBROWN,
                                   hover_width=1) else user
    user = 'Inventory' if button('Inventory',
                                 LENGTH - (margin + usualWidth * LENGTH / 554),
                                 340 * HEIGHT / 454,
                                 usualWidth * LENGTH / 554,
                                 30 * HEIGHT / 454,
                                 DARKBROWN,
                                 x_offset=20 + (10**(LENGTH / 554)) / 3,
                                 text_col=WHITE,
                                 text_size=16,
                                 hover_col=BLACKBROWN,
                                 hover_width=1) else user
    user = 'Cheaterlist' if button('Cheaters\' list',
                                   LENGTH -
                                   (margin + usualWidth * LENGTH / 554),
                                   380 * HEIGHT / 454,
                                   usualWidth * LENGTH / 554,
                                   30 * HEIGHT / 454,
                                   DARKBROWN,
                                   x_offset=7 + (10**(LENGTH / 554)) / 3,
                                   text_col=WHITE,
                                   text_size=16,
                                   hover_col=BLACKBROWN,
                                   hover_width=1) else user
    user = 'Licenses' if button('SEE LEGAL INFO',
                                (LENGTH - (140 * LENGTH / 554)) / 2,
                                380 * HEIGHT / 454,
                                140 * LENGTH / 554,
                                30 * HEIGHT / 454,
                                LIGHTBROWN,
                                x_offset=(10**(LENGTH / 554)) / 3,
                                text_col=DARKBROWN,
                                text_size=16,
                                hover_col=BLACKBROWN,
                                hover_width=1) else user

    # if not done:
    #     d = screen_animation()
    #     done = d
    # if done:
    #     d = screen_animation(True)
    #     done = not d


def arsenal():
    global user, start, SCREEN, selected_items, coin_2, point_2, Pop, userSettings,sensitivity
    LENGTH = pygame.display.get_surface().get_width()
    # LENGTH = 554
    # SCREEN = pygame.display.set_mode((LENGTH, 454))
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('Your Arsenel for the game', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)

        mul = (LENGTH - 30) // 3
        for i, item in enumerate(list_items['Powerups'].items()):
            if i <= 2:
                global event_list
                pos = pygame.mouse.get_pos()
                x, y, width, height = (20 + i * mul, 70, mul - 20, 135)
                pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                pygame.draw.rect(SCREEN, LIGHTBROWN,
                                 (x + 5, y + 5, width - 10, height - 10))
                SCREEN.blit(def_powerup, (60 + i * mul, 80))
                if i == 1:
                    show(item[0], BLACK, 30 + i * mul, 165, 14)
                    show(f'{item[1][0]} in stock', WHITE, 30 + i * mul, 185,
                         12)
                else:
                    show(item[0], BLACK, (65 if i == 2 else 35) + i * mul, 165,
                         16)
                    show(f'{item[1][0]} in stock', WHITE, 30 + i * mul, 185,
                         12)
                s = pygame.Surface((width, height))
                s.set_colorkey(GREY)
                s.set_alpha(0)
                if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
                        1] <= y + height and not Pop:
                    if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                        sensitivity=time.time()
                        if item[1][0] != '0' or selected_items[i]:
                            with open('items.dat', 'wb') as f:
                                list_items['Powerups'][item[0]] = (str(
                                    int(item[1][0]) +
                                    (1 if selected_items[i] else -1)),
                                                                   item[1][1])
                                pickle.dump(list_items, f)
                            selected_items[i] = not selected_items[i]
                        else:
                            Pop = True
                    s.set_alpha(60)
                if selected_items[i]:
                    s.set_alpha(120)
                SCREEN.blit(s, (x, y))

            elif i <= 5:
                x, y, width, height = (20 + (i - 3) * mul, 230, mul - 20, 135)
                pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                pygame.draw.rect(SCREEN, LIGHTBROWN,
                                 (x + 5, y + 5, width - 10, height - 10))
                SCREEN.blit(def_powerup, (60 + (i - 3) * mul, 240))
                show(item[0], BLACK, (45 if i == 4 else 65) + (i - 3) * mul,
                     325, 16)
                show(f'{item[1][0]} in stock', WHITE, 30 + (i - 3) * mul, 345,
                     12)
                s = pygame.Surface((width, height))
                pos = pygame.mouse.get_pos()
                s.set_colorkey(GREY)
                s.set_alpha(0)
                if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
                        1] <= y + height and not Pop:
                    if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                        sensitivity=time.time()
                        if item[1][0] != '0' or selected_items[i]:
                            with open('items.dat', 'wb') as f:
                                list_items['Powerups'][item[0]] = (str(
                                    int(item[1][0]) +
                                    (1 if selected_items[i] else -1)),
                                                                   item[1][1])
                                pickle.dump(list_items, f)
                            selected_items[i] = not selected_items[i]
                        else:
                            Pop = True
                    s.set_alpha(60)
                if selected_items[i]:
                    s.set_alpha(120)
                SCREEN.blit(s, (x, y))
    if Pop:
        Popup('Item not in stock')
    with open('missions.dat', 'rb') as file:
        list_items = pickle.load(file)
        coin_2 = list_items['coins']['coins']
        point_2 = list_items['coins']['points']
        for i, item in enumerate(list_items['coins'].items()):
            if i <= 5:
                if item[1][1]:
                    t = float(f"{(time.time()-item[1][2]):.2f}")
                    if t >= (float(item[0].split()[2]) * 60):
                        with open('missions.dat', 'wb') as f:
                            list_items['coins'][item[0]][1] = False
                            if i <= 2:
                                list_items['coins']['coins'] = False
                            elif i <= 5:
                                list_items['coins']['points'] = False
                            pickle.dump(list_items, f)

    show('2x Coins :' + ('Activated' if coin_2 else 'Not Activated'), WHITE,
         25, 375, 18)
    show('2x Points :' + ('Activated' if point_2 else 'Not Activated'), WHITE,
         305, 375, 18)
    if button('Start Game',
              LENGTH // 2 - 55,
              410,
              110,
              32,
              DARKBROWN,
              text_col=WHITE,
              text_size=16,
              hover_width=0):
        if userSettings['music']:
            pygame.mixer.music.set_volume(userSettings['volume'] / 100)
            pygame.mixer.music.play(loops=-1)
        user = 'Emulator'
    if button('Home',
            LENGTH - 154,
            5,
            100,
            30,
            LIGHTBROWN,
            x_offset=10,
            text_col=DARKBROWN,
            text_size=16,
            hover_col=BLACKBROWN,
            hover_width=1):
        user = 'Home' 
        with open('items.dat', 'rb') as file:
            list_items = pickle.load(file)

            for i, item in enumerate(list_items['Powerups'].items()):
                list_items['Powerups'][item[0]] = (str(
                    int(item[1][0]) +
                    (1 if selected_items[i] else 0)),
                                                    item[1][1])
                selected_items[i]=False
        with open('items.dat', 'wb') as f:
            pickle.dump(list_items, f)
    if user == 'Emulator':
        emulator_params()
        daily()


def emulator_params():
    global Blocks, snake, direction, body, Apple, random_cord, Bomb, SpeedUp, SpeedDown, counter, rnt, score, ee_dec, ee_done, realm
    global Theme, blocks, LENGTH, rate, start, SCREEN, popup, applex, appley, m_counter, st, speed_checker,petyr
    LENGTH = 454
    rate = 4 if selected_items[3] else (12 if selected_items[2] else 8)

    Theme = [
        LIGHTBROWN, (210, 190, 210), RED, YELLOW, GREY, GREEN, BLUE, WHITE,
        DARKBROWN
    ]
    # bg_color, bomb_col, snake_col, apple_col, empty_col, sup_col, sdown_col, text_col, text_bg
    with open('items.dat', 'rb') as file:
        l = pickle.load(file)
        Theme[4] = globals()[list(
            l['Themes'][l['Offers']['pseudo']['background']].keys())[0]]
        Theme[2] = globals()[list(
            l['Themes'][l['Offers']['pseudo']['snake']].keys())[1]]
    score = 0
    realm = False
    rnt = [0, 0, 0]
    ee_dec = False
    popup = False
    ee_done = False
    counter = [0, 0, 0]  #bomb,speedup,speeddown
    Apple = True
    Bomb, SpeedUp, SpeedDown = False, False, False
    snake = [LENGTH // 2, LENGTH // 2]
    direction = 'up'
    body = [(LENGTH // 2, LENGTH // 2 + PIXEL),
            (LENGTH // 2, LENGTH // 2 + 2 * PIXEL)]

    class Blocks:
        def __init__(self, x, y, block_type=None) -> None:
            self.x = x
            self.y = y
            self.block_type = block_type
            self.color = Theme[4]

        def draw(self):
            if self.block_type == "snake" or self.block_type == "head":
                self.color = Theme[2]
            elif self.block_type == None:
                self.color = Theme[4]
            elif self.block_type == 'apple':
                self.color = Theme[3]
            elif self.block_type == 'bomb':
                self.color = Theme[1]
            elif self.block_type == 'speedup':
                self.color = Theme[5]
            elif self.block_type == 'speeddown':
                self.color = Theme[6]
            pygame.draw.rect(SCREEN, self.color,
                             (self.x + 1, self.y + 1, PIXEL - 2, PIXEL - 2))
    petyr=0
    blocks = []
    # missions initialize
    with open('missions.dat', 'rb') as file:
        miss = pickle.load(file)
        m_counter = {'apple': [], 'up': [], 'down': []}
        speed_checker = []
        st = []
        for m in miss['missions']:
            if m[0] in ('apple', 'up', 'down'):
                m_counter[m[0]].append(m[3])
            if m[0] == 'speed':
                speed_checker.append(m[1])
            if m[0] == 'st':
                st.append(m[1])

    #Spawner Function
    def random_cord(lis):
        b = random.choice(list(filter(lambda x: x.block_type == None, lis)))
        return (b.x, b.y)

    #Main Block loop
    for x in range(0, (LENGTH // PIXEL)):
        X = 2 + x * PIXEL
        for y in range(0, (LENGTH // PIXEL) - 2):
            Y = 2 + (y + 2) * PIXEL
            block = Blocks(X, Y)
            blocks.append(block)
    SCREEN = pygame.display.set_mode((LENGTH, LENGTH))
    start = time.time()
    applex, appley = random_cord(blocks)

changeNameForLead = False
showHomeButton = False
tempDataForLead = {
    'score':0,
    'time':0
}

def emulator():
    global direction, Apple, Bomb, SpeedUp, SpeedDown, counter, rnt, Theme, event_list, realm, t0, start, selected_items, blocks, popup, coin_2, point_2
    global applex, appley, bombx, bomby, speedupx, speedupy, speeddownx, speeddowny, score, rate, ee_dec, ee_done, user, data, coins, t, SCREEN
    global sortedData, Pop, PopT, userSettings,sensitivity,petyr, changeNameForLead, showHomeButton, tempDataForLead
    gameover = False
    SCREEN.fill(Theme[0])
    pygame.draw.rect(SCREEN, BLACK, (2, 32, LENGTH - 4, LENGTH - 35))
    body.insert(0, tuple(snake))
    body.pop(-1)
    if not popup:
        #Bomb
        if counter[0] == 0:
            bombx, bomby = -1, -1
            rnt[0] = random.randint((150 if selected_items[4] else 20),
                                    (160 if selected_items[4] else 35))
        elif counter[0] == rnt[0]:
            Bomb = True
        elif counter[0] == rnt[0] + 40:
            counter[0] = -1
        #SpeedUp
        if counter[1] == 0:
            speedupx, speedupy = -1, -1
            rnt[1] = random.randint((20 if selected_items[1] else 65),
                                    (35 if selected_items[1] else 85))
        elif counter[1] == rnt[1]:
            SpeedUp = True
        elif counter[1] == rnt[1] + 60:  # + (rate - 8) * 5:
            counter[1] = -1
        #SpeedDown
        if counter[2] == 0:
            speeddownx, speeddowny = -1, -1
            rnt[2] = random.randint((20 if selected_items[0] else 65),
                                    (35 if selected_items[0] else 85))
        elif counter[2] == rnt[2]:
            SpeedDown = True
        elif counter[2] == rnt[2] + 60:
            counter[2] = -1

        counter = [x + 1 for x in counter]
        #Spawner
        if Bomb == True:
            bombx, bomby = random_cord(blocks)
            Bomb = False
        if SpeedUp == True:
            speedupx, speedupy = random_cord(blocks)
            SpeedUp = False
        if SpeedDown == True:
            speeddownx, speeddowny = random_cord(blocks)
            SpeedDown = False
        # Teleportation
        if selected_items[5]:
            snake[0] = -13 if snake[0] > 452 else (
                452 if snake[0] < -13 else snake[0])
            snake[1] = 17 if snake[1] > 453 else (
                452 if snake[1] < 17 else snake[1])
            
        #Collision Logics
        if tuple(snake) == (applex, appley):
            if userSettings['sound']:
                appleMusic.play(loops=0)
            body.append(body[-1])
            Apple = True
            for i, c in enumerate(m_counter['apple']):
                C = c.split('/')
                m_counter['apple'][i] = str(
                    int(C[0]) +
                    (1 if int(C[0]) < int(C[1]) else 0)) + '/' + C[1]
            if obj['mission'][0] == 'apple':
                c = obj['mission'][3]
                C = c.split('/')
                obj['mission'][3] = str(
                    int(C[0]) +
                    (1 if int(C[0]) < int(C[1]) else 0)) + '/' + C[1]
            score += 100 if point_2 else 50
            for pair in st:
                if (time.time() - start) <= pair[1] and score == pair[0]:
                    with open('missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'st' and pair == m[1]:
                                with open('missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
        elif tuple(snake) == (bombx, bomby):
            if userSettings['sound']:
                bombMusic.play(loops=0)
            bombx, bomby = -1, -1
            score -= 100
        elif tuple(snake) == (speedupx, speedupy):
            if userSettings['sound']:
                speedupMusic.play(loops=0)
            speedupx, speedupy = -1, -1
            rate += 2
            for i, c in enumerate(m_counter['up']):
                C = c.split('/')
                m_counter['up'][i] = str(
                    int(C[0]) +
                    (1 if int(C[0]) < int(C[1]) else 0)) + '/' + C[1]
            if obj['mission'][0] == 'up':
                c = obj['mission'][3]
                C = c.split('/')
                obj['mission'][3] = str(
                    int(C[0]) +
                    (1 if int(C[0]) < int(C[1]) else 0)) + '/' + C[1]
            score += 300 if point_2 else 150
            for pair in st:
                if (time.time() - start) <= pair[1] and score == pair[0]:
                    with open('missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'st' and pair == m[1]:
                                with open('missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            for v in speed_checker:
                if rate == v:
                    with open('missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'speed' and m[1] == v:
                                with open('missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            if obj['mission'][0] == 'speed':
                if rate == obj['mission'][1]:
                    obj['mission'][3] = True
        elif tuple(snake) == (speeddownx, speeddowny):
            if userSettings['sound']:
                speeddownMusic.play(loops=0)
            speeddownx, speeddowny = -1, -1
            for i, c in enumerate(m_counter['down']):
                C = c.split('/')
                m_counter['down'][i] = str(
                    int(C[0]) +
                    (1 if int(C[0]) < int(C[1]) else 0)) + '/' + C[1]
            if obj['mission'][0] == 'down':
                c = obj['mission'][3]
                C = c.split('/')
                obj['mission'][3] = str(
                    int(C[0]) +
                    (1 if int(C[0]) < int(C[1]) else 0)) + '/' + C[1]
            rate -= 2
            score += 300 if point_2 else 150
            for pair in st:
                if (time.time() - start) <= pair[1] and score == pair[0]:
                    with open('missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'st' and pair == m[1]:
                                with open('missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            for v in speed_checker:
                if rate == v:
                    with open('missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'speed' and m[1] == v:
                                with open('missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            if obj['mission'][0] == 'speed':
                if rate == obj['mission'][1]:
                    obj['mission'][3] = True
        if Apple == True:
            applex, appley = random_cord(blocks)
            Apple = False
        if (tuple(snake) in body[1::]):
            gameover = True
        if (not (-10 <= snake[0] <= 450) or not (20 <= snake[1] <=
                                              450)) and not selected_items[5]:
            gameover = True
        # 0 speed Realm
        if rate == 0:
            realm = True
            t0 = time.time()
            rate = 200
        if realm:
            selected_items[5] = True
            Theme[2], Theme[7] = Theme[7], Theme[2]
            Theme[4] = Theme[0]
            Theme[5], Theme[3], Theme[6], Theme[
                1] = VOILET, VOILET, VOILET, VOILET
            if counter[0] % 5 == 0:
                body.append(body[-1])
            if counter[0] % 2 == 0:
                direction = 'up' if snake[1] > 250 else 'down'
            else:
                direction = 'left' if snake[0] > 250 else 'right'

            if time.time() - t0 > 3:
                SCREEN.fill((0, 0, 0))
                show('The laws of Physics tends to bend when', (200, 200, 200),
                     20, 210, 22)
                show('someone enters the speed 0 realm', (200, 200, 200), 45,
                     240, 22)
            else:
                if not ee_done:
                    ee_dec = screen_animation(False, 5, Theme[7], 0.001)
                    ee_done = ee_dec
                if ee_done:
                    ee_dec = screen_animation(True, 5, Theme[7], 0.0001)
                    ee_done = not ee_dec
        #event loop
        for event in event_list:
            if event.type == pygame.KEYDOWN and not snake[0] in (452,-13) and not snake[1] in (452,17) and (time.time()-sensitivity)>0.01*((16-rate) if rate<=14 else 0):
                sensitivity=time.time()
                
                if event.key == (pygame.K_UP if userSettings['arrow'] else pygame.K_w) and not direction == "down":
                    direction = "up"
                if event.key == (pygame.K_DOWN if userSettings['arrow'] else pygame.K_s) and not direction == "up":
                    direction = "down"
                if event.key == (pygame.K_LEFT if userSettings['arrow'] else pygame.K_a) and not direction == "right":
                    direction = "left"
                if event.key == (pygame.K_RIGHT if userSettings['arrow'] else pygame.K_d) and not direction == "left":
                    direction = "right"
        #Movement
        if direction == 'up':
            snake[1] -= PIXEL
        elif direction == 'down':
            snake[1] += PIXEL
        elif direction == 'left':
            snake[0] -= PIXEL
        elif direction == 'right':
            snake[0] += PIXEL
        #GameOver
        if gameover:
            pygame.mixer.music.stop()
            gameOverSound.play(loops=0)
            popup = True
            t = f'{(time.time() - start):.2f}'
            coins = int(8 * (score / 1000) -
                        (time.time() - start) / 60) * (2 if coin_2 else 1)

            
    #block loop
    for block in blocks:
        block.block_type = None
        for part in body:
            if (block.x, block.y) == part:
                block.block_type = 'head'
        if (block.x, block.y) == tuple(snake):
            block.block_type = 'snake'
        elif (block.x, block.y) == (applex, appley):
            block.block_type = 'apple'
        elif (block.x, block.y) == (bombx, bomby):
            block.block_type = 'bomb'
        elif (block.x, block.y) == (speedupx, speedupy):
            block.block_type = 'speedup'
        elif (block.x, block.y) == (speeddownx, speeddowny):
            block.block_type = 'speeddown'
        block.draw()
    #Score
    data['highscore'] = score if score > data['highscore'] else data[
        'highscore']
    mul = (LENGTH) // 3
    pygame.draw.rect(SCREEN, DARKBROWN, (mul - 140, 2, 105, 24))
    show("Score :" + str(score), Theme[7], mul - 140 + 5, 6, 16)
    pygame.draw.rect(SCREEN, DARKBROWN, (mul * 2 - 140, 2, 90, 24))
    show("Speed :" + str(rate if rate < 200 else 0), Theme[7],
         mul * 2 - 140 + 5, 6, 16)
    pygame.draw.rect(SCREEN, DARKBROWN, (mul * 3 - 145, 2, 140, 24))
    show("High Score :" + str(data['highscore']), Theme[7], mul * 3 - 145 + 5,
         6, 16)
    if popup:
        petyr+=1
        s = pygame.Surface((LENGTH, LENGTH))
        s.set_colorkey(GREY)
        s.set_alpha(200)
        SCREEN.blit(s, (0, 0))
        pygame.draw.rect(SCREEN, DARKBROWN,
                         (LENGTH // 2 - 180, LENGTH // 2 - 150, 360, 300), 0,
                         1)
        pygame.draw.rect(
            SCREEN, LIGHTBROWN,
            (LENGTH // 2 - 180 + 5, LENGTH // 2 - 150 + 5, 350, 290), 0, 1)
        show('Game Over', DARKBROWN, LENGTH // 2 - 120, LENGTH // 2 - 130, 40)
        show("Score :" + str(score), WHITE, LENGTH // 2 - 100,
             LENGTH // 2 - 80, 20)
        show("High Score :" + str(data['highscore']), WHITE, LENGTH // 2 - 100,
             LENGTH // 2 - 50, 20)
        show("Time :" + t, WHITE, LENGTH // 2 - 100, LENGTH // 2 - 20, 20)
        show("Coins :" + str(coins), WHITE, LENGTH // 2 - 100,
             LENGTH // 2 + 10, 20)

        if petyr==3:
            data['coin'] = f"{int(data['coin'])+coins}"
            if data['highscore'] == score:
                data['time'] = t
            with open('missions.dat', 'rb') as file:
                miss = pickle.load(file)
                for i, m in enumerate(miss['missions']):
                    if m[0] == 'points' and m[1] <= score:
                        with open('missions.dat', 'wb') as f:
                            miss['missions'][i][3] = True
                            pickle.dump(miss, f)
                    if m[0] in ('apple', 'up', 'down'):
                        for k in m_counter[m[0]]:
                            if m[3].split('/')[1] == k.split('/')[1]:
                                with open('missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = k
                                    pickle.dump(miss, f)

            if obj['mission'][0] == 'points':
                if score >= obj['mission'][1]:
                    obj['mission'][3] = True
            update_obj()
            update_data()
            bigGame = bigGameVar()
            if internet:
                try:
                    changeNameForLead = pushData(data['name'], score, t, bigGame)
                    if not changeNameForLead:
                        showHomeButton = True
                    else:
                        showHomeButton = False
                except:
                    print(
                        'Data not sent to servers due to an unexpected error')
                    saveGameDataForLater(data['name'], score, t)
                    showHomeButton = True
            else:
                print(
                    'Data not sent as there is no internet. The data is saved and will be sent when there is an internet connection and the game is opened.'
                )
                saveGameDataForLater(data['name'], score, t)
                showHomeButton = True
            sent=True
        
        if showHomeButton:
            if button('Home', LENGTH // 2 - 100, LENGTH // 2 + 40, 100,30,WHITE, x_offset=10,text_col=DARKBROWN,text_size=16,hover_col=GREY,hover_width=1):
                user = 'Home'
                selected_items = [False, False, False, False, False, False]
                SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH), pygame.RESIZABLE)
        
        if changeNameForLead:
            show(f"Unable to send data to cloud as a player", DARKBROWN, LENGTH // 2 - 160, LENGTH // 2 + 38, 17)
            show(f"already thrives on the leadername by the", DARKBROWN, LENGTH // 2 - 160, LENGTH // 2 + 56, 17)
            show(f"name of {data['name']}", DARKBROWN, LENGTH // 2 - 160, LENGTH // 2 + 74, 17)
            
            if button('Don\'t Send Data', LENGTH // 2 - 140, LENGTH // 2 + 100, 140, 25, WHITE, x_offset=10,text_col=DARKBROWN,text_size=15,hover_col=GREY,hover_width=1):
                showHomeButton = True
                changeNameForLead = False
            
            if button('Change Name', LENGTH // 2 + 10, LENGTH // 2 + 100, 130, 25, DARKBROWN, x_offset=10,text_col=WHITE,text_size=15,hover_col=GREY,hover_width=1):
                tempDataForLead['score'] = score
                tempDataForLead['time'] = t
                user = 'ChangeNameForLead'
        
        if not showHomeButton and not changeNameForLead:
            show(f"Analysing and Sending", DARKBROWN, LENGTH // 2 - 120, LENGTH // 2 + 56, 18)
            show(f"your data to cloud ....", DARKBROWN, LENGTH // 2 - 120, LENGTH // 2 + 78, 18)
              

    if Pop:
        Popup(PopT)


def leaderboard():
    global sortedData, user
    # fauna
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('LEADERBOARDS', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if len(sortedData) > 0:
        for i, dt in enumerate(sortedData):
            if i < 10:
                show(dt[0], BLACK, 30, 78 + i * 35, 30)
                show(str(dt[1]), BLACK, 305, 78 + i * 35, 30)
                show(str(dt[2]), BLACK, 420, 78 + i * 35, 30)
    else:
        show('Oops! No Data Available', WHITE, 50, 200, 30)
    if (button('R', LENGTH - 40, 10, 20, 20, BLACKBROWN, 4, 14, WHITE,
               LIGHTBROWN)):
        sortedData = pullingSortedData()
        print('Refresh clicked')
    user = 'Home' if button('Home',
                            LENGTH - 154,
                            5,
                            100,
                            30,
                            LIGHTBROWN,
                            x_offset=10,
                            text_col=DARKBROWN,
                            text_size=16,
                            hover_col=BLACKBROWN,
                            hover_width=1) else user


def missions():
    global user, obj
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('MISSIONS', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (20, 50, LENGTH - 40, 40), 0, 8)

    def miss_txt(m):
        txt = ''
        if m[0] == 'points':
            txt = f'Reach {m[1]} points.'
        elif m[0] == 'speed':
            txt = f'Reach {m[1]} speed.'
        elif m[0] == 'st':
            txt = f'Reach {m[1][0]} points under {m[1][1]} seconds.'
        elif m[0] == 'leaderboard':
            txt = 'Get on the leaderboards.'
        elif m[0] == 'rank':
            txt = 'Beat your curren Rank' if m[
                1] == 'prev' else f'Reach {m[1]} rank or below.'
        elif m[0] == 'up':
            txt = f'Collect {m[1]} green apples in total.'
        elif m[0] == 'down':
            txt = f'Collect {m[1]} ice apples in total.'
        elif m[0] == 'apple':
            txt = f'Collect {m[1]} normal apples in total.'
        return txt

    show("Today's Special Mission :", WHITE, 30, 54, 16)
    m = obj['mission']
    txt = miss_txt(m)
    show(txt, WHITE, 35, 74, 14)
    show('Rewards :', DARKBROWN, LENGTH - 150, 55, 13)
    if m[0] in ('up', 'down', 'apple'):
        show('Status : ' + m[3], DARKBROWN, LENGTH - 300, 55, 13)
    else:
        show('Status : ' + ('Completed' if m[3] else 'Pending'), DARKBROWN,
             LENGTH - 300, 55, 13)

    if ((m[3] == True) if str(type(m[3])) == "<class 'bool'>" else
        (m[3].split('/')[0] == m[3].split('/')[1])) and not m[4]:
        if button('Claim', LENGTH - 300, 70, 70, 17, DARKBROWN, 10, 13, WHITE,
                  DARKBROWN, 0):
            with open('missions.dat', 'rb') as file:
                miss = pickle.load(file)
                with open('missions.dat', 'wb') as f:
                    obj['mission'][4] = True
                    x = m[2][0].split('-')
                    miss['coins']["2x " +
                                  ('Coins ' if x[1] == 'C' else 'Points ') +
                                  x[0] + ' min'][0] = str(
                                      int(miss['coins']["2x " +
                                                        ('Coins ' if x[1] ==
                                                         'C' else 'Points ') +
                                                        x[0] + ' min'][0]) + 1)
                    pickle.dump(miss, f)
                    data['coin'] = str(int(data['coin']) + m[2][1])
                    update_data()
                    update_obj()
    if m[4]:
        show('Claimed', BLACK, LENGTH - 300, 75, 13)
    show(f'{m[2][1]} coins', DARKBROWN, LENGTH - 80, 55, 13)
    M = m[2][0].replace('-', ' min 2x ')
    M += 'oins' if M[-1] == 'C' else 'oints'
    show(f'{M} ', DARKBROWN, LENGTH - 150, 75, 13)

    pygame.draw.line(SCREEN, WHITE, (10, 100), (LENGTH - 20, 100), 3)
    with open('missions.dat', 'rb') as file:
        miss = pickle.load(file)
        for i, m in enumerate(miss['missions']):
            pygame.draw.rect(SCREEN, LIGHTBROWN,
                             (20, 110 + i * 50, LENGTH - 40, 40), 0, 8)
            show(f"Mission {i+1} :", BLACK, 30, 114 + i * 50, 16)
            txt = miss_txt(m)
            show(txt, WHITE, 35, 134 + i * 50, 14)
            show('Rewards :', DARKBROWN, LENGTH - 150, 115 + i * 50, 13)
            if m[0] in ('up', 'down', 'apple'):
                show('Status : ' + m[3], DARKBROWN, LENGTH - 300, 115 + i * 50,
                     13)
            else:
                show('Status : ' + ('Completed' if m[3] else 'Pending'),
                     DARKBROWN, LENGTH - 300, 115 + i * 50, 13)

            if ((m[3] == True) if str(type(m[3])) == "<class 'bool'>" else
                (m[3].split('/')[0] == m[3].split('/')[1])) and not m[4]:
                if button('Claim', LENGTH - 300, 130 + i * 50, 70, 17,
                          DARKBROWN, 10, 13, WHITE, DARKBROWN, 0):
                    with open('missions.dat', 'wb') as f:
                        miss['missions'][i][4] = True
                        x = m[2][0].split('-')
                        miss['coins'][
                            "2x " + ('Coins ' if x[1] == 'C' else 'Points ') +
                            x[0] + ' min'][0] = str(
                                int(miss['coins']["2x " + (
                                    'Coins ' if x[1] == 'C' else 'Points ') +
                                                  x[0] + ' min'][0]) + 1)
                        pickle.dump(miss, f)
                        data['coin'] = str(int(data['coin']) + m[2][1])
                        update_data()
            if m[4]:
                show('Claimed', BLACK, LENGTH - 300, 135 + i * 50, 13)
            show(f'{m[2][1]} coins', DARKBROWN, LENGTH - 80, 115 + i * 50, 13)
            M = m[2][0].replace('-', ' min 2x ')
            M += 'oins' if M[-1] == 'C' else 'oints'
            show(f'{M} ', DARKBROWN, LENGTH - 150, 135 + i * 50, 13)
    user = 'Home' if button('Home',
                            LENGTH - 154,
                            5,
                            100,
                            30,
                            LIGHTBROWN,
                            x_offset=10,
                            text_col=DARKBROWN,
                            text_size=16,
                            hover_col=BLACKBROWN,
                            hover_width=1) else user


opened = [True, False, False, False]

pop = False


def marketplace():
    global user, start, SCREEN, LENGTH, opened, pop, q, Pop,sensitivity
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('MARKET PLACE', WHITE, 10, 10, 20)
    mul = (LENGTH - 30) // 4
    pygame.draw.rect(SCREEN, DARKBROWN, (10, 50, mul - 10, 390))
    if button("Background",
              10,
              50,
              mul - 10,
              30, (LIGHTBROWN if opened[0] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [True, False, False, False]
    if button("Snake",
              10,
              80,
              mul - 10,
              30, (LIGHTBROWN if opened[1] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [False, True, False, False]
    if button("Powerups",
              10,
              110,
              mul - 10,
              30, (LIGHTBROWN if opened[2] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, True, False]
    if button("Offers",
              10,
              140,
              mul - 10,
              30, (LIGHTBROWN if opened[3] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, False, True]
    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))
    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)
        if opened[2]:
            for i, item in enumerate(list_items['Powerups'].items()):

                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i == 1:
                        show(str(item[1][1]), BLACK, 30 + (i + 1) * mul, 165,
                             18)
                        show(item[0], BLACK, 25 + (i + 1) * mul, 185, 11)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    else:
                        show(str(item[1][1]), BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 165, 18)
                        show(item[0], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 185, 12)
                        show(f'{item[1][0]} in stock', WHITE,
                             30 + (i + 1) * mul, 210, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop or not Pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                                sensitivity=time.time()
                                pop = True
                                q = i
                            s.set_alpha(60)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(str(item[1][1]), BLACK, 30 + (i - 2) * mul, 355, 18)
                    show(item[0], BLACK, 30 + (i - 2) * mul, 375, 12)
                    show(f'{item[1][0]} in stock', WHITE, 30 + (i - 2) * mul,
                         400, 10)
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop or not Pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                                sensitivity=time.time()
                                pop = True
                                q = i
                            s.set_alpha(60)
                    SCREEN.blit(s, (x, y))
            if pop:
                cont = Popup('Would you like to make this purchase',mode='yesno')
                if cont==True:
                    t = list_items['Powerups'][list(
                        list_items['Powerups'].keys())[q]]
                    data['coin'] = str(int(data['coin']) - int(t[1]))
                    if int(data['coin']) >= 0:
                        update_data()
                        with open('items.dat', 'wb') as f:
                            list_items['Powerups'][list(
                                list_items['Powerups'].keys())[q]] = (
                                    str(int(t[0]) + 1), t[1])
                            pickle.dump(list_items, f)
                    else:
                        data['coin'] = str(int(data['coin']) + int(t[1]))
                        Pop = True
                    pop = False
                if cont!=None:
                    pop=False
        elif opened[3]:
            for i, item in enumerate(list_items['Offers'].items()):
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i <= 1:
                        show('', BLACK, 30 + (i + 1) * mul, 165, 18)
                        show('', BLACK, 25 + (i + 1) * mul, 185, 14)
                    else:
                        show('40', BLACK, 30 + (i + 1) * mul, 165, 18)
                        show('2x Box', BLACK, 30 + (i + 1) * mul, 185, 14)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                            sensitivity=time.time()
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    k = sum([(40 if x == '5' else
                              (15 if x == '4' else
                               (12 if int(x) <= 1 else 8))) * int(y)
                             for x, y in item[1].items()])
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    if i == 5:
                        show('15', BLACK, 30 + (i - 2) * mul, 355, 18)
                        show('Lucky Box', BLACK, 30 + (i - 2) * mul, 375, 14)
                    else:
                        show(str(int(k * 0.8)), BLACK, 30 + (i - 2) * mul, 355,
                             18)
                        show(str(k), BLACK, 30 + (i - 2) * mul, 375, 14)
                        pygame.draw.line(SCREEN, BLACK,
                                         (60 + (i - 2) * mul, 382),
                                         (65 + (i - 2) * mul - 50, 382), 1)
                        show(item[0], BLACK, 30 + (i - 2) * mul, 400, 14)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                            sensitivity=time.time()
                            selected_items[i] = not selected_items[i]
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))
        else:
            for i, item in enumerate(list_items['Themes'].items()):
                Dic = list(item[1].keys())
                D = list(item[1].values())
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    show(('25' if opened[0] else '15'), BLACK,
                         30 + (i + 1) * mul, 165, 18)
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i + 1) * mul,
                         185, 14)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop or not Pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed(
                            )[0] and not D[0 if opened[0] else 1]:
                                pop = True
                                q = i
                            s.set_alpha(60)
                    if D[0 if opened[0] else 1]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(('25' if opened[0] else '15'), BLACK,
                         30 + (i - 2) * mul, 355, 18)
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i - 2) * mul,
                         375, 14)
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop or not Pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed(
                            )[0] and not D[0 if opened[0] else 1]:
                                pop = True
                                q = i
                            s.set_alpha(60)
                    if D[0 if opened[0] else 1]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))
            if pop:
                cont = Popup('Would you like to make this purchase',mode='yesno')
                if cont:
                    t = list_items['Themes'][list(
                        list_items['Themes'].keys())[q]]
                    data['coin'] = str(
                        int(data['coin']) - (25 if opened[0] else 15))
                    if int(data['coin']) >= 0:
                        update_data()
                        with open('items.dat', 'wb') as f:
                            t[list(t.keys())[0 if opened[0] else 1]] = True
                            list_items['Themes'][list(
                                list_items['Themes'].keys())[q]] = t
                            pickle.dump(list_items, f)
                    else:
                        Pop = True
                        data['coin'] = str(
                            int(data['coin']) + (25 if opened[0] else 15))
                    pop = False
                if cont!=None:
                    pop=False
    if Pop:
        Popup('Not enough coins')
        

    user = 'Home' if button('Home',
                            LENGTH - 154,
                            5,
                            100,
                            30,
                            LIGHTBROWN,
                            x_offset=10,
                            text_col=DARKBROWN,
                            text_size=16,
                            hover_col=BLACKBROWN,
                            hover_width=1) else user
    show(str(data['coin'])+' coin(s)', LIGHTBROWN, LENGTH -270, 10, 19)


def inventory():
    global user, start, SCREEN, LENGTH, opened, Pop,sensitivity
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('INVENTORY', WHITE, 10, 10, 20)
    mul = (LENGTH - 30) // 4
    pygame.draw.rect(SCREEN, DARKBROWN, (10, 50, mul - 10, 390))
    if button("Background",
              10,
              50,
              mul - 10,
              30, (LIGHTBROWN if opened[0] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [True, False, False, False]
    if button("Snake",
              10,
              80,
              mul - 10,
              30, (LIGHTBROWN if opened[1] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        opened = [False, True, False, False]
    if button("Powerups",
              10,
              110,
              mul - 10,
              30, (LIGHTBROWN if opened[2] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, True, False]
    if button("2x",
              10,
              140,
              mul - 10,
              30, (LIGHTBROWN if opened[3] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        opened = [False, False, False, True]
    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))

    with open('items.dat', 'rb') as file:
        list_items = pickle.load(file)
        if opened[2]:
            for i, item in enumerate(list_items['Powerups'].items()):

                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                    if i == 1:
                        show(item[0], BLACK, 25 + (i + 1) * mul, 200, 11)
                        show(f'{item[1][0] } left ', WHITE, 50 + (i + 1) * mul,
                             165, 24)
                    else:
                        show(item[0], BLACK,
                             (85 if
                              (i + 1) == 2 else 30) + (i + 1) * mul, 200, 12)
                        show(f'{item[1][0] } left', WHITE, 50 + (i + 1) * mul,
                             165, 24)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        s.set_alpha(60)
                    if selected_items[i]:
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(item[0], BLACK, 30 + (i - 2) * mul, 390, 12)
                    show(f'{item[1][0] } left', WHITE, 50 + (i - 2) * mul, 355,
                         24)
                    SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        s.set_alpha(60)
                    SCREEN.blit(s, (x, y))
  
        elif opened[3]:
            with open('missions.dat', 'rb') as file:
                list_items = pickle.load(file)
                for i, item in enumerate(list_items['coins'].items()):
                    if i <= 2:
                        global event_list
                        pos = pygame.mouse.get_pos()
                        x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                            160)
                        pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                        pygame.draw.rect(SCREEN, LIGHTBROWN,
                                        (x + 5, y + 5, width - 10, height - 10))
                        SCREEN.blit(def_powerup, (37 + (i + 1) * mul, 80))
                        if i == 1:
                            show(item[0], BLACK, 25 + (i + 1) * mul, 210, 12)
                            show(f'{item[1][0]} left', WHITE, 55 + (i + 1) * mul,
                                165, 20)
                        else:
                            show(item[0], BLACK,
                                (85 if
                                (i + 1) == 2 else 30) + (i + 1) * mul, 210, 12)
                            show(f'{item[1][0]} left', WHITE, 50 + (i + 1) * mul,
                                165, 20)
                        if item[1][1]:
                            t = float(f"{(time.time()-item[1][2]):.2f}")
                            T = float(item[0].split()[2]) * 60 - t
                            ss = '0' if int(T % 60) // 10 == 0 else ''
                            show(f"{int(T//60)}:{ss}{int(T%60)}", WHITE,
                                50 + (i + 1) * mul, 187, 20)
                            if t >= (float(item[0].split()[2]) * 60):
                                with open('missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][1] = False
                                    list_items['coins']['coins'] = False
                                    pickle.dump(list_items, f)
                        elif item[1][0] != '0' and not list_items['coins']['coins']:
                            if button('Activate', 35 + (i + 1) * mul, 187, 80, 22,
                                    DARKBROWN, 10, 13, WHITE, DARKBROWN, 0):
                                with open('missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][0] = str(
                                        int(item[1][0]) - 1)
                                    list_items['coins'][item[0]][1] = True
                                    list_items['coins'][item[0]][2] = time.time()
                                    list_items['coins']['coins'] = True
                                    pickle.dump(list_items, f)

                        s = pygame.Surface((width, height))
                        s.set_colorkey(GREY)
                        s.set_alpha(0)
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            s.set_alpha(60)
                        if selected_items[i]:
                            s.set_alpha(120)
                        if list_items['coins']['coins'] and not item[1][1]:
                            s.set_alpha(120)
                        SCREEN.blit(s, (x, y))

                    elif i <= 5:
                        x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                            160)
                        pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                        pygame.draw.rect(SCREEN, LIGHTBROWN,
                                        (x + 5, y + 5, width - 10, height - 10))
                        pos = pygame.mouse.get_pos()
                        show(item[0], BLACK, 30 + (i - 2) * mul, 400, 12)
                        show(f'{item[1][0]} left', WHITE, 55 + (i - 2) * mul, 355,
                            24)
                        SCREEN.blit(def_powerup, (37 + (i - 2) * mul, 270))
                        if item[1][1]:
                            t = float(f"{(time.time()-item[1][2]):.2f}")
                            T = float(item[0].split()[2]) * 60 - t
                            ss = '0' if int(T % 60) // 10 == 0 else ''
                            show(f"{int(T//60)}:{ss}{int(T%60)}", WHITE,
                                50 + (i - 2) * mul, 377, 20)
                            if t >= (float(item[0].split()[2]) * 60):
                                with open('missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][1] = False
                                    list_items['coins']['points'] = False
                                    pickle.dump(list_items, f)
                        elif item[1][0] != '0' and not list_items['coins'][
                                'points']:
                            if button('Activate', 35 + (i - 2) * mul, 377, 80, 22,
                                    DARKBROWN, 10, 13, WHITE, DARKBROWN, 0):
                                with open('missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][0] = str(
                                        int(item[1][0]) - 1)
                                    list_items['coins'][item[0]][1] = True
                                    list_items['coins'][item[0]][2] = time.time()
                                    list_items['coins']['points'] = True
                                    pickle.dump(list_items, f)
                        s = pygame.Surface((width, height))
                        s.set_colorkey(GREY)
                        s.set_alpha(0)
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            s.set_alpha(60)
                        if list_items['coins']['points'] and not item[1][1]:
                            s.set_alpha(120)

                        SCREEN.blit(s, (x, y))
          
        else:
            for i, item in enumerate(list_items['Themes'].items()):
                Dic = list(item[1].keys())
                D = list(item[1].values())
                if i <= 2:
                    global event_list
                    pos = pygame.mouse.get_pos()
                    x, y, width, height = (20 + (i + 1) * mul, 70, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i + 1) * mul,
                         170, 16)
                    show(
                        'Purchased' if D[0 if opened[0] else 1] else
                        'Not Purchased', WHITE, 32 + (i + 1) * mul, 215, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                            sensitivity=time.time()
                            if D[0 if opened[0] else 1]:
                                with open('items.dat', 'wb') as f:
                                    list_items['Offers']['pseudo'][
                                        'background'
                                        if opened[0] else 'snake'] = item[0]
                                    pickle.dump(list_items, f)
                            else:
                                Pop = True
                        s.set_alpha(60)
                    if item[0] == list_items['Offers']['pseudo'][
                            'background' if opened[0] else 'snake']:
                        show('In Use', BLACK, 40 + (i + 1) * mul, 190, 16)
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))

                elif i <= 5:
                    x, y, width, height = (20 + (i - 2) * mul, 260, mul - 20,
                                           160)
                    pygame.draw.rect(SCREEN, DARKBROWN, (x, y, width, height))
                    pygame.draw.rect(SCREEN, LIGHTBROWN,
                                     (x + 5, y + 5, width - 10, height - 10))
                    pos = pygame.mouse.get_pos()
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i - 2) * mul,
                         360, 16)
                    show(
                        'Purchased' if D[0 if opened[0] else 1] else
                        'Not Purchased', BLACK, 32 + (i - 2) * mul, 405, 10)
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0] and (time.time()-sensitivity)>0.1:
                            sensitivity=time.time()
                            if D[0 if opened[0] else 1]:
                                with open('items.dat', 'wb') as f:
                                    list_items['Offers']['pseudo'][
                                        'background'
                                        if opened[0] else 'snake'] = item[0]
                                    pickle.dump(list_items, f)
                            else:
                                Pop = True
                        s.set_alpha(60)
                    if item[0] == list_items['Offers']['pseudo'][
                            'background' if opened[0] else 'snake']:
                        show('In Use', BLACK, 40 + (i - 2) * mul, 380, 16)
                        s.set_alpha(120)
                    SCREEN.blit(s, (x, y))


     
    if Pop:
        Popup('Theme not purchased')
    user = 'Home' if button('Home',
                            LENGTH - 154,
                            5,
                            100,
                            30,
                            LIGHTBROWN,
                            x_offset=10,
                            text_col=DARKBROWN,
                            text_size=16,
                            hover_col=BLACKBROWN,
                            hover_width=1) else user


openedSettings = [True, False, False, False]

namepop = False
popinit = True
popupClose = False

def settings():
    global user, start, SCREEN, LENGTH, openedSettings, pop, q
    global data, namepop, popinit, fromsetting, popupClose, userSettings, sortedData, bigGame
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('SETTINGS', WHITE, 10, 10, 20)
    mul = (LENGTH - 30) // 4
    pygame.draw.rect(SCREEN, DARKBROWN, (10, 50, mul - 10, 390))
    if button("Basic",
              10,
              50,
              mul - 10,
              30, (LIGHTBROWN if openedSettings[0] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        openedSettings = [True, False, False, False]
    if button("Account",
              10,
              80,
              mul - 10,
              30, (LIGHTBROWN if openedSettings[1] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_width=0,
              hover_col=LIGHTBROWN):
        openedSettings = [False, True, False, False]
    if button("Themes",
              10,
              110,
              mul - 10,
              30, (LIGHTBROWN if openedSettings[2] else DARKBROWN),
              3,
              20,
              WHITE,
              hover_col=LIGHTBROWN,
              hover_width=0):
        openedSettings = [False, False, True, False]

    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))

    if openedSettings[0]:
        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 100), (LENGTH - 30, 100),
                         width=3)

        show('Music', DARKBROWN, mul + 35, 120, 21)
        if (button('', mul + 110, 122, 15, 15,
                   WHITE if userSettings['music'] == False else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['music'] == True else DARKBROWN)):
            userSettings['music'] = not userSettings['music']
            updateSettings(userSettings)
        show('Sounds', DARKBROWN, mul + 220, 120, 21)
        if (button('', mul + 310, 122, 15, 15,
                   WHITE if userSettings['sound'] == False else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['sound'] == True else DARKBROWN)):
            userSettings['sound'] = not userSettings['sound']
            updateSettings(userSettings)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 155), (LENGTH - 30, 155),
                         width=3)

        show('VOLUME: ', DARKBROWN, mul + 35, 175, 20)
        if (button('-', mul + 200, 170, 30, 25, DARKBROWN, 10, 17, WHITE,
                   BLACK)):
            userSettings['volume'] -= 5
            updateSettings(userSettings)
        pygame.draw.rect(SCREEN, WHITE, (mul + 235, 170, 40, 25))
        show(str(userSettings['volume']), DARKBROWN, mul + 240, 175, 19)
        if (button('+', mul + 280, 170, 30, 25, DARKBROWN, 10, 19, WHITE,
                   BLACK)):
            if userSettings['volume'] < 100:
                userSettings['volume'] += 5
                updateSettings(userSettings)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 210), (LENGTH - 30, 210),
                         width=3)

        show('PREFERRED CONTROLS: ', DARKBROWN, mul + 35, 230, 20)
        show('Arrow Keys ', BLACK, mul + 55, 270, 21)
        if (button('', mul + 100, 300, 20, 20,
                   WHITE if userSettings['arrow'] == False else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['arrow'] == True else DARKBROWN)):
            userSettings['arrow'] = not userSettings['arrow']
            updateSettings(userSettings)
        show('AWSD Keys ', BLACK, mul + 225, 270, 21)
        if (button('', mul + 270, 300, 20, 20,
                   WHITE if userSettings['arrow'] == True else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['arrow'] == False else DARKBROWN)):
            userSettings['arrow'] = not userSettings['arrow']
            updateSettings(userSettings)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 335), (LENGTH - 30, 335),
                         width=3)
        
    elif openedSettings[1]:
        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 100), (LENGTH - 30, 100),
                         width=3)

        show('currently playing as: ', DARKBROWN, mul + 30, 125, 19)
        show(data['name'].upper(), BLACK, mul + 40, 157, 30)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 210), (LENGTH - 30, 210),
                         width=3)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 280), (LENGTH - 30, 280),
                         width=3)
        if not namepop:
            if (button('Change Name', mul + 250, 155, 145, 30, WHITE, 15, 17,
                       DARKBROWN, GREY)):
                namepop = True
            if (button('Sign Up as a New User', mul + 45, 230, 210, 30, WHITE,
                       15, 17, DARKBROWN, GREY)):
                newUser_init()
                user = 'NewUser'
                fromsetting = True
            show('Please note that your name on the leaderboard' , DARKBROWN, mul + 25, 310, 16)
            show('won\'t be updated when you change name, and' , DARKBROWN, mul + 25, 330, 16)
            show('you\'ll be treated as a new user altogether.', DARKBROWN, mul + 25, 350, 16)
            show('Your coins, items and completed missions will' , DARKBROWN, mul + 25, 370, 16)
            show('still be yours.' , DARKBROWN, mul + 25, 390, 16)
    elif openedSettings[2]:
        pass

    user = 'Home' if button('Home',
                            LENGTH - 154,
                            5,
                            100,
                            30,
                            LIGHTBROWN,
                            x_offset=10,
                            text_col=DARKBROWN,
                            text_size=16,
                            hover_col=BLACKBROWN,
                            hover_width=1) else user

    if namepop:
        if popinit:
            newUser_init()
            popinit = False
        fromsetting = True
        newuser(changename = True)
        


errormsg = False
errorstart = 0


def newuser(changename=False):
    LENGTH = pygame.display.get_surface().get_width()
    global user, Text_Val, iterrr, Cursor, data, fromsetting, namepop, Pop, Popup, popinit, errormsg, errorstart, sortedData, bigGame
    if not changename:
        SCREEN.fill(BLACKBROWN)
        pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
        show('SIGN UP', WHITE, 10, 10, 20)
        pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if changename:
        s = pygame.Surface((LENGTH * 2, LENGTH * 2))
        s.set_colorkey(GREY)
        s.set_alpha(200)
        SCREEN.blit(s, (0, 0))
        pygame.draw.rect(SCREEN, LIGHTBROWN, (27, 125, LENGTH - 54, 200))
    if len(Text_Val) == 0:
        show("Type your name here.", WHITE, (LENGTH - 200) // 2, 220, 20)
    else:
        show(Text_Val, WHITE, (LENGTH - len(Text_Val) * 10) // 2, 220, 20)
        if iterrr % 8 == 0:
            Text_Val = Text_Val[:-1] + '|'
            Cursor = True
        if iterrr % 8 == 4 and Cursor:
            Text_Val = Text_Val[:-1] + ' '
            Cursor = False
        iterrr += 1
    if not fromsetting:
        if button('Home', LENGTH - 154, 5, 100, 30, LIGHTBROWN, x_offset=10, text_col=DARKBROWN, text_size=16, hover_col=BLACKBROWN, hover_width=1):
            user = 'Home'
            Text_Val = ''
    else:
        if button('Settings', LENGTH - 154, 5, 100, 30, LIGHTBROWN, x_offset=10, text_col=DARKBROWN, text_size=16, hover_col=BLACKBROWN, hover_width=1):
            user = 'Settings'
            fromsetting = False
            namepop = False
            Text_Val = ''

    #
    # if iterrr>10:
    #     Text_Val+='|'
    # else:
    #     Text_Val=Text_Val[:-1]
    # iterrr+=1
    # iterrr=0 if iterrr>20 else iterrr
    pygame.draw.line(SCREEN, DARKBROWN, (50, 250), (LENGTH - 50, 250), 1)
    Text_Ent = button('Change Name' if changename else 'Create Account',
                      (LENGTH - 155) // 2,
                      280,
                      140,
                      40,
                      bg_color=DARKBROWN,
                      text_col=WHITE,
                      text_size=14,
                      hover_width=0)
    if not Pop:
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.unicode in ALPHA:
                    Text_Val = Text_Val[:-1] + str(
                        event.unicode) + ('|' if Cursor else ' ')
                elif event.key == pygame.K_BACKSPACE:
                    Text_Val = Text_Val[:-2] + ('|' if Cursor else ' ')
                elif event.unicode == '\r':
                    Text_Ent = True
                elif not event.unicode in ALPHA:
                    errormsg = True
                    errorstart = time.time()
    if 3 < len(Text_Val) <= 11:
        allowed_name = True
    else:
        allowed_name = False
    if Text_Ent:
        if allowed_name:
            if not changename:
                bigGame = False
                print('The condition is to sign up as a new user')
                data = {
                    'name': Text_Val[:-1],
                    'highscore': 0,
                    'coin': '0',
                    'time': ''
                }
                # bigGame = False
                with open('missions.dat','rb') as f:
                    miss=pickle.load(f)
                    for i,j in enumerate(miss['missions']):
                        if j[0] in ('apple','up','down'):
                            miss['missions'][i][3]='0'+'/'+j[3].split('/')[1]
                        else:
                            miss['missions'][i][3]=False
                        miss['missions'][i][4]=False
                    for i in list(miss['coins'].keys()):
                        if i in('coins','points'):
                            miss['coins'][i]=False
                        else:
                            miss['coins'][i]=['10',False,0]
                with open('missions.dat','wb') as f:
                    pickle.dump(miss,f)
                with open('items.dat','rb') as f:
                    item_list=pickle.load(f)
                    for i in list(item_list['Themes'].keys()):
                        if i==0:
                            continue
                        for a in list(item_list['Themes'][i].keys()):
                            item_list['Themes'][i][a]=False
                    for i in list(item_list['Powerups'].keys()):
                        item_list['Powerups'][i]=('0',item_list['Powerups'][i][1])
                    item_list['Offers']['pseudo']={'background': 'Theme1', 'snake': 'Theme1'}
                        
                with open('items.dat','wb') as f:
                    pickle.dump(item_list,f)
                
                print('Signed up as new user')               

            if changename:
                print('The condition is to change name')
                bigGame = bigGameVar()
                if bigGame:
                    print('Player is on the leaderboard')
                    try:
                        for i in sortedData:
                            if i[0] == data['name']:
                                dataDict = {
                                    'name': Text_Val[:-1],
                                    'score': i[1],
                                    'time': i[2],
                                }
                                deleteDoc(collection='testcollection', refid=i[4])
                                pushDictData('testcollection', dataDict)
                                print(f"Your Name on Leaderboard updated successfully!! {data['name']} changed to {Text_Val[:-1]}")
                    except:
                        print('Your name on the leaderboard could not be updated due to an unexpedted error')
                else:
                    print('Player doesn\'t exist on the leaderboard')
                data['name'] = Text_Val[:-1]            
            update_data()
            writeBigGame(data['name'], bigGame)
            if changename:
                namepop = False
                fromsetting = False
                popinit = True
            if fromsetting:
                user = 'Settings'
            else:
                user = 'Home'                
            Text_Val = ''            
        else:
            Pop = True
    if errormsg:
        show("*Only Uppercase/Lowercase letters, numbers and '_' is allowed",
             RED, (LENGTH - 310) // 2, 260, 12)
        if time.time() - errorstart > 4:
            errormsg = False
    if Pop:
        Popup("Username must be between 3 to 10 letters.")


def changeNameForLeadFunc():
    LENGTH = pygame.display.get_surface().get_width()
    global user, Text_Val, iterrr, Cursor, data, fromsetting, namepop, Pop, Popup, popinit, errormsg, errorstart, sortedData, bigGame, tempDataForLead
    Text_Val = ''
    show(f"Score: {tempDataForLead['score']}, Time Played: {tempDataForLead['time']}", DARKBROWN, 30, 80, 18)
    
    if button('Don\'t Send',
                      (LENGTH - 155) // 2,
                      280,
                      140,
                      40,
                      bg_color=DARKBROWN,
                      text_col=WHITE,
                      text_size=14,
                      hover_width=0):
        user = 'Home'
    
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('CHANGE NAME', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    
    if len(Text_Val) == 0:
        show("Type your name here.", WHITE, (LENGTH - 200) // 2, 220, 20)
    else:
        show(Text_Val, WHITE, (LENGTH - len(Text_Val) * 10) // 2, 220, 20)
        if iterrr % 8 == 0:
            Text_Val = Text_Val[:-1] + '|'
            Cursor = True
        if iterrr % 8 == 4 and Cursor:
            Text_Val = Text_Val[:-1] + ' '
            Cursor = False
        iterrr += 1

    pygame.draw.line(SCREEN, DARKBROWN, (50, 250), (LENGTH - 50, 250), 1)
       

    Text_Ent = button('Change Name',
                      (LENGTH - 20) // 2,
                      280,
                      140,
                      40,
                      bg_color=DARKBROWN,
                      text_col=WHITE,
                      text_size=14,
                      hover_width=0)

    if not Pop:
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.unicode in ALPHA:
                    Text_Val = Text_Val[:-1] + str(
                        event.unicode) + ('|' if Cursor else ' ')
                elif event.key == pygame.K_BACKSPACE:
                    Text_Val = Text_Val[:-2] + ('|' if Cursor else ' ')
                elif event.unicode == '\r':
                    Text_Ent = True
                elif not event.unicode in ALPHA:
                    errormsg = True
                    errorstart = time.time()
    if 3 < len(Text_Val) <= 11:
        allowed_name = True
    else:
        allowed_name = False
    if Text_Ent:
        if allowed_name:
            if not changename:
                bigGame = False
                print('The condition is to sign up as a new user')
                data = {
                    'name': Text_Val[:-1],
                    'highscore': 0,
                    'coin': '0',
                    'time': ''
                }
                # bigGame = False
                with open('missions.dat','rb') as f:
                    miss=pickle.load(f)
                    for i,j in enumerate(miss['missions']):
                        if j[0] in ('apple','up','down'):
                            miss['missions'][i][3]='0'+'/'+j[3].split('/')[1]
                        else:
                            miss['missions'][i][3]=False
                        miss['missions'][i][4]=False
                    for i in list(miss['coins'].keys()):
                        if i in('coins','points'):
                            miss['coins'][i]=False
                        else:
                            miss['coins'][i]=['10',False,0]
                with open('missions.dat','wb') as f:
                    pickle.dump(miss,f)
                with open('items.dat','rb') as f:
                    item_list=pickle.load(f)
                    for i in list(item_list['Themes'].keys()):
                        if i==0:
                            continue
                        for a in list(item_list['Themes'][i].keys()):
                            item_list['Themes'][i][a]=False
                    for i in list(item_list['Powerups'].keys()):
                        item_list['Powerups'][i]=('0',item_list['Powerups'][i][1])
                    item_list['Offers']['pseudo']={'background': 'Theme1', 'snake': 'Theme1'}
                        
                with open('items.dat','wb') as f:
                    pickle.dump(item_list,f)
                
                print('Signed up as new user')               

            if changename:
                print('The condition is to change name')
                bigGame = bigGameVar()
                if bigGame:
                    print('Player is on the leaderboard')
                    try:
                        for i in sortedData:
                            if i[0] == data['name']:
                                dataDict = {
                                    'name': Text_Val[:-1],
                                    'score': i[1],
                                    'time': i[2],
                                }
                                deleteDoc(collection='testcollection', refid=i[4])
                                pushDictData('testcollection', dataDict)
                                print(f"Your Name on Leaderboard updated successfully!! {data['name']} changed to {Text_Val[:-1]}")
                    except:
                        print('Your name on the leaderboard could not be updated due to an unexpedted error')
                else:
                    print('Player doesn\'t exist on the leaderboard')
                data['name'] = Text_Val[:-1]            
            update_data()
            writeBigGame(data['name'], bigGame)
            if changename:
                namepop = False
                fromsetting = False
                popinit = True
            if fromsetting:
                user = 'Settings'
            else:
                user = 'Home'                
            Text_Val = ''            
        else:
            Pop = True
    if errormsg:
        show("*Only Uppercase/Lowercase letters, numbers and '_' is allowed",
             RED, (LENGTH - 310) // 2, 260, 12)
        if time.time() - errorstart > 4:
            errormsg = False
    if Pop:
        Popup("Username must be between 3 to 10 letters.")


def cheater():
    LENGTH = pygame.display.get_surface().get_width()
    # fauna
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 90))
    show('CHEATER CHEATER,', WHITE, 10, 16, 30)
    show('COMPULSIVE EATER', WHITE, 10, 51, 30)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 100, LENGTH - 20, 345))
    SCREEN.blit(cheaterImage, (30, 135))
    show('YOU CAN\'T CHEAT YOUR WAY TO THE TOP', RED, 30, 380, 23)

    with open('userData.dat', 'wb') as file:
        pickle.dump({
            'name': '',
            'highscore': 0,
            'coin': '0',
            'time': ''
        }, file)



def cheaterlist():
    global user
    listOfCheaters = cheaterlistData()
    # fauna
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('Cheaters\' List', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if len(listOfCheaters) > 0:
        for i, dt in enumerate(listOfCheaters):
            if i < 10:
                show(dt, BLACK, 40, 78 + i * 35, 30)
    else:
        show('Oops! No Data Available', WHITE, 50, 200, 30)
    if (button('R', LENGTH - 40, 10, 20, 20, BLACKBROWN, 4, 14, WHITE,
               LIGHTBROWN)):
        listOfCheaters = pullingSortedData()
        print('Refresh clicked')
    user = 'Home' if button('Home',
                            LENGTH - 154,
                            5,
                            100,
                            30,
                            LIGHTBROWN,
                            x_offset=10,
                            text_col=DARKBROWN,
                            text_size=16,
                            hover_col=BLACKBROWN,
                            hover_width=1) else user


def Popup(txt,mode='ok'):
    global Pop
    s = pygame.Surface((LENGTH * 2, LENGTH * 2))
    s.set_colorkey(GREY)
    s.set_alpha(200)
    SCREEN.blit(s, (0, 0))
    pygame.draw.rect(SCREEN, LIGHTBROWN, (50, 150, 450, 200), 0, 1)
    show(txt, DARKBROWN, 70, 170, 20)
    if mode=='ok':
        if button('Ok',
                350,
                300,
                100,
                30,
                DARKBROWN,
                text_col=WHITE,
                hover_col=DARKBROWN):
            Pop = False
    elif mode=='yesno':
        if button('Yes',
                350,
                300,
                100,
                30,
                DARKBROWN,
                text_col=WHITE,
                hover_col=DARKBROWN):
            Popyn = False
            return True
        if button('No',
                70,
                300,
                100,
                30,
                DARKBROWN,
                text_col=WHITE,
                hover_col=DARKBROWN):
            Popyn = False
            return False


def main():
    global event_list, Text_Val
    SCREEN.fill(BLACK)
    home_params()
    while True:
        event_list = pygame.event.get()
        if user == 'Home':
            home()
        elif user == 'Emulator':
            emulator()
        elif user == 'LeaderBoard':
            leaderboard()
        elif user == 'Settings':
            settings()
        elif user == 'NewUser':
            newuser()
        elif user == 'ChangeNameForLead':
            changeNameForLeadFunc()
        elif user == 'Cheater':
            cheater()
        elif user == 'Arsenal':
            arsenal()
        elif user == 'MarketPlace':
            marketplace()
        elif user == 'Inventory':
            inventory()
        elif user == 'Missions':
            missions()
        elif user == 'Cheaterlist':
            cheaterlist()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        CLOCK.tick(rate)
        if breaker:
            break


main()

if breaker:
    with open('Builder.py', 'r') as f:
        file = f.read()
        exec(file)