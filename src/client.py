import json
from urllib.parse import urlparse, urljoin

import chess
import chess.engine
import chess.pgn

import pickle
import re
import sys
import argparse
import requests
import asyncio
import websockets
from easydict import EasyDict as edict

from filtermachine import FilterMachine

LOGIN_PATH = '/user/login'
LOGOUT_PATH = '/user/logout'
EN_AVAIL_PATH = '/engine/available'
EN_START_PATH = '/engine/start'
EN_STOP_PATH = '/engine/stop'
WS_EN_PATH = '/ws_engine'


class Client:
    def __init__(self, config):
        # input params
        self.header = config.header
        self.centipawns = config.centipawns
        self.depth = config.depth
        self.n_variations = config.n_variations
        self.output_file = config.output_pgn_path
        self.engine = config.engine
        self.verbose = config.verbose

        # connection settings
        self.url = config.url
        self.ws_url = config.ws_url

        # account settings
        self.login = config.login
        self.password = config.password

        # load pgn file
        with open(config.input_pgn_path) as pgn_file:
            self.game = chess.pgn.read_game(pgn_file)

        # login & get token
        response = requests.post(urljoin(self.url, LOGIN_PATH), json={'login': self.login, 'password': self.password})
        json = response.json()
        self.req_header = {'Authorization': 'Bearer {}'.format(json['token'])}

        # start the engine
        response = requests.post(urljoin(self.url, EN_START_PATH), json={'engine': self.engine['name']},
                                 headers=self.req_header)
        json = response.json()

    def get_game(self):
        return self.game

    def get_moves(self):
        async def get_moves():
            async with websockets.connect(urljoin(self.ws_url, WS_EN_PATH), extra_headers=self.req_header) as websocket:
                await websocket.send('isready')
                while True:
                    recv = await websocket.recv()
                    if recv == 'readyok':
                        break
                await websocket.send('ucinewgame')
                await websocket.send('setoption name multipv value {}'.format(self.n_variations))
                for name, value in self.engine['options'].items():
                    await websocket.send('setoption name {} value {}'.format(name, value))
                board = chess.Board()
                board_move_list = []
                for move in self.game.mainline_moves():
                    board_move_list.append((board.fen(), move.uci(), board.fullmove_number))
                    board.push(move)
                board_move_list.append((board.fen(), '', board.fullmove_number))  # blank move = no move

                move_list = []
                for white, (board_fen, game_move, move_nb) in enumerate(board_move_list):
                    await websocket.send('position fen ' + board_fen)
                    await websocket.send('go depth {}'.format(self.depth))
                    for x in range(self.depth * self.n_variations + 1):
                        recv = await websocket.recv()
                        # whitespace here is important
                        if ' depth {}'.format(
                                self.depth) in recv and 'score cp' in recv:  # mate moves have `score mate` instead of `score cp`, ommiting cuz they obvious
                            m = re.search(r'pv ([a-h][1-8][a-h][1-8])', recv)
                            move = m.group(1)
                            m = re.search(r' score cp (-?\d+) ', recv)
                            score = m.group(1)
                            next_moves = recv.split('pv ')[-1].split(' ')[1:]
                            move_list.append((move_nb, move, score, game_move == move, next_moves, white % 2 == 0))
                        if 'bestmove' in recv: break

            return move_list

        move_list = asyncio.get_event_loop().run_until_complete(asyncio.gather(get_moves()))
        return move_list[0]

    def __del__(self):
        # stop the engine
        response = requests.post(urljoin(self.url, EN_STOP_PATH), headers=self.req_header)

        # logout
        response = requests.get(urljoin(self.url, LOGOUT_PATH), headers=self.req_header)


def main(args):
    client = Client(args)
    moves = client.get_moves()
    game = client.get_game()
    fm = FilterMachine(game, moves, args.centipawns, args.n_variations)
    print(moves)
    new_moves = fm.process()
    print(new_moves)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # w wymaganiach jest -h, ale -h jest zarezerwowane dla --help, wiec poki co robie --header
    parser.add_argument('--header', type=str, choices=['all', 'concise', 'minimal'], default='minimal')
    parser.add_argument('-cp', type=int, default=50, dest='centipawns')
    parser.add_argument('-d', type=int, default=4, dest='depth')
    parser.add_argument('-n', type=int, default=2, dest='n_variations')
    parser.add_argument('-e', type=str, default='./../uciServer.json')
    parser.add_argument('-v', type=bool, default=False, dest='verbose')
    parser.add_argument('input_pgn_path', type=str)
    parser.add_argument('output_pgn_path', type=str)
    args = parser.parse_args()

    with open(args.e) as f:
        config = json.load(f)
    url = urlparse(config['url'])
    args.url = url.geturl()
    ws_url = url._replace(scheme='ws')
    args.ws_url = ws_url.geturl()
    args.login = config['login']
    args.password = config['password']
    args.engine = config['engine']

    if args.n_variations < 2:
        raise ValueError('Minimal acceptable value is: 2')

    main(args)
