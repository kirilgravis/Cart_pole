import gym
import numpy as np
import math


class CartPoleQAgent():
    def __init__(self, buckets=(1, 1, 6, 12), num_episodes=1000, min_lr=0.1, min_explore=0.1, discount=1.0, decay=25):
        self.buckets = buckets
        self.num_episodes = num_episodes
        self.min_lr = min_lr
        self.min_explore = min_explore
        self.discount = discount
        self.decay = decay
        self.env = gym.make('CartPole-v0')
        self.upper_bounds = [self.env.observation_space.high[0], 0.5, self.env.observation_space.high[2], math.radians(50) / 1.]
        self.lower_bounds = [self.env.observation_space.low[0], -0.5, self.env.observation_space.low[2], -math.radians(50) / 1.]
        self.Q_table = np.zeros(self.buckets + (self.env.action_space.n,))

    def update_q(self, state, action, reward, new_state):
        self.Q_table[state][action] += self.lr * (
                    reward + self.discount * np.max(self.Q_table[new_state]) - self.Q_table[state][action])

    def get_explore_rate(self, t):
        return max(self.min_explore, min(1., 1. - math.log10((t + 1) / self.decay)))

    def get_lr(self, t):
        return max(self.min_lr, min(1., 1. - math.log10((t + 1) / self.decay)))

    def choose_action(self, state):
        if (np.random.random() < self.explore_rate):
            return self.env.action_space.sample()
        else:
            return np.argmax(self.Q_table[state])

    def discretize_state(self, obs):
        discretized = list()
        for i in range(len(obs)):
            scaling = (obs[i] + abs(self.lower_bounds[i])) / (self.upper_bounds[i] - self.lower_bounds[i])
            new_obs = int(round((self.buckets[i] - 1) * scaling))
            new_obs = min(self.buckets[i] - 1, max(0, new_obs))
            discretized.append(new_obs)
        return tuple(discretized)

    def train(self):
        for e in range(self.num_episodes):
            current_state = self.discretize_state(self.env.reset())
            self.lr = self.get_lr(e)
            self.explore_rate = self.get_explore_rate(e)
            done = False
            while not done:
                action = self.choose_action(current_state)
                obs, reward, done, _ = self.env.step(action)
                new_state = self.discretize_state(obs)
                self.update_q(current_state, action, reward, new_state)
                current_state = new_state
        print('Finished training!')

    def run(self):
        self.env = gym.wrappers.Monitor(self.env, directory='cartpole', force=True)
        while True:
            current_state = self.discretize_state(self.env.reset())
            done = False
            while not done:
                self.env.render()
                action = self.choose_action(current_state)
                obs, reward, done, _ = self.env.step(action)
                new_state = self.discretize_state(obs)
                current_state = new_state


if __name__ == "__main__":
    agent = CartPoleQAgent()
    agent.train()
    agent.run()
