import chess.engine
import chess

import socket

import pickle
import sys
import json
import argparse

from easydict import EasyDict as edict
from urllib.parse import urlparse


class Server:
    def __init__(self, config):
        self.config = config
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        parsed = urlparse(config['url'])
        self.serv.bind((parsed.hostname, parsed.port))
        # dunno what this listen(5) does.
        self.serv.listen(5)

    def read(self, conn):
        from_client = bytes()
        while True:
            # TODO think of adding timeout
            data = conn.recv(4096)
            from_client += data
            deserialized = pickle.loads(from_client)
            # checking if we've read everything
            try:
                if deserialized.size == sys.getsizeof(deserialized):
                    break
            except AttributeError:
                pass
        # received message will be actually a dictionary
        client_dick = deserialized
        return client_dick

    def infere(self, args, data):
        # TODO use self.config here to setup the engine
        engine = chess.engine.SimpleEngine.popen_uci(args.stockfish_path)
        res = engine.play(data.board, data.limit)
        engine.quit()
        return res

    def reply(self, res, conn):
        serv_dick = edict()
        serv_dick.size = 0

        serv_dick.res = res
        # and again, we put size of our dictionary so does client know when to stop reading
        serv_dick.size = sys.getsizeof(serv_dick)

        serialized = pickle.dumps(serv_dick)
        conn.send(serialized)

    def run(self, args):
        while True:
            conn, addr = self.serv.accept()
            data = self.read(conn)
            res = self.infere(args, data)
            # TODO do we filter the moves on the server side or on the client side?
            self.reply(res, conn)
            conn.close()


def main(args):
    with open(args.config_path) as f:
        config = json.load(f)
    server = Server(config)
    server.run(args)


if __name__ == "__main__":
    stockfish_path_windows = './../stockfish-11-win/stockfish-11-win/Windows/stockfish_20011801_x64.exe'
    stockfish_path_mac = './../stockfish-11-mac/MAC/stockfish-11-64'
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=str, default='./../uciServer.json')
    parser.add_argument('--stockfish-path', type=str,
                        default=stockfish_path_mac)

    args, _ = parser.parse_known_args()

    main(args)
