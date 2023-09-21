from unione import ScopaGame
from agente import DQNAgent

players = []

N_agenti=10

for i in range(N_agenti):
    players.append({'model': DQNAgent(), 'filename': 'modelli salvati/player-'+str(i)+'.h5', 'punteggio': 0})
    
for i in range(N_agenti):
    players[i]['model'].loadModel(players[i]['filename'])


game = ScopaGame()

# Ogni agente gioca contro tutti gli altri
for i in range(N_agenti):
    for j in range(N_agenti):
        if(j!=i):
            game.agent1 = players[i]['model']
            game.agent2 = players[j]['model']

            reward1, reward2 = game.play()

            # Aggiorna i punteggi totali
            players[i]['punteggio'] += reward1
            players[j]['punteggio'] += reward2
    game.episodio=i
    
# Trova il giocatore con il punteggio più alto
best_player = max(players, key=lambda x:x['punteggio'])

# Salva il modello del giocatore con il punteggio più alto
best_player['model'].saveModel(best_player['filename'])

# Stampa i punteggi finali per riferimento
for player in players:
    print(player['filename'], player['punteggio'])




# game.agent1.loadModel('modelli salvati/model1')
# game.agent2.loadModel('modelli salvati/model2')

# for i in range(1):
#     game.play()
#     game.episodio = i

# game.agent1.saveModel('modelli salvati/model1')
# game.agent2.saveModel('modelli salvati/model2')