"""
Reinforcement Learning Game (OpenAI Gym)

Features:
- RL agent training
- Game environment
- Visualization
- Modular design
- CLI interface
- Error handling
"""
import gym
import numpy as np
import sys
import matplotlib.pyplot as plt

class RLAgent:
    def __init__(self, env_name):
        self.env = gym.make(env_name)
        self.q_table = np.zeros((self.env.observation_space.n, self.env.action_space.n))
    def train(self, episodes=1000, alpha=0.1, gamma=0.6, epsilon=0.1):
        rewards = []
        for ep in range(episodes):
            state = self.env.reset()
            total_reward = 0
            done = False
            while not done:
                if np.random.uniform(0,1) < epsilon:
                    action = self.env.action_space.sample()
                else:
                    action = np.argmax(self.q_table[state])
                next_state, reward, done, _ = self.env.step(action)
                old_value = self.q_table[state, action]
                next_max = np.max(self.q_table[next_state])
                new_value = (1-alpha)*old_value + alpha*(reward + gamma*next_max)
                self.q_table[state, action] = new_value
                state = next_state
                total_reward += reward
            rewards.append(total_reward)
        return rewards
    def play(self, episodes=10):
        for ep in range(episodes):
            state = self.env.reset()
            done = False
            while not done:
                action = np.argmax(self.q_table[state])
                state, reward, done, _ = self.env.step(action)
                self.env.render()
        self.env.close()

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python reinforcement_learning_game_openai_gym.py <env_name>")
            sys.exit(1)
        env_name = sys.argv[1]
        agent = RLAgent(env_name)
        print("Training RL agent...")
        rewards = agent.train(500)
        plt.plot(rewards)
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Training Rewards')
        plt.show()
        print("Playing trained agent...")
        agent.play(5)

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
