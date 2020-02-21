import chess.engine
import socket
import chess
import pickle
import sys
from easydict import EasyDict as edict

PATH_TO_STOCKFISH = '.\..\stockfish-11-win\stockfish-11-win\Windows\stockfish_20011801_x64.exe'


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('127.0.0.1', 8080))

#dunno what this listen(5) does.
serv.listen(5)
while True:
    conn, addr = serv.accept()
    from_client = bytes()
    while True:
        #TODO think of adding timeout
        data = conn.recv(4096)
        from_client += data
        deserialized = pickle.loads(from_client)
        #checking if we've read everything
        try:
            if deserialized.size == sys.getsizeof(deserialized):
                break
        except AttributeError:
            pass
    #received message will be actually a dicktionary
    client_dick = deserialized

    engine = chess.engine.SimpleEngine.popen_uci(PATH_TO_STOCKFISH)
    res = engine.play(client_dick.board, client_dick.limit)
    engine.quit()

    serv_dick = edict()
    serv_dick.size = 0

    serv_dick.res = res
    #and again, we put size of our dictionary so does client know when to stop reading
    serv_dick.size = sys.getsizeof(serv_dick)

    serialized = pickle.dumps(serv_dick)
    conn.send(serialized)
    conn.close()
