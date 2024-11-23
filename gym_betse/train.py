# gym_betse/train.py

import gymnasium as gym
from gym_betse.envs import BetseEnv
from gym_betse.agents.dqn_agent import DQNAgent

def main():
    env = BetseEnv(config_path='config/betse_config.yml')
    agent = DQNAgent(
        state_size=env.observation_space.shape[0],
        action_size=env.action_space.n
    )

    num_episodes = 1000
    max_steps_per_episode = 100

    for episode in range(num_episodes):
        state, _ = env.reset()
        total_reward = 0

        for t in range(max_steps_per_episode):
            action = agent.act(state)
            next_state, reward, done, _, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            if done:
                print(f"Episode {episode+1}/{num_episodes} finished after {t+1} steps with reward {total_reward}")
                break

        if (episode + 1) % 100 == 0:
            agent.save(f"models/dqn_agent_{episode+1}.pth")

    env.close()

if __name__ == "__main__":
    main()

