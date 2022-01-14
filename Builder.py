# l=['home','arsenal','emulator_params','emulator','leaderboard','missions','marketplace','inventory','settings','newuser','cheater','main']
# q=False
# while True:
#     print("Press 'q' to exit")
#     # f=input('Enter a function to edit :')
#     f='home'
#     f=f.strip()
#     if f in l:
#         break
#     elif f=='q':
#         q=True
#     else:
#         print('Please enter a valid function to edit')

# # Receiver
# if not q:
#     with open('TheSnakeGame.py', 'r') as file:
#         code=file.read()
#         splitted=[]
#         s=code.split('def '+str(f)+'():')
#         splitted.append(s[0])
#         splitted.extend(s[1].split('def '+str(l[l.index(f)+1])+'():'))
#         a=''

# # Initializer
# add=''
# add+=f"def {f}():"
# add+=splitted[1]
# add+="    show('yoooo', WHITE, 100, 0, 32)\n"
# add+=f"def {l[l.index(f)+1]}():"
# # Writer
# with open('TheSnakeGame.py', 'w') as code:
#     splitted[1]=add
#     code.write(''.join(splitted))
# # Executer
# exec(''.join(splitted))

import pickle

# with open('items.dat', 'wb') as file:
#     obj = {
#         "Themes": {
#             "Theme1": {'BLACK':False,'RED':False},
#             "Theme2": {'RED':False,'BLUE':False},
#             "Theme3": {'BLUE':False,'GREEN':False},
#             "Theme4": {'GREEN':False,'PINK':False},
#             "Theme5": {'RED':False,'YELLOW':False},
#             "Theme6": {'YELLOW':False,'BLUE':False}
#         },
#         "Powerups": {
#             "More Ice Apples": ('6','12'),
#             "More Green Apples": ('8','12'),
#             "High Vel": ('4','8'),
#             "Low Vel": ('3','8'),
#             "Fewer Bombs": ('2','15'),
#             "Teleport": ("8",'40'),
#         },
#         "Offers":{
#             "pseudo":{},
#             "2x Coins": {'5 min':'4','10 min':'4','30 min':'3'},
#             "2x Points": {'5 min':'4','10 min':'4','30 min':'3'},
#             "Small Box":{'0':'2','1':'2','2':'3','3':'3'},
#             "Large Box":{'0':'2','1':'2','2':'2','3':'2','4':'1','5':'1'},
#             "Lucky Box":{}
#         }
#     }
#     pickle.dump(obj, file)

with open('missions.dat', 'wb') as file:
    obj = {
        "missions": [['points', 1000, ('5-C', 3), False, False],
                     ['up', 20, ('5-P', 3), '0/20', False],
                     ['down', 40, ('10-P', 6), '0/40', False],
                     ['apple', 100, ('30-C', 10), '0/100', False],
                     ['leaderboard', None, ('30-P', 10), False, False],
                     ['rank', 'prev', ('30-C', 12), False, False],
                     ['speed', 0, ('10-P', 7), False, False],
                     ['st', (1800, 60), ('30-P', 10), False, False]]
    }
    pickle.dump(obj, file)
