import gym
from stable_baselines3 import PPO
from ambiente import SimpleScopaEnv
    
# Creiamo l'ambiente
env = SimpleScopaEnv()

model = PPO.load('modelli/scopa_ppo',env)

# Creiamo il modello
#model = PPO("MlpPolicy", env, verbose=1)

# Addestriamo il modello
model.learn(total_timesteps=1000)

model.save('modelli/scopa_ppo')

