import chess
import chess.engine

import socket

import pickle
import sys
import argparse

from easydict import EasyDict as edict


class Client():
    def __init__(self):
        # dunno what these flags mean - I've taken them from some random tutorial.
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pass

    def send(self, args):
        # TODO argparse here?
        board = chess.Board("r4rk1/pp5p/2p2ppB/3pP3/2P2Q2/P1N2P2/1q4PP/n4R1K w - - 0 21")
        limit = chess.engine.Limit(depth=10)

        # funny javascript dictionary ;D
        client_dick = edict()
        client_dick.size = 0

        client_dick.board = board
        client_dick.limit = limit
        # we put size here because we want to know when the server sould stop reading
        client_dick.size = sys.getsizeof(client_dick)

        # socket connections need bytes to be send
        serialized = pickle.dumps(client_dick)
        self.client.connect(('127.0.0.1', 8080))
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
    client = Client()
    client.send(args)
    data = client.read_and_close()
    print(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # TODO add argparse arguments here

    args, _ = parser.parse_known_args()

    main(args)
