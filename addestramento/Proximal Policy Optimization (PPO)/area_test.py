import numpy as np
from stable_baselines3 import PPO
import matplotlib.pyplot as plt


def posSeme(seme):
    if seme=='coppe':
        return 0
    elif seme=='denari':
        return 1
    elif seme=='spade':
        return 2
    elif seme=='bastoni':
        return 3

def get_observation(mano, tavolo, raccolte, raccolte_avv):
    # Creiamo un array vuoto di dimensione 10*4*6.
    obs = np.zeros((10, 4, 6), dtype=np.float32)
    
    # carte che il giocatore ha in mano
    for i, carta in enumerate(mano):
        obs[carta['numero']-1, posSeme(carta['seme']), i] = 1
    
    #carte sul tavolo
    for carta in tavolo:
        obs[carta['numero']-1, posSeme(carta['seme']), 3] = 1
        
    #carte raccolte dal giocatore
    for carta in raccolte:
        obs[carta['numero']-1, posSeme(carta['seme']), 4] = 1
    
    #carte raccolte dall'aversario
    for carta in raccolte_avv:
        obs[carta['numero']-1, posSeme(carta['seme']), 5] = 1

    
    obs = obs.flatten()
    obs = np.expand_dims(obs, axis=0)
    
    return obs

# Carica il modello
model = PPO.load('modelli/scopa_ppo')

# Definisci le variabili
mano=[{'numero': 7, 'seme': 'bastoni'},{'numero': 6, 'seme': 'coppe'},{'numero': 5, 'seme': 'denari'}]
tavolo=[{'numero': 7, 'seme': 'denari'},{'numero': 10, 'seme': 'bastoni'},{'numero': 6, 'seme': 'bastoni'}]
raccolte=[]
raccolte_avv=[]

# Crea un dizionario per tracciare le scelte
choices = {0: 0, 1: 0, 2: 0}

# Esegui le previsioni e conta le scelte
for i in range(100):
    action, _ = model.predict(get_observation(mano, tavolo, raccolte, raccolte_avv))
    choices[np.argmax(action)] += 1

# Crea un grafico a barre delle scelte
plt.bar(choices.keys(), choices.values())
plt.xlabel('Scelta')
plt.ylabel('Frequenza')
plt.title('Frequenza delle scelte dell\'agente')
plt.show()