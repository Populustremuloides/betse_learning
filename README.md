# BETSE Gymnasium Environment and Koopman Operator Learning

## Project Overview

This project integrates the BETSE simulation engine with Gymnasium to enable reinforcement learning and Koopman operator learning for controlling bioelectric gradients in a 7-cell system.

## File Structure

- **gym_betse/**: Contains the Gymnasium environment, agents, and utilities.
- **koopman/**: Contains the Koopman operator learning framework using PyTorch.
- **train.py**: Script for training RL agents.
- **train_koopman.py**: Script for training the Koopman operator model.

## Getting Started

1. Install the required packages:
   ```
   pip install -e gym_betse/
   ```

2. Run the training script for RL agents:
   ```
   python gym_betse/train.py
   ```

3. Run the training script for the Koopman operator model:
   ```
   python koopman/train_koopman.py
   ```

## Requirements

- Python 3.7+
- PyTorch
- Gymnasium
- BETSE
- h5py
- numpy

## Authors

- [Your Name](mailto:your.email@example.com)

## License

This project is licensed under the MIT License.
