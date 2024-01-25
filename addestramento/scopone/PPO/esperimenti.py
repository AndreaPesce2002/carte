import torch
from agente import ActorCritic
from ambiente import Scopone

print('hello')

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
    
def AIvsRandom():
    pass

def test1():
    #carte dell'avversario: 7 spade, 7 bastoni
    #certe tavolo: 6,7,2,3 denari
    #carte mano: 7 bello, 5, 3 denari
    #carte raccolte: asso denari, 2 denari
    ambiente.tavolo=[{}]
    