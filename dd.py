import pickle
with open('data/bin/userData.dat', 'rb') as file:
    d = pickle.load(file)
    with open('data/bin/userData.dat', 'wb') as file:
        d['coin'] = '799'
        pickle.dump(d, file)
