from faunadb.errors import ErrorData
import pygame
import sys
import time
import random
import pickle
import os
pygame.init()

import urllib.request


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



def pushData(name, score, time):

    sortedData1 = sortedLeaderboardList(index = 'testindex', collection = 'testcollection')

    # for i in sortedData1:
    #     print(i)

    lScores = []

    for i in sortedData1:
        lScores.append(i[1])

    # print(lScores)

    count = countDocs(collection = 'testcollection')

    dataDict = {'name':name, 'score':score, 'time':time}

    sending = False

    lTimes = sameScoreTimes(data = sortedData1, score = min(lScores))

    if count < ndataset:
        sending = True
    elif score > min(lScores):
        sending = True
        if lScores.count(min(lScores)) == 1:
            for i in sortedData1:
                if i[1] == min(lScores):
                    deleteDoc(collection = 'testcollection', refid = i[4])
    elif score == min(lScores):
        if time < max(lTimes):
            sending = True
            for i in sortedData1:
                if i[2] == max(lTimes):
                    deleteDoc(collection = 'testcollection', refid = i[4])

    if (sending):
        pushDictData(collection = 'testcollection', data = dataDict)
        print("Data sent successfully!")
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
        fileR = open('savedData.dat',"rb")
        data = pickle.load(fileR)
        if data['score'] < score:
            fileW = open('savedData.dat','wb')
            pickle.dump(data, fileW)
        elif data['score'] == score:
            if data['time'] > time:
                fileW = open('savedData.dat','wb')
                pickle.dump(data, fileW)
        fileR.close()
    except:
        file = open('savedData.dat','wb')
        data = {'name':name, 'score':score, 'time':time}
        pickle.dump(data, file)
        file.close()

sortedData = pullingSortedData()

if internet and os.path.exists("savedData.dat"):
    try:
        fileR = open('savedData.dat',"rb")
        data = pickle.load(fileR)
        pushData(name = data['name'], score = data['score'], time = data['time'])
        fileR.close()
        os.remove("savedData.dat")
        print('Saved data from previous games sent')
    except:
        print('Saved data from previous games couldn\'t be sent due to an unexpected error')

# line pygame.draw.line(SCREEN, BLUE, (100,200), (300,450),5) #screen, color, starting point, ending point, width
# rect pygame.draw.rect(SCREEN, BLUE, (400,400,50,25)) #screen, color, (starting_x, starting_y, width,height)
# circle pygame.draw.circle(SCREEN, BLUE, (150,150), 75) #screen, color, (center_x, center_y), radius)
# polygon pygame.draw.polygon(SCREEN, BLUE, ((25,75),(76,125),(250,375),(400,25),(60,540))) #screen, color, (coordinates of polygon(consecutive))
# image pygame.image.load("space-invaders.png")

#constants
LENGTH = 454
PIXEL = 15
SCREEN = pygame.display.set_mode((LENGTH, LENGTH))
CLOCK = pygame.time.Clock()
rate = 8
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

#[[name,score,timeplayed,1_time,ref_id]]


#user data
def newUser_init():
    global Cursor, Text_Ent, Text_Val, iterrr
    iterrr = 0
    Cursor = False
    Text_Val = ''
    Text_Ent = False


try:
    file = open('userData.dat', 'rb')
    data = pickle.load(file)
    non_cheater = True
except pickle.UnpicklingError:
    user = 'Cheater'
    non_cheater = False
if non_cheater:
    if data['name'] == '' or data['name'] == None:
        user = 'NewUser'
        newUser_init()
    else:
        user = 'Home'
    file.close()


def show(msg, color, x, y, size):
    score_show = pygame.font.Font("freesansbold.ttf",
                                  size).render(msg, True, color)
    SCREEN.blit(score_show, (x, y))


I = 0
iterr = 0


def update_data():
    with open('userData.dat', 'wb') as file:
        pickle.dump(data, file)


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
    global event_list
    pos = pygame.mouse.get_pos()
    if pos[0] >= x and pos[0] <= x + width and pos[1] >= y and pos[
            1] <= y + height:
        pygame.draw.rect(SCREEN, hover_col,
                         (x - hover_width, y - hover_width,
                          width + hover_width * 2, height + hover_width * 2))
        if pygame.mouse.get_pressed()[0]:
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


def home():
    SCREEN.fill(BLACK)
    global i, decreaser, done, user, start
    show('home', WHITE, 0, 0, 32)
    show(data['name'], WHITE, 350, 0, 16)
    newUser = button('NewUser', 200, 250, 100, 30)
    if newUser:
        newUser_init()
        user = 'NewUser'
    user = 'Emulator' if button('Emulator', 200, 200, 100, 30) else user
    if user == 'Emulator':
        start = time.time()
    user = 'LeaderBoard' if button('LeaderBoard', 200, 300, 100, 30) else user

    # if not done:
    #     d = screen_animation()
    #     done = d
    # if done:
    #     d = screen_animation(True)
    #     done = not d


def emulator_params():
    global Blocks, snake, direction, body, Apple, random_cord, Bomb, SpeedUp, SpeedDown, counter, rnt, score, ee_dec, ee_done, realm, teleport
    global Theme
    Theme = [BLACK, (210, 190, 210), RED, YELLOW, GREY, GREEN, BLUE, WHITE]
    # bg_color, bomb_col, snake_col, apple_col, empty_col, sup_col, sdown_col, text_col

    teleport = True
    score = 0
    realm = False
    rnt = [0, 0, 0]
    ee_dec = False
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

    blocks = []

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
    return blocks


def emulator(blocks):
    global direction, Apple, Bomb, SpeedUp, SpeedDown, counter, rnt, Theme, event_list, realm, t0, start
    global applex, appley, bombx, bomby, speedupx, speedupy, speeddownx, speeddowny, score, rate, ee_dec, ee_done, teleport, user, data
    gameover = False
    SCREEN.fill(Theme[0])
    #Bomb
    if counter[0] == 0:
        bombx, bomby = -1, -1
        rnt[0] = random.randint(20, 35)
    elif counter[0] == rnt[0]:
        Bomb = True
    elif counter[0] == rnt[0] + 40:
        counter[0] = -1
    #SpeedUp
    if counter[1] == 0:
        speedupx, speedupy = -1, -1
        rnt[1] = random.randint(65, 85)
    elif counter[1] == rnt[1]:
        SpeedUp = True
    elif counter[1] == rnt[1] + 60:  # + (rate - 8) * 5:
        counter[1] = -1
    #SpeedDown
    if counter[2] == 0:
        speeddownx, speeddowny = -1, -1
        rnt[2] = random.randint(50, 65)
    elif counter[2] == rnt[2]:
        SpeedDown = True
    elif counter[2] == rnt[2] + 60:
        counter[2] = -1

    counter = [x + 1 for x in counter]
    #Spawner
    if Apple == True:
        applex, appley = random_cord(blocks)
        Apple = False
    if Bomb == True:
        bombx, bomby = random_cord(blocks)
        Bomb = False
    if SpeedUp == True:
        speedupx, speedupy = random_cord(blocks)
        SpeedUp = False
    if SpeedDown == True:
        speeddownx, speeddowny = random_cord(blocks)
        SpeedDown = False
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

    body.insert(0, tuple(snake))
    body.pop(-1)
    #Collision Logics
    if tuple(snake) == (applex, appley):
        body.append(body[-1])
        Apple = True
        score += 50
    elif tuple(snake) == (bombx, bomby):
        bombx, bomby = -1, -1
        score -= 100
    elif tuple(snake) == (speedupx, speedupy):
        speedupx, speedupy = -1, -1
        rate += 2
        score += 150
    elif tuple(snake) == (speeddownx, speeddowny):
        speeddownx, speeddowny = -1, -1
        rate -= 2
        score += 150
    if (tuple(snake) in body[1::]):
        gameover = True
    if not (-10 < snake[0] <
            450) or not (-10 + 2 * PIXEL < snake[1] < 450) and not teleport:
        gameover = True
    if teleport:
        snake[0] = -13 if snake[0] == 452 else (
            452 if snake[0] == -13 else snake[0])
        snake[1] = 17 if snake[1] == 452 else (
            452 if snake[1] == 17 else snake[1])
    #GameOver
    if gameover:
        user = 'GameOver'
        data['time'] = f'{(time.time() - start):.2f}'
        update_data()

        if internet:
            try:
                # pushData(name = data['name'], score = score, time = time)
                pushData(data['name'], score, data['time'])
            except:
                print('Data not sent to servers due to an unexpected error')
                saveGameDataForLater(data['name'], score, data['time'])
        else:
            print('Data not sent as there is no internet. The data is saved and will be sent when there is an internet connection and the game is opened.')
            saveGameDataForLater(data['name'], score, data['time'])

    #Score
    data['highscore'] = score if score > data['highscore'] else data[
        'highscore']
    show("Score :" + str(score), Theme[7], 0, 0, 16)
    show("Speed :" + str(rate if rate < 200 else 0), Theme[7], 100, 0, 16)
    show("High Score :" + str(data['highscore']), Theme[7], 200, 0, 16)
    # 0 speed Realm
    if rate == 0:
        realm = True
        t0 = time.time()
        rate = 200
    if realm:
        teleport = True
        Theme[2], Theme[7] = Theme[7], Theme[2]
        Theme[4] = Theme[0]
        Theme[5], Theme[3], Theme[6], Theme[1] = VOILET, VOILET, VOILET, VOILET
        if counter[0] % 5 == 0:
            body.append(body[-1])
        if counter[0] % 2 == 0:
            direction = 'up' if snake[1] > 250 else 'down'
        else:
            direction = 'left' if snake[0] > 250 else 'right'

        if time.time() - t0 > 3:
            SCREEN.fill((0, 0, 0))
            show('The laws of Physics tends to bend when', (200, 200, 200), 20,
                 210, 22)
            show('someone enters the speed 0 realm', (200, 200, 200), 45, 240,
                 22)
        else:
            if not ee_done:
                ee_dec = screen_animation(False, 5, Theme[7], 0.001)
                ee_done = ee_dec
            if ee_done:
                ee_dec = screen_animation(True, 5, Theme[7], 0.0001)
                ee_done = not ee_dec
    #event loop

    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and not direction == "down":
                direction = "up"
            if event.key == pygame.K_DOWN and not direction == "up":
                direction = "down"
            if event.key == pygame.K_LEFT and not direction == "right":
                direction = "left"
            if event.key == pygame.K_RIGHT and not direction == "left":
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


def leaderboard_params():
    # global Variables
    # var1 = 'abcd'
    # var2 = 1234
    # var3 = 'Bruce'
    # var4 = 'JS'
    # Variables = [var1, var2, var3, var4]
    pass


def leaderboard():
    global Variables, sortedData
    # fauna
    SCREEN.fill(BLACKBROWN)
    pygame.draw.rect(SCREEN, DARKBROWN, (0, 0, LENGTH, 40))
    show('LEADERBOARDS', WHITE, 10, 10, 20)
    pygame.draw.rect(SCREEN, LIGHTBROWN, (10, 60, LENGTH - 20, LENGTH - 74))
    if len(sortedData) > 0:
        for i, dt in enumerate(sortedData):
            if i < 10:
                show(dt[0], BLACK, 30, 78 + i * 35, 30)
                show(str(dt[1]), BLACK, 175, 78 + i * 35, 30)
                show(str(dt[2]), BLACK, 320, 78 + i * 35, 30)
    else:
        show('Oops! No Data Available', WHITE, 50, 200, 30)
    if (button('R', LENGTH - 40, 10, 20, 20, BLACKBROWN, 4, 14, WHITE,
               LIGHTBROWN)):
        sortedData = pullingSortedData()
        print('Refresh clicked')


def settings_params():
    pass


def settings():
    SCREEN.fill(BLACK)
    pass


def gameover():
    SCREEN.fill(BLACK)
    show('Game Over', WHITE, 100, 200, 42)


def newuser():
    global user, Text_Val, Text_Ent, iterrr, Cursor, data
    SCREEN.fill(BLACK)
    show('Start typing your name :', WHITE, 20, 30, 32)
    show(Text_Val, WHITE, 20, 100, 32)
    if iterrr % 8 == 0:
        Text_Val = Text_Val[:-1] + '|'
        Cursor = True
    if iterrr % 8 == 4 and Cursor:
        Text_Val = Text_Val[:-1] + ' '
        Cursor = False
    iterrr += 1
    #
    # if iterrr>10:
    #     Text_Val+='|'
    # else:
    #     Text_Val=Text_Val[:-1]
    # iterrr+=1
    # iterrr=0 if iterrr>20 else iterrr
    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if event.unicode in ALPHA:
                Text_Val = Text_Val[:-1] + str(
                    event.unicode) + ('|' if Cursor else ' ')
            elif event.key == pygame.K_BACKSPACE:
                Text_Val = Text_Val[:-2] + ('|' if Cursor else ' ')
            elif event.unicode == '\r':
                Text_Ent = True

    if Text_Ent:
        data = {'name': Text_Val[:-1], 'highscore': 0, 'coins': 0, 'time': ''}
        update_data()
        user = 'Home'

    hScreen = button('Home', 200, 200, 100, 50)
    if hScreen: user = 'Home'


def cheater():
    SCREEN.fill(BLACK)
    show('Cheater Cheater Compulsive Eater', WHITE, 20, 30, 24)
    with open('userData.dat', 'wb') as file:
        pickle.dump({'name': '', 'highscore': 0, 'coins': 0, 'time': ''}, file)


def main():
    global event_list, Text_Val
    SCREEN.fill(BLACK)
    leaderboard_params()
    settings_params()
    blocks = emulator_params()
    home_params()
    while True:
        event_list = pygame.event.get()
        if user == 'Home':
            home()
        elif user == 'Emulator':
            emulator(blocks)
        elif user == 'LeaderBoard':
            leaderboard()
        elif user == 'Settings':
            settings()
        elif user == 'GameOver':
            gameover()
        elif user == 'NewUser':
            newuser()
        elif user == 'Cheater':
            cheater()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        CLOCK.tick(rate)


main()
