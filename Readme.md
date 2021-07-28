# Reinforcement Learning Racing Kings

This repository contains the Code for EMLP Project as part of Master of Applied Research Studies at University of Applied Sciences Augsburg.

It contains code for a stable baselines based PPO approach and a DQN based on keras.
We wanted to implement a model based rl approach but did not have enough time during the project phase.

You can as well run tensorboard in the Training/Logs directory to visualize the training metrics.

Additionally there are existing 2 different environments. The 'alex' version adds 2 more layers in the state description and therefore has a model input shape of (14, 8, 8). Those 2 Layers describe the given squares of pieces that are allowed to move in the current state.

The game input is buggy in some rendering variants of jupyter. It did work in the browser when using ***jupyter notebook*** in the command line to launch a server.

**Please read the documentation first!**