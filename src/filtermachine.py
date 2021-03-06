import chess


class FilterMachine:
    def __init__(self, game, moves, cp, n_variations):
        self.game = game
        self.values = {
            1: 1,  # pawn
            2: 3,  # knight
            3: 3,  # bishop
            4: 5,  # rook
            5: 9,  # queen
            6: 4,  # king
        }
        self.cp = cp
        self.sf_moves = moves
        self.n_variations = n_variations

    def min_centipawn_filter(self, best_move, second_best):
        return abs(best_move[1]-second_best[1]) < self.cp

    def is_material_gain(self, sf_move, board):
        # remove moves that are captures by a minor piece, leading to material advantage
        move = sf_move
        mv = chess.Move.from_uci(move)
        ts = mv.to_square
        fs = mv.from_square
        if ts not in board.piece_map():
            return False
        else:
            ts_p = board.piece_map()[ts]
            fs_p = board.piece_map()[fs]
            ts_p_v = self.values[ts_p.piece_type]
            fs_p_v = self.values[fs_p.piece_type]

            # if to_square piece value is less or equal than from_square piece value, then probably it could be interesting move
            if ts_p_v <= fs_p_v:
                return False
        return True

    def is_fork(self, sf_move, board):
        # check if move is a simple fork https://en.wikipedia.org/wiki/Fork_(chess)
        new_moves = []
        move = sf_move[3][0]
        next_moves = sf_move[3][2]
        # we cannot check if there is fork if not enought data
        if len(next_moves) < 2:
            return False

        board_after_move = board.copy()
        mv = chess.Move.from_uci(move)
        rp = chess.Move.from_uci(next_moves[0])
        # there is no fork when the piece is down
        if mv.to_square == rp.to_square:
            return False

        board_after_move.set_piece_at(mv.to_square, board.piece_map()[mv.from_square])
        board_after_move.remove_piece_at(mv.from_square)
        number_of_material_gains = 0
        for followup in board_after_move.legal_moves:
            # if this is the same piece
            if mv.to_square == followup.from_square:
                mg = self.is_material_gain(followup.uci(), board_after_move)
                if mg:
                    number_of_material_gains += 1
        if number_of_material_gains < 2:
            return False
        return True

    def is_only_possible(self, sf_move):
        if len(sf_move[4]) == 0: return True
        return False

    def is_variant_end(self, sf_move, board):
        board.push(chess.Move.from_uci(sf_move))
        return board.is_variant_end()

    def is_variant_loss(self, sf_move, board):
        board.push(chess.Move.from_uci(sf_move))
        return board.is_variant_loss()

    def is_insufficient_material(self, sf_move, board):
        board.push(chess.Move.from_uci(sf_move))
        return board.is_insufficient_material()

    def is_lomonosov_endgame(self, sf_move, board):
        board.push(chess.Move.from_uci(sf_move))
        if len(board.piece_map()) < 8: return True
        return False

    def apply_all_filters(self, move_entry):
        # if false, then false
        if self.min_centipawn_filter(move_entry[3], move_entry[4][0]): return True
        if self.is_material_gain(move_entry[3][0], chess.Board(fen=move_entry[1])): return True
        if self.is_fork(move_entry, chess.Board(fen=move_entry[1])): return True
        if self.is_only_possible(move_entry): return True
        if self.is_variant_end(move_entry[3][0], chess.Board(fen=move_entry[1])): return True
        if self.is_variant_loss(move_entry[3][0], chess.Board(fen=move_entry[1])): return True
        if self.is_insufficient_material(move_entry[3][0], chess.Board(fen=move_entry[1])): return True
        if self.is_lomonosov_endgame(move_entry[3][0], chess.Board(fen=move_entry[1])): return True
        return False

    def process(self):
        # TODO do sth with centipawns
        new_moves = []
        current_turn = True  # True is White
        mainline_iter = iter(self.game.mainline_moves())
        # move entry = (move number, fen position, game_move, (best_move, score, [possible continuation]), [(other_move, score)])
        for move_entry in self.sf_moves:
            # if none of filters were True
            if not self.apply_all_filters(move_entry):
                new_moves.append(move_entry)
        return new_moves