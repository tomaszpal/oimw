import json
from urllib.parse import urlparse

import chess
import chess.engine

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

        # dunno what these flags mean - I've taken them from some random tutorial.
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self):
        board = chess.Board("r4rk1/pp5p/2p2ppB/3pP3/2P2Q2/P1N2P2/1q4PP/n4R1K w - - 0 21")
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


def main(args):
    client = Client(args)
    client.send()
    data = client.read_and_close()
    print(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # w wymaganiach jest -h, ale -h jest zarezerwowane dla --help, wiec poki co robie --header
    parser.add_argument('--header', type=str, choices=['all', 'concise', 'minimal'], default='minimal')
    parser.add_argument('-cp', type=int, default=50, dest='centipawns')
    parser.add_argument('-d', type=int, default=30, dest='depth')
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
