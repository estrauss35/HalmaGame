import tkinter as tk
from Board import Board
from MachinePlayer import MachinePlayer
import sys

class GameBoard(tk.Frame):
    def __init__(self, parent, hplayer, photo1=None, photo2=None, rows=8, columns=8, tlimit=30, color1="white", color2="black"):
        # General Initialization
        self.rows = rows
        self.columns = columns
        self.sqrSize = 32
        self.color1 = color1
        self.color2 = color2
        self.pieces = {}
        self.photo1 = photo1
        self.photo2 = photo2
        self.tlimit = tlimit
        self.humanPlayer = hplayer

        # Using this for later to distinguish between human and AI moves
        if hplayer == "green":
            self.humanTurn = 2
        elif hplayer == "red":
            self.humanTurn = 1

        # Holding where the latest tile moved from
        self.currentMoveCoords = ()

        self.totalPieces = 0

        # Initializer for the win text
        self.greenText = 0
        self.redText = 0

        self.turn = 2

        # Data representation of the board
        self.data_board = Board(rows)
        self.data_board.initRedPieces(int(rows/2))
        self.data_board.initGreenPieces(int(rows/2))

        # Image to show valid move locations
        self.moveHighlight = tk.PhotoImage(file="validmove.png")
        self.moveHighlight = self.moveHighlight.zoom(25)
        self.moveHighlight = self.moveHighlight.subsample(100)

        # Image to show latest move
        self.latestMove = tk.PhotoImage(file="latestMove.png")
        self.latestMove = self.latestMove.zoom(25)
        self.latestMove = self.latestMove.subsample(100)

        boardWidth = columns * self.sqrSize
        boardHeight = rows * self.sqrSize

        self.pieceTracker = {}

        # Creating the canvas
        tk.Frame.__init__(self, parent)
        self.board = tk.Canvas(self, borderwidth=10, highlightthickness=0, width=boardWidth, height=boardHeight,
                               background="SteelBlue2")

        self.board.bind("<Button-1>", self.playerClick)

        self.board.pack(side="top", fill="both", expand=True, padx=2, pady=2)

        self.board.bind("<Configure>", self.refresh)

        self.draw_pieces()

    # Method to update the board when the window is resized
    def refresh(self, event):
        xsize = int((event.width - 1) / self.columns)
        ysize = int((event.height - 1) / self.rows)
        self.sqrSize = min(xsize, ysize)
        self.board.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.sqrSize)
                y1 = (row * self.sqrSize)
                x2 = x1 + self.sqrSize
                y2 = y1 + self.sqrSize
                self.board.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.placePiece(name, self.pieces[name][0], self.pieces[name][1])
        self.board.tag_raise("piece")
        self.board.tag_lower("square")

    # Method to update the board manually without being resized
    def manualRefresh(self):
        self.board.delete("square")
        color = self.color2
        for row in range(self.rows):
            color = self.color1 if color == self.color2 else self.color2
            for col in range(self.columns):
                x1 = (col * self.sqrSize)
                y1 = (row * self.sqrSize)
                x2 = x1 + self.sqrSize
                y2 = y1 + self.sqrSize
                self.board.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
                color = self.color1 if color == self.color2 else self.color2
        for name in self.pieces:
            self.placePiece(name, self.pieces[name][0], self.pieces[name][1])
        self.board.tag_raise("piece")
        self.board.tag_lower("square")

    # Method to create a piece
    def createPiece(self, name, image, row, col):
        self.board.create_image(0, 0, tags=(name, 'piece'), image=image, anchor='center')
        self.placePiece(name, row, col)

    # Used in the createPiece method, just places the piece on the board after it is created
    def placePiece(self, name, row, col):
        self.pieces[name] = (row, col)
        x0 = (col * self.sqrSize) + int(self.sqrSize / 2)
        y0 = (row * self.sqrSize) + int(self.sqrSize / 2)
        self.board.coords(name, x0, y0)

    # Detecting win condition
    def detectWin(self):
        greenWin = False
        redWin = False

        # Checking if all the tiles in the green corner are filled with red tiles
        for coord in self.data_board.greenCorner:
            if self.data_board.get_piece_at(coord[0], coord[1]) == False or self.data_board.get_piece_at(coord[0], coord[1]) == 2:
                redWin = False
                break
            elif self.data_board.get_piece_at(coord[0], coord[1]) == 1:
                redWin = True

        # Checking if all the tiles in the red corner are filled with green tiles
        for coord in self.data_board.redCorner:
            if self.data_board.get_piece_at(coord[0], coord[1]) == False or self.data_board.get_piece_at(coord[0], coord[1]) == 1:
                greenWin = False
                break
            elif self.data_board.get_piece_at(coord[0], coord[1]) == 2:
                greenWin = True

        rtn = (redWin, greenWin)

        return rtn

    # Function to catch when a player clicks
    def playerClick(self, event):
        row = event.y
        col = event.x
        counter1 = 0
        counter2 = 0
        while row >= 0:
            row -= self.sqrSize
            counter1 += 1

        while col >= 0:
            col -= self.sqrSize
            counter2 += 1

        # Generating the coordinate of the tile that the user clicked
        coords = (counter1 - 1, counter2 - 1)

        # If a piece exists in the clicked tile and it is that color's turn...
        if self.data_board.get_piece_at(coords[0], coords[1]) == self.turn:
            humanPlayer.piece_selected = self.data_board.get_piece_at(coords[0], coords[1])
            humanPlayer.selected_coords = (coords[0], coords[1])
            self.currentMoveCoords = (coords[0], coords[1])

            # If no other tile has already been clicked, generate moves for this tile
            if humanPlayer.move_list == []:
                humanPlayer.prevSpots = []
                humanPlayer.generate_legal_moves(coords[0], coords[1], self.data_board.get_board())
                self.drawMoves(humanPlayer.move_list)

            # If another tile has been clicked, clear everything and select this one
            elif humanPlayer.move_list != []:
                self.board.delete("all")
                self.manualRefresh()
                self.draw_pieces()
                humanPlayer.clear_move_list()
                humanPlayer.prevSpots = []
                humanPlayer.generate_legal_moves(coords[0], coords[1], self.data_board.get_board())
                self.drawMoves(humanPlayer.move_list)
        # No piece exists at the tile, implying that the user is moving a piece
        else:
            coordinate_tuple = (coords[0], coords[1])
            if coordinate_tuple in humanPlayer.move_list:
                self.data_board.remove_piece_at(humanPlayer.selected_coords[0], humanPlayer.selected_coords[1])
                self.data_board.place_piece(humanPlayer.piece_selected, coords[0], coords[1])
                self.board.delete("all")
                self.manualRefresh()
                self.draw_pieces()
                self.drawLatestMove(self.currentMoveCoords, 'a')
                self.drawLatestMove(coordinate_tuple, 'b')
                humanPlayer.selected_coords = (coords[0], coords[1])
                win = self.detectWin()
                if win[0] is True and win[1] is True:
                    print("HOW DID YOU GET A TIE?")
                elif win[0] is True:
                    print("RED IS THE WINNER!")
                    self.redText = self.board.create_text(250, 250, font=("Purisa", 50), fill="red", text="Red Wins")
                    xOffset = self.findCenter(self.redText)
                    self.board.move(self.redText, xOffset, 0)
                elif win[1] is True:
                    print("GREEN IS THE WINNER!")
                    self.greenText = self.board.create_text(250, 250, font=("Purisa", 50), fill="green",
                                                            text="Green Wins")
                    xOffset = self.findCenter(self.greenText)
                    self.board.move(self.greenText, xOffset, 0)
                # Changing whose turn it is
                if self.turn == 1:
                    self.turn = 2
                else:
                    self.turn = 1
                humanPlayer.clear_move_list()
        return coords

    # Populate the GUI with tiles at the appropriate locations
    def draw_pieces(self):
        red_count = 0
        green_count = 0
        for i in range(0, self.data_board.get_height()):
            for j in range(0, self.data_board.get_width()):
                if self.data_board.get_piece_at(i, j) == 1:
                    self.createPiece("p1_" + str(red_count), photo, i, j)
                    red_count += 1
                elif self.data_board.get_piece_at(i, j) == 2:
                    self.createPiece("p2_" + str(green_count), p2, i, j)
                    green_count += 1

    # Find the center of the board
    def findCenter(self, item):
        coords = self.board.bbox(item)
        xOffset = (self.board.winfo_width() / 2) - ((coords[2] - coords[0]) / 2)
        return xOffset

    # Highlighting the squares that the currently selected piece can move to
    def drawMoves(self, moveList):
        name = -1
        for coords in moveList:
            self.board.create_image(0, 0, tags=name, image=self.moveHighlight, anchor='center')
            x0 = (coords[1] * self.sqrSize) + int(self.sqrSize / 2)
            y0 = (coords[0] * self.sqrSize) + int(self.sqrSize / 2)
            self.board.coords(name, x0, y0)
            name -= 1

    # Draw two circles, one where the moved piece just was and where it is now
    def drawLatestMove(self, coords, name):
        self.board.create_image(0, 0, tags=name, image=self.latestMove, anchor='center')
        x0 = (coords[1] * self.sqrSize) + int(self.sqrSize / 2)
        y0 = (coords[0] * self.sqrSize) + int(self.sqrSize / 2)
        self.board.coords(name, x0, y0)


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=True, height=True)
    root.minsize(width=666, height=666)
    photo = tk.PhotoImage(file="red.png")
    photo = photo.zoom(25)
    photo = photo.subsample(100)

    p2 = tk.PhotoImage(file="green.png")
    p2 = p2.zoom(25)
    p2 = p2.subsample(100)

    humanPlayer = MachinePlayer()

    bsize = int(sys.argv[1])
    timeLimit = int(sys.argv[2])
    hPlayer = sys.argv[3]

    board = GameBoard(root, hPlayer, columns=bsize, rows=bsize, tlimit=timeLimit)
    board.master.title("HALMA GAME")

    board.pack(side="top", fill="both", expand="true", padx=4, pady=4)
    root.mainloop()
