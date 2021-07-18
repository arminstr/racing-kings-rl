# First Model - Rewarding Correct Moves and Wins
- Small Rewards for learning correct moves.
- Penalty for wrong moves
- Big Reward for winning a game
- Playing against a random Player

Outcome after 1 million Training Steps: Model learns to repeat a move as often as possible. This enables it to collect an infinite amount of small rewards without getting penalized 

# Second Model - Rewarding Correct Moves and Wins - Selfplay
Same as First Model but with Selfplay.

Assumtion: Changing the Opponent to the same RL Model, will lead to draws if the same move is repeated all of the time. The random opponent from the First Model prevented this from happening.

Outcome: ?