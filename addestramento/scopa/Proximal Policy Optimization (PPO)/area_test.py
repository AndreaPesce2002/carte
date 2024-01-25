import itertools
import numpy as np
from stable_baselines3 import PPO
import matplotlib.pyplot as plt
from ambiente import gamePlayer


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

def calcolo_punti(raccolte,raccolte_avv, val=None):
    punteggio=0
    
    _valori={
        '7 bello':0,
        're bello':0,
        'carte':0,
        'denari':0,
        'premiera':0,
        'napoletana':0
    }
    
    #7 bello
    if {'numero': 7, 'seme': 'denari'} in raccolte:
        punteggio+=1
        _valori['7 bello']=1
    
    #re bello
    if {'numero': 10, 'seme':'denari'} in raccolte:
        punteggio+=1
        _valori['re bello']=1

    #carte
    punteggio+=min(len(raccolte)/21,1)
    _valori['carte']=min(len(raccolte)/21,1)
    
    #denari
    denari=0
    for carta in raccolte:
        if carta['seme']=='denari':
            denari+=1
            
    punteggio+=min(denari/6,1)
    
    _valori['denari']=min(denari/6,1)
    
    #premiera
    valori = {'7': 0, '6': 0, '5': 0, '1': 0}
    semi = {'denari': True, 'spade': True, 'bastoni': True, 'coppe': True}

    for valore in valori:
        for carta in raccolte:
            if carta['numero'] == int(valore) and semi[carta['seme']]:
                valori[valore] += 1
                semi[carta['seme']] = False

    tot=0
    if not any(semi.values()):
        tot=valori['7']*7
        tot+=valori['6']*6
        tot+=valori['5']*5
        tot+=valori['1']*5.5
        
    tot1=tot
    
    valori = {'7': 0, '6': 0, '5': 0, '1': 0}
    semi = {'denari': True, 'spade': True, 'bastoni': True, 'coppe': True}

    for valore in valori:
        for carta in raccolte_avv:
            if carta['numero'] == int(valore) and semi[carta['seme']]:
                valori[valore] += 1
                semi[carta['seme']] = False

    tot=0
    if not any(semi.values()):
        tot=valori['7']*7
        tot+=valori['6']*6
        tot+=valori['5']*5
        tot+=valori['1']*5.5
        
    tot2=tot

    ris=(tot1/84)-(tot2/84)
    
    if ris>0:  
        punteggio+=ris
        _valori['premiera']=ris
    
    #napoletana
    if {'numero': 1, 'seme': 'denari'} in raccolte:
        if {'numero': 2, 'seme': 'denari'} in raccolte:
            if {'numero': 3, 'seme': 'denari'} in raccolte:
                punteggio+=1
                _valori['napoletana']=1
                #aggiungi un punto per ogni altro denaro consecutivo
                for num in range(3,10):
                    if {'numero': num, 'seme': 'denari'} in raccolte:
                        punteggio+=1
                        _valori['napoletana']+=1
                    else:
                        break
                    
    if val is None:
        return punteggio
    else:
        return _valori 
    
def gioca(carta_giocata, tavolo):
    raccolte=[]
    if carta_giocata['numero']==1:
        raccolte.append(carta_giocata)
        for carta in tavolo:
            raccolte.append(carta)
        tavolo=[]
    else:
        combinazioni_validi = trova_combinazioni(carta_giocata, tavolo)
        if combinazioni_validi:
            # Prendo la prima combinazione valida (puoi scegliere di fare diversamente)
            combinazioni_validi=combinazioni_validi[0]
            raccolte.append(carta_giocata)
            tavolo_copy = tavolo[:]
            for carta in combinazioni_validi:
                raccolte.append(carta)
                tavolo_copy.remove(carta) 
            tavolo = tavolo_copy
        else: # se non c'è stata corrispondenza, aggiungi la carta giocata al tavolo
            tavolo.append(carta_giocata)
        
        if len(tavolo)==0:
            scope+=1
    
    return calcolo_punti(raccolte,[])
            
def trova_combinazioni(carta_giocata, tavolo):
    # Crea tutte le combinazioni possibili di carte sul tavolo
    combinazioni = [combin for i in range(len(tavolo)) for combin in itertools.combinations(tavolo, i+1)]
    # Trova quelle combinazioni la cui somma è uguale al numero della carta giocata
    validi = [combin for combin in combinazioni if sum(card['numero'] for card in combin) == carta_giocata['numero']]
    return validi

def test1(mano, tavolo, raccolte, raccolte_avv):
    for carta in mano:
        print(gioca(carta, tavolo))

    # Crea un dizionario per tracciare le scelte
    choices = {str(carta): 0 for carta in mano}

    # Esegui le previsioni e conta le scelte
    for i in range(1000):
        action, _ = model.predict(get_observation(mano, tavolo, raccolte, raccolte_avv))
        carta_scelta = mano[np.argmax(action)]
        choices[str(carta_scelta)] += 1
        
    print(choices)

    # Crea un grafico a torta delle scelte
    plt.pie(choices.values(), labels=choices.keys(), autopct='%1.1f%%')
    plt.title('Frequenza delle scelte dell\'agente')
    plt.show()

def test2():
    model = PPO.load('modelli/scopa_ppo')
    game=gamePlayer()
    print('tavolo:', game.tavolo)
    game.done=False
    while not game.done:
        model_p=game.giocatori[game.turno]
        player=game.giocatori[game.turno-1]
        
        action=model.predict(get_observation(model_p.carte, game.tavolo, model_p.raccolte, player.raccolte))[0]
        # Prendiamo solo i primi 'action_posible' numeri
        action_limited = action[:len(model_p.carte)]
        # Troviamo la posizione del valore più grande
        action = np.argmax(action_limited)
        
        print('AI:', model_p.carte[action])
        game.step(action)
        print('tavolo:', game.tavolo)
        game.step(int(input('scegli una carta:'+ str(player.carte)))-1)

# Carica il modello
test2()

# # Definisci le variabili
# mano=[{'numero': 3, 'seme': 'coppe'},{'numero': 7, 'seme': 'bastoni'},{'numero': 5, 'seme': 'spade'}]
# tavolo=[{'numero': 7, 'seme': 'denari'},{'numero': 5, 'seme': 'bastoni'},{'numero': 3, 'seme': 'denari'}]
# raccolte=[]
# raccolte_avv=[]

# test1(mano, tavolo, raccolte, raccolte_avv)

# mano=[{'numero': 8, 'seme': 'coppe'},{'numero': 7, 'seme': 'denari'},{'numero': 2, 'seme': 'spade'}]
# tavolo=[{'numero': 7, 'seme': 'coppe'},{'numero': 2, 'seme': 'bastoni'},{'numero': 8, 'seme': 'denari'}]
# raccolte=[]
# raccolte_avv=[]
# test1(mano, tavolo, raccolte, raccolte_avv)
