from typing import Dict
import os
import chess.pgn
from chess.engine import PovScore, Cp
import io

INACCURACY_THRESHOLD = 50
MISTAKE_THRESHOLD = 100
BLUNDER_THRESHOLD = 200
TIME_PER_MOVE = 0.3
ENGINE_PATH = "/usr/local/bin/stockfish"


def read_game(pgn_string: str) -> chess.pgn.Game:
    pgn = io.StringIO(pgn_string)
    return chess.pgn.read_game(pgn)


def calculate_summary(diff: int, turn: bool, results: Dict):
    # Update summary for side which just made a move (not that is going to)
    color = "black" if turn else "white"

    if INACCURACY_THRESHOLD < diff:
        if MISTAKE_THRESHOLD < diff:
            if BLUNDER_THRESHOLD < diff:
                results[color]["blunders"] += 1
            else:
                results[color]["mistakes"] += 1
        else:
            results[color]["innacuracies"] += 1


def analyze_game(pgn_string: str) -> Dict:
    # Main logic, go through each move and evaluate position.
    # Update results accordingly and then return it.
    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
    game = read_game(pgn_string)
    prev_move_score = PovScore(Cp(0.2), turn=chess.WHITE)

    results = {
        "white": {
            "innacuracies": 0,
            "mistakes": 0,
            "blunders": 0
        },
        "black": {
            "innacuracies": 0,
            "mistakes": 0,
            "blunders": 0
        }
    }

    for node in game.mainline():
        board = node.board()
        turn = board.turn
        res = engine.analyse(board=node.board(),
                             limit=chess.engine.Limit(time=TIME_PER_MOVE))
        score = res.get("score")

        if board.is_checkmate():
            return results

        if not score.is_mate():
            if prev_move_score.is_mate():  # blunder by not finding a mate
                calculate_summary(1000, turn, results)
            else:
                if turn:  # White to move, calculate diff for black
                    diff_black = prev_move_score.black().cp - score.black().cp
                    calculate_summary(diff_black, turn, results)

                else:
                    diff_white = prev_move_score.white().cp - score.white().cp
                    calculate_summary(diff_white, turn, results)

        else:
            # There's a mate in x moves
            if not prev_move_score.is_mate():  # blunder by allowing mate
                calculate_summary(1000, turn, results)
            # If mate still exists, don't count a blunder.

        prev_move_score = score
    return results


game1 = '''[Event "Rated Blitz game"]
[Site "https://lichess.org/EEjpsPHx"]
[Date "2021.07.20"]
[White "dkol"]
[Black "happydogue"]
[Result "1-0"]
[UTCDate "2021.07.20"]
[UTCTime "10:39:55"]
[WhiteElo "1809"]
[BlackElo "1825"]
[WhiteRatingDiff "+6"]
[BlackRatingDiff "-6"]
[Variant "Standard"]
[TimeControl "300+3"]
[ECO "B20"]
[Opening "Sicilian Defense: Wing Gambit"]
[Termination "Normal"]

1. e4 c5 2. b4 e6 3. bxc5 Bxc5 4. d4 Bb6 5. Nf3 Nf6 6. e5 Nd5 7. c4 Ne7 8. Bd3 O-O 9. Bxh7+ Kxh7 10. Ng5+ Kg6 11. Qg4 Ba5+ 12. Kf1 Qb6 13. Nxe6+ Kh7 14. Qxg7# 1-0
'''

game2 = '''[Event "USSR Championship"]
[Site "https://lichess.org/5kFoQLlu"]
[Date "1933.08.28"]
[Round "11"]
[White "Leonid Savitsky"]
[Black "Mikhail Botvinnik"]
[Result "0-1"]
[WhiteElo "?"]
[BlackElo "?"]
[Variant "Standard"]
[TimeControl "-"]
[ECO "A47"]
[Opening "Queen's Indian Defense"]
[Termination "Normal"]

1. d4 Nf6 2. Nf3 b6 3. g3 Bb7 4. c4 e5 5. dxe5 Ng4 6. Bg2 Nxe5 7. Nbd2 Be7 8. O-O Ng6 9. Nb1 O-O 10. Nc3 Na6 11. h4 Bf6 12. h5 Ne7 13. Qc2 Nc5 14. Be3 Re8 15. Rad1 Bxc3 16. Bxc5 Bf6 17. Bd4 Bxd4 18. Rxd4 Nc6 19. Rg4 Qf6 20. Ng5 Qh6 21. Bd5 Re7 22. Qf5 Rf8 23. Be4 Re5 24. Qxh7+ Qxh7 25. Bxh7+ Kh8 26. Bd3 Nb4 27. f4 Re7 28. h6 gxh6 29. Rh4 Kg7 30. Nf3 Nxd3 31. exd3 Re3 32. Nd4 f5 33. g4 fxg4 34. Rxg4+ Kh7 35. Nc2 Re2 36. Re1 Rxc2 0-1
'''

game3 = '''[Event "Rated Bullet game"]
[Site "https://lichess.org/juoWnjn3"]
[Date "2021.09.27"]
[White "dkol"]
[Black "Lepidipidi_la_mmatau"]
[Result "0-1"]
[UTCDate "2021.09.27"]
[UTCTime "18:57:19"]
[WhiteElo "1607"]
[BlackElo "1695"]
[WhiteRatingDiff "-4"]
[BlackRatingDiff "+16"]
[Variant "Standard"]
[TimeControl "120+1"]
[ECO "B01"]
[Opening "Scandinavian Defense: Mieses-Kotroc Variation"]
[Termination "Normal"]

1. e4 d5 2. exd5 Qxd5 3. Nf3 Bg4 4. Be2 Nf6 5. O-O c6 6. h3 h5 7. hxg4 hxg4 8. Nc3 Qd6 9. Ng5 Qh2# 0-1
'''


def run():
    print("Analysing games: ")
    result_1 = analyze_game(game1)
    result_2 = analyze_game(game2)
    result_3 = analyze_game(game3)
    print("Game 1 analysis: ", result_1)
    print("Game 2 analysis: ", result_2)
    print("Game 3 analysis: ", result_3)
    os._exit(os.EX_OK)


if __name__ == "__main__":
    run()
