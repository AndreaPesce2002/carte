import itertools
import random
import gym
import numpy as np
from stable_baselines3 import PPO

class Giocatore:
    def __init__(self):
        self.carte = []
        self.raccolte = []
        self.scope=0
    def reset(self):
        self.carte = []
        self.raccolte = []
        self.scope=0

# Creiamo un ambiente molto semplice che rappresenta una partita di Scopa
class SimpleScopaEnv(gym.Env):
    def __init__(self):
        super(SimpleScopaEnv, self).__init__()
        # Definisci lo spazio di azione e osservazione qui
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(280,), dtype=np.float32)
        self.action_space = gym.spaces.Box(0, 1, (3,))
        self.done=True
        self.giocatori = [Giocatore(),Giocatore()]
        self.mazzo = [{'numero': numero, 'seme': seme} for numero in range(1, 11) for seme in ['coppe', 'denari', 'spade', 'bastoni']] # 40 carte nel mazzo di scopa, ciascuna con un seme
        self.tavolo = []
        self.turno=0
        self.reset()

    def consegna_carte(self):
        random.shuffle(self.mazzo)
        for giocatore in self.giocatori:
            giocatore.carte = self.mazzo[:3] # dai 3 carte a ciascun giocatore
            self.mazzo = self.mazzo[3:] # rimuovi le carte date dal mazzo
        self.tavolo = self.mazzo[:4] # metti 4 carte sul tavolo
        self.mazzo = self.mazzo[4:] # rimuovi le carte messe sul tavolo dal mazzo
    
    def trova_combinazioni(self, carta_giocata, tavolo):
        # Crea tutte le combinazioni possibili di carte sul tavolo
        combinazioni = [combin for i in range(len(tavolo)) for combin in itertools.combinations(tavolo, i+1)]
        # Trova quelle combinazioni la cui somma è uguale al numero della carta giocata
        validi = [combin for combin in combinazioni if sum(card['numero'] for card in combin) == carta_giocata['numero']]
        return validi
        
    def calcolo_punti(self, raccolte,raccolte_avv, val=None):
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
        punteggio=min(len(raccolte)/21,1)
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
    
    def step(self, action_originale):
        # Implementa la logica del tuo gioco qui
        giocatore = self.giocatori[self.turno]
        
        # Prendiamo solo i primi 'action_posible' numeri
        action_limited = action_originale[:len(giocatore.carte)]

        # Troviamo la posizione del valore più grande
        action = np.argmax(action_limited)
            
        carta_giocata = giocatore.carte.pop(action) # il giocatore gioca una carta
        
        #print('giocatore:', self.turno, "carte:", giocatore.carte, "ha giocato:", carta_giocata)

        if carta_giocata['numero']==1:
            giocatore.raccolte.append(carta_giocata)
            for carta in self.tavolo:
                giocatore.raccolte.append(carta)
            self.tavolo=[]
        else:
            combinazioni_validi = self.trova_combinazioni(carta_giocata, self.tavolo)
            if combinazioni_validi:
                # Prendo la prima combinazione valida (puoi scegliere di fare diversamente)
                combinazioni_validi=combinazioni_validi[0]
                giocatore.raccolte.append(carta_giocata)
                tavolo_copy = self.tavolo[:]
                for carta in combinazioni_validi:
                    giocatore.raccolte.append(carta)
                    tavolo_copy.remove(carta) 
                self.tavolo = tavolo_copy
            else: # se non c'è stata corrispondenza, aggiungi la carta giocata al self.tavolo
                self.tavolo.append(carta_giocata)
            
            if len(self.tavolo)==0:
                giocatore.scope+=1
        
        self.done = len(self.mazzo) == 0 and len(self.giocatori[0].carte)==0 and len(self.giocatori[1].carte)==0
        
        if self.done:
            for carta in self.tavolo:
                giocatore.raccolte.append(carta)
            self.tavolo=[]
        
        reward=self.calcolo_punti(giocatore.raccolte,self.giocatori[1-self.turno].raccolte)+giocatore.scope
        
        new_state=self.get_observation()
        
        if self.turno == 0:
            self.turno=1
        else:
            self.turno=0
        
        if np.argmax(action_originale)>len(giocatore.carte):
            reward = -1
        
        if len(giocatore.carte)==0 and not len(self.mazzo) == 0:
            giocatore.carte = self.mazzo[:3] # dai 3 carte a ciascun giocatore
            self.mazzo = self.mazzo[3:] # rimuovi le carte date dal mazzo
                                
        #print('tavolo:',self.tavolo)
        
        # Restituisci il nuovo stato, la ricompensa e se il gioco è finito
        return new_state, reward, self.done, {}
    

    def reset(self):
        # Resetta il gioco qui
        if self.done:
            print('partita conclusa')
            print(self.calcolo_punti(self.giocatori[0].raccolte,self.giocatori[1].raccolte, 'ss'))
            print('-------------------------------')
            print(self.calcolo_punti(self.giocatori[1].raccolte,self.giocatori[0].raccolte, 'ss'))            
            print('-------------------------------')
            #print('giocatore 1: ',self.giocatori[0].raccolte)
            #print('giocatore 2: ',self.giocatori[1].raccolte)
            #print('-------------------------------')

            ######################################
            self.observation_space = gym.spaces.Box(low=0, high=1, shape=(240,), dtype=np.float32)
            self.action_space = gym.spaces.Box(0, 1, (3,))
            self.done=True
            for giocatore in self.giocatori:
                giocatore.reset()
            self.mazzo = [{'numero': numero, 'seme': seme} for numero in range(1, 11) for seme in ['coppe', 'denari', 'spade', 'bastoni']] # 40 carte nel mazzo di scopa, ciascuna con un seme
            self.tavolo = []
            self.turno=0
            self.consegna_carte()
        
        return self.get_observation()
    
    
    def posSeme(self,seme):
        if seme=='coppe':
            return 0
        elif seme=='denari':
            return 1
        elif seme=='spade':
            return 2
        elif seme=='bastoni':
            return 3

    def get_observation(self):
        # Creiamo un array vuoto di dimensione 10*4*6.
        obs = np.zeros((10, 4, 6), dtype=np.float32)
        
        # carte che il giocatore ha in mano
        for i, carta in enumerate(self.giocatori[self.turno].carte):
            obs[carta['numero']-1, self.posSeme(carta['seme']), i] = 1
        
        #carte sul tavolo
        for carta in self.tavolo:
            obs[carta['numero']-1, self.posSeme(carta['seme']), 3] = 1
            
        #carte raccolte dal giocatore
        for carta in self.giocatori[self.turno].raccolte:
            obs[carta['numero']-1, self.posSeme(carta['seme']), 4] = 1
        
        #carte raccolte dall'aversario
        for carta in self.giocatori[1-self.turno].raccolte:
            obs[carta['numero']-1, self.posSeme(carta['seme']), 5] = 1

        
        obs = obs.flatten()
        obs = np.expand_dims(obs, axis=0)
        
        return obs
        