# D:\Adnan_project\TradingBot\ml_models\rl_agent.py
import numpy as np
from indicator_calculator import calculate_indicators # Import indicators

class TradingEnvironment:
    def __init__(self, df):
        self.df = df
        self.current_step = 0
        self.state_size = 5
    
    def reset(self):
        self.current_step = 0
        state = self._get_state()
        return state
    
    def step(self, action):
        self.current_step += 1
        reward = self._calculate_reward(action)
        done = self.current_step >= len(self.df) -1
        next_state = self._get_state() if not done else None
        return next_state, reward, done
    
    def _get_state(self):
        if self.current_step >= len(self.df):
           return None
        
        current_data = self.df.iloc[self.current_step]
        state = np.array([current_data['rsi6'], current_data['rsi12'], current_data['bb up'], current_data['bb dn'], current_data['macd dif']])
        return state

    def _calculate_reward(self, action):
        if self.current_step >= len(self.df) - 1:
            return 0
        
        current_price = self.df['close'].iloc[self.current_step]
        next_price = self.df['close'].iloc[self.current_step+1]
        
        if action == 0: #BUY
            if next_price > current_price:
                return 1
            else:
                return -1
        elif action == 1:  # SELL
            if next_price < current_price:
                return 1
            else:
                return -1
        else: #HOLD
           return 0
        
class QLearningAgent:
    def __init__(self, state_size, action_size, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, min_exploration_rate=0.01, exploration_decay_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = np.zeros((state_size, action_size))
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.min_exploration_rate = min_exploration_rate
        self.exploration_decay_rate = exploration_decay_rate
        
    def choose_action(self, state):
         if state is None:
             return 2 #HOLD
         if np.random.rand() < self.exploration_rate:
            return np.random.choice(self.action_size)
         else:
            return np.argmax(self.q_table[state,:])
        
    def update_q_table(self, state, action, reward, next_state):
        if next_state is None:
            return
        
        best_next_q = np.max(self.q_table[next_state,:])
        self.q_table[state, action] = self.q_table[state, action] + self.learning_rate * (reward + self.discount_factor * best_next_q - self.q_table[state, action])
    
    def decay_exploration_rate(self):
        self.exploration_rate = max(self.min_exploration_rate, self.exploration_rate - self.exploration_decay_rate)


def run_rl_agent(df, agent, num_episodes):
      env = TradingEnvironment(df)
      for episode in range(num_episodes):
        state = env.reset()
        done = False
        
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            if state is not None and next_state is not None:
                agent.update_q_table(state, action, reward, next_state)
            agent.decay_exploration_rate()
            state = next_state
