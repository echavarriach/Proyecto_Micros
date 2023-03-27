# Este documento almacena toda la información actual del juego.
# También determina las jugadas válidas en el movimiento actual
# Mantiene un registro de los movimientos (puede deshacer jugadas y así)
class Estado_Juego():
    def __init__(self):
        # Se crea una nueva clase que va a representar el tablero del juego,
        # En este caso, es una lista 2D y 8x8, cada elemeto de la lista tiene
        # 2 caracteres strings, el primero indica el color b:black o w:white
        # El segundo indica el tipo de pieza R:Roock N:Nkight B:Bishop Q:Queen
        # K:King y P:Pawn. Por último, un espacio vacío se representa "--"
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"], ]
        self.mueve_blanco = True
        self.registro_movimiento = []  # Move log

    def Jugada(self, movimiento, objeto):
        # Se "mueven" las piezas
        self.board[movimiento.start_fila][movimiento.start_colum] = "--"
        pos_final = movimiento.pieza_movida
        self.board[movimiento.end_fila][movimiento.end_colum] = pos_final
        if objeto.tipo == "K":
            if objeto.enroqueCorto and objeto.tipo == "K":
                if objeto.color == "w" and movimiento.end_colum == 6:
                    self.board[7][7] = "--"
                    self.board[7][5] = "wR"
                    movimiento.end_colum = 6
                if objeto.color == "b" and movimiento.end_colum == 6:
                    self.board[0][7] = "--"
                    self.board[0][5] = "bR"
                    movimiento.end_colum = 6
            if objeto.enroqueLargo and objeto.tipo == "K":
                if objeto.color == "w" and movimiento.end_colum == 2:
                    self.board[7][0] = "--"
                    self.board[7][3] = "wR"
                    movimiento.end_colum = 2
                if objeto.color == "b" and movimiento.end_colum == 2:
                    self.board[0][0] = "--"
                    self.board[0][3] = "bR"
                    movimiento.end_colum = 2
        # Se almacena el movimiento realizado
        self.registro_movimiento.append(movimiento)
        # Esto es para que de fijo se tenga que mover una ficha negra después
        # de una blanca, ESTO PUEDE SER LO QUE SE MODIFIQUE AL HACER EL BOTÓN
        # QUE SALTA LA JUGADA DEL OPONENTE
        # NOTA:
        # DE MOMENTO NO HACE NADA, SOLO CAMBIA DE TRUE A FALSE,
        # PERO CUANDO YA SE PONGAN LAS REGLAS DE JUEGO AHÍ VA A SER ÚTIL ESTA
        # VARIABLE, LE PUEDO PONER UN IF PARA QUE SOLO PUEDA MOVER UNA BLANCA
        # Y LUEGO SOLO PUEDA MOVER UNA NEGRA PERO ESTO CAMBIA SI EN UNA JUGADA
        # SE PUEDEN MOVER 2 PIEZAS BLANCAS AL MISMO TIEMPO
        self.mueve_blanco = not self.mueve_blanco


class Movimiento():
    # Se usan diccionarios que le asigna valores a llaves string para
    # las filas y columna según la notación del ajedres (letras:columnas
    # y números:filas)
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1,
                     "8": 0}
    # Esta línea hace lo inverso de la anterior
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_colums = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6,
                       "h": 7}
    # Esta línea hace lo inverso de la anterior
    colums_to_files = {v: k for k, v in files_to_colums.items()}

    def __init__(self, start_sq, end_sq, board):
        # Variables que facilitan el manejo de los atributos de la clase
        # para tenerlos ya separados en filas y columnas.
        self.start_fila = start_sq[0]
        self.start_colum = start_sq[1]
        self.end_fila = end_sq[0]
        self.end_colum = end_sq[1]
        # Estas variables solo almacenan la información del movimiento o jugada
        # Y adicionalmente si se captura una pieza del oponente
        self.pieza_movida = board[self.start_fila][self.start_colum]
        self.pieza_capturada = board[self.end_fila][self.end_colum]

    def Notacion_chess(self):
        # Devuelve la notación de ajedrez para la casilla donde está la pieza
        # que quiero mover y la notación del cuadro a donde la quiero mover
        notacion_in = self.letra_numero(self.start_fila, self.start_colum)
        notacion_fi = self.letra_numero(self.end_fila, self.end_colum)
        return notacion_in + notacion_fi

    def letra_numero(self, fila, columna):
        # Devuelve la notación de ajedrez, primero columna y luego fila (ej:a1)
        return self.colums_to_files[columna] + self.rows_to_ranks[fila]


class Estado_promotion_b():
    # Se crea una nueva clase que va a representar la interfaz de selección
    # del promotion pawns de color negro.
    # En este caso, es una lista 2D y 2x2, cada elemeto de la lista tiene
    # 2 caracteres strings, el primero indica el color b:black
    # El segundo indica el tipo de pieza R:Roock N:Nkight B:Bishop Q:Queen
    def __init__(self):
        self.board = [
            ["bQ", "bR"],
            ["bB", "bN"],
        ]


class Estado_promotion_w():
    # Se crea una nueva clase que va a representar la interfaz de selección
    # del promotion pawns de color blanco.
    # En este caso, es una lista 2D y 2x2, cada elemeto de la lista tiene
    # 2 caracteres strings, el primero indica el color w:white
    # El segundo indica el tipo de pieza R:Roock N:Nkight B:Bishop Q:Queen
    def __init__(self):
        self.board = [
            ["wQ", "wR"],
            ["wB", "wN"],
        ]


class cambiar_board():
    def __init__(self):
        # Se crea una nueva clase que va a representar el tablero del juego,
        # En este caso, es una lista 2D y 8x8, cada elemeto de la lista tiene
        # 2 caracteres strings, el primero indica el color b:black o w:white
        # El segundo indica el tipo de pieza R:Roock N:Nkight B:Bishop Q:Queen
        # K:King y P:Pawn. Por último, un espacio vacío se representa "--"
        self.board = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "wP", "wR", "wN", "wB", "wQ", "wK", "--"],
            ["--", "bP", "bR", "bN", "bB", "bQ", "bK", "--"],
        ]

    def Jugada(self, mov_in, mov_fin, origen, destino):
        # Se "mueven" las piezas
        self.board[mov_in[0]][mov_in[1]] = origen
        self.board[mov_fin[0]][mov_fin[1]] = destino
