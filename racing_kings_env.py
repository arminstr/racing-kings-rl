import chess.variant
import random
import time
from IPython.display import display, HTML, clear_output
import numpy as np
import gym
from gym.spaces import Discrete, Box

# from Learning_Chess pdf
class RacingKingsEnvironment(gym.Env):
    def __init__(self):
        super(RacingKingsEnvironment, self).__init__()
        self.board = chess.variant.RacingKingsBoard()
        self.reward = 0
        self.state_shape = (14, 8, 8)
        self.action_shape = 4096
        self.action_space = Discrete(self.action_shape)
        self.observation_space = Box(low=0, high=1, shape=self.state_shape, dtype=np.uint8)
    def who(self, player):
        return "White" if player == chess.WHITE else "Black"
    def display_board(self, use_svg):
        if use_svg:
            return self.board._repr_svg_()
        else:
            return "<pre>" + str(self.board) + "</pre>"
    def board_square_to_index(self, name):
        return (int(name[1])-1) * 8 + (ord(name[0])-97) 
    def action_index_to_uci(self, index):
        index_from = index//64
        index_to = index%64
        name = chr(index_from%8 + 97) + str(index_from//8 +1) + chr(index_to%8 + 97) + str(index_to//8 + 1)
        return name
    def action_uci_to_index(self, uci):
        index_from = (int(uci[1])-1) * 8 + (ord(uci[0])-97) 
        index_to = (int(uci[3])-1) * 8 + (ord(uci[2])-97) 
        return index_from*64 + index_to
    @property
    def actions(self):
        moves = list(self.board.legal_moves)
        moves_string = []
        for move in moves:
            moves_string.append(move.uci())
        boardActions = np.zeros(N_DISCRETE_ACTIONS, dtype=np.int8)
        for move in moves_string:
            boardActions[self.board_square_to_index(move[0:2])*64 + self.board_square_to_index(move[2:4])] = 1
        return boardActions
    @property
    def states(self):
        boardState = np.zeros(self.state_shape, dtype=np.int8)
        for piece in chess.PIECE_TYPES:
            for square in self.board.pieces(piece, chess.WHITE):
                idNum = square//8
                idAlph = square%8
                boardState[piece - 1][7 - idNum][idAlph] = 1
            for square in self.board.pieces(piece, chess.BLACK):
                idNum = square//8
                idAlph = square%8
                boardState[piece + 5][7 - idNum][idAlph] = 1        
        
            temp = self.board.turn
            self.board.turn = chess.WHITE
            for move in list(self.board.legal_moves):
                square = self.board_square_to_index(move.uci())
                idNum = square//8
                idAlph = square%8
                boardState[12][7 - idNum][idAlph] = 1
            self.board.turn = chess.BLACK
            for move in list(self.board.legal_moves):
                square = self.board_square_to_index(move.uci())
                idNum = square//8
                idAlph = square%8
                boardState[13][7 - idNum][idAlph] = 1
            self.board.turn = temp
        return boardState
    
    def step(self, action):
        done = False
        step_reward = 0
        info = {}
        
# check if it is not your turn -> then make a random move
# when uncommenting this code the ai will play moves for both players
        if self.board.turn == chess.WHITE:
            try:
                self.board.push(random.choice(list(self.board.legal_moves)))
                step_reward += 0
                info = {"msg":"White Did a valid move"}
            except:
                info = {"msg":"Passed an already finished board"} 
                done = True

        if not self.board.is_game_over(claim_draw=True):
            if action is not None:
                try:
                    self.board.push_uci(self.action_index_to_uci(action))
                    step_reward += 0.1
                    info = {"msg":"Did a valid move"}
                except:
                    step_reward -= 1
                    info = {"msg":"Action is not a valid move"} 
                    done = True
                if self.board.is_variant_end():
                    if self.who(not self.board.turn) == "Black":
                        step_reward += 10
                        info = {"msg":"AI won the game (being black)!"} 
                        done = True
                    else:
                        step_reward +=0.5
                        info = {"msg":"Random Player won!"} 
                        done = True
                    info = {"msg":"racing kings: " + self.who(not self.board.turn) + " wins!"}
        else:
            step_reward +=1
            done = True
            info = {"msg":"game over"}

        self.reward += step_reward
        
        return self.states, step_reward, done, info
    def reset(self):
        # reset the board
        self.board.reset()
        # play random amount of actions
        for i in range((random.randint(0, 50)*2)):
            try:
                move = random.choice(list(self.board.legal_moves))
                self.board.push(move)
            except:
                self.board.reset()
                
        self.reward = 0.0
        return self.step(None)[0]  # reward, done, info can't be included
    def render(self, mode="human", pause=0.5):
        name = self.who(self.board.turn)
        use_svg = (mode == "human")
        board_stop = self.display_board(use_svg)
        html = "<b>Move %s %s:</b><br/>%s" % (
                    len(self.board.move_stack), name, board_stop)
        if mode is not None:
                if mode == "human":
                    clear_output(wait=True)
                display(HTML(html))
                if mode == "human":
                    time.sleep(pause)
    def close (self):
        print("closing")