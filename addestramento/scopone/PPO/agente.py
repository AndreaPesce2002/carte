import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from ambiente import Scopone

class ActorCritic(nn.Module):
    def __init__(self, num_inputs, num_actions):
        super(ActorCritic, self).__init__()
        # Esempio di strato condiviso
        self.shared_layers = nn.Sequential(
            nn.Linear(num_inputs, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU()
        )
        # L'Actor decide le azioni da prendere
        self.actor = nn.Linear(128, num_actions)
        # Il Critic valuta lo stato attuale
        self.critic = nn.Linear(128, 1)

    def forward(self, x):
        x = self.shared_layers(x)
        action_probs = torch.softmax(self.actor(x), dim=-1)
        state_values = self.critic(x)
        return action_probs, state_values

class Modello:
    def __init__(self, model=None):
        if model is not None:
            self.model = model
        else:
            num_actions = 10
            num_inputs=528
            self.model = ActorCritic(num_inputs, num_actions)
        self.optimizer_actor = optim.Adam(self.model.actor.parameters(), lr=1e-3)
        self.optimizer_critic = optim.Adam(self.model.critic.parameters(), lr=1e-3)
        self.ricompensa=0
        self.punteggi=[]
    
    def azione(self, stato):
            # Converti lo stato in tensori PyTorch e passalo al modello del giocatore corrente
            stato_tensor = torch.from_numpy(stato).float().unsqueeze(0)
            action_probs, state_value = self.model(stato_tensor)

            # Assicurati che action_probs abbia la dimensione corretta (10)
            action_probs = action_probs.view(-1, 10)

            # Converti le probabilità di azione in numpy per passarle all'ambiente
            azione_numpy = action_probs.squeeze().detach().cpu().numpy()
            
            return azione_numpy

def allenamento(numero_episodi=1000):

    #inizio del programma    
    num_actions = 10
    num_inputs=528

    migliorModello=False


    # Istanzia l'ambiente e il modello
    ambiente = Scopone()

    modelli=[Modello(),Modello(),Modello(),Modello()]

    try:
        if migliorModello:
            modello_risvegliato = ActorCritic(num_inputs, num_actions)  # Assumi che sia la classe del tuo modello
            modello_risvegliato.load_state_dict(torch.load(f'modelli/scopone/modello_vincente_10k.pth'))
            modello_risvegliato.eval()
            
            modelli=[Modello(modello_risvegliato),Modello(modello_risvegliato),Modello(modello_risvegliato),Modello(modello_risvegliato)]
    except:
        print('non è stato possibile importare il modello migliore')

    # Ciclo di addestramento
    for episodio in range(numero_episodi):
        stato = ambiente.reset()
        done = False
        turno = 0  # Inizia dal primo giocatore
        gamma=0.8
        
        while not done:
            # Converti lo stato in tensori PyTorch e passalo al modello del giocatore corrente
            stato_tensor = torch.from_numpy(stato).float().unsqueeze(0)
            action_probs, state_value = modelli[turno].model(stato_tensor)

            # Assicurati che action_probs abbia la dimensione corretta (10)
            action_probs = action_probs.view(-1, 10)

            # Campiona un'azione dalle probabilità di azione
            distribuzione = torch.distributions.Categorical(action_probs)
            azione = distribuzione.sample()
            log_prob = distribuzione.log_prob(azione)

            # Converti le probabilità di azione in numpy per passarle all'ambiente
            azione_numpy = action_probs.squeeze().detach().cpu().numpy()

            # Esegui l'azione nell'ambiente passando l'array completo delle probabilità
            nuovo_stato, ricompensa, done,punteggio_reale = ambiente.step(azione_numpy)
            
            
            #addestramento del modello
            # Calcola il vantaggio
            vantaggio = ricompensa + (0 if done else gamma * modelli[turno].model(torch.from_numpy(nuovo_stato).float().unsqueeze(0))[1]) - state_value

            # Calcola le perdite per l'attore e il critico
            perdita_attore = -(log_prob * vantaggio.detach())  # Usa il vantaggio
            perdita_critico = F.smooth_l1_loss(state_value, vantaggio.detach())


            # Aggiorna i pesi del modello del giocatore corrente
            # Sfruttiamo il fatto che possiamo sommare le perdite prima di fare un unico backward
            # Questo conserva il grafico computazionale
            perdita_totale = perdita_attore + perdita_critico
            modelli[turno].optimizer_actor.zero_grad()
            modelli[turno].optimizer_critic.zero_grad()
            perdita_totale.backward()  # Facciamo un solo passaggio all'indietro
            modelli[turno].optimizer_actor.step()
            modelli[turno].optimizer_critic.step()

            modelli[turno].ricompensa=punteggio_reale

            # Aggiorna lo stato per il prossimo ciclo
            stato = nuovo_stato

            # Passa al prossimo giocatore o ricomincia dal primo se siamo all'ultimo
            turno = (turno + 1) % 4
        
        
        # Calcola la vittoria del modello
        squadrea1=modelli[turno].ricompensa
        squadrea2=modelli[(turno + 2) % 4].ricompensa
        
        modelli[turno].punteggi.append(squadrea1)
        modelli[(turno + 2) % 4].punteggi.append(squadrea2)

        #sposta i modellli
        modelli = modelli[1:] +modelli[:1]

        
        print(f'partita conclsa: {squadrea1}-{squadrea2} \n addestramento comletato al', str((episodio*100)/numero_episodi)+'%')

    #stampa la percentuale di vittorie
    print('fine simulazione')

    punteggi_totali = [modello.punteggi for modello in modelli]
    media_punteggi = np.mean(punteggi_totali)
    mediana_punteggi = np.median(punteggi_totali)
    deviazione_standard_punteggi = np.std(punteggi_totali)

    for i, modello in enumerate(modelli):
        partite_giocate = modello.punteggi
        #percentuale_punteggi = (modello.punteggi * 100) / partite_giocate if partite_giocate > 0 else 0
        print(f"squadrea: {i+1}:")
        #print(f"    percentuale punteggi: {percentuale_punteggi:.2f}%")
        print(f"    media punteggi: {media_punteggi:.2f}")
        print(f"    mediana punteggi: {mediana_punteggi:.2f}")
        print(f"    deviazione standard punteggi: {deviazione_standard_punteggi:.2f}")
        if i==1:
            break

    # Prima determiniamo quale modello ha la percentuale di punteggi più alta
    miglior_punteggio = -float('inf')
    modello_vincente = None
    indice_modello_vincente = -1

    # for i in range(4):
    #     partite_giocate = modelli[i].punteggi
    #     percentuale_punteggi = (modelli[i].punteggi * 100) / partite_giocate if partite_giocate > 0 else 0
    #     if percentuale_punteggi > miglior_punteggio:
    #         miglior_punteggio = percentuale_punteggi
    #         modello_vincente = modelli[i]
    #         indice_modello_vincente = i

    # # Assicurati che le cartelle esistano o creale
    # os.makedirs('modelli/scopone', exist_ok=True)
    # os.makedirs('modelli/scopone/squadra1', exist_ok=True)
    # os.makedirs('modelli/scopone/squadra2', exist_ok=True)

    # # Ora che abbiamo il modello vincente, salviamolo per l'eternità (o finché non viene sovrascritto)
    # if modello_vincente is not None:
        
    #     #salva i modelli
    #     for i in range(4):
    #         if i%2==0:
    #             torch.save(modelli[0].model.state_dict(), f'modelli/scopone/squadra1/modello_{i}')
    #         else:
    #             torch.save(modelli[0].model.state_dict(), f'modelli/scopone/squadra2/modello_{i}')
        
    # else:
    #     print("Sembra che non ci siano modelli da salvare. Assicurati che la competizione sia iniziata!")

    # Se in futuro desideri risvegliare il modello vincente dal suo sonno magico, ecco come potresti farlo:
    # modello_risvegliato = ActorCritic(num_inputs, num_actions)  # Assumi che sia la classe del tuo modello
    # modello_risvegliato.load_state_dict(torch.load(f'modello_vincente_{indice_modello_vincente}.pth'))
    # modello_risvegliato.eval()
