import pickle

# with open('userData.dat', 'wb') as file:
#     obj = {'name': 'Divij', 'highscore': 0, 'coin': '0', 'time': ''}
#     pickle.dump(obj, file)

with open('items.dat', 'wb') as file:
    obj = {
        "Themes": {
            "Theme1": {
                'LIGHTBLACK': True,
                'DARKRED': True
            },
            "Theme2": {
                'DARKCYAN': True,
                'ORANGE': True
            },
            "Theme3": {
                'GRAY': True,
                'CADET': True
            },
            "Theme4": {
                'DARKGREEN': True,
                'PINK': True
            },
            "Theme5": {
                'DARKBLUE': True,
                'GOLD': True
            },
            "Theme6": {
                'DARKBROWN': True,
                'LIGHTBROWN': True
            }
        },
        "Powerups": {
            "More Ice Apples": ('6', '12'),
            "More Green Apples": ('8', '12'),
            "High Vel": ('4', '8'),
            "Low Vel": ('3', '8'),
            "Fewer Bombs": ('2', '15'),
            "Teleport": ("8", '40'),
        },
        "Offers": {
            "pseudo": {
                'background': 'Theme1',
                'snake': 'Theme1'
            },
            "2x Coins": {
                '5 min': '4',
                '10 min': '4',
                '30 min': '3'
            },
            "2x Points": {
                '5 min': '4',
                '10 min': '4',
                '30 min': '3'
            },
            "Small Box": {
                '0': '2',
                '1': '2',
                '2': '3',
                '3': '3'
            },
            "Large Box": {
                '0': '2',
                '1': '2',
                '2': '2',
                '3': '2',
                '4': '1',
                '5': '1'
            },
            "Lucky Box": {}
        }
    }
    pickle.dump(obj, file)
with open('missions.dat', 'wb') as file:
    obj = {
        "missions": [['points', 1000, ('5-C', 3), False, False],
                     ['up', 20, ('5-P', 3), '0/20', False],
                     ['down', 40, ('10-P', 6), '0/40', False],
                     ['apple', 100, ('30-C', 10), '0/100', False],
                     ['leaderboard', None, ('30-P', 10), False, False],
                     ['rank', 'prev', ('30-C', 12), False, False],
                     ['speed', 0, ('10-P', 7), False, False],
                     ['st', (1800, 60), ('30-P', 10), False, False]],
        "coins": {
            "2x Coins 5 min": ['6', False, 0],
            "2x Coins 10 min": ['8', False, 0],
            "2x Coins 30 min": ['4', False, 0],
            "2x Points 5 min": ['3', False, 0],
            "2x Points 10 min": ['2', False, 0],
            "2x Points 30 min": ["8", False, 0],
            "coins": False,
            "points": False
        },
    }
    pickle.dump(obj, file)

# import time
# s = time.time()

# with open('daily.dat', 'wb') as file:
#     obj = {'mission': '', 'offer1': '', 'offer2': '', 'time': 0, 'day': (((time.time() + 19800) / 3600) // 24)-1}
#     pickle.dump(obj, file)
