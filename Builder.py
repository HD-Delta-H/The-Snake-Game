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
with open('items.dat', 'rb') as file:
    list_items = pickle.load(file)
    for i, item in enumerate(list_items['Powerups'].items()):
        list_items['Powerups'][item[0]] = ['5', '0']
    with open('items.dat', 'wb') as f:
        pickle.dump(list_items, f)
