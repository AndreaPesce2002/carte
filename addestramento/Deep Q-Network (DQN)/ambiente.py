import itertools
import random
import numpy as np

class Giocatore:
    def __init__(self, model):
        self.model = model
        self.carte = []
        self.raccolte = []
        self.scope=0
    def reset(self):
        self.carte = []
        self.raccolte = []
        self.scope=0

class Scopa:
    def __init__(self, giocatore1, giocatore2):
        self.giocatori = [Giocatore(giocatore1), Giocatore(giocatore2)]
        self.mazzo = [{'numero': numero, 'seme': seme} for numero in range(1, 10) for seme in ['coppe', 'denari', 'spade', 'bastoni']] # 40 carte nel mazzo di scopa, ciascuna con un seme
        self.tavolo = []
        self.turno=0
        self.AvviaPartita()
        
        
    def mescola_mazzo(self):
        random.shuffle(self.mazzo)

    def da_carte(self):
        for giocatore in self.giocatori:
            giocatore.carte = self.mazzo[:3] # dai 3 carte a ciascun giocatore
            self.mazzo = self.mazzo[3:] # rimuovi le carte date dal mazzo

    def metti_carte_sul_tavolo(self):
        self.tavolo = self.mazzo[:4] # metti 4 carte sul tavolo
        self.mazzo = self.mazzo[4:] # rimuovi le carte messe sul tavolo dal mazzo
        
    def trova_combinazioni(self, carta_giocata, tavolo):
        # Crea tutte le combinazioni possibili di carte sul tavolo
        combinazioni = [combin for i in range(len(tavolo)) for combin in itertools.combinations(tavolo, i+1)]
        # Trova quelle combinazioni la cui somma è uguale al numero della carta giocata
        validi = [combin for combin in combinazioni if sum(card['numero'] for card in combin) == carta_giocata['numero']]
        return validi
    
    def calcolo_punti(self):
        raccolte=self.giocatori[self.turno].raccolte
        punteggio=0
        
        #7 bello
        if {'numero': 7, 'seme': 'denri'} in raccolte:
            punteggio+=1
        
        #re bello
        if {'numero': 10, 'seme':'denri'} in raccolte:
            punteggio+=1

        #carte
        punteggio=len(raccolte)/21
        
        #scope
        punteggio+=self.giocatori[self.turno].scope
        
        #denari
        denari=0
        for carta in raccolte:
            if carta['seme']=='denari':
                denari+=1
                
        punteggio+=denari/5
        
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
        
        if self.turno==1:
            raccolte2=self.giocatori[0].raccolte
        else:
            raccolte2=self.giocatori[1].raccolte
        
        valori = {'7': 0, '6': 0, '5': 0, 'asso': 0}
        semi = {'denari': True, 'spade': True, 'bastoni': True, 'coppe': True}

        for valore in valori:
            for carta in raccolte2:
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

    def gioca_turno(self, action):
        giocatore = self.giocatori[self.turno]
        
        if action > len(giocatore.carte) - 1:
            action = 0
            
        carta_giocata = giocatore.carte.pop(action) # il giocatore gioca una carta
        match_found = False
        
        print('giocatore:', self.turno, "ha giocato:", carta_giocata)

        if carta_giocata['numero']==1:
            for carta in self.tavolo:
                giocatore.raccolte.append(carta)
            self.tavolo=[]
        else:
            combinazioni_validi = self.trova_combinazioni(carta_giocata, self.tavolo)
            if combinazioni_validi:
                # Prendo la prima combinazione valida (puoi scegliere di fare diversamente)
                combinazioni_validi=combinazioni_validi[0]
                giocatore.raccolte.append(carta_giocata)
                for carta in combinazioni_validi:
                    giocatore.raccolte.append(carta)
                    self.tavolo.remove(carta) # rimuovi le carte dal tavolo
                    match_found=True
            if not match_found: # se non c'è stata corrispondenza, aggiungi la carta giocata al tavolo
                self.tavolo.append(carta_giocata)
            
            if len(self.tavolo)==0:
                giocatore.scope+=1
                
        if len(giocatore.carte)==0:
            giocatore.carte = self.mazzo[:3] # dai 3 carte a ciascun giocatore
            self.mazzo = self.mazzo[3:] # rimuovi le carte date dal mazzo
            
        if self.turno == 0:
            self.turno=1
        else:
            self.turno=0
        
        if action>len(giocatore.carte):
            reward = -100
        else:
            reward = self.calcolo_punti()
        
        done = len(self.mazzo) == 0

        
        print('tavolo:',self.tavolo)

        return self.last_state, reward, done
        
                
    def AvviaPartita(self):
        for giocatore in self.giocatori:
            giocatore.reset()
        self.mazzo = [{'numero': numero, 'seme': seme} for numero in range(1, 10) for seme in ['coppe', 'denari', 'spade', 'bastoni']] # 40 carte nel mazzo di scopa, ciascuna con un seme
        self.tavolo = []
        self.turno=0
        self.mescola_mazzo()
        self.da_carte()
        self.metti_carte_sul_tavolo()

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
            obs[carta['numero'], self.posSeme(carta['seme']), i] = 1
        
        #carte sul tavolo
        for carta in self.tavolo:
            obs[carta['numero'], self.posSeme(carta['seme']), 3] = 1
            
        #carte raccolte dal giocatore
        for carta in self.giocatori[self.turno].raccolte:
            obs[carta['numero'], self.posSeme(carta['seme']), 4] = 1
        
        #carte raccolte dall'aversario
        if self.turno==0:
            for carta in self.giocatori[1].raccolte:
                obs[carta['numero'], self.posSeme(carta['seme']), 5] = 1
        else:
            for carta in self.giocatori[0].raccolte:
                obs[carta['numero'], self.posSeme(carta['seme']), 5] = 1
        
        obs = obs.flatten()
        obs = np.expand_dims(obs, axis=0)
        
        return obs

