import json
from urllib.parse import urlparse

import chess
import chess.engine
import chess.pgn

import socket

import pickle
import sys
import argparse

from easydict import EasyDict as edict


class Client:
    def __init__(self, config):
        self.header = config.header
        self.centipawns = config.centipawns
        self.depth = config.depth
        self.n_variations = config.n_variations
        self.host = config.host
        self.port = config.port
        self.output_file = config.output_pgn_path
        pgn_file = open(config.input_pgn_path)
        self.game = chess.pgn.read_game(pgn_file)
        pgn_file.close()

        self.board = self.game.board()

        self.values = {'p':1
                       }

    def send(self):
        # dunno what these flags mean - I've taken them from some random tutorial.
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        board = self.board
        limit = chess.engine.Limit(depth=self.depth)

        # funny javascript dictionary ;D
        client_dict = edict()
        client_dict.size = 0

        client_dict.board = board
        client_dict.limit = limit
        # we put size here because we want to know when the server sould stop reading
        client_dict.size = sys.getsizeof(client_dict)

        # socket connections need bytes to be send
        serialized = pickle.dumps(client_dict)
        self.client.connect((self.host, self.port))
        self.client.send(serialized)

    def read_and_close(self):
        from_server = bytes()
        while True:
            # TODO think of adding timeout
            data = self.client.recv(4096)
            from_server += data
            deserialized = pickle.loads(from_server)
            # and again, we check if we've read everything
            try:
                if deserialized.size == sys.getsizeof(deserialized):
                    break
            except AttributeError:
                pass
        self.client.close()
        return deserialized

    def process(self):
        for move in self.game.mainline_moves():
            self.send()
            data = self.read_and_close()
            fm = FilterMachine(self.board, self.centipawns)
            nontrivial = fm.apply_all_filters(data.res)
            print(nontrivial)
            self.board.push(move)



class FilterMachine:
    def __init__(self, board, cp):
        self.board = board
        self.values = {
            1: 1, # pawn
            2: 3, # knight
            3: 3, # bishop
            4: 5, # rook
            5: 9, # queen
            6: 4, # king
        }

    def apply_all_filters(self, moves):
        #TODO do sth with centipawns
        moves = self.filter_1(moves)
        moves = self.filter_2(moves)
        moves = self.filter_3(moves)
        return moves

    def filter_1(self, moves):
        #remove moves that are captures by a minor piece, leading to material advantage
        new_moves = []
        for (move, score) in moves:
            ts = move.to_square
            fs = move.from_square
            if ts not in self.board.piece_map():
                new_moves.append((move, score))
            else:
                ts_p = self.board.piece_map()[ts]
                fs_p = self.board.piece_map()[fs]
                ts_p_v = self.values[ts_p.piece_type]
                fs_p_v = self.values[fs_p.piece_type]

                #if to_square piece value is less than from_square piece value, then probably it could be interesting move
                if ts_p_v < fs_p_v:
                    new_moves.append((move, score))
        return moves

    def filter_2(self, moves):
        return moves

    def filter_3(self, moves):
        return moves

def main(args):
    client = Client(args)
    client.process()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # w wymaganiach jest -h, ale -h jest zarezerwowane dla --help, wiec poki co robie --header
    parser.add_argument('--header', type=str, choices=['all', 'concise', 'minimal'], default='minimal')
    parser.add_argument('-cp', type=int, default=50, dest='centipawns')
    parser.add_argument('-d', type=int, default=4, dest='depth')
    parser.add_argument('-n', type=int, default=2, dest='n_variations')
    parser.add_argument('-e', type=str, default='./../uciServer.json')
    parser.add_argument('input_pgn_path', type=str)
    parser.add_argument('output_pgn_path', type=str)
    args = parser.parse_args()

    with open(args.e) as f:
        config = json.load(f)
    url = urlparse(config['url'])
    args.host = url.hostname
    args.port = url.port
    args.login = config['login']
    args.password = config['password']

    if args.n_variations < 2:
        raise ValueError('Minimal acceptable value is: 2')

    main(args)
