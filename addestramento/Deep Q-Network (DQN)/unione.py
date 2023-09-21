from ambiente import Scopa
from agente import DQNAgent,Alg

class ScopaGame:
    def __init__(self):
        self.agent1 = DQNAgent()
        self.agent2 = DQNAgent()
        self.episodio=1
        self.env = Scopa(self.agent1,self.agent2)
        self.state = self.env.get_observation()  # Salva lo stato iniziale

    def play(self):
        done = False
        self.env.AvviaPartita()
        while not done:
            action1 = self.agent1.select_action(self.state,self.episodio)
            next_state, reward1, done = self.env.gioca_turno(action1)
            self.agent1.remember(self.state, action1, reward1, next_state)
            self.state = next_state
            if done:
                break

            action2 = self.agent2.select_action(self.state,self.episodio)
            next_state, reward2, done= self.env.gioca_turno(action2)
            self.agent2.remember(self.state, action2, reward2, next_state)
            self.state = next_state
            if done:
                break
        
        self.agent1.replay()
        self.agent2.replay()
        
        return reward1, reward2
            

class ScopaAIVsAlg:
    def __init__(self):
        self.agent1 = DQNAgent()
        self.agent2 = Alg()
        self.episodio=1
        self.env = Scopa(self.agent1,self.agent2)
        self.state = self.env.get_observation()  # Salva lo stato iniziale

    def play(self):
        done = False
        self.env.AvviaPartita()
        while not done:
            action1 = self.agent1.select_action(self.state,self.episodio)
            next_state, reward1, done = self.env.gioca_turno(action1)
            self.agent1.remember(self.state, action1, reward1, next_state)
            self.state = next_state
            if done:
                break

            action2 = self.agent2.select_action(self.state,self.episodio)
            next_state, reward2, done= self.env.gioca_turno(action2)
            self.agent2.remember(self.state, action2, reward2, next_state)
            self.state = next_state
            if done:
                break
        
        self.agent1.replay()
        self.agent2.replay()
        
        return reward1, reward2


ScopaAIVsAlg().play()
