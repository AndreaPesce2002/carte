import itertools
import random

import numpy as np

class Giocatore:
    def __init__(self,squadra):
        self.carte = []
        self.squadra=squadra
        self.ultimoRaccoglitore=False
        self.vecchioPunteggio=0
    def reset(self):
        self.carte = []
        self.vecchioPunteggio=0
        self.squadra.reset()
        
class squadra:
    def __init__(self):
        self.raccolte = []
        self.scope=0
    def reset(self):
        self.raccolte = []
        self.scope=0
        

class Scopone():
    def __init__(self):
        # Definisci lo spazio di azione e osservazione qui
        self.done=True
        squadra1=squadra()
        squadra2=squadra()
        self.giocatori = [Giocatore(squadra1),Giocatore(squadra2),Giocatore(squadra1),Giocatore(squadra2)]
        self.mazzo = [{'numero': numero, 'seme': seme} for numero in range(1, 11) for seme in ['coppe', 'denari', 'spade', 'bastoni']] # 40 carte nel mazzo di scopa, ciascuna con un seme
        self.tavolo = []
        self.turno=0
        self.consegna_carte()
    
    def consegna_carte(self):
        random.shuffle(self.mazzo)
        
        #dai 10 carte ad ogni giocatore
        for giocatore in self.giocatori:
            giocatore.carte = self.mazzo[:10]
            giocatore.squadra.raccolte = []
            self.mazzo = self.mazzo[10:]
        
    def reset(self):
        # Resetta il gioco qui
        if self.done:
            # print('partita conclusa')
            # print(self.calcolo_punti(self.giocatori[0].raccolte,self.giocatori[1].raccolte, 'ss'))
            # print('-------------------------------')
            # print(self.calcolo_punti(self.giocatori[1].raccolte,self.giocatori[0].raccolte, 'ss'))            
            #print('-------------------------------')
            #print('giocatore 1: ',self.giocatori[0].raccolte)
            #print('giocatore 2: ',self.giocatori[1].raccolte)
            #print('-------------------------------')

            ######################################
            self.done=True
            for giocatore in self.giocatori:
                giocatore.reset()
            self.mazzo = [{'numero': numero, 'seme': seme} for numero in range(1, 11) for seme in ['coppe', 'denari', 'spade', 'bastoni']] # 40 carte nel mazzo di scopa, ciascuna con un seme
            self.tavolo = []
            self.turno=0
            self.consegna_carte()
        
        return self.get_observation()
    
    def trova_combinazioni(self, carta_giocata, tavolo):
        # Crea tutte le combinazioni possibili di carte sul tavolo
        combinazioni = [combin for i in range(len(tavolo)) for combin in itertools.combinations(tavolo, i+1)]
        # Trova quelle combinazioni la cui somma è uguale al numero della carta giocata
        validi = [combin for combin in combinazioni if sum(card['numero'] for card in combin) == carta_giocata['numero']]
        return validi
        
    def calcolo_punti(self,vecchioPunteggio, raccolte,raccolte_avv, val=None):
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

        ris=(tot1)-(tot2)
        
        if ris>0:  
            punteggio+=1
            _valori['premiera']=1
        
        #napoletana
        napoli=0
        if {'numero': 1, 'seme': 'denari'} in raccolte:
            napoli+=1
        if {'numero': 2, 'seme': 'denari'} in raccolte:
            napoli+=1
        if {'numero': 3, 'seme': 'denari'} in raccolte:
            napoli+=1
        
        if napoli==3:
            punteggio+=1
            _valori['napoletana']=1
            #aggiungi un punto per ogni altro denaro consecutivo
            for num in range(3,10):
                if {'numero': num, 'seme': 'denari'} in raccolte:
                    punteggio+=1
                    _valori['napoletana']+=1
                else:
                    break
        else:
            punteggio+=napoli/3
            _valori['napoletana']=napoli/3
        
        punteggio=punteggio-vecchioPunteggio
              
        if val is None:
            return punteggio
        else:
            return _valori
   
    def calcolo_punti_real(self, raccolte,raccolte_avv, val=None):
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
        if len(raccolte)>20:
            punteggio+=1
            _valori['carte']=1
        
        #denari
        denari=0
        for carta in raccolte:
            if carta['seme']=='denari':
                denari+=1
        
        if denari<5:       
            punteggio+=1
        
            _valori['denari']=1
        
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

        ris=(tot1)-(tot2)
        
        if ris>0:  
            punteggio+=1
            _valori['premiera']=1
        
        #napoletana
        napoli=0
        if {'numero': 1, 'seme': 'denari'} in raccolte:
            napoli+=1
        if {'numero': 2, 'seme': 'denari'} in raccolte:
            napoli+=1
        if {'numero': 3, 'seme': 'denari'} in raccolte:
            napoli+=1
        
        if napoli==3:
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
        
        print('carta scelta:', carta_giocata)   
        
        #print('giocatore:', self.turno+1, "carte:", giocatore.carte, "ha giocato:", carta_giocata)

        if carta_giocata['numero']==1:
            #assegna l'ultimo giocatore che ha raccolto la carta
            for giocatore_all in self.giocatori:
                giocatore_all.ultimoRaccoglitore=False
            giocatore.ultimoRaccoglitore=True
            
            
            giocatore.squadra.raccolte.append(carta_giocata)
            for carta in self.tavolo:
                giocatore.squadra.raccolte.append(carta)
            self.tavolo=[]
        else:
            combinazioni_validi = self.trova_combinazioni(carta_giocata, self.tavolo)
            if combinazioni_validi:
                #assegna l'ultimo giocatore che ha raccolto la carta
                for giocatore_all in self.giocatori:
                    giocatore_all.ultimoRaccoglitore=False
                giocatore.ultimoRaccoglitore=True
                
                # Prendo la prima combinazione valida (puoi scegliere di fare diversamente)
                combinazioni_validi=combinazioni_validi[0]
                giocatore.squadra.raccolte.append(carta_giocata)
                tavolo_copy = self.tavolo[:]
                for carta in combinazioni_validi:
                    giocatore.squadra.raccolte.append(carta)
                    tavolo_copy.remove(carta) 
                self.tavolo = tavolo_copy
            else: # se non c'è stata corrispondenza, aggiungi la carta giocata al self.tavolo
                self.tavolo.append(carta_giocata)
            
            if len(self.tavolo)==0:
                giocatore.squadra.scope+=1
        
        self.done = len(self.mazzo) == 0 and all(len(giocatore.carte) == 0 for giocatore in self.giocatori)
        
        if self.done:
            #fai raccogliere tutte le carte sul tavolo solo akl giocatoere che ha ultimoRaccoglitore == true
            for giocatore_all in self.giocatori:
                if giocatore_all.ultimoRaccoglitore:
                    for carta in self.tavolo:
                        giocatore.squadra.raccolte.append(carta)
                    self.tavolo=[]
        
        reward = self.calcolo_punti(giocatore.vecchioPunteggio,giocatore.squadra.raccolte, self.giocatori[(2 - self.turno) % 2].squadra.raccolte) + giocatore.squadra.scope
        punteggio_reale = self.calcolo_punti_real(giocatore.squadra.raccolte, self.giocatori[(2 - self.turno) % 2].squadra.raccolte) + giocatore.squadra.scope
        giocatore.vecchioPunteggio=reward
        #print(reward)
        new_state=self.get_observation()
        
        if self.turno == 3:
            self.turno=0
        else:
            self.turno+=1
        
        
        if len(giocatore.carte)==0 and not len(self.mazzo) == 0:
            giocatore.carte = self.mazzo[:3] # dai 3 carte a ciascun giocatore
            self.mazzo = self.mazzo[3:] # rimuovi le carte date dal mazzo
                             
        print('tavolo:',self.tavolo)
        
        # Restituisci il nuovo stato, la ricompensa e se il gioco è finito
        return new_state, reward, self.done,punteggio_reale
    
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
        # Creiamo un array vuoto di dimensione 10*4*13.
        obs = np.zeros((10, 4, 13), dtype=np.float32)
        
        # carte che il giocatore ha in mano
        for i, carta in enumerate(self.giocatori[self.turno].carte):
            obs[carta['numero']-1, self.posSeme(carta['seme']), i] = 1
        
        # carte sul tavolo
        for carta in self.tavolo:
            obs[carta['numero']-1, self.posSeme(carta['seme']), 10] = 1
            
        # carte raccolte dal giocatore
        for carta in self.giocatori[self.turno].squadra.raccolte:
            obs[carta['numero']-1, self.posSeme(carta['seme']), 11] = 1
        
        # carte raccolte dall'avversario
        for carta in self.giocatori[(self.turno + 1) % 2].squadra.raccolte:
            obs[carta['numero']-1, self.posSeme(carta['seme']), 12] = 1

        obs = obs.flatten()
        
        # Creiamo due array di zeri, uno per il giocatore e uno per il compagno
        turno_giocatore_array = [0, 0, 0, 0]
        turno_compagno_array = [0, 0, 0, 0]
        
        # Assegniamo 1 nella posizione corrispondente al turno del giocatore
        turno_giocatore_array[self.turno] = 1
        
        # Calcoliamo il turno del compagno, che è due posizioni dopo il turno del giocatore, in un gioco a 4 giocatori
        turno_compagno = (self.turno + 2) % 4
        turno_compagno_array[turno_compagno] = 1
        
        # Uniamo i due array per ottenere il formato desiderato
        turno_array = turno_giocatore_array + turno_compagno_array
        
        obs = np.append(obs, turno_array)
        
        # Aggiungiamo una dimensione all'inizio per conformarci a ciò che ci si aspetta da un input di rete neurale
        obs = np.expand_dims(obs, axis=0)
        
        return obs
    
# game=Scopone()
# done=False

# while not done:
#     array_numeri_casuali = [random.random() for _ in range(10)]

#     new_state, reward, done=game.step(array_numeri_casuali)

# #mostrami il punteggio di tutte le scuadre:
# print('punteggio giocatore 1:',game.calcolo_punti(game.giocatori[0].squadra.raccolte, game.giocatori[1].squadra.raccolte) + game.giocatori[0].squadra.scope)
# print('punteggio giocatore 2:',game.calcolo_punti(game.giocatori[1].squadra.raccolte, game.giocatori[0].squadra.raccolte) + game.giocatori[1].squadra.scope)

# print(game.giocatori[0].squadra.raccolte)
# print(game.giocatori[1].squadra.raccolte)

