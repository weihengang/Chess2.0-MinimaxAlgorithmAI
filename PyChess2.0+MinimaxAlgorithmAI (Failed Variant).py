#CHESS2.0 + MINIMAX AI ALGORITHM -ANG WEIHENG 9B
"""
ACKNOWLEDGEMENTS:
This is the first time that I've researched the subject extensively, and links to the websites are below:
  -https://www.freecodecamp.org/news/simple-chess-ai-step-by-step-1d55a9266977/ (tutorial, programming language is in javascript)
  -https://dev.to/zeyu2001/build-a-simple-chess-ai-in-javascript-18eg (tutorial, programming language is in javascript)
  -https://www.chessprogramming.org/ (chess programming in general)
    -https://www.chessprogramming.org/Alpha-Beta 
    -https://www.chessprogramming.org/Board_Representation
    -https://www.chessprogramming.org/Piece-Square_Tables 
    -https://www.chessprogramming.org/Simplified_Evaluation_Function 
    -https://www.chessprogramming.org/Evaluation
Stuff used from other websites includes:
  -Piece Square Tables (line 381-445), from https://www.freecodecamp.org/news/simple-chess-ai-step-by-step-1d55a9266977/, who in turn took in from https://chessprogramming.wikispaces.com/Simplified+evaluation+function
  -Board colors and pieces, from https://lichess.org/
The rest is completely original code, as you might be able to tell by the slowness and inefficiency (100 nodes per second!!!)
"""
import turtle as t #display chess board
import math as m #get coordinates and index of click
import os #chess images
import time as tm
import copy as c #deepcopying list_piece and list_PieceSquareTurtle
import random as r
import multiprocessing as mp
def decode_fen(str):
    list_board =[]
    list_row =[]
    for i in str:
        if (i == "/"):
            list_board.append(list_row)
            list_row =[]
        elif (i.isdigit()):
            for j in range(0, int(i)):
                list_row.append("-")
        elif (i == "r"):
            list_row.append("c")
        elif (i == "R"):
            list_row.append("C")
        elif (i == "n"):
            list_row.append("h")
        elif (i == "N"):
            list_row.append("H")
        else:
            list_row.append(i)
    list_board.append(list_row)
    return list_board
list_piece =decode_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
player_castle_queenside =True
player_castle_kingside =True
def draw_screen(): #600 total, -300 to 300
    t.up()
    t.goto(-300, 300)
    for i in range(0, 8): #y value
        list_pos_list =[]
        for j in range(0, 8): #x value
            if (j % 2 == 0 and i % 2 == 0 or j % 2 != 0 and i % 2 != 0):
                square_color =(240, 217, 181)
            else:
                square_color =(181, 136, 99)
            t.color(square_color)
            t.begin_fill()
            t.goto(t.xcor() + 75, t.ycor())
            t.goto(t.xcor(), t.ycor() - 75)
            list_pos_list.append([t.xcor() - 75/2, t.ycor() + 75/2])
            t.goto(t.xcor() - 75, t.ycor())
            t.goto(t.xcor(), t.ycor() + 75)
            t.end_fill()
            t.goto(t.xcor() + 75, t.ycor())
        t.goto(-300, t.ycor() - 75)
        list_pos.append(list_pos_list)
        list_pos_list =[]
    t.goto(-305, -305)
    t.width(5)
    t.color((255, 255, 255))
    t.down()
    t.goto(305, -305)
    t.goto(305, 305)
    t.goto(-305, 305)
    t.goto(-305, -305)
    t.update()
class GenerateMoves:
    @staticmethod
    def generate_pawn_moves(x, y, ai_or_player, move_generation =False, board =list_piece):
        pawn_moves =[]
        if (ai_or_player == "player"):
            if (y == 6 and board[5][x] == "-" and board[4][x] == "-"): #double pawn push at start
                pawn_moves.append([x, 4])
            if (board[y - 1][x] == "-"):
                pawn_moves.append([x, y - 1])
            if (x != 0 and board[y - 1][x - 1].islower()):
                pawn_moves.append([x - 1, y - 1])
            if (x != 7 and board[y - 1][x + 1].islower()):
                pawn_moves.append([x + 1, y - 1])
            if (not move_generation):
                draw_moves(pawn_moves, x, y)
        else:
            if (y == 1 and board[2][x] == "-" and board[3][x] == "-"): #moves are inversed, +1 instead of -1 for y
                pawn_moves.append([x, 3])
            if (y != 7 and board[y + 1][x] == "-"):
                pawn_moves.append([x, y + 1])
            if (y != 7 and x != 0 and board[y + 1][x - 1].isupper()):
                pawn_moves.append([x - 1, y + 1])
            if (y != 0 and x != 7 and board[y + 1][x + 1].isupper()):
                pawn_moves.append([x + 1, y + 1])
        return pawn_moves
    @staticmethod
    def generate_castle_moves(x, y, ai_or_player, if_king =False, move_generation =False, board =list_piece):
        castle_moves =[]
        for i in range(0, 4): #up down left right
            iteration =8
            if (if_king):
                iteration =2
            for j in range(1, iteration):
                match i:
                    case 0:
                        ind_x =x
                        ind_y =y - j
                    case 1:
                        ind_x =x
                        ind_y =y + j
                    case 2:
                        ind_x =x - j
                        ind_y =y
                    case 3:
                        ind_x =x + j
                        ind_y =y
                if (ind_x < 0 or ind_x > 7 or ind_y < 0 or ind_y > 7):
                    break
                square =board[ind_y][ind_x]
                if (square == "-"):
                    castle_moves.append([ind_x, ind_y])
                    continue
                if (square.islower() and ai_or_player == "player" or square.isupper() and ai_or_player == "ai"):
                    castle_moves.append([ind_x, ind_y])
                break
        if (not if_king and ai_or_player == "player" and not move_generation):
            draw_moves(castle_moves, x, y)
        return castle_moves
    @staticmethod
    def generate_bishop_moves(x, y, ai_or_player, if_king =False, move_generation =False, board =list_piece):
        bishop_moves =[]
        for i in range(0, 4):
            iteration =8
            if (if_king):
                iteration =2
            for j in range(1, iteration): #leftup rightup leftdown rightdown1
                match i:
                    case 0:
                        ind_x =x - j
                        ind_y =y - j
                    case 1:
                        ind_x =x + j
                        ind_y =y - j
                    case 2:
                        ind_x =x - j
                        ind_y =y + j
                    case 3:
                        ind_x =x + j
                        ind_y =y + j
                if (ind_x < 0 or ind_x > 7 or ind_y < 0 or ind_y > 7):
                    break
                square =board[ind_y][ind_x]
                if (square == "-"):
                    bishop_moves.append([ind_x, ind_y])
                    continue
                if (square.islower() and ai_or_player == "player" or square.isupper() and ai_or_player == "ai"):
                    bishop_moves.append([ind_x, ind_y])
                break
        if (not if_king and ai_or_player == "player" and not move_generation):
            draw_moves(bishop_moves, x, y)
        return bishop_moves
    @staticmethod
    def generate_horse_moves(x, y, ai_or_player, move_generation =False, board =list_piece):
        horse_moves =[]
        for i in range(0, 8): #start from +3, -1 and move counter clockwise
            match i:
                case 0:
                    ind_x =x + 2
                    ind_y =y - 1
                case 1:
                    ind_x =x + 1
                    ind_y =y - 2
                case 2:
                    ind_x =x - 1
                    ind_y =y - 2
                case 3:
                    ind_x =x - 2
                    ind_y =y - 1
                case 4:
                    ind_x =x - 2
                    ind_y =y + 1
                case 5:
                    ind_x =x - 1
                    ind_y =y + 2
                case 6:
                    ind_x =x + 1
                    ind_y =y + 2
                case 7:
                    ind_x =x + 2
                    ind_y =y + 1
            if (ind_x < 0 or ind_x > 7 or ind_y < 0 or ind_y > 7):
                continue
            square =board[ind_y][ind_x]
            if (square == "-"):
                horse_moves.append([ind_x, ind_y])
            if (square.islower() and ai_or_player == "player" or square.isupper() and ai_or_player == "ai"):
                horse_moves.append([ind_x, ind_y])
        if (ai_or_player == "player" and not move_generation):
            draw_moves(horse_moves, x, y)
        return horse_moves
    @staticmethod
    def generate_king_moves(x, y, ai_or_player, move_generation =False, board =list_piece):
        king_moves =GenerateMoves.generate_castle_moves(x, y, ai_or_player, True, board =board) + GenerateMoves.generate_bishop_moves(x, y, ai_or_player, True, board =board)
        if (ai_or_player == "player" and player_castle_queenside and not False in [board[7][i] == "-" for i in range(1, 4)]):
            king_moves.append([2, 7])
        if (ai_or_player == "player" and player_castle_kingside and not False in [board[7][i] == "-" for i in range(5, 7)]):
            king_moves.append([6, 7])
        if (not move_generation):
            draw_moves(king_moves, x, y)
        return king_moves
    @staticmethod
    def generate_queen_moves(x, y, ai_or_player, move_generation =False, board =list_piece):
        return GenerateMoves.generate_castle_moves(x, y, ai_or_player, move_generation =move_generation, board =board) + (GenerateMoves.generate_bishop_moves(x, y, ai_or_player, move_generation =move_generation, board =board))
minimax_iteration_amount =0
class MinimaxAI:
    @staticmethod
    def generate_all_moves(ai_or_player, piece_class, board):
        total_moves ={}
        for i in piece_class:
            if (ai_or_player == "ai" and i.piece.islower()):
                match i.piece:
                    case "p":
                        total_moves[i] =GenerateMoves.generate_pawn_moves(i.column, i.row, "ai", move_generation =True, board =board)
                    case "c":
                        total_moves[i] =GenerateMoves.generate_castle_moves(i.column, i.row, "ai", move_generation =True, board =board)
                    case "h":
                        total_moves[i] =GenerateMoves.generate_horse_moves(i.column, i.row, "ai", move_generation =True, board =board)
                    case "b":
                        total_moves[i] =GenerateMoves.generate_bishop_moves(i.column, i.row, "ai", move_generation =True, board =board)
                    case "q":
                        total_moves[i] =GenerateMoves.generate_queen_moves(i.column, i.row, "ai", move_generation =True, board =board)
                    case "k":
                        total_moves[i] =GenerateMoves.generate_king_moves(i.column, i.row, "ai", move_generation =True, board =board)
            elif (ai_or_player == "player" and i.piece.isupper()):
                match i.piece:
                    case "P":
                        total_moves[i] =GenerateMoves.generate_pawn_moves(i.column, i.row, "player", move_generation =True, board =board)
                    case "C":
                        total_moves[i] =GenerateMoves.generate_castle_moves(i.column, i.row, "player", move_generation =True, board =board)
                    case "H":
                        total_moves[i] =GenerateMoves.generate_horse_moves(i.column, i.row, "player", move_generation =True, board =board)
                    case "B":
                        total_moves[i] =GenerateMoves.generate_bishop_moves(i.column, i.row, "player", move_generation =True, board =board)
                    case "Q":
                        total_moves[i] =GenerateMoves.generate_queen_moves(i.column, i.row, "player", move_generation =True, board =board)
                    case "K":
                        total_moves[i] =GenerateMoves.generate_king_moves(i.column, i.row, "player", move_generation =True, board =board)
        list_remove =[]
        for i in total_moves:
            if (len(total_moves[i]) == 0):
                list_remove.append(i)
        [total_moves.pop(i) for i in list_remove]
        return total_moves
    @staticmethod
    def change_board_data(i, j, board):
        changed_board =c.deepcopy(board)
        changed_board[i.row][i.column] ="-"
        changed_board[j[1]][j[0]] =i.piece
        changed_piece_class =[]
        y_counter =0
        for k in changed_board:
            x_counter =0
            for l in k:
                if (l != "-"):
                    changed_piece_class.append(PieceSquareTurtle(x_counter, y_counter, l, "MINIMAX"))
                x_counter += 1
            y_counter += 1
        return [changed_piece_class, changed_board]
    alpha ="not set"
    beta ="not set"
    @staticmethod
    def minimax(list_args): #piece_class, board, level): #oh shit here goes 2
        piece_class, board, level =list_args
        global minimax_iteration_amount
        minimax_iteration_amount += 1
        total_moves ={}
        move =[]
        if (level == 1 or level == 3):
            total_moves =MinimaxAI.generate_all_moves("ai", piece_class, board)
        elif (level == 2 or level == 4):
            total_moves =MinimaxAI.generate_all_moves("player", piece_class, board)
        list_value =[]
        if (level == 1):
            minimax_process_pool =mp.Pool(processes =len(total_moves))
            process_pool_args =[]
            for i in total_moves:
                for j in total_moves[i]:
                    changed_piece_class, changed_board =MinimaxAI.change_board_data(i, j, board)
                    process_pool_args.append([changed_piece_class, changed_board, level + 1])
                    move.append([i, j])
            list_value =minimax_process_pool.map(MinimaxAI.minimax, [i for i in process_pool_args])
            print(list_value)
        else:
            for i in total_moves:
                for j in total_moves[i]:
                    #changed_piece_class =c.deepcopy(piece_class)
                    changed_piece_class, changed_board =MinimaxAI.change_board_data(i, j, board)
                    #if (level == 1):
                    #    value =MinimaxAI.minimax(changed_piece_class, changed_board, level + 1)
                    #    move.append([i, j]) #[selected class PieceSquareTurtle, move ([x, y])]
                    if (level == 2):
                        value =MinimaxAI.minimax([changed_piece_class, changed_board, level + 1])
                        #if (isinstance(MinimaxAI.alpha, float) and value > MinimaxAI.alpha): #ai will not choose this move, skip
                            #return 10000
                        #else:
                        move.append([i, j]) 
                    elif (level == 3): 
                        value =MinimaxAI.minimax([changed_piece_class, changed_board, level + 1])
                        #if (isinstance(MinimaxAI.beta, float) and value < MinimaxAI.beta): #player will not choose this move, skip
                            #return -10000
                        #else:
                        move.append([i, j])
                        #value =MinimaxAI.minimax(changed_piece_class, changed_board, level + 1)
                    elif (level == 4):
                        value =MinimaxAI.evaluate(changed_board)
                        move.append([i, j])
                """
                elif (level == 4):
                    value =MinimaxAI.evaluate(changed_board)
                    #if (isinstance(MinimaxAI.gamma, float) and value > MinimaxAI.gamma): #ai will not choose this move, skip
                    #    return 10000
                    #else:
                    move.append([i, j]) 
                """
                list_value.append(value)
        if (level == 1):
            #MinimaxAI.alpha ="not set"
            #MinimaxAI.beta ="not set"
            for i in move:
                print(f"{i}: {list_value[move.index(i)]}")
            min_random =[]
            counter =0
            for i in list_value:
                if (i == min(list_value)):
                    min_random.append(counter)
                counter += 1
            return move[r.choice(min_random)]
            #return move[list_value.index(min(list_value))]
        #return -1 * min(list_value)
        elif (level == 2):
            #if (MinimaxAI.alpha == "not set"):
            #    MinimaxAI.alpha =max(list_value)
            return max(list_value)
        elif (level == 3):
            #if (MinimaxAI.beta == "not set"):
            #    MinimaxAI.beta =min(list_value)
            return min(list_value)
        elif (level == 4):
            return max(list_value)
        """
        elif (level == 4):
            #if (MinimaxAI.gamma == "not set"):
                #MinimaxAI.gamma =max(list_value)
            return max(list_value)
        """
    @staticmethod
    def construct_ai_PST(PST_list):
        reversed_PST =list(reversed(PST_list))
        ai_PST =[]
        for i in reversed_PST:
            ai_PST_list =[]
            [ai_PST_list.append(-1 * j) for j in i]
            ai_PST.append(ai_PST_list)
        return ai_PST
    PST_PAWN =[
        [0, 0, 0, 0, 0, 0, 0, 0],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [1, 1, 2, 3, 3, 2, 1, 1],
        [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
        [0.5, 1, 1, -2, -2, 1, 1, 0.5],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]
    PST_pawn =construct_ai_PST(PST_PAWN)
    PST_HORSE =[
        [-5, -4, -3, -3, -3, -3, -4, -5],
        [-4, -2, 0, 0, 0, 0, -2, -4],
        [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
        [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
        [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
        [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
        [-4, -2, 0, 0, 0, 0, -2, -4],
        [-5, -4, -3, -3, -3, -3, -4, -5]
    ]
    PST_horse =construct_ai_PST(PST_HORSE)
    PST_BISHOP =[
        [-2, -1, -1, -1, -1, -1, -1, -2],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
        [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
        [-1, 0, 1, 1, 1, 1, 0, -1],
        [-1, 1, 1, 1, 1, 1, 1, -1],
        [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
        [-2, -1, -1, -1, -1, -1, -1, -2]
    ]
    PST_bishop =construct_ai_PST(PST_BISHOP)
    PST_CASTLE =[
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0.5, 1, 1, 1, 1, 1, 1, 0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
        [0, 0, 0, 0.5, 0.5, 0, 0, 0]
    ]
    PST_castle =construct_ai_PST(PST_CASTLE)
    PST_QUEEN =[
        [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
        [-1, 0, 0, 0, 0, 0, 0, -1],
        [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
        [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
        [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
        [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
        [-1, 0, 0.5, 0, 0, 0, 0, -1],
        [-2, -1, -1, -0.5, -0.5, -1, -1, -2]
    ]
    PST_queen =construct_ai_PST(PST_QUEEN)
    PST_KING =[
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-3, -4, -4, -5, -5, -4, -4, -3],
        [-2, -3, -3, -4, -4, -3, -3, -2],
        [-1, -2, -2, -2, -2, -2, -2, -1],
        [2, 2, 0, 0, 0, 0, 2, 2],
        [2, 3, 1, 0, 0, 1, 3, 2]
    ]
    PST_king =construct_ai_PST(PST_KING)
    @staticmethod
    def evaluate(board): #evaluation strategy: material (easy), piece square tables (easy), defense amount (difficult), mobility (moderate)
        piece_value ={
            "p": [-10, MinimaxAI.PST_pawn],
            "h": [-30, MinimaxAI.PST_horse],
            "b": [-30, MinimaxAI.PST_bishop],
            "c": [-50, MinimaxAI.PST_castle],
            "q": [-90, MinimaxAI.PST_queen],
            "k": [-1000, MinimaxAI.PST_king],
            "P": [10, MinimaxAI.PST_PAWN],
            "H": [30, MinimaxAI.PST_HORSE],
            "B": [30, MinimaxAI.PST_BISHOP],
            "C": [50, MinimaxAI.PST_CASTLE],
            "Q": [90, MinimaxAI.PST_QUEEN],
            "K": [1000, MinimaxAI.PST_KING]
        }
        board_value =0
        for i in board:
            for j in i:
                if (j in piece_value):
                    try:
                        board_value += piece_value[j][0] + piece_value[j][1][board.index(i)][i.index(j)]
                    except (Exception):
                        print(f"PieceSquareTable Error: {j}")
                        board_value += piece_value[j][0]
        return board_value
class PieceSquareTurtle:
        def __init__(self, column, row, piece, img_file):
            self.row =row
            self.column =column
            self.piece =piece
            if (img_file != "MINIMAX"):
                self.turtle =t.Turtle()
                self.turtle.speed(0)
                self.turtle.up()
                self.turtle.shape(img_file)
                self.turtle.hideturtle()
        def __repr__(self):
            return f"{self.piece} =({self.column}, {self.row})"
def draw_moves(list_moves, x, y):
    t.tracer(0)
    dot.up()
    dot.goto(list_pos[y][x][0] - 75/2, list_pos[y][x][1] - 75/2)
    dot.down()
    dot.goto(dot.xcor() + 75, dot.ycor())
    dot.goto(dot.xcor(), dot.ycor() + 75)
    dot.goto(dot.xcor() - 75, dot.ycor())
    dot.goto(dot.xcor(), dot.ycor() - 75)
    dot.up()
    for i in list_moves:
        dot.goto(list_pos[i[1]][i[0]])
        dot.dot(18, (255, 255, 255))
    t.update()
    t.tracer(1)
def draw_last_move(move_last, move_now):
    last_move.clear()
    t.tracer(0)
    last_move.up()
    last_move.color((32, 32, 32))
    last_move.goto(list_pos[move_last[1]][move_last[0]][0] - 75/2, list_pos[move_last[1]][move_last[0]][1] - 75/2)
    last_move.down()
    last_move.goto(last_move.xcor() + 75, last_move.ycor())
    last_move.goto(last_move.xcor(), last_move.ycor() + 75)
    last_move.goto(last_move.xcor() - 75, last_move.ycor())
    last_move.goto(last_move.xcor(), last_move.ycor() - 75)
    last_move.color((128, 128, 128))
    last_move.up()
    last_move.goto(list_pos[move_now[1]][move_now[0]][0] - 75/2, list_pos[move_now[1]][move_now[0]][1] - 75/2)
    last_move.down()
    last_move.goto(last_move.xcor() + 75, last_move.ycor())
    last_move.goto(last_move.xcor(), last_move.ycor() + 75)
    last_move.goto(last_move.xcor() - 75, last_move.ycor())
    last_move.goto(last_move.xcor(), last_move.ycor() - 75)
    t.update()
    t.tracer(1)
def screen_onclick(x, y):
    global click_type
    global move_turn
    global selected_piece
    global legitimate_moves
    global player_castle_kingside
    global player_castle_queenside
    for i in list_pos:
        for j in i:
            if (m.sqrt(pow(j[0] - x, 2) + pow(j[1] - y, 2)) <= 75/2):
                ind_x =i.index(j)
                ind_y =list_pos.index(i)
                if (click_type == "select"):
                    click_type ="move"
                    for k in list_PieceSquareTurtle:
                        if (k.column == ind_x and k.row == ind_y and k.piece.isupper()):
                            selected_piece =k
                            match k.piece:
                                case "P": #k is class PieceTurtleSquare which contains index and turtle
                                    legitimate_moves =GenerateMoves.generate_pawn_moves(k.column, k.row, ai_or_player ="player") 
                                case "C":
                                    legitimate_moves =GenerateMoves.generate_castle_moves(k.column, k.row, ai_or_player ="player")
                                case "H":
                                    legitimate_moves =GenerateMoves.generate_horse_moves(k.column, k.row, ai_or_player ="player")
                                case "B":
                                    legitimate_moves =GenerateMoves.generate_bishop_moves(k.column, k.row, ai_or_player ="player")
                                case "K":
                                    legitimate_moves =GenerateMoves.generate_king_moves(k.column, k.row, ai_or_player ="player") #based on castle and bishop functions
                                case "Q":
                                    legitimate_moves =GenerateMoves.generate_queen_moves(k.column, k.row, ai_or_player ="player") #based on castle and bishop functions
                            return
                if (click_type == "move"):
                    click_type ="select"
                    if (not [ind_x, ind_y] in legitimate_moves):
                        dot.clear()
                        #screen_onclick(x, y)
                        return
                    else:
                        if (selected_piece.piece == "C" and selected_piece.column == 0 and player_castle_queenside):
                            player_castle_queenside =False
                        if (selected_piece.piece == "C" and selected_piece.column == 7 and player_castle_kingside):
                            player_castle_kingside =False
                        draw_last_move([selected_piece.column, selected_piece.row], [ind_x, ind_y])
                        selected_piece.turtle.goto(list_pos[ind_y][ind_x][0], list_pos[ind_y][ind_x][1])
                        if (list_piece[ind_y][ind_x] != "-"): #capture
                            for i in list_PieceSquareTurtle:
                                if (i.row == ind_y and i.column == ind_x):
                                    i.turtle.hideturtle()
                                    list_PieceSquareTurtle.remove(i)
                                    break
                        list_piece[selected_piece.row][selected_piece.column] ="-"
                        selected_piece.column =ind_x
                        selected_piece.row =ind_y
                        list_piece[ind_y][ind_x] =selected_piece.piece
                        dot.clear()
                        if (selected_piece.piece == "K" and player_castle_queenside and ind_x == 2 and ind_y == 7): #queenside castle
                            player_castle_queenside =False
                            player_castle_kingside =False
                            for i in list_PieceSquareTurtle:
                                if (i.row == 7 and i.column == 0):
                                    i.turtle.goto(list_pos[7][3])
                                    i.row =7
                                    i.column =3
                                    break
                            list_piece[7][0] ="-"
                            list_piece[7][3] ="C"
                        elif (selected_piece.piece == "K" and player_castle_kingside and ind_x == 6 and ind_y == 7):
                            player_castle_queenside =False
                            player_castle_kingside =False
                            for i in list_PieceSquareTurtle:
                                if (i.row == 7 and i.column == 7):
                                    i.turtle.goto(list_pos[7][5])
                                    i.row =7
                                    i.column =5
                                    break
                            list_piece[7][7] ="-"
                            list_piece[7][5] ="C"
                        elif (selected_piece.piece == "K"):
                            player_castle_queenside =False
                            player_castle_kingside =False
                        if (selected_piece.piece == "P" and selected_piece.row == 0):
                            while True:
                                promoted_piece =t.textinput("PAWN PROMOTION", "Select: H, B, C, Q")
                                if (promoted_piece in ["H", "B", "C", "Q"]):
                                    selected_piece.piece =promoted_piece
                                    [selected_piece.turtle.shape(f"{directory}/{i}") for i in image_files if (i[5:][:1] == promoted_piece)]
                                    t.update()
                                    list_piece[ind_y][ind_x] =promoted_piece
                                    break
                        time_start =tm.time()
                        ai_move =MinimaxAI.minimax([list_PieceSquareTurtle, list_piece, 1])
                        time_end =tm.time()
                        print(minimax_iteration_amount)
                        print(time_end - time_start)
                        draw_last_move([ai_move[0].column, ai_move[0].row], ai_move[1])
                        print(ai_move)
                        for i in list_PieceSquareTurtle:
                            if (i.row == ai_move[0].row and i.column == ai_move[0].column):
                                i.turtle.goto(list_pos[ai_move[1][1]][ai_move[1][0]])
                                if (list_piece[ai_move[0].row][ai_move[0].column] != "-"):
                                    for j in list_PieceSquareTurtle:
                                        if (j.row == ai_move[1][1] and j.column == ai_move[1][0]):
                                            j.turtle.hideturtle()
                                            list_PieceSquareTurtle.remove(j)
                                            break
                                list_piece[ai_move[0].row][ai_move[0].column] ="-"
                                i.column =ai_move[1][0]
                                i.row =ai_move[1][1]
                                list_piece[ai_move[1][1]][ai_move[1][0]] =ai_move[0].piece
                                break
if (__name__ == "__main__"):
    tscreen =t.Screen()
    tscreen.bgcolor("black")
    t.tracer(100)
    t.hideturtle()
    t.colormode(255)
    dot =t.Turtle()
    dot.hideturtle()
    dot.color((255, 255, 255))
    dot.width(5)
    last_move =t.Turtle()
    last_move.hideturtle()
    last_move.width(5)
    directory =__file__.replace("\PyChess2.0+MinimaxAlgorithmAI (Failed Variant).py", "") #directory to load lichess chess images
    list_pos =[] #positions of square
    list_PieceSquareTurtle =[] #list containing classes of type PieceSquareTurtle which contains xy index, piece type, color, and turtle image
    click_type ="select" #click_type can be select or place
    move_turn ="WHITE" #whose turn to move, white or black (ai)
    selected_piece =None #if piece was selected, store selected square here
    legitimate_moves =[] #generate all legitimate moves once piece is selected and store here
    draw_screen()
    image_files =os.listdir(directory)
    remove_files =[]
    [tscreen.addshape(f"{directory}/{i}") if (i[-4:] == ".gif") else remove_files.append(i) for i in image_files]
    [image_files.remove(i) for i in remove_files] #for some reason can't put this in image_file for loop and must create new variable remove_files
    for i in list_piece:
        x_counter =0
        for j in i:
            if (j != "-"):
                for k in image_files:
                    if (k[5:][:1] == j.upper() and ((j.islower() and k[:5] == "Black") or (j.isupper() and k[:5] == "White"))):
                        list_PieceSquareTurtle.append(PieceSquareTurtle(x_counter, list_piece.index(i), j, f"{directory}/{k}"))
                        break
            x_counter += 1
    for i in list_PieceSquareTurtle:
        i.turtle.goto(list_pos[i.row][i.column])
        i.turtle.showturtle()
    t.tracer(1)
    tscreen.onclick(screen_onclick)
    tscreen.mainloop()