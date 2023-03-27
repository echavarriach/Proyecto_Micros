from chess_assistant import Estado_Juego, Movimiento
import copy
juego_temporal = Estado_Juego()


# Clase madre
class pieza:
    # promotion = False

    def __init__(self, tipo, color, fila, col, cas_avail, cas_take, board):
        self.tipo = " "  # Define cuál pieza es
        self.color = color
        self.fila = fila
        self.col = col
        self.cas_avail = []  # Define las casillas donde se puede mover
        self.cas_take = []  # Define las casillas donde puede comer
        self.board = board


class pawn(pieza):
    def __init__(self, tipo, color, fila, col, cas_avail, cas_take,
                 board, historial_mov):
        super().__init__(tipo, color, fila, col, cas_avail, cas_take, board)
        self.tipo = tipo
        self.cuadro_alpaso = ()
        self.historial_mov = historial_mov
        self.get_cas_avail()
        self.get_cas_take()

    def get_cas_avail(self):
        # Se revisa si la self es blanca para asignar los valores
        # en los que se van a poner dos cuadros
        if self.color == "w":
            a = -1  # Incremento fila
            b = 6  # Fila inicial
        else:
            a = 1  # Incremento fila
            b = 1  # Fila inicial
        # Si la posición aledaña está vacía se asigna a su lista de
        # posiciones disponibles, la posición vieja se vacía.
        if self.board[self.fila+a][self.col] == "--":
            self.cas_avail.append((self.fila+a, self.col))
        # Se revisa si está en posición inicial del pawn y de ser
        # así le permite moverse dos hacia delante.
        if self.fila == b:
            if self.board[self.fila+(a*2)][self.col] == "--":
                if self.board[self.fila+a][self.col] == "--":
                    self.cas_avail.append((self.fila+(a*2), self.col))

    def get_cas_take(self):

        # Parametriza a para usar una misma ecuación.
        if self.color == "w":
            a = -1
        else:
            a = 1

        # Revisa si es posible comer hacia la diagonal que va
        # a la izquierda del tablero
        if (self.col != 7 and self.color == "b") or self.color == "w":
            if self.board[self.fila+a][self.col+a] != "--" and self.board[self.fila+a][self.col+a][0] != self.color:
                self.cas_take.append((self.fila+a, self.col+a))

        # Revisa si es posible comer hacia la diagonal que va
        # a la derecha del tablero
        if (self.col != 7 and self.color == "w") or self.color == "b":
            if self.board[self.fila+a][self.col-a] != "--" and self.board[self.fila+a][self.col-a][0] != self.color:
                self.cas_take.append((self.fila+a, self.col-a))

        # Se encarga de revisar si es posible comer al paso, de ser así agrega
        # la casilla a cas_take para que se pinte de amarillo y también la
        # agrega a cuadro_alpaso que se usa posteriormente para retirar
        # al peón que se comió.
        if self.historial_mov != []:
            if self.board[self.historial_mov[1][0]][self.historial_mov[1][1]][1] == "P":
                if (self.fila == 3) and (self.color == "w") and ((self.historial_mov[1][0] - self.historial_mov[0][0]) == 2):
                    self.cas_take.append(
                        (self.historial_mov[1][0] - 1, self.historial_mov[1][1]))
                    self.cuadro_alpaso = (
                        (self.historial_mov[1][0] - 1, self.historial_mov[1][1]))
                elif (self.fila == 4) and (self.color == "b") and ((self.historial_mov[0][0] - self.historial_mov[1][0]) == 2):
                    self.cas_take.append(
                        (self.historial_mov[1][0] + 1, self.historial_mov[1][1]))
                    self.cuadro_alpaso = (
                        self.historial_mov[1][0] + 1, self.historial_mov[1][1])


class bishop(pieza):

    def __init__(self, tipo, color, fila, col, cas_avail, cas_take, board):
        super().__init__(tipo, color, fila, col, cas_avail, cas_take, board)
        self.tipo = tipo
        self.get_cas_avail_take()

    def get_cas_avail_take(self):
        d1 = 0
        d2 = 0
        d3 = 0
        d4 = 0
        for i in range(1, 8):  # Se revisa en un rango de 8
            if self.col + i <= 7 and self.fila + i <= 7 and d1 == 0:
                # Se revisa que no se salga del tablero usando posición+1>7.
                # Se revisa iteradamente la diagonal superior derecha y d1
                # indica si ya se encontró una pieza en el camino, si es
                # así se pasa a d1=1 y se detiene la iteración.

                # Si la posición revisada está vacía, se mete
                # dicha posición como disponible.
                if self.board[self.fila+i][self.col+i] == "--":
                    self.cas_avail.append((self.fila+i, self.col+i))
                else:
                    d1 = 1
                    # Si la pieza que está en el camino es
                    # de color opuesto, la añade para comer.
                    if self.board[self.fila+i][self.col+i][0] != self.color:
                        self.cas_take.append((self.fila+i, self.col+i))

            # La misma lógica, pero con la diagonal superior izquierda
            if self.col-i >= 0 and self.fila+i <= 7 and d2 == 0:
                if self.board[self.fila+i][self.col-i] == "--":
                    self.cas_avail.append((self.fila+i, self.col-i))
                else:
                    d2 = 1
                    if self.board[self.fila+i][self.col-i][0] != self.color:
                        self.cas_take.append((self.fila+i, self.col-i))

            # La misma lógica, pero con la diagonal inferior izquierda
            if self.col-i >= 0 and self.fila-i >= 0 and d3 == 0:
                if self.board[self.fila-i][self.col-i] == "--":
                    self.cas_avail.append((self.fila-i, self.col-i))
                else:
                    d3 = 1
                    if self.board[self.fila-i][self.col-i][0] != self.color:
                        self.cas_take.append((self.fila-i, self.col-i))
            # La misma lógoca, pero con la diagonal inferior derecha
            if self.col + i <= 7 and self.fila - i >= 0 and d4 == 0:
                if self.board[self.fila-i][self.col+i] == "--":
                    self.cas_avail.append((self.fila-i, self.col+i))
                else:
                    d4 = 1
                    if self.board[self.fila-i][self.col+i][0] != self.color:
                        self.cas_take.append((self.fila-i, self.col+i))


class rook(pieza):

    def __init__(self, tipo, color, fila, col, cas_avail, cas_take, board):
        super().__init__(tipo, color, fila, col, cas_avail, cas_take, board)
        self.tipo = tipo
        self.get_cas_avail_take()

    def get_cas_avail_take(self):
        d1 = 0
        d2 = 0
        d3 = 0
        d4 = 0
        # Si la self es tipo Rook se revisa igual que el bishop,
        # nada más que por filas y columnas, no por diagonales
        for i in range(1, 8):
            if self.fila + i <= 7 and d1 == 0:
                if self.board[self.fila+i][self.col] == "--":
                    self.cas_avail.append((self.fila+i, self.col))
                else:
                    d1 = 1
                    if self.board[self.fila+i][self.col][0] != self.color:
                        self.cas_take.append((self.fila+i, self.col))
            if self.col+i <= 7 and d2 == 0:
                if self.board[self.fila][self.col+i] == "--":
                    self.cas_avail.append((self.fila, self.col+i))
                else:
                    d2 = 1
                    if self.board[self.fila][self.col+i][0] != self.color:
                        self.cas_take.append((self.fila, self.col+i))
            if self.fila-i >= 0 and d3 == 0:
                if self.board[self.fila-i][self.col] == "--":
                    self.cas_avail.append((self.fila-i, self.col))
                else:
                    d3 = 1
                    if self.board[self.fila-i][self.col][0] != self.color:
                        self.cas_take.append((self.fila-i, self.col))
            if self.col - i >= 0 and d4 == 0:
                if self.board[self.fila][self.col-i] == "--":
                    self.cas_avail.append((self.fila, self.col-i))
                else:
                    d4 = 1
                    if self.board[self.fila][self.col-i][0] != self.color:
                        self.cas_take.append((self.fila, self.col-i))


class queen(pieza):

    def __init__(self, tipo, color, fila, col, cas_avail, cas_take, board):
        super().__init__(tipo, color, fila, col, cas_avail, cas_take, board)
        self.tipo = tipo
        self.get_cas_avail_take()

    def get_cas_avail_take(self):
        d1 = 0
        d2 = 0
        d3 = 0
        d4 = 0
        q1 = 0
        q2 = 0
        q3 = 0
        q4 = 0

        # Tiene exactamente la misma lógica que la torre en esta parte.
        for i in range(1, 8):
            if self.fila + i <= 7 and q1 == 0:
                if self.board[self.fila+i][self.col] == "--":
                    self.cas_avail.append((self.fila+i, self.col))
                else:
                    q1 = 1
                    if self.board[self.fila+i][self.col][0] != self.color:
                        self.cas_take.append((self.fila+i, self.col))
            if self.col+i <= 7 and q2 == 0:
                if self.board[self.fila][self.col+i] == "--":
                    self.cas_avail.append((self.fila, self.col+i))
                else:
                    q2 = 1
                    if self.board[self.fila][self.col+i][0] != self.color:
                        self.cas_take.append((self.fila, self.col+i))
            if self.fila-i >= 0 and q3 == 0:
                if self.board[self.fila-i][self.col] == "--":
                    self.cas_avail.append((self.fila-i, self.col))
                else:
                    q3 = 1
                    if self.board[self.fila-i][self.col][0] != self.color:
                        self.cas_take.append((self.fila-i, self.col))
            if self.col - i >= 0 and q4 == 0:
                if self.board[self.fila][self.col-i] == "--":
                    self.cas_avail.append((self.fila, self.col-i))
                else:
                    q4 = 1
                    if self.board[self.fila][self.col-i][0] != self.color:
                        self.cas_take.append((self.fila, self.col-i))

        # Tiene exactamente la misma lógica que el alfil en esta parte.
        for i in range(1, 8):  # Se revisa en un rango de 8

            # Diagonal superior derecha
            if self.col + i <= 7 and self.fila + i <= 7 and d1 == 0:
                if self.board[self.fila+i][self.col+i] == "--":
                    self.cas_avail.append((self.fila+i, self.col+i))
                else:
                    d1 = 1
                    if self.board[self.fila+i][self.col+i][0] != self.color:
                        self.cas_take.append((self.fila+i, self.col+i))
            # Diagonal superior izquierda
            if self.col-i >= 0 and self.fila+i <= 7 and d2 == 0:
                if self.board[self.fila+i][self.col-i] == "--":
                    self.cas_avail.append((self.fila+i, self.col-i))
                else:
                    d2 = 1
                    if self.board[self.fila+i][self.col-i][0] != self.color:
                        self.cas_take.append((self.fila+i, self.col-i))
            # Diagonal inferior izquierda
            if self.col-i >= 0 and self.fila-i >= 0 and d3 == 0:
                if self.board[self.fila-i][self.col-i] == "--":
                    self.cas_avail.append((self.fila-i, self.col-i))
                else:
                    d3 = 1
                    if self.board[self.fila-i][self.col-i][0] != self.color:
                        self.cas_take.append((self.fila-i, self.col-i))
            # Diagonal inferior derecha
            if self.col + i <= 7 and self.fila - i >= 0 and d4 == 0:
                if self.board[self.fila-i][self.col+i] == "--":
                    self.cas_avail.append((self.fila-i, self.col+i))
                else:
                    d4 = 1
                    if self.board[self.fila-i][self.col+i][0] != self.color:
                        self.cas_take.append((self.fila-i, self.col+i))


class knight(pieza):

    def __init__(self, tipo, color, fila, col, cas_avail, cas_take, board):
        super().__init__(tipo, color, fila, col, cas_avail, cas_take, board)
        self.tipo = tipo
        self.enroque = []
        self.get_cas_avail_take()

    def get_cas_avail_take(self):
        # Se revisan las 8 L que se forman y además se corrobora que no
        # se vaya a salir de los límites del tablero antes de consultar.
        if self.col + 1 <= 7 and self.fila + 2 <= 7:
            if self.board[self.fila+2][self.col+1] == "--":
                self.cas_avail.append((self.fila+2, self.col+1))
            elif self.board[self.fila+2][self.col+1][0] != self.color:
                self.cas_take.append((self.fila+2, self.col+1))
        if self.col + 2 <= 7 and self.fila + 1 <= 7:
            if self.board[self.fila+1][self.col+2] == "--":
                self.cas_avail.append((self.fila+1, self.col+2))
            elif self.board[self.fila+1][self.col+2][0] != self.color:
                self.cas_take.append((self.fila+1, self.col+2))
        if self.col + 2 <= 7 and self.fila - 1 >= 0:
            if self.board[self.fila-1][self.col+2] == "--":
                self.cas_avail.append((self.fila-1, self.col + 2))
            elif self.board[self.fila-1][self.col+2][0] != self.color:
                self.cas_take.append((self.fila-1, self.col+2))
        if self.col + 1 <= 7 and self.fila - 2 >= 0:
            if self.board[self.fila-2][self.col+1] == "--":
                self.cas_avail.append((self.fila-2, self.col+1))
            elif self.board[self.fila-2][self.col+1][0] != self.color:
                self.cas_take.append((self.fila-2, self.col+1))
        if self.col - 1 >= 0 and self.fila-2 >= 0:
            if self.board[self.fila-2][self.col-1] == "--":
                self.cas_avail.append((self.fila-2, self.col-1))
            elif self.board[self.fila-2][self.col-1][0] != self.color:
                self.cas_take.append((self.fila-2, self.col-1))
        if self.col - 2 >= 0 and self.fila - 1 >= 0:
            if self.board[self.fila-1][self.col-2] == "--":
                self.cas_avail.append((self.fila-1, self.col-2))
            elif self.board[self.fila-1][self.col-2][0] != self.color:
                self.cas_take.append((self.fila-1, self.col-2))
        if self.col - 2 >= 0 and self.fila + 1 <= 7:
            if self.board[self.fila+1][self.col-2] == "--":
                self.cas_avail.append((self.fila+1, self.col-2))
            elif self.board[self.fila+1][self.col-2][0] != self.color:
                self.cas_take.append((self.fila+1, self.col-2))
        if self.col - 1 >= 0 and self.fila + 2 <= 7:
            if self.board[self.fila+2][self.col-1] == "--":
                self.cas_avail.append((self.fila+2, self.col-1))
            elif self.board[self.fila+2][self.col-1][0] != self.color:
                self.cas_take.append((self.fila+2, self.col-1))


class king(pieza):
    def __init__(self, tipo, color, fila, col, cas_avail, cas_take,
                 board, primerMovimiento):
        super().__init__(tipo, color, fila, col, cas_avail, cas_take, board)
        self.tipo = tipo
        self.enroqueCorto = False
        self. enroqueLargo = False
        self.primerMovimiento = primerMovimiento
        self.get_cas_avail_take()

    def get_cas_avail_take(self):
        quitar_avail = []
        quitar_take = []

        # Revisa las 8 posiciones aledañas del rey para ver si es
        # posible desplazarse o comer en estas
        if self.fila + 1 <= 7:
            if self.board[self.fila+1][self.col] == "--":
                self.cas_avail.append((self.fila+1, self.col))
            elif self.board[self.fila+1][self.col][0] != self.color:
                self.cas_take.append((self.fila+1, self.col))
        if self.col + 1 <= 7:
            if self.board[self.fila][self.col+1] == "--":
                self.cas_avail.append((self.fila, self.col+1))
            elif self.board[self.fila][self.col+1][0] != self.color:
                self.cas_take.append((self.fila, self.col+1))
        if self.col - 1 >= 0:
            if self.board[self.fila][self.col-1] == "--":
                self.cas_avail.append((self.fila, self.col-1))
            elif self.board[self.fila][self.col-1][0] != self.color:
                self.cas_take.append((self.fila, self.col-1))
        if self.fila - 1 >= 0:
            if self.board[self.fila-1][self.col] == "--":
                self.cas_avail.append((self.fila-1, self.col))
            elif self.board[self.fila-1][self.col][0] != self.color:
                self.cas_take.append((self.fila-1, self.col))
        if self.col - 1 >= 0 and self.fila + 1 <= 7:
            if self.board[self.fila+1][self.col-1] == "--":
                self.cas_avail.append((self.fila+1, self.col-1))
            elif self.board[self.fila+1][self.col-1][0] != self.color:
                self.cas_take.append((self.fila+1, self.col-1))
        if self.col + 1 <= 7 and self.fila - 1 >= 0:
            if self.board[self.fila-1][self.col+1] == "--":
                self.cas_avail.append((self.fila-1, self.col+1))
            elif self.board[self.fila-1][self.col+1][0] != self.color:
                self.cas_take.append((self.fila-1, self.col+1))
        if self.col + 1 <= 7 and self.fila + 1 <= 7:
            if self.board[self.fila+1][self.col+1] == "--":
                self.cas_avail.append((self.fila+1, self.col+1))
            elif self.board[self.fila+1][self.col+1][0] != self.color:
                self.cas_take.append((self.fila+1, self.col+1))
        if self.col - 1 >= 0 and self.fila - 1 >= 0:
            if self.board[self.fila-1][self.col-1] == "--":
                self.cas_avail.append((self.fila-1, self.col-1))
            elif self.board[self.fila-1][self.col-1][0] != self.color:
                self.cas_take.append((self.fila-1, self.col-1))

        # Revisa si se cumplen las condiciones iniciales de las piezas, así
        # como los espacios necesarios para enrocas, de ser así enciende
        # las booleanas de enroqueCorto o enroqueLargo.
        if self.tipo == "K" and self.color == "w" and self.primerMovimiento[0] == 1:
            if self.board[self.fila][self.col+1] == "--" and self.board[self.fila][self.col+2] == "--":
                if self.board[self.fila][self.col+3] == "wR" and self.primerMovimiento[2] == 1:
                    self.cas_avail.append((self.fila, self.col+2))
                    self.enroqueCorto = True
            if self.board[self.fila][self.col-1] == "--" and self.board[self.fila][self.col-2] == "--" and self.board[self.fila][self.col-3] == "--":
                if self.board[self.fila][self.col-4] == "wR" and self.primerMovimiento[3] == 1:
                    self.cas_avail.append((self.fila, self.col-2))
                    self.enroqueLargo = True
        if self.tipo == "K" and self.color == "b" and self.primerMovimiento[1] == 1:
            if self.board[self.fila][self.col+1] == "--" and self.board[self.fila][self.col+2] == "--":
                if self.board[self.fila][self.col+3] == "bR" and self.primerMovimiento[4] == 1:
                    self.cas_avail.append((self.fila, self.col+2))
                    self.enroqueCorto = True
            if self.board[self.fila][self.col-1] == "--" and self.board[self.fila][self.col-2] == "--" and self.board[self.fila][self.col-3] == "--":
                if self.board[self.fila][self.col-4] == "bR" and self.primerMovimiento[5] == 1:
                    self.cas_avail.append((self.fila, self.col-2))
                    self.enroqueLargo = True

        # Revisa si en las posiciones disponibles, se caería en un
        # jaque y de ser así las quita del arreglo.
        for disponible in self.cas_avail:
            juego_temporal.board = copy.deepcopy(self.board)
            mov = Movimiento((self.fila, self.col),
                             disponible, juego_temporal.board)
            juego_temporal.Jugada(mov, self)
            if self.check(juego_temporal.board):
                quitar_avail.append(disponible)
        for h in quitar_avail:
            self.cas_avail.remove(h)

        # Revisa si en las posiciones disponibles para comer del rey
        # se caería en un jaque y de ser así las quita del arreglo.
        for disponible in self.cas_take:
            juego_temporal.board = copy.deepcopy(self.board)
            mov = Movimiento((self.fila, self.col),
                             disponible, juego_temporal.board)
            juego_temporal.Jugada(mov, self)
            if self.check(juego_temporal.board):
                quitar_take.append(disponible)
        for r in quitar_take:
            self.cas_take.remove(r)

        # Quita la posibilidad de enrocar si la posición aledaña al rey,
        # del lado que se va a enrocar, está siendo atacada.
        if self.color == "w":
            if self.enroqueCorto and not ((7, 5) in self.cas_avail):
                self.enroqueCorto = False
                self.cas_avail.remove((7, 6))
            if self.enroqueLargo and not ((7, 3) in self.cas_avail):
                self.enroqueCorto = False
                self.cas_avail.remove((7, 2))
        elif self.color == "b":
            if self.enroqueCorto and not ((0, 5) in self.cas_avail):
                self.enroqueCorto = False
                self.cas_avail.remove((0, 6))
            if self.enroqueLargo and not ((0, 3) in self.cas_avail):
                self.enroqueCorto = False
                self.cas_avail.remove((0, 2))

    # Revisa si en la posición indicada del tablero se presenta un jaque.
    def check(self, board_temporal):
        total_take = []
        for a in range(8):
            for b in range(8):
                if self.color != board_temporal[a][b][0]:
                    if board_temporal[a][b][1] == "P":
                        objeto = pawn("P", board_temporal[a][b][0], a, b, [
                        ], [], board_temporal, [])
                    elif board_temporal[a][b][1] == "B":
                        objeto = bishop(
                            "B", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "R":
                        objeto = rook(
                            "R", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "Q":
                        objeto = queen(
                            "Q", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "N":
                        objeto = knight(
                            "N", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "K":
                        pass  # El rey nunca puede dar jaque
                    if board_temporal[a][b][1] != "K" and board_temporal[a][b] != "--":
                        if objeto.cas_take != []:
                            for t in objeto.cas_take:
                                if t not in total_take:
                                    total_take.append(t)
                elif board_temporal[a][b][1] == "K":
                    fila_rey = a
                    col_rey = b
        if (fila_rey, col_rey) in total_take:
            return True

    # Se consultan todas las casillas donde se puede mover alguna pieza
    # y esto se utiliza para ver si coinciden con alguna de las que se
    # puede mover el rey
    def total_avail(self, board_temporal):
        total_avail = []
        for a in range(8):
            for b in range(8):
                if self.color != board_temporal[a][b][0]:
                    if board_temporal[a][b][1] == "P":
                        objeto = pawn("P", board_temporal[a][b][0], a, b, [
                        ], [], board_temporal, [])
                    elif board_temporal[a][b][1] == "B":
                        objeto = bishop(
                            "B", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "R":
                        objeto = rook(
                            "R", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "Q":
                        objeto = queen(
                            "Q", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "N":
                        objeto = knight(
                            "N", board_temporal[a][b][0], a, b, [], [], board_temporal)
                    elif board_temporal[a][b][1] == "K":
                        pass
                    if board_temporal[a][b][1] != "K" and board_temporal[a][b] != "--":
                        if objeto.cas_avail != []:
                            for t in objeto.cas_avail:
                                if t not in total_avail:
                                    total_avail.append(t)
        return total_avail
