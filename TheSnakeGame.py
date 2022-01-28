try:
    import pygame
    import sys
    import time
    import random
    import pickle
    import os
    import operator
    from faunadb import query as q
    from faunadb.client import FaunaClient
    import re
    import urllib.request
except:
    import subprocess
    subprocess.run(r'data\Installer.bat')
    import pygame
    import sys
    import time
    import random
    import pickle
    import os
    import operator
    from faunadb import query as q
    from faunadb.client import FaunaClient
    import re
    import urllib.request
# global
pygame.init()

def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        # print('Internet is on')
        return True
    except:
        return False


internet = connect()

if internet:
    client = FaunaClient(
        secret = "fnAEd7T4kkAASRXchQUxZbvl68JiGY1-lXFL6WuT",
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

    result = re.findall('\d+', str([indexes['data']
                                    ]))  # to find all the numbers in the list

    dataDict = {}

    details = client.query(
        q.get(q.ref(q.collection("dailymissions"), result[0])))['data']

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
    elif os.path.exists(r"data\bin\bigGame.dat"):
        with open(r'data\bin\bigGame.dat', 'rb') as file:
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
    with open(r'data\bin\bigGame.dat', 'wb') as file:
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

    returnDict = {
        'sent': False,
        'updated': False,
        'notUpdated': False,
        'thrives': False,
        'notSent': False
    }

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
                        returnDict['updated'] = True
                        return returnDict
                    elif score == i[1]:
                        if time < i[2]:
                            deleteDoc(collection='testcollection', refid=i[4])
                            pushDictData(collection='testcollection',
                                         data=dataDict)
                            print(
                                "Your data on Leaderboard updated successfully!"
                            )
                            writeBigGame(data['name'], True)
                            returnDict['updated'] = True
                            return returnDict
                    else:
                        returnDict['notUpdated'] = True
                        return returnDict
        else:
            if name in lnames:
                print(
                    'A player already thrives on the leaderboard with this name. Kindly follow the promts to change name or to not send the data to servers.'
                )
                returnDict['thrives'] = True
                return returnDict
            else:
                pushDictData(collection='testcollection', data=dataDict)
                print("Data sent successfully!")
                writeBigGame(data['name'], True)
                returnDict['sent'] = True
                return returnDict
    else:
        if (bigGameP):
            for i in sortedData1:
                if name == i[0]:
                    returnDict['notUpdated'] = True
                    return returnDict
        else:
            print("Data not sent to the servers since conditions are not met")
            returnDict['notSent'] = True
            return returnDict


# pulling data
def pullingSortedData():
    try:
        data = sortedLeaderboardList(index='testindex',
                                     collection='testcollection')
        file = open(r"data\bin\sortedData.dat", "wb")
        pickle.dump(data, file)
        file.close()
        print('data pulled')
        return data
    except:
        try:
            file = open(r"data\bin\sortedData.dat", "rb")
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
        fileR = open(r'data\bin\savedData.dat', "rb")
        data = pickle.load(fileR)
        if data['score'] < score:
            fileW = open(r'data\bin\savedData.dat', 'wb')
            pickle.dump(data, fileW)
        elif data['score'] == score:
            if data['time'] > time:
                fileW = open(r'data\bin\savedData.dat', 'wb')
                pickle.dump(data, fileW)
        fileR.close()
    except:
        file = open(r'data\bin\savedData.dat', 'wb')
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
        file = open(r"data\bin\cheaterlist.dat", "wb")
        pickle.dump(data, file)
        file.close()
        print('data pulled')
        return data
    except:
        try:
            file = open(r"data\bin\cheaterlist.dat", "rb")
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
    with open(r'data\bin\daily.dat', 'wb') as file:
        pickle.dump(obj, file)


sortedData = pullingSortedData()
# print(sortedData)
maintain10onleaderboard()
savedDataNameThrives = False
tempDataForLead = {
        'score':0,
        'time':0
    }

s = time.time()
day = int(((s + 19800) / 3600) // 24)
with open(r'data\bin\daily.dat', 'rb') as file:
    dail = pickle.load(file)
    if dail['day'] < day:
        obj = pullOBJ()
        update_obj()

savedDataDict = {'score':0, 'time':0}

if internet and os.path.exists(r"data\bin\savedData.dat"):
    try:
        fileR = open(r'data\bin\savedData.dat', "rb")
        data = pickle.load(fileR)
        bigGame = bigGameVar()
        savedDataReturns = pushData(name=data['name'],
                 score=data['score'],
                 time=data['time'],
                 bigGameP=bigGame)
        print(savedDataReturns)
        fileR.close()
        if savedDataReturns['thrives']:
            savedDataNameThrives = True
            savedDataDict['score'] = data['score']
            savedDataDict['time'] = data['time']
        os.remove(r"data\bin\savedData.dat")
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
        with open(r'data\bin\userSettings.dat', 'rb') as file:
            setData = pickle.load(file)
        return setData
    except:
        setData = {
            'volume': 80,
            'music': True,
            'sound': True,
            'arrow': True,
            'fauna': True,
            'darkTheme': False,
        }
        with open(r'data\bin\userSettings.dat', 'wb') as file:
            pickle.dump(setData, file)
        return setData


def updateSettings(setData):
    with open(r'data\bin\userSettings.dat', 'wb') as file:
        pickle.dump(setData, file)
    # print('Settings Updated')



#constants
LENGTH = 454
PIXEL = 15
SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH), pygame.RESIZABLE)

CLOCK = pygame.time.Clock()
coin_2, point_2 = False, False
sensitivity = 0
#colours
#Theme
WHITE = pygame.Color('#FFFFFF')
BLACK = pygame.Color('#181818')

# Apples and Bomb
RED = pygame.Color('#FF4000')  # Apple
BLUE = pygame.Color('#40FFC0')  # Down
GREEN = pygame.Color('#00C000')  # Up
GREY = pygame.Color('#606060')  # Bomb

# Snake
ORANGE = pygame.Color('#FF8000')
CADET = pygame.Color('#5f9ea0')
GOLD = pygame.Color('#FFC000')
PINK = pygame.Color('#ee70d3')
DARKRED = pygame.Color('#811a13')

# Background
LIGHTBLACK = pygame.Color('#282828')
DARKCYAN = pygame.Color('#2f4f4f')
GRAY = pygame.Color('#454545')
DARKGREEN = pygame.Color('#556b2f')
DARKBLUE = pygame.Color('#6b5fb4')

DARKYELLOW = pygame.Color('#b8860b')
COL1 = pygame.Color('#ce71f3')
COL2 = pygame.Color('#f7c05a')

VOILET = pygame.Color('#400080')

def lightTheme():
    global LIGHTBROWN, DARKBROWN, BLACKBROWN
    LIGHTBROWN = pygame.Color('#AD9157')
    DARKBROWN = pygame.Color('#4F3119')
    BLACKBROWN = pygame.Color('#11110F')

def darkTheme():
    global LIGHTBROWN, DARKBROWN, BLACKBROWN
    LIGHTBROWN = pygame.Color('#AD9157')
    BLACKBROWN = pygame.Color('#4F3119')
    DARKBROWN = pygame.Color('#11110F')  

userSettings = readSettings()

def updateTheme():
    global userSettings
    if userSettings['darkTheme']:
        darkTheme()
    else:
        lightTheme()

updateTheme()

def loader(s):
    return pygame.transform.scale(
    pygame.image.load('data\\images\\powerups\\'+s+'.png').convert_alpha(),
    (70, int(70 * 322 / 301)))

powerup_img = ['down','up','high','low','bomb','teleport','2xp','2xc']
for i,j in enumerate(powerup_img):
    powerup_img[i]=loader(j)
cheaterImage = pygame.image.load(r'data\images\cheater.png').convert()
deltaH = pygame.image.load(r'data\images\delta-h.PNG').convert()
sideSnake = pygame.image.load(r'data\images\side-snake.png').convert_alpha()
frontSnake = pygame.image.load(r'data\images\front-snake.png').convert_alpha()


A = "".join([chr(x) for x in range(65, 91)])
ALPHA = A + A.lower() + '_' + ''.join([str(x) for x in range(10)])
bgMusic = pygame.mixer.music.load(r'data\audios\bgmusic.mp3')
speedupMusic = pygame.mixer.Sound(r'data\audios\speedup.wav')
buttonSound = pygame.mixer.Sound(r'data\audios\button.wav')
appleMusic = pygame.mixer.Sound(r'data\audios\apple.wav')
bombMusic = pygame.mixer.Sound(r'data\audios\bomb.wav')
speeddownMusic = pygame.mixer.Sound(r'data\audios\speeddown.wav')
gameOverSound = pygame.mixer.Sound(r'data\audios\gameOver.wav')

#user data
def newUser_init():
    global Cursor, Text_Val, iterrr
    iterrr = 0
    Cursor = False
    Text_Val = ''


fromsetting = False
try:
    file = open(r'data\bin\userData.dat', 'rb')
    data = pickle.load(file)
    non_cheater = True
except pickle.UnpicklingError:
    user = 'Cheater'
    non_cheater = False
    try:
        with open(r'data\bin\bigGame.dat', 'rb') as file:
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
        user = 'DeltaH'
    file.close()


def show(msg, color, x, y, size, mode='n'):
    f = r'data\font\design.graffiti.comicsansmsgras.ttf' if mode == 'b' else (
        r'data\font\comici.ttf' if mode == 'i' else
        (r'data\font\comicz.ttf' if mode == 'ib' else r'data\font\COMIC.ttf'))
    score_show = pygame.font.Font(f, size).render(msg, True, color)
    SCREEN.blit(score_show, (x, y))


selected_items = [False, False, False, False, False, False]
fromLB = False
Pop = False
I = 0
iterr = 0


def update_data():
    with open(r'data\bin\userData.dat', 'wb') as file:
        pickle.dump(data, file)


def daily():
    global obj, petyr
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
    with open(r'data\bin\daily.dat', 'rb') as file:
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
            petyr = 0
        else:
            obj = dail
            petyr = 4


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
           hover_width=2,
           mode='n'):
    global buttonSound, sensitivity
    pos = pygame.mouse.get_pos()
    if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
            1] <= y + height:
        pygame.draw.rect(SCREEN, hover_col,
                         (x - hover_width, y - hover_width,
                          width + hover_width * 2, height + hover_width * 2))
        if pygame.mouse.get_pressed()[0] and (time.time() - sensitivity) > 0.1:
            sensitivity = time.time()
            if userSettings['sound']:
                buttonSound.play(loops=0)
            return True
    pygame.draw.rect(SCREEN, bg_color, (x, y, width, height))
    show(text, text_col, x + x_offset,
         (y + abs(height - text_size) // 2-int(text_size/5)),
         text_size, mode)


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


breaker = False
petyr = 0

rate = 40
w = 0
h = 0


breaker = False
changeNamePop = False
    
def home():
    global i, decreaser, done, user, start, breaker, frontSnake, savedDataNameThrives, Pop, changeNamePop
def circ(x1, x2, i, n, m, c):
    x = x1 - (x1 - x2) * i / n
    pygame.draw.circle(SCREEN, WHITE, (x, m * x + c), 4)


def delta_h():
    global petyr, user, rate
    SCREEN.fill((0, 0, 0))
    LENGTH = pygame.display.get_surface().get_width()
    HEIGHT = pygame.display.get_surface().get_height()
    m1 = (160 - 252) / (238 - 197)
    m2 = (252 - 240) / (197 - 274)
    m3 = (240 - 192) / (274 - 248)
    m4 = (192 - 287) / (248 - 205)
    c1 = 160 - m1 * 238
    c2 = 252 - m2 * 197
    c3 = 240 - m3 * 274
    c4 = 192 - m4 * 248
    deltaHSize = deltaH.get_size()
    if petyr < 230:

        if petyr < 30:
            for i in range(4):
                circ(358 + i, 197 + i, petyr, 30, m1, c1)
        if 30 < petyr < 45:
            for i in range(4):
                circ(197 + i, 274 + i, (petyr - 30), 15, m2, c2)
        if 45 < petyr < 60:
            for i in range(4):
                circ(274 + i, 248 + i, (petyr - 45), 15, m3, c3)
        if 60 <= petyr < 90:
            for i in range(4):
                circ(248 + i, 120 + i, (petyr - 60), 15, m4, c4)
        if petyr > 15:
            deltaH.set_alpha(255 * ((petyr - 20) if petyr <= 140 else 120) /
                             120)
            if petyr > 140:
                deltaH.set_alpha(195 + (abs(petyr - 200)))
            SCREEN.blit(deltaH, ((LENGTH - deltaHSize[0]) // 2,
                                 (HEIGHT - deltaHSize[1]) // 2 - 15))
    petyr += 1
    if petyr >= 230:
        global frontSnake, flippedScaledSideSnake, scaledFrontSnake, frontSnakeSize, scaledSideSnake, sideSnakeSize, w, h
        LENGTH = pygame.display.get_surface().get_width()
        HEIGHT = pygame.display.get_surface().get_height()
        SCREEN.fill(BLACKBROWN)
        pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
        pygame.draw.rect(SCREEN, LIGHTBROWN,
                         (10, 50, LENGTH - 20, HEIGHT - 60))
        usualWidth, margin = 120, 65
        if petyr < 270:
            scaledFrontSnake = pygame.transform.scale(
                frontSnake, (int(250 * HEIGHT / 400), int(250 * HEIGHT / 400)))
            frontSnakeSize = scaledFrontSnake.get_size()
            scaledFrontSnake.set_alpha(
                255 * ((petyr - 230) if petyr <= 270 else 40) / 40)
        SCREEN.blit(scaledFrontSnake,
                    ((LENGTH - frontSnakeSize[0]) / 2, 30 +
                     (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2))
        if petyr <= 300:
            scaledSideSnake = pygame.transform.scale(
                sideSnake, (int(250 * HEIGHT / 454), int(250 * HEIGHT / 454)))
            sideSnakeSize = scaledSideSnake.get_size()
            scaledSideSnake.set_alpha(
                55 * ((petyr - 270) if petyr <= 300 else 30) / 30)

            flippedScaledSideSnake = pygame.transform.flip(
                scaledSideSnake, True, False)
            flippedScaledSideSnake.set_alpha(
                55 * ((petyr - 270) if petyr <= 300 else 30) / 30)
            SCREEN.blit(
                scaledSideSnake,
                ((LENGTH - sideSnakeSize[0]) / 2 +
                 (margin + (usualWidth * LENGTH / 554 - sideSnakeSize[0]) / 2 -
                  (LENGTH - sideSnakeSize[0]) / 2) * (petyr - 270) / 30, 40 +
                 (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2 +
                 frontSnakeSize[1] / 4))
            SCREEN.blit(
                flippedScaledSideSnake,
                ((LENGTH - sideSnakeSize[0]) / 2 +
                 (margin + 45 +
                  (usualWidth * LENGTH / 554) / 2 + sideSnakeSize[0] / 2 -
                  (LENGTH - sideSnakeSize[0]) / 2) * (petyr - 270) / 30, 40 +
                 (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2 +
                 frontSnakeSize[1] / 4))
        if petyr > 300:
            SCREEN.blit(
                scaledSideSnake,
                (margin + (usualWidth * LENGTH / 554 - sideSnakeSize[0]) / 2,
                 40 + (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2 +
                 frontSnakeSize[1] / 4))
            SCREEN.blit(
                flippedScaledSideSnake,
                (LENGTH -
                 (margin +
                  (usualWidth * LENGTH / 554) / 2 + sideSnakeSize[0] / 2 + 15),
                 40 + (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2 +
                 frontSnakeSize[1] / 4))
        if petyr > 330:
            for j in range(3):
                pygame.draw.rect(
                    SCREEN, DARKBROWN,
                    ((-40 + (petyr - 330) if petyr < 370 else 0) + margin,
                     (300 + 40 * j) * HEIGHT / 454, usualWidth * LENGTH / 554,
                     30 * HEIGHT / 454))
                pygame.draw.rect(
                    SCREEN, DARKBROWN,
                    ((40 - (petyr - 330) if petyr < 370 else 0) + LENGTH -
                     (margin + usualWidth * LENGTH / 554),
                     (300 + 40 * j) * HEIGHT / 454, usualWidth * LENGTH / 554,
                     30 * HEIGHT / 454))
            s = pygame.Surface((170 * LENGTH / 554, 55 * HEIGHT / 454))
            s.fill(DARKBROWN)
            s.set_alpha(255 * (petyr - 330) / 40)
            SCREEN.blit(s, ((LENGTH -
                             (170 * LENGTH / 554)) / 2, 265 * HEIGHT / 454))
    show('Press Space Bar to skip animation.', WHITE, 20, HEIGHT - 20, 14, 'i')
    stopper = False
    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                stopper = True
    if petyr > 370:
        w += 100
        h += 100
        pygame.draw.rect(SCREEN, BLACK,
                         (((LENGTH - w) / 2, (HEIGHT - h) / 2, w, h)))
    if petyr == 377 or stopper:
        user = 'Home'
        rate = 8
        petyr = 0


def home():
    global i, decreaser, done, user, start, breaker, frontSnake, petyr,changeNamePop
    LENGTH = pygame.display.get_surface().get_width()
    HEIGHT = pygame.display.get_surface().get_height()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, HEIGHT - 60))
    usualWidth, margin = 120, 65
                     
    scaledFrontSnake = pygame.transform.scale(
        frontSnake, (int(250 * HEIGHT / 400), int(250 * HEIGHT / 400)))
    frontSnakeSize = scaledFrontSnake.get_size()
    SCREEN.blit(scaledFrontSnake,
                ((LENGTH - frontSnakeSize[0]) / 2, 30 +
                 (265 * HEIGHT / 454 - frontSnakeSize[1]) / 2))

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

    show('playing as ', LIGHTBROWN, 20, 16, 16)
    show(data['name'], WHITE, 110, 9, 24,'ib')
    show(data['coin'] + ' coin(s)', WHITE, 275, 9, 24)
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
    user = 'Arsenal' if button('Play Game',
                               (LENGTH - (170 * LENGTH / 554)) / 2,
                               265 * HEIGHT / 454 - 10,
                               170 * LENGTH / 554,
                               55 * HEIGHT / 454,
                               DARKBROWN,
                               x_offset=30 + (10**(LENGTH / 554)) / 5,
                               text_col=WHITE,
                               text_size=int(28 * LENGTH / 700),
                               hover_col=BLACKBROWN,
                               hover_width=1,
                               mode='b') else user

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

    if button('LeaderBoard',
              margin,
              300 * HEIGHT / 454,
              usualWidth * LENGTH / 554,
              30 * HEIGHT / 454,
              DARKBROWN,
              x_offset=7 + (10**(LENGTH / 554)) / 3,
              text_col=WHITE,
              text_size=16,
              hover_col=BLACKBROWN,
              hover_width=1):
        user = 'LeaderBoard'
        petyr = 4
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
    user = 'Inventory' if button('Inventory',
                                 LENGTH - (margin + usualWidth * LENGTH / 554),
                                 300 * HEIGHT / 454,
                                 usualWidth * LENGTH / 554,
                                 30 * HEIGHT / 454,
                                 DARKBROWN,
                                 x_offset=20 + (10**(LENGTH / 554)) / 3,
                                 text_col=WHITE,
                                 text_size=16,
                                 hover_col=BLACKBROWN,
                                 hover_width=1) else user
    user = 'MarketPlace' if button('Shop',
                                   LENGTH -
                                   (margin + usualWidth * LENGTH / 554),
                                   340 * HEIGHT / 454,
                                   usualWidth * LENGTH / 554,
                                   30 * HEIGHT / 454,
                                   DARKBROWN,
                                   x_offset=35 + (10**(LENGTH / 554)) / 3,
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

    if savedDataNameThrives:
        if button('Attention', LENGTH - (margin + usualWidth * LENGTH / 554) + 50, 70 * HEIGHT / 454, 100, 30, RED, x_offset=10, text_col=WHITE, text_size=17, hover_col=BLACKBROWN, hover_width=1):
            changeNamePop = True
    if changeNamePop:
        attentionChangeNamePopup()

    # if not done:
    #     d = screen_animation()
    #     done = d
    # if done:
    #     d = screen_animation(True)
    #     done = not d


def arsenal():
    global user, start, SCREEN, selected_items, coin_2, point_2, Pop, userSettings, sensitivity
    LENGTH = pygame.display.get_surface().get_width()
    # LENGTH = 554
    # SCREEN = pygame.display.set_mode((LENGTH, 454))
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('Your Arsenel for the game', WHITE, 10, 10, 20,'b')
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    with open(r'data\bin\items.dat', 'rb') as file:
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
                SCREEN.blit(powerup_img[i], (60 + i * mul, 80))
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
                    if pygame.mouse.get_pressed()[0] and (time.time() -
                                                          sensitivity) > 0.1:
                        sensitivity = time.time()
                        if item[1][0] != '0' or selected_items[i]:
                            with open(r'data\bin\items.dat', 'wb') as f:
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
                SCREEN.blit(powerup_img[i], (60 + (i - 3) * mul, 240))
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
                    if pygame.mouse.get_pressed()[0] and (time.time() -
                                                          sensitivity) > 0.1:
                        sensitivity = time.time()
                        if item[1][0] != '0' or selected_items[i]:
                            with open(r'data\bin\items.dat', 'wb') as f:
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
    with open(r'data\bin\missions.dat', 'rb') as file:
        list_items = pickle.load(file)
        coin_2 = list_items['coins']['coins']
        point_2 = list_items['coins']['points']
        for i, item in enumerate(list_items['coins'].items()):
            if i <= 5:
                if item[1][1]:
                    t = float(f"{(time.time()-item[1][2]):.2f}")
                    if t >= (float(item[0].split()[2]) * 60):
                        with open(r'data\bin\missions.dat', 'wb') as f:
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
        with open(r'data\bin\items.dat', 'rb') as file:
            list_items = pickle.load(file)

            for i, item in enumerate(list_items['Powerups'].items()):
                list_items['Powerups'][item[0]] = (
                    str(int(item[1][0]) + (1 if selected_items[i] else 0)),
                    item[1][1])
                selected_items[i] = False
        with open(r'data\bin\items.dat', 'wb') as f:
            pickle.dump(list_items, f)
    if user == 'Emulator':
        daily()
        emulator_params()

fromSD = False


def attentionChangeNamePopup():
    global changeNamePop, savedDataNameThrives, user, fromSD
    s = pygame.Surface((LENGTH * 2, LENGTH * 2))
    s.set_colorkey(GREY)
    s.set_alpha(200)
    SCREEN.blit(s, (0, 0))
    pygame.draw.rect(SCREEN, LIGHTBROWN, (50, 60, 450, 180), 0, 1)
    show("Unable to send data to cloud as a player", DARKBROWN, 80, 80, 20)
    show("already thrives on the leadername by the", DARKBROWN, 80, 121, 20)
    show(f"name of {data['name']}", DARKBROWN, 80, 142, 20)
    
    if button('Don\'t Send Data', 100, 180, 160, 30, WHITE, x_offset=10,text_col=DARKBROWN,text_size=18, hover_col=GREY,hover_width=1):
        changeNamePop, savedDataNameThrives = False, False
    
    if button('Change Name', 290, 180, 150, 30, DARKBROWN, x_offset=10,text_col=WHITE,text_size=18, hover_col=GREY,hover_width=1):
        newUser_init()
        fromSD = True
        changeNamePop, savedDataNameThrives = False, False
        user = 'NewUser'
             


def emulator_params():
    global Blocks, snake, direction, body, Apple, random_cord, Bomb, SpeedUp, SpeedDown, counter, rnt, score, ee_dec, ee_done, realm
    global Theme, blocks, LENGTH, rate, start, SCREEN, popup, applex, appley, m_counter, st, speed_checker, petyr
    global changeNameForLead, showHomeButton, tempDataForLead, popForLeadInit, dataSent, dataNotSent, dataUpdated, dataNotUpdated, errorButDataSaved
    LENGTH = 454
    rate = 4 if selected_items[3] else (12 if selected_items[2] else 8)

    Theme = [LIGHTBROWN, GREY, CADET, RED, GREY, GREEN, BLUE, WHITE, DARKBROWN]
    # bg_color, bomb_col, snake_col, apple_col, empty_col, sup_col, sdown_col, text_col, text_bg
    with open(r'data\bin\items.dat', 'rb') as file:
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

    petyr = 0
    blocks = []
    # missions initialize
    with open(r'data\bin\missions.dat', 'rb') as file:
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
    dataSent = False
    dataNotSent = False
    dataUpdated = False
    dataNotUpdated = False
    errorButDataSaved = False
    tempDataForLead = {'score': 0, 'time': 0}
    popForLeadInit = True


old_rank = None

def emulator():
    global direction, Apple, Bomb, SpeedUp, SpeedDown, counter, rnt, Theme, event_list, realm, t0, start, selected_items, blocks, popup, coin_2, point_2
    global applex, appley, bombx, bomby, speedupx, speedupy, speeddownx, speeddowny, score, rate, ee_dec, ee_done, user, data, coins, t, SCREEN
    global sortedData, Pop, PopT, userSettings, sensitivity, petyr, internet, fromLB, old_rank, sortedData
    global changeNameForLead, showHomeButton, tempDataForLead, popForLeadInit, dataSent, dataNotSent, dataUpdated, dataNotUpdated, errorButDataSaved
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
                    with open(r'data\bin\missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'st' and pair == m[1]:
                                with open(r'data\bin\missions.dat', 'wb') as f:
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
            body.append(body[-1])
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
                    with open(r'data\bin\missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'st' and pair == m[1]:
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            for v in speed_checker:
                if rate == v:
                    with open(r'data\bin\missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'speed' and m[1] == v:
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            if obj['mission'][0] == 'speed':
                if rate == obj['mission'][1]:
                    obj['mission'][3] = True
        elif tuple(snake) == (speeddownx, speeddowny):
            if userSettings['sound']:
                speeddownMusic.play(loops=0)
            speeddownx, speeddowny = -1, -1
            body.append(body[-1])
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
                    with open(r'data\bin\missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'st' and pair == m[1]:
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = True
                                    pickle.dump(miss, f)
            for v in speed_checker:
                if rate == v:
                    with open(r'data\bin\missions.dat', 'rb') as file:
                        miss = pickle.load(file)
                        for i, m in enumerate(miss['missions']):
                            if m[0] == 'speed' and m[1] == v:
                                with open(r'data\bin\missions.dat', 'wb') as f:
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
        if (not (-10 <= snake[0] <= 450)
                or not (20 <= snake[1] <= 450)) and not selected_items[5]:
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
            if event.type == pygame.KEYDOWN and not snake[0] in (
                    452, -13) and not snake[1] in (
                        452, 17) and (time.time() - sensitivity) > 0.01 * (
                            (16 - rate) if rate <= 14 else 0):
                sensitivity = time.time()

                if event.key == (pygame.K_UP if userSettings['arrow'] else
                                 pygame.K_w) and not direction == "down":
                    direction = "up"
                if event.key == (pygame.K_DOWN if userSettings['arrow'] else
                                 pygame.K_s) and not direction == "up":
                    direction = "down"
                if event.key == (pygame.K_LEFT if userSettings['arrow'] else
                                 pygame.K_a) and not direction == "right":
                    direction = "left"
                if event.key == (pygame.K_RIGHT if userSettings['arrow'] else
                                 pygame.K_d) and not direction == "left":
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
            if userSettings['sound']:
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
        petyr += 1
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

        if petyr == 3:
            data['coin'] = f"{int(data['coin'])+coins}"
            with open(r'data\bin\missions.dat', 'rb') as file:
                miss = pickle.load(file)
                for i, m in enumerate(miss['missions']):
                    if m[0] == 'points' and m[1] <= score:
                        with open(r'data\bin\missions.dat', 'wb') as f:
                            miss['missions'][i][3] = True
                            pickle.dump(miss, f)
                    if m[0] in ('apple', 'up', 'down'):
                        for k in m_counter[m[0]]:
                            if m[3].split('/')[1] == k.split('/')[1]:
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    miss['missions'][i][3] = k
                                    pickle.dump(miss, f)

            if obj['mission'][0] == 'points':
                if score >= obj['mission'][1]:
                    obj['mission'][3] = True
            update_obj()
            update_data()
            bigGame = bigGameVar()
            internet = connect()
            if internet:
                try:
                    for i in len(sortedData):
                        if sortedData[i][0] == data['name']:
                            old_rank = i
                    print(f'old rank : {old_rank}')
                    pushReturnDict = pushData(data['name'], score, t, bigGame)
                    changeNameForLead = pushReturnDict['thrives']
                    dataSent = pushReturnDict['sent']
                    dataNotSent = pushReturnDict['notSent']
                    dataUpdated = pushReturnDict['updated']
                    dataNotUpdated = pushReturnDict['notUpdated']
                    showHomeButton = not changeNameForLead
                except:
                    print(
                        'Data not sent due to an unexpected error. The data is saved and will be sent when there is an internet connection and the game is opened.'
                    )
                    saveGameDataForLater(data['name'], score, t)
                    errorButDataSaved = True
                    showHomeButton = True
            else:
                print(
                    'Data not sent as there is no internet. The data is saved and will be sent when there is an internet connection and the game is opened.'
                )
                saveGameDataForLater(data['name'], score, t)
                showHomeButton = True

        if not internet:
            show("Data couldn't be sent to servers due", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 78, 17)
            show("to an internet error. It's saved and ", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 97, 17)
            show("will be sent next time you open game.", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 116, 17)
        elif dataSent:
            show("Your Game Data sent to the servers.", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 87, 17)
        elif dataNotSent:
            show("Data hasn't been sent to servers as", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 85, 17)
            show("you don't qualify to be on leaderboard.", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 103, 17)
        elif dataUpdated:
            # new_rank = 
            # with open('missions.dat', 'rb') as file:
            #     miss = pickle.load(file)
            #     for i, m in enumerate(miss['missions']):
            #         if m[0] == 'rank' :
            #             complete=False
            #             if m[1]=='prev':
            #                 if new_rank>old_rank:
            #                     complete=True
            #             else:
            #                 if new_rank>int(m[1]):
            #                     complete=True
            #             if complete:
            #                 with open('missions.dat', 'wb') as f:
            #                     miss['missions'][i][3] = True
            #                     pickle.dump(miss, f)
            show("Your data on servers has been updated", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 87, 17)
        elif dataNotUpdated:
            show("You already exist on the leaderboard. ", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 85, 17)
            show("Beat your previous score to be promoted.", DARKBROWN,
                 LENGTH // 2 - 165, LENGTH // 2 + 103, 17)
        elif errorButDataSaved:
            show("Your data couldn't be sent to servers ", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 78, 17)
            show("due to an unexpected error. It is saved ", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 97, 17)
            show("and will be sent next time you open game.", DARKBROWN,
                 LENGTH // 2 - 160, LENGTH // 2 + 116, 17)

        if showHomeButton:
            if button('Home',
                      LENGTH // 2 - 100,
                      LENGTH // 2 + 40,
                      100,
                      30,
                      WHITE,
                      x_offset=10,
                      text_col=DARKBROWN,
                      text_size=16,
                      hover_col=GREY,
                      hover_width=1):
                user = 'Home'
                selected_items = [False, False, False, False, False, False]
                SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH))

        if changeNameForLead:
            show("Unable to send data to cloud as a player", DARKBROWN, LENGTH // 2 - 163, LENGTH // 2 + 38, 17)
            show("already thrives on the leadername by the", DARKBROWN, LENGTH // 2 - 163, LENGTH // 2 + 56, 17)
            show(f"name of {data['name']}", DARKBROWN, LENGTH // 2 - 163, LENGTH // 2 + 74, 17)
            
            if button('Don\'t Send Data', LENGTH // 2 - 140, LENGTH // 2 + 100, 140, 25, WHITE, x_offset=10,text_col=DARKBROWN,text_size=15,hover_col=GREY,hover_width=1):
                showHomeButton = True
                changeNameForLead = False

            if button('Change Name',
                      LENGTH // 2 + 10,
                      LENGTH // 2 + 100,
                      130,
                      25,
                      DARKBROWN,
                      x_offset=10,
                      text_col=WHITE,
                      text_size=15,
                      hover_col=GREY,
                      hover_width=1):
                tempDataForLead['score'] = score
                tempDataForLead['time'] = t
                newUser_init()
                user='NewUser'
                fromLB=True                
        
        if not showHomeButton and not changeNameForLead:
            show(f"Analysing and Sending", DARKBROWN, LENGTH // 2 - 120,
                 LENGTH // 2 + 56, 18)
            show(f"your data to cloud ....", DARKBROWN, LENGTH // 2 - 120,
                 LENGTH // 2 + 78, 18)
            # loading_anime=''
            # load_i=petyr%10
            # if load_i>5:
            #     loading_anime+='|'
            # else:
            #     loading_anime=loading_anime[:-1]
            # show(loading_anime, DARKBROWN, LENGTH // 2 - 120, LENGTH // 2 + 100, 18)


def leaderboard():
    global sortedData, user, petyr
    # fauna
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('LEADERBOARDS', WHITE, 10, 10, 20, 'b')
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if len(sortedData) > 0:
        for i, dt in enumerate(sortedData):
            if i < 10:
                show(dt[0], BLACK, 30, 78 + i * 35, 30, 'ib')
                show(str(dt[1]), BLACK, 305, 78 + i * 35, 30, 'ib')
                show(str(dt[2]), BLACK, 420, 78 + i * 35, 30, 'ib')
    else:
        show('Oops! No Data Available', WHITE, 50, 200, 30, 'b')
    if (button('R', LENGTH - 40, 10, 20, 20, BLACKBROWN, 4, 14, WHITE,
               LIGHTBROWN)):
        petyr = 0
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
        petyr = 0
    if petyr == 2:
        Popup(mode='loading')
    if petyr == 3:
        sortedData = pullingSortedData()
    petyr += 1


def missions():
    global user, obj, petyr
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('MISSIONS', WHITE, 10, 10, 20,'b')
    show(data['coin'] + ' coin(s)', WHITE, 275, 9, 24)
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

    show("Today's Special Mission :", BLACK, 30, 54, 16)
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
            with open(r'data\bin\missions.dat', 'rb') as file:
                miss = pickle.load(file)
                with open(r'data\bin\missions.dat', 'wb') as f:
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
    with open(r'data\bin\missions.dat', 'rb') as file:
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
                    with open(r'data\bin\missions.dat', 'wb') as f:
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
        petyr = 0
    if petyr == 1:
        Popup(mode='loading')
    if petyr == 2:
        indexes = client.query(q.paginate(q.match(q.index('missionsindex'))))
        result = re.findall('\d+',
                            str([indexes['data']
                                 ]))  # to find all the numbers in the list
        deleteDoc('dailymissions', result[0])
        pushDictData(collection='dailymissions', data=obj)
        obj = pullOBJ()
    petyr += 1


opened = [True, False, False, False]

pop = False


def marketplace():
    global user, start, SCREEN, LENGTH, opened, pop, q, Pop, sensitivity
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('MARKET PLACE', WHITE, 10, 10, 20,'b')
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
    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))
    with open(r'data\bin\items.dat', 'rb') as file:
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
                    SCREEN.blit(powerup_img[i], (37 + (i + 1) * mul, 80))
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
                            if pygame.mouse.get_pressed()[0] and (
                                    time.time() - sensitivity) > 0.1:
                                sensitivity = time.time()
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
                    SCREEN.blit(powerup_img[i], (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if not pop or not Pop:
                        if pos[0] >= x and pos[0] <= x + width and pos[
                                1] >= y and pos[1] <= y + height:
                            if pygame.mouse.get_pressed()[0] and (
                                    time.time() - sensitivity) > 0.1:
                                sensitivity = time.time()
                                pop = True
                                q = i
                            s.set_alpha(60)
                    SCREEN.blit(s, (x, y))
            if pop:
                cont = Popup('Would you like to make this purchase',
                             mode='yesno')
                if cont == True:
                    t = list_items['Powerups'][list(
                        list_items['Powerups'].keys())[q]]
                    data['coin'] = str(int(data['coin']) - int(t[1]))
                    if int(data['coin']) >= 0:
                        update_data()
                        with open(r'data\bin\items.dat', 'wb') as f:
                            list_items['Powerups'][list(
                                list_items['Powerups'].keys())[q]] = (
                                    str(int(t[0]) + 1), t[1])
                            pickle.dump(list_items, f)
                    else:
                        data['coin'] = str(int(data['coin']) + int(t[1]))
                        Pop = True
                    pop = False
                if cont != None:
                    pop = False
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
                cont = Popup('Would you like to make this purchase',
                             mode='yesno')
                if cont:
                    t = list_items['Themes'][list(
                        list_items['Themes'].keys())[q]]
                    data['coin'] = str(
                        int(data['coin']) - (25 if opened[0] else 15))
                    if int(data['coin']) >= 0:
                        update_data()
                        with open(r'data\bin\items.dat', 'wb') as f:
                            t[list(t.keys())[0 if opened[0] else 1]] = True
                            list_items['Themes'][list(
                                list_items['Themes'].keys())[q]] = t
                            pickle.dump(list_items, f)
                    else:
                        Pop = True
                        data['coin'] = str(
                            int(data['coin']) + (25 if opened[0] else 15))
                    pop = False
                if cont != None:
                    pop = False
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
    show(str(data['coin']) + ' coin(s)', LIGHTBROWN, LENGTH - 270, 10, 19)


def inventory():
    global user, start, SCREEN, LENGTH, opened, Pop, sensitivity
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('INVENTORY', WHITE, 10, 10, 20,'b')
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

    with open(r'data\bin\items.dat', 'rb') as file:
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
                    SCREEN.blit(powerup_img[i], (37 + (i + 1) * mul, 80))
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
                    SCREEN.blit(powerup_img[i], (37 + (i - 2) * mul, 270))
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        s.set_alpha(60)
                    SCREEN.blit(s, (x, y))

        elif opened[3]:
            with open(r'data\bin\missions.dat', 'rb') as file:
                list_items = pickle.load(file)
                for i, item in enumerate(list_items['coins'].items()):
                    if i <= 2:
                        global event_list
                        pos = pygame.mouse.get_pos()
                        x, y, width, height = (20 + (i + 1) * mul, 70,
                                               mul - 20, 160)
                        pygame.draw.rect(SCREEN, DARKBROWN,
                                         (x, y, width, height))
                        pygame.draw.rect(
                            SCREEN, LIGHTBROWN,
                            (x + 5, y + 5, width - 10, height - 10))
                        SCREEN.blit(powerup_img[6], (37 + (i + 1) * mul, 80))
                        if i == 1:
                            show(item[0], BLACK, 25 + (i + 1) * mul, 210, 12)
                            show(f'{item[1][0]} left', WHITE,
                                 55 + (i + 1) * mul, 165, 20)
                        else:
                            show(item[0], BLACK,
                                 (85 if (i + 1) == 2 else 30) + (i + 1) * mul,
                                 210, 12)
                            show(f'{item[1][0]} left', WHITE,
                                 50 + (i + 1) * mul, 165, 20)
                        if item[1][1]:
                            t = float(f"{(time.time()-item[1][2]):.2f}")
                            T = float(item[0].split()[2]) * 60 - t
                            ss = '0' if int(T % 60) // 10 == 0 else ''
                            show(f"{int(T//60)}:{ss}{int(T%60)}", WHITE,
                                 50 + (i + 1) * mul, 187, 20)
                            if t >= (float(item[0].split()[2]) * 60):
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][1] = False
                                    list_items['coins']['coins'] = False
                                    pickle.dump(list_items, f)
                        elif item[1][0] != '0' and not list_items['coins'][
                                'coins']:
                            if button('Activate', 35 + (i + 1) * mul, 187, 80,
                                      22, DARKBROWN, 10, 13, WHITE, DARKBROWN,
                                      0):
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][0] = str(
                                        int(item[1][0]) - 1)
                                    list_items['coins'][item[0]][1] = True
                                    list_items['coins'][
                                        item[0]][2] = time.time()
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
                        x, y, width, height = (20 + (i - 2) * mul, 260,
                                               mul - 20, 160)
                        pygame.draw.rect(SCREEN, DARKBROWN,
                                         (x, y, width, height))
                        pygame.draw.rect(
                            SCREEN, LIGHTBROWN,
                            (x + 5, y + 5, width - 10, height - 10))
                        pos = pygame.mouse.get_pos()
                        show(item[0], BLACK, 30 + (i - 2) * mul, 400, 12)
                        show(f'{item[1][0]} left', WHITE, 55 + (i - 2) * mul,
                             355, 24)
                        SCREEN.blit(powerup_img[7], (37 + (i - 2) * mul, 270))
                        if item[1][1]:
                            t = float(f"{(time.time()-item[1][2]):.2f}")
                            T = float(item[0].split()[2]) * 60 - t
                            ss = '0' if int(T % 60) // 10 == 0 else ''
                            show(f"{int(T//60)}:{ss}{int(T%60)}", WHITE,
                                 50 + (i - 2) * mul, 377, 20)
                            if t >= (float(item[0].split()[2]) * 60):
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][1] = False
                                    list_items['coins']['points'] = False
                                    pickle.dump(list_items, f)
                        elif item[1][0] != '0' and not list_items['coins'][
                                'points']:
                            if button('Activate', 35 + (i - 2) * mul, 377, 80,
                                      22, DARKBROWN, 10, 13, WHITE, DARKBROWN,
                                      0):
                                with open(r'data\bin\missions.dat', 'wb') as f:
                                    list_items['coins'][item[0]][0] = str(
                                        int(item[1][0]) - 1)
                                    list_items['coins'][item[0]][1] = True
                                    list_items['coins'][
                                        item[0]][2] = time.time()
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
                    if Dic[0 if opened[0] else 1] == 'LIGHTBROWN':
                        pygame.draw.rect(SCREEN, DARKBROWN,
                                         (x + 14, y + 14, width - 28, 68))
                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))
                    show(Dic[0 if opened[0] else 1], BLACK, 32 + (i + 1) * mul,
                         170, 14)
                    show(
                        'Purchased' if D[0 if opened[0] else 1] else
                        'Not Purchased', WHITE, 32 + (i + 1) * mul, 215, 10)
                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0] and (
                                time.time() - sensitivity) > 0.1:
                            sensitivity = time.time()
                            if D[0 if opened[0] else 1]:
                                with open(r'data\bin\items.dat', 'wb') as f:
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
                         360, 14)
                    show(
                        'Purchased' if D[0 if opened[0] else 1] else
                        'Not Purchased', WHITE, 32 + (i - 2) * mul, 405, 10)
                    if Dic[0 if opened[0] else 1] == 'LIGHTBROWN':
                        pygame.draw.rect(SCREEN, BLACK,
                                         (x + 14, y + 14, width - 28, 67))

                    pygame.draw.rect(SCREEN,
                                     globals()[Dic[0 if opened[0] else 1]],
                                     (x + 15, y + 15, width - 30, 65))

                    s = pygame.Surface((width, height))
                    s.set_colorkey(GREY)
                    s.set_alpha(0)
                    if pos[0] >= x and pos[0] <= x + width and pos[
                            1] >= y and pos[1] <= y + height:
                        if pygame.mouse.get_pressed()[0] and (
                                time.time() - sensitivity) > 0.1:
                            sensitivity = time.time()
                            if D[0 if opened[0] else 1]:
                                with open(r'data\bin\items.dat', 'wb') as f:
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


openedSettings = [True, False, False]

namepop = False
popinit = True
popupClose = False


def settings():
    global user, start, SCREEN, LENGTH, openedSettings, pop, q
    global data, namepop, popinit, fromsetting, popupClose, userSettings, sortedData, bigGame
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('SETTINGS', WHITE, 10, 10, 20,'b')
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
        openedSettings = [True, False, False]
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
        openedSettings = [False, True, False]
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
        openedSettings = [False, False, True]

    pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 5, 50, LENGTH - 10 - mul - 5, 390))

    if openedSettings[0]:
        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 100), (LENGTH - 30, 100),
                         width=3)

        show('Music', DARKBROWN, mul + 35, 110, 21)
        if (button('', mul + 110, 122, 15, 15,
                   WHITE if userSettings['music'] == False else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['music'] == True else DARKBROWN)):
            userSettings['music'] = not userSettings['music']
            updateSettings(userSettings)
        show('Sounds', DARKBROWN, mul + 220, 110, 21)
        if (button('', mul + 310, 122, 15, 15,
                   WHITE if userSettings['sound'] == False else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['sound'] == True else DARKBROWN)):
            userSettings['sound'] = not userSettings['sound']
            updateSettings(userSettings)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 155), (LENGTH - 30, 155),
                         width=3)

        show('VOLUME: ', DARKBROWN, mul + 35, 165, 20)
        if (button('-', mul + 200, 170, 30, 25, DARKBROWN, 10, 17, WHITE,
                   BLACK)):
            userSettings['volume'] -= 5
            updateSettings(userSettings)
        pygame.draw.rect(SCREEN, WHITE, (mul + 235, 170, 40, 25))
        show(str(userSettings['volume']), DARKBROWN, mul + 240, 170, 19)
        if (button('+', mul + 280, 170, 30, 25, DARKBROWN, 10, 19, WHITE,
                   BLACK)):
            if userSettings['volume'] < 100:
                userSettings['volume'] += 5
                updateSettings(userSettings)

        pygame.draw.line(SCREEN,
                         DARKBROWN, (mul + 20, 210), (LENGTH - 30, 210),
                         width=3)

        show('PREFERRED CONTROLS: ', DARKBROWN, mul + 35, 220, 20)
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
        show(data['name'], BLACK, mul + 40, 157, 30, mode='ib')

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
    
    elif openedSettings[2]:
        pygame.draw.rect(SCREEN, pygame.Color('#11110F'),
                     (mul + 30, 100, 170, 110))
        pygame.draw.rect(SCREEN, pygame.Color('#4F3119'),
                     (mul + 30, 100, 170, 12))
        pygame.draw.rect(SCREEN, pygame.Color('#4F3119'),
                     (mul + 30, 117, 30, 110 - 12 - 5))
        pygame.draw.rect(SCREEN, pygame.Color('#AD9157'),
                     (mul + 30 + 34, 117, 170 - 38, 110 - 12 - 10))
        
        pygame.draw.rect(SCREEN, BLACKBROWN,
                     (mul + 220, 100, 170, 110))
        pygame.draw.rect(SCREEN, DARKBROWN,
                     (mul + 220, 100, 170, 12))
        pygame.draw.rect(SCREEN, DARKBROWN,
                     (mul + 220, 117, 30, 110 - 12 - 5))
        pygame.draw.rect(SCREEN, LIGHTBROWN,
                     (mul + 220 + 34, 117, 170 - 38, 110 - 12 - 10))       
        
        
        if (button('', mul + 110, 225, 15, 15,
                   WHITE if userSettings['darkTheme'] else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if not userSettings['darkTheme'] else DARKBROWN)):
            userSettings['darkTheme'] = not userSettings['darkTheme']
            updateSettings(userSettings)
            updateTheme()
        if (button('', mul + 300, 225, 15, 15,
                   WHITE if not userSettings['darkTheme'] else DARKBROWN, 7,
                   21, BLACK,
                   WHITE if userSettings['darkTheme'] else DARKBROWN)):
            userSettings['darkTheme'] = not userSettings['darkTheme']
            updateSettings(userSettings)
            updateTheme()

        


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
        newuser(changename=True)


errormsg = False
errorstart = 0


def newuser(changename=False):
    LENGTH = pygame.display.get_surface().get_width()
    global user, Text_Val, iterrr, Cursor, data, fromsetting, namepop, Pop, Popup, popinit, errormsg, errorstart, sortedData, bigGame,fromLB,selected_items,SCREEN, savedDataDict, tempDataForLead, fromSD

    if not changename:
        SCREEN.fill(BLACKBROWN)
        pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
        pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
        if fromLB or fromSD:
            show('CHANGE NAME', WHITE, 10, 10, 20)
        else:
            show('SIGN UP', WHITE, 10, 10, 20,'b')
    if changename:
        s = pygame.Surface((LENGTH * 2, LENGTH * 2))
        s.set_colorkey(GREY)
        s.set_alpha(200)
        SCREEN.blit(s, (0, 0))
        pygame.draw.rect(SCREEN, LIGHTBROWN, (27, 125, LENGTH - 54, 200))
    if len(Text_Val) == 0:
        show("Type your name here.", WHITE, (LENGTH - 200) // 2, 220, 20,'i')
    else:
        show(Text_Val, WHITE, (LENGTH - len(Text_Val) * 10) // 2, 220, 20,'i')
        if iterrr % 8 == 0:
            Text_Val = Text_Val[:-1] + '|'
            Cursor = True
        if iterrr % 8 == 4 and Cursor:
            Text_Val = Text_Val[:-1] + ' '
            Cursor = False
        iterrr += 1
    if not fromsetting:
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
            Text_Val = ''
    else:
        if button('Settings',
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
            user = 'Settings'
            fromsetting = False
            namepop = False
            Text_Val = ''
    # if iterrr>10:
    #     Text_Val+='|'
    # else:
    #     Text_Val=Text_Val[:-1]
    # iterrr+=1
    # iterrr=0 if iterrr>20 else iterrr
    pygame.draw.line(SCREEN, DARKBROWN, (50, 250), (LENGTH - 50, 250), 1)
    Text_Ent = button('Change Name' if (changename or fromLB or fromSD) else 'Create Account',
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
            if fromLB:                
                data['name']= Text_Val[:-1]
                data['highscore'] = tempDataForLead['score']
                data['time'] = tempDataForLead['time']
                dictData = {'name':Text_Val[:-1], 'score':tempDataForLead['score'], 'time':tempDataForLead['time']}
                try:
                    pushDictData('testcollection', dictData)
                    print('Data with changed name sent')
                    bigGame=True
                except:
                    print('Name changed but data couldn\'t be sent due to an unexpected error')
                    bigGame=False
            elif fromSD:
                data['name']= Text_Val[:-1]
                data['highscore'] = savedDataDict['score']
                data['time'] = savedDataDict['time']
                dictData = {'name':Text_Val[:-1], 'score':savedDataDict['score'], 'time':savedDataDict['time']}
                try:
                    pushDictData('testcollection', dictData)
                    print('Data with changed name sent')
                    bigGame=True
                except:
                    print('Name changed but data couldn\'t be sent due to an unexpected error')
                    bigGame=False
            elif not changename:
                bigGame = False
                print('The condition is to sign up as a new user')
                data = {
                    'name': Text_Val[:-1],
                    'highscore': 0,
                    'coin': '0',
                    'time': ''
                }
                with open(r'data\bin\missions.dat', 'rb') as f:
                    miss = pickle.load(f)
                    for i, j in enumerate(miss['missions']):
                        if j[0] in ('apple', 'up', 'down'):
                            miss['missions'][i][3] = '0' + '/' + j[3].split(
                                '/')[1]
                        else:
                            miss['missions'][i][3] = False
                        miss['missions'][i][4] = False
                    for i in list(miss['coins'].keys()):
                        if i in ('coins', 'points'):
                            miss['coins'][i] = False
                        else:
                            miss['coins'][i] = ['10', False, 0]
                with open(r'data\bin\missions.dat', 'wb') as f:
                    pickle.dump(miss, f)
                with open(r'data\bin\items.dat', 'rb') as f:
                    item_list = pickle.load(f)
                    for i in list(item_list['Themes'].keys()):
                        if i == 0:
                            continue
                        for a in list(item_list['Themes'][i].keys()):
                            item_list['Themes'][i][a] = False
                    for i in list(item_list['Powerups'].keys()):
                        item_list['Powerups'][i]=('0',item_list['Powerups'][i][1])
                    item_list['Offers']['pseudo']={'background': 'Theme1', 'snake': 'Theme1'}
                        
                with open(r'data\bin\items.dat','wb') as f:
                    pickle.dump(item_list,f)
                try:
                    os.remove(r'data\bin\savedData.dat')
                except:
                    pass
                print('Signed up as new user')               

            elif changename:
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
                                deleteDoc(collection='testcollection',
                                          refid=i[4])
                                pushDictData('testcollection', dataDict)
                                print(
                                    f"Your Name on Leaderboard updated successfully!! {data['name']} changed to {Text_Val[:-1]}"
                                )
                    except:
                        print(
                            'Your name on the leaderboard could not be updated due to an unexpedted error'
                        )
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
            elif fromLB:
                selected_items = [False, False, False, False, False, False]
                SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH))
                user='Home'
                fromLB = False
            elif fromSD:
                selected_items = [False, False, False, False, False, False]
                SCREEN = pygame.display.set_mode((LENGTH + 100, LENGTH))
                user='Home'
                fromSD = False
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
    global user
    LENGTH = pygame.display.get_surface().get_width()
    # fauna
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 90))
    show('CHEATER CHEATER,', WHITE, 10, 16, 30,'b')
    show('COMPULSIVE EATER', WHITE, 10, 51, 30,'b')
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 100, LENGTH - 20, 345))
    SCREEN.blit(cheaterImage, (30, 135))
    show('YOU CAN\'T CHEAT YOUR WAY TO THE TOP', RED, 30, 380, 23,'ib')
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
            user = 'NewUser'
    with open(r'data\bin\userData.dat', 'wb') as file:
        pickle.dump({
            'name': '',
            'highscore': 0,
            'coin': '0',
            'time': ''
        }, file)


def cheaterlist():
    global user, petyr, listOfCheaters
    # fauna
    LENGTH = pygame.display.get_surface().get_width()
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('Cheaters\' List', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 50, LENGTH - 20, 390))
    if petyr > 3:
        if len(listOfCheaters) > 0:
            for i, dt in enumerate(listOfCheaters):
                if i < 10:
                    show(dt, BLACK, 40, 78 + i * 35, 30)
        else:
            show('Oops! No Data Available', WHITE, 50, 200, 30)
    if (button('R', LENGTH - 40, 10, 20, 20, BLACKBROWN, 4, 14, WHITE,
               LIGHTBROWN)):
        petyr = 0
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
        petyr = 0
    if petyr == 2:
        Popup(mode='loading')
    if petyr == 3:
        listOfCheaters = cheaterlistData()
    petyr += 1


def Popup(txt='A Popup', mode='ok'):
    global Pop
    LENGTH = pygame.display.get_surface().get_width()
    s = pygame.Surface((LENGTH * 2, LENGTH * 2))
    s.set_colorkey(GREY)
    s.set_alpha(200)
    SCREEN.blit(s, (0, 0))
    pygame.draw.rect(SCREEN, LIGHTBROWN, (50, 150, LENGTH - 100, 200), 0, 1)
    if mode == 'ok':
        show(txt, DARKBROWN, 70, 170, 20)
        if button('Ok',
                  350,
                  300,
                  100,
                  30,
                  DARKBROWN,
                  text_col=WHITE,
                  hover_col=DARKBROWN):
            Pop = False
    elif mode == 'yesno':
        show(txt, DARKBROWN, 70, 170, 20)
        if button('No',
                  350,
                  300,
                  100,
                  30,
                  DARKBROWN,
                  text_col=WHITE,
                  hover_col=DARKBROWN):
            return False
        if button('Yes',
                  70,
                  300,
                  100,
                  30,
                  DARKBROWN,
                  text_col=WHITE,
                  hover_col=DARKBROWN):
            return True
    if mode == 'loading':
        show('Loading Please Wait...', DARKBROWN, 70, 260, 20)


def main():
    global event_list, Text_Val
    SCREEN.fill(BLACK)
    while True:
        event_list = pygame.event.get()
        if user == 'Home':
            home()
        elif user == 'Emulator':
            emulator()
        elif user == 'LeaderBoard':
            leaderboard()
        elif user == 'DeltaH':
            delta_h()
        elif user == 'Settings':
            settings()
        elif user == 'NewUser':
            newuser()
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


if __name__ == '__main__':
    main()
