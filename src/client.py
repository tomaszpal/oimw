import chess
import chess.engine
import socket
import pickle
from easydict import EasyDict as edict
import sys


#dunno what these flags mean - I've taken them from some random tutorial.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


board = chess.Board("r4rk1/pp5p/2p2ppB/3pP3/2P2Q2/P1N2P2/1q4PP/n4R1K w - - 0 21")
limit = chess.engine.Limit(depth=10)

#funny javascript dicktionary ;D
client_dick = edict()
client_dick.size = 0

client_dick.board = board
client_dick.limit = limit
#we put size here because we want to know when the server sould stop reading
client_dick.size = sys.getsizeof(client_dick)

#socket connections need bytes to be send
serialized = pickle.dumps(client_dick)
client.connect(('127.0.0.1', 8080))
client.send(serialized)
from_serv = bytes()

from_server = bytes()
while True:
    #TODO think of adding timeout
    data = client.recv(4096)
    from_server += data
    deserialized = pickle.loads(from_server)
    #and again, we check if we've read everything
    try:
        if deserialized.size == sys.getsizeof(deserialized):
            break
    except AttributeError:
        pass
client.close()
print(deserialized)

