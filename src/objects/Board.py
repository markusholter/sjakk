from flask import current_app

class Board:
    def __init__(self):
        self.board: list[list[tuple[str, str]]] = self.make_board()
        self.rows: list[str] = [str(x) for x in range(8, 0, -1)]
        self.cols: list[str] = ["A", "B", "C", "D", "E", "F", "G", "H"]

    # Make board top to bottom from the white players perspective
    def make_board(self):
        piece_positions = {
            0: ["rook-b.svg", "knight-b.svg", "bishop-b.svg", "queen-b.svg", "king-b.svg", "bishop-b.svg", "knight-b.svg", "rook-b.svg"],
            1: ["pawn-b.svg"] * 8,
            6: ["pawn-w.svg"] * 8,
            7: ["rook-w.svg", "knight-w.svg", "bishop-w.svg", "queen-w.svg", "king-w.svg", "bishop-w.svg", "knight-w.svg", "rook-w.svg"]
        }

        return [
            [
                ("cell black", piece_positions.get(i, [""] * 8)[j], f"{i} {j}") if (i + j) % 2 == 1 
                else ("cell white", piece_positions.get(i, [""] * 8)[j], f"{i} {j}")
                for j in range(8)
            ]
            for i in range(8)
        ]
    
    def get_white_board(self):
        return self.rows, self.cols, self.board
    
    def get_black_board(self):
        return self.rows[::-1], self.cols[::-1], [x[::-1] for x in self.board][::-1]
    
    def turn(self, move: str):
        current_app.logger.info(move)

        start = [int(x) for x in move.split(",")[0].split(" ")]
        end = [int(x) for x in move.split(",")[1].split(" ")]
        
        
        if not self.board[start[0]][start[1]][1]:
            return False
        if self.board[end[0]][end[1]][1]:
            return False
        
        piece = self.board[start[0]][start[1]][1]

        self.board[end[0]][end[1]] = (self.board[end[0]][end[1]][0], piece, self.board[end[0]][end[1]][2])
        self.board[start[0]][start[1]] = (self.board[start[0]][start[1]][0], "", self.board[start[0]][start[1]][2])
        return True



if __name__ == "__main__":
    board = Board()
    for row in board.board:
        print(row)