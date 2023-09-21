import gym
from stable_baselines3 import PPO
from ambiente import SimpleScopaEnv
    
# Creiamo l'ambiente
env = SimpleScopaEnv()

# Creiamo il modello
model = PPO("MlpPolicy", env, verbose=1)
#model = PPO.load('modelli/scopa_ppo')

# Addestriamo il modello
model.learn(total_timesteps=100000)

model.save('modelli/scopa_ppo')

