import random
import numpy as np
import torch
from agente import ActorCritic, allenamento
from ambiente import Scopone

num_actions = 10
num_inputs=528


modello_risvegliato1 = ActorCritic(num_inputs, num_actions)  # Assumi che sia la classe del tuo modello
modello_risvegliato1.load_state_dict(torch.load(f'modelli/scopone/miglior_risultato/squadra1/modello_0'))
modello_risvegliato1.eval()


modello_risvegliato2 = ActorCritic(num_inputs, num_actions)  # Assumi che sia la classe del tuo modello
modello_risvegliato1.load_state_dict(torch.load(f'modelli/scopone/miglior_risultato/squadra1/modello_2'))
modello_risvegliato2.eval()

ambiente = Scopone()


def giocoUtente():
    pass
    
def AIvsUman():
    class Man():
        def __init__(self):
            self.vittorie=0
            self.sconfitte=0
            self.ricompensa=0
        def azione(self, stato):
            inp = [0 for _ in range(10)]
            inp[int(input('Scegli una carta: ')) - 1] = 1
            return inp 
        
    class Modello:
        def __init__(self, model):
            self.model = model
            self.vittorie=0
            self.sconfitte=0
            self.ricompensa=0
        
        def azione(self, stato):
                # Converti lo stato in tensori PyTorch e passalo al modello del giocatore corrente
                stato_tensor = torch.from_numpy(stato).float().unsqueeze(0)
                action_probs, state_value = self.model(stato_tensor)

                # Assicurati che action_probs abbia la dimensione corretta (10)
                action_probs = action_probs.view(-1, 10)

                # Converti le probabilità di azione in numpy per passarle all'ambiente
                azione_numpy = action_probs.squeeze().detach().cpu().numpy()
                
                return azione_numpy
        
    modelli=[Man(), Modello(modello_risvegliato1), Man(), Modello(modello_risvegliato2)]
    numero_episodi=10000
    
    for episodio in range(numero_episodi):
        stato = ambiente.reset()
        done = False
        turno = 0  # Inizia dal primo giocatore
        gamma=0.8
            
        while not done:# Esegui l'azione nell'ambiente passando l'array completo delle probabilità
            print('tavolo:',ambiente.tavolo)
            print('mano:', ambiente.giocatori[ambiente.turno].carte)
            nuovo_stato, ricompensa, done,punteggio_reale = ambiente.step(modelli[turno].azione(stato))
            
            modelli[turno].ricompensa=punteggio_reale

            # Aggiorna lo stato per il prossimo ciclo
            stato = nuovo_stato

            # Passa al prossimo giocatore o ricomincia dal primo se siamo all'ultimo
            turno = (turno + 1) % 4
        
        # Calcola la vittoria del modello
        squadrea1=modelli[turno].ricompensa
        squadrea2=modelli[(turno + 2) % 4].ricompensa
        
        if squadrea1 > squadrea2:
            modelli[turno].vittorie += 1
            modelli[(turno + 2) % 4].sconfitte+=1
        else:
            modelli[turno].sconfitte += 1
            modelli[(turno + 2) % 4].vittorie+=1

        #sposta i modellli
        modelli = modelli[1:] +modelli[:1]
        
        print(f'partita conclsa: {squadrea1}-{squadrea2} \n addestramento comletato al', str((episodio*100)/numero_episodi)+'%')
    
    #stampa la percentuale di vittorie
    print('fine simulazione')

    vittorie_totali = [modello.vittorie for modello in modelli]
    media_vittorie = np.mean(vittorie_totali)
    mediana_vittorie = np.median(vittorie_totali)
    deviazione_standard_vittorie = np.std(vittorie_totali)

    for i, modello in enumerate(modelli):
        partite_giocate = modello.vittorie + modello.sconfitte
        percentuale_vittorie = (modello.vittorie * 100) / partite_giocate if partite_giocate > 0 else 0
        print(f"squadrea: {i+1}:")
        print(f"    vittorie e sconfittte: {modello.vittorie} vittorie e {modello.sconfitte} sconfitte.")
        print(f"    percentuale vittorie: {percentuale_vittorie:.2f}%")
        print(f"    media vittorie: {media_vittorie:.2f}")
        print(f"    mediana vittorie: {mediana_vittorie:.2f}")
        print(f"    deviazione standard vittorie: {deviazione_standard_vittorie:.2f}")
        if i==1:
            break

def test1():
    #carte dell'avversario: 7 spade, 7 bastoni
    #certe tavolo: 6,7,2,3 denari
    #carte mano: 7 bello, 5, 3 denari
    #carte raccolte: asso denari, 2 denari
    ambiente.tavolo=[{}]

#AIvsUman()

allenamento()