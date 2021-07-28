import chess.variant
import random
import time
from IPython.display import display, HTML, clear_output
import numpy as np
import gym
from gym.spaces import Discrete, Box

# this is the racing kings environment class which inherits from the gym environment by OpenAI
class RacingKingsEnvironment(gym.Env):
    def __init__(self):
        super(RacingKingsEnvironment, self).__init__()
        self.board = chess.variant.RacingKingsBoard()
        self.reward = 0
        self.state_shape = (12, 8, 8)
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
    # the functions below do some conversions between differnet internally used representation of the board
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
        boardActions = np.zeros(self.action_shape, dtype=np.int8)
        for move in moves_string:
            boardActions[self.board_square_to_index(move[0:2])*64 + self.board_square_to_index(move[2:4])] = 1
        return boardActions
    @property
    def states(self):
        # add all of the pieces to the board
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
        return boardState
    
    def step(self, action, isGame = False):
        done = False
        step_reward = 0
        info = {}
    
        # first check if it's a game against another agent
        if not isGame:
            # if it's not let white play a random move
            if self.board.turn == chess.WHITE:
                try:
                    self.board.push(random.choice(list(self.board.legal_moves)))
                    step_reward += 0
                    info = {"msg":"White Did a valid move"}
                except:
                    info = {"msg":"Passed an already finished board"} 
                    done = True
        # then try pushing the action to the board if not possible return a penalty
        # if game is over or someone did win return different reward
        if not self.board.is_game_over(claim_draw=True):
            if action is not None:
                try:
                    self.board.push_uci(self.action_index_to_uci(action))
                    # rewarding steps lead to repetition of single moves you can enable it for faster training results
                    # step_reward += 0.001
                    info = {"msg":"Did a valid move"}
                except:
                    step_reward += 0
                    info = {"msg":"Action is not a valid move"} 
                    done = True
                if self.board.is_variant_end():
                    if self.who(not self.board.turn) == "Black":
                        step_reward += 100
                        info = {"msg":"AI won the game (being black)!"} 
                        done = True
                    else:
                        step_reward += 0
                        info = {"msg":"Random Player won!"} 
                        done = True
                    info = {"msg":"racing kings: " + self.who(not self.board.turn) + " wins!"}
        else:
            step_reward += 0
            done = True
            info = {"msg":"game over"}

        self.reward += step_reward
        
        return self.states, step_reward, done, info
    # when resetting the board chosse a random starting position. 
    # this is done by making a random amount of moves
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
        # display the board as an image
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