import itertools
import numpy as np
from tensorflow import keras
from random import sample

class DQNAgent:
    def __init__(self):
        self.memory = []
        self.q_network = self.build_network()

    def build_network(self):
            model = keras.models.Sequential()
            model.add(keras.layers.Dense(32, activation='relu', input_shape=(10*4*6,)))
            model.add(keras.layers.Dense(32, activation='relu'))
            model.add(keras.layers.Dense(3, activation='linear')) # ora sono 3 i possibili output
            model.compile(loss='mse', optimizer=keras.optimizers.Adam())
            return model

    def select_action(self, state, epsilon):
        if np.random.random() > epsilon*0.1:
            return np.random.choice(3)
        else:
            q_values = self.q_network.predict(state)
            return np.argmax(q_values[0])

    def replay(self, batch_size=10000):
        minibatch =sample(self.memory,min(len(self.memory),batch_size))
            
        for state, action, reward, next_state in minibatch:
            target = self.q_network.predict(state)

            t = self.q_network.predict(next_state)
            target[0][action] = reward + 0.99 * np.amax(t)
                
            self.q_network.fit(state, target, epochs=1, verbose=0)
            
            
    def remember(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))
        
    def saveModel(self, name='model'):
         self.q_network.save(name+'.h5')
         print("Model saved")
         
    def loadModel(self, name='model.h5'):
        try:
            self.q_network = keras.models.load_model(name+'.h5')
            print("Model loaded")
        except:
            print("c'è stato un problemac on il carcamento del modello")

class Alg:
    def __init__(self):
        pass
    
    def replay(self, batch_size=10000):
        pass
            
    def remember(self, state, action, reward, next_state):
        pass
        
    def saveModel(self, name='model'):
        pass
         
    def loadModel(self, name='model.h5'):
        pass
    
    def ele(self,obs):
        # Iniziamo con un array vuoto per le carte raccolte
        raccolte = []
        raccolte_avv = []
        tavolo=[]
        
        carta1=None
        carta2=None
        carta3=None

        # Riportiamo l'osservazione alla sua forma originale
        obs = np.reshape(obs, (10, 4, 6))

        # Cerchiamo tra i sembianti
        for seme_idx, seme in enumerate(['coppe', 'denari', 'spade', 'bastoni']):
            # E tra i numeri
            for numero in range(10):
                # Se il giocatore ha raccolto la carta, aggiungila alle raccolte
                if obs[numero, seme_idx, 4] == 1:
                    raccolte.append({'numero': numero+1, 'seme': seme})
                
                if obs[numero,seme_idx,5]==1:
                    raccolte_avv.append({'numero': numero+1, 'seme': seme})
                    
                if obs[numero,seme_idx,0]==1:
                    carta1={'numero': numero+1, 'seme': seme}
                    
                if obs[numero,seme_idx,1]==1:
                    carta2={'numero': numero+1, 'seme': seme}
                    
                if obs[numero,seme_idx,2]==1:
                    carta3={'numero': numero+1, 'seme': seme}
                
                if obs[numero,seme_idx,3]==1:
                    tavolo.append({'numero': numero+1,'seme': seme})
                    
        return raccolte,raccolte_avv,tavolo,carta1,carta2,carta3
    
    def select_action(self, obs, epsilon):
        
        raccolte,raccolte_avv,tavolo,carta1,carta2,carta3 = self.ele(obs)
        
                
        if carta1 is not None:
            scope1, raccolte1 = self.simulaGIocata(carta1, tavolo, raccolte)
            punteggio1=self.calcolo_punti(raccolte1,raccolte_avv)+scope1
        else:
            punteggio1=-100
        if carta2 is not None:
            scope2, raccolte2 = self.simulaGIocata(carta2, tavolo, raccolte)
            punteggio2=self.calcolo_punti(raccolte2,raccolte_avv)+scope2
        else:
            punteggio2=-100
        if carta3 is not None:
            scope3, raccolte3 = self.simulaGIocata(carta3, tavolo, raccolte)
            punteggio3=self.calcolo_punti(raccolte3,raccolte_avv)+scope3
        else:
            punteggio3=-100
            
        #calcola il ounteggio massimo
        punteggio_max=max(punteggio1,punteggio2,punteggio3)
        
        if punteggio_max==punteggio1:
            return 0
        if punteggio_max==punteggio2:
            return 1
        if punteggio_max==punteggio3:
            return 2

    def trova_combinazioni(self, carta_giocata, tavolo):
        # Crea tutte le combinazioni possibili di carte sul tavolo
        combinazioni = [combin for i in range(len(tavolo)) for combin in itertools.combinations(tavolo, i+1)]
        # Trova quelle combinazioni la cui somma è uguale al numero della carta giocata
        validi = [combin for combin in combinazioni if sum(card['numero'] for card in combin) == carta_giocata['numero']]
        return validi
        
    def simulaGIocata(self,carta_giocata, tavolo, raccolte):
        match_found = False
        scope=0
        if carta_giocata['numero']==1:
            for carta in tavolo:
                raccolte.append(carta)
            tavolo=[]
        else:
            combinazioni_validi = self.trova_combinazioni(carta_giocata, tavolo)
            if combinazioni_validi:
                # Prendo la prima combinazione valida (puoi scegliere di fare diversamente)
                combinazioni_validi=combinazioni_validi[0]
                raccolte.append(carta_giocata)
                for carta in combinazioni_validi:
                    raccolte.append(carta)
                    tavolo.remove(carta) # rimuovi le carte dal tavolo
                    match_found=True
            if not match_found: # se non c'è stata corrispondenza, aggiungi la carta giocata al tavolo
                tavolo.append(carta_giocata)
            
            if len(tavolo)==0:
                scope=1
        
        return scope, raccolte
    
    def calcolo_punti(self, raccolte,raccolte_avv):
        punteggio=0
        
        #7 bello
        if {'numero': 7, 'seme': 'denri'} in raccolte:
            punteggio+=1
        
        #re bello
        if {'numero': 10, 'seme':'denri'} in raccolte:
            punteggio+=1

        #carte
        punteggio=min(len(raccolte)/21,1)
        
        #denari
        denari=0
        for carta in raccolte:
            if carta['seme']=='denari':
                denari+=1
                
        punteggio+=min(denari/5,1)
        
        #premiera
        valori = {'7': 0, '6': 0, '5': 0, 'asso': 0}
        semi = {'denari': True, 'spade': True, 'bastoni': True, 'coppe': True}

        for valore in valori:
            for carta in raccolte:
                if carta['numero'] == valore and semi[carta['seme']]:
                    valori[valore] += 1
                    semi[carta['seme']] = False

        tot=0
        if not any(semi.values()):
            tot=valori['7']*7
            tot+=valori['6']*6
            tot+=valori['5']*5
            tot+=valori['asso']*5.5
            
        tot1=tot
        
        valori = {'7': 0, '6': 0, '5': 0, 'asso': 0}
        semi = {'denari': True, 'spade': True, 'bastoni': True, 'coppe': True}

        for valore in valori:
            for carta in raccolte_avv:
                if carta['numero'] == valore and semi[carta['seme']]:
                    valori[valore] += 1
                    semi[carta['seme']] = False

        tot=0
        if not any(semi.values()):
            tot=valori['7']*7
            tot+=valori['6']*6
            tot+=valori['5']*5
            tot+=valori['asso']*5.5
            
        tot2=tot
    
        if (tot1/84)-(tot2/84)<0:
            punteggio=0
        else:    
            punteggio+=(tot1/84)-(tot2/84)
        
        #napoletana
        if {'numero': 1, 'seme': 'denri'} in raccolte:
            if {'numero': 2, 'seme': 'denri'} in raccolte:
                if {'numero': 3, 'seme': 'denri'} in raccolte:
                    punteggio+=1
                    #aggiungi un punto per ogni altro denaro consecutivo
                    for num in range(3,10):
                        if {'numero': num, 'seme': 'denri'} in raccolte:
                            punteggio+=1
                        else:
                            break

        return punteggio
            
            
            