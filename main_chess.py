import copy
import pygame as p
from chess_assistant import Estado_Juego, Movimiento, Estado_promotion_b, cambiar_board
from chess_assistant import Estado_promotion_w
from Clases import pawn, bishop, rook, queen, knight, king
import random


# Colores del tablero
white = p.Color("white")
brown = 0x01579b
# Colores para movimientos permitidos
lightgreen = 0x81c784
green = 0x43a047
# Color para comer
yellow = p.Color("yellow")
# Colores para movimientos no permitidos
red = 0xffab91
darkred = p.Color("red")

p.init()  # Inicialización de pygame

# Variables que definen el tamaño del tablero (display)
alto = 512
ancho = 512
dimension = 8  # Porque un tablero de ajerez es 8x8
SQ_size = alto // dimension
max_FPS = 15  # Variable necesaria para la animacion del juego
imagenes = {}


# Se necesita que las imagenes del juego se carguen una sola vez, porque
# si no, se va laggear el juego
# Entonces, se inicializa un diccionario global que almacene las imagenes
# Este diccionario va a llamarse una sola vez en el main
def load_images():
    piezas = ["wP", "wR", "wN", "wB", "wK", "wQ"]
    piezas += ["bP", "bR", "bN", "bB", "bK", "bQ"]
    for pieza in piezas:
        imagen = p.image.load("imagenes/" + pieza + ".png")
        imagenes[pieza] = p.transform.scale(imagen, (SQ_size, SQ_size))


# El driver principal del código, se encarga de recibir las entradas del
# usuario y de actualizar los graficos
def main():

    screen = p.display.set_mode((ancho, alto))  # Genera el display
    reloj = p.time.Clock()
    screen.fill(white)
    juego = Estado_Juego()
    juego.board = AsignarTablero(juego.board)
    juego_temporal = Estado_Juego()
    cas_disp = []
    cas_tomar = []
    primerMovimiento = [1, 1, 1, 1, 1, 1]
    historial_mov = [(0, 0), (0, 0)]
    vsPC = False
    TurnoPC = False
    load_images()
    running = True
    ValidosenCheck = []
    jaque = "-"
    cuadro_selec = ()  # Tupla (fila, columna) que Va a iniciar vacía,
    # porque no hay ningún cuadro seleccionado, además, guarda la
    # información del último click del usuario
    historial_clicks = []  # 2 Tuplas (fila, columna) que guardan la
    # información de donde el usuario hizo click. EJ: [(6,4),(4,4)]
    random.seed()
    vsPC = EscogerModo()
    print(vsPC)
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Detecta click del mouse
            elif e.type == p.MOUSEBUTTONDOWN or (vsPC and TurnoPC):
                if not TurnoPC:
                    ubicacion_mouse = p.mouse.get_pos()  # Posición (x,y) del mouse

                    # Variables para obtener la fila y la columna donde está el
                    # mouse y cual pieza se eligió
                    columna = ubicacion_mouse[0]//SQ_size
                    fila = ubicacion_mouse[1]//SQ_size

                    # Caso en que haya seleccionado el mismo cuadro 2 veces
                    if cuadro_selec == (fila, columna):
                        cuadro_selec = ()  # Se "deselecciona" el cuadro (Vacío)
                        historial_clicks = []  # Se limpia el historial de clicks

                    # Caso en el que se seleccione un cuadro diferente, o no
                    # se haya seleccionado ninguno aún.
                    else:
                        cuadro_selec = (fila, columna)

                        # Si se escoge una casilla no vacía o ya se tenía un
                        # click, se procede a guardar el cuadro en el
                        # historial de clicks
                        if juego.board[fila][columna] != "--" or len(historial_clicks) == 1:
                            historial_clicks.append(cuadro_selec)

                        # Si sólo se tiene seleccionada la pieza con el 1er click
                        # Se crea un objeto con los atributos de la pieza escogida
                        # Guarda array y array2 que son necesarias para pintar el
                        # tablero.
                        if len(historial_clicks) == 1:
                            # if jaque!="-": ValidosenCheck = MovValidosCheck(juego.board, juego_temporal, historial_mov, ValidosenCheck, primerMovimiento)
                            objeto1 = CrearObjeto(
                                historial_clicks[0], juego.board, historial_mov, primerMovimiento, ValidosenCheck, jaque)
                            cas_disp = objeto1.cas_avail
                            cas_tomar = objeto1.cas_take
                else:  # Si es el turno de la PC
                    escoge = True
                    # Procede a escoger una casilla random de todo el tablero
                    while escoge:
                        pcfila = random.randint(0, 7)
                        pccol = random.randint(0, 7)
                        # Procede, si la casilla no está vacía y es negra,
                        # a crear un objeto de esa casilla y con esto escoger
                        # de sus casillas disponibles(si las tiene) o de sus
                        # casillas por comer(si las tiene) un movimiento, en
                        # caso de no tener ninguna, escoge otra casilla
                        if juego.board[pcfila][pccol] != "--" and juego.board[pcfila][pccol][0] == "b":
                            historial_clicks.append((pcfila, pccol))
                            objeto1 = CrearObjeto(
                                (pcfila, pccol), juego.board, historial_mov, primerMovimiento, ValidosenCheck, jaque)
                            cas_disp = objeto1.cas_avail
                            cas_tomar = objeto1.cas_take
                            rand = random.randint(0, 1)
                            if (rand == 0 or cas_tomar == []) and cas_disp != []:
                                historial_clicks.append(
                                    random.choice(cas_disp))
                                escoge = False
                            elif rand == 1 and cas_tomar != []:
                                historial_clicks.append(
                                    random.choice(cas_tomar))
                                escoge = False
                            else:
                                historial_clicks = []
                # Si ya escogió hacia donde se quiere mover, se
                # entra a este condicional.
                if len(historial_clicks) == 2:
                    # El if corrobora que la combinación de las dos elecciones
                    # es válida, es decir, que es un movimiento legal.
                    if Valida(historial_clicks, juego_temporal, historial_mov, juego.board, objeto1):
                        # Se utiliza la clase "Movimiento", que permite
                        # llevar un mejor orden, permite ver la notación.
                        mov_in = historial_clicks[0]
                        mov_fin = historial_clicks[1]
                        mov = Movimiento(mov_in, mov_fin, juego.board)
                        print(mov.Notacion_chess())

                        # Almacena el movimiento que se acaba de hacer
                        # y se va a mantener ahí, hasta que se haga otro válido
                        historial_mov = (
                            historial_clicks[0], historial_clicks[1])

                        # Actualiza atributos del objeto, en caso de que se
                        # vaya a dar una promoción
                        if isinstance(objeto1, pawn):
                            objeto1.fila = mov_fin[0]
                            objeto1.col = mov_fin[1]
                            mov.pieza_movida = promotion(
                                objeto1, mov.pieza_movida)

                        # Se actualiza el tablero con la jugada
                        juego.Jugada(mov, objeto1)

                        # Modifica el arreglo de booleanas en caso de que
                        # se haya dado el primer movimiento en una de las
                        # piezas que afectan el enroque.
                        if juego.board[7][4] == "--" and primerMovimiento[0]:
                            primerMovimiento[0] = 0
                        if juego.board[0][4] == "--" and primerMovimiento[1]:
                            primerMovimiento[1] = 0
                        if juego.board[7][7] == "--" and primerMovimiento[2]:
                            primerMovimiento[2] = 0
                        if juego.board[7][0] == "--" and primerMovimiento[3]:
                            primerMovimiento[3] = 0
                        if juego.board[0][7] == "--" and primerMovimiento[4]:
                            primerMovimiento[4] = 0
                        if juego.board[0][0] == "--" and primerMovimiento[5]:
                            primerMovimiento[5] = 0

                        # Revisa si existe un jaque o un mate después del mov.
                        if vsPC:
                            TurnoPC = ~TurnoPC
                        jaque = check(juego.board, historial_mov)
                        if jaque != "-":
                            ValidosenCheck = MovValidosCheck(
                                juego.board, juego_temporal, historial_mov, ValidosenCheck, primerMovimiento)
                        checkmate(juego.board, historial_mov, ValidosenCheck)

                    # Se resetean las variables que guardan el último click
                    # del usuario y el historial de clicks.
                    cuadro_selec = ()
                    historial_clicks = []

        # Se encarga de pintar en pantalla el tablero, así
        # como los colores correspondientes en las otras casillas

        Dibujo_Estado_Juego(screen, juego, cas_disp,
                            cas_tomar, historial_clicks)
        reloj.tick(max_FPS)
        p.display.flip()


def EscogerModo():
    altotemp = 256
    anchotemp = 512
    dimension_temp = 2
    SQ_size_temp = anchotemp // dimension_temp
    screen1 = p.display.set_mode((anchotemp, altotemp))  # Genera el display
    reloj1 = p.time.Clock()
    screen1.fill(white)

    # Carga las imágenes desde la carpeta y las escala
    img1 = p.image.load("imagenes/" + "PC" + ".png")
    img2 = p.image.load("imagenes/" + "Asistente" + ".png")
    img1 = p.transform.scale(img1, (SQ_size_temp, SQ_size_temp))
    img2 = p.transform.scale(img2, (SQ_size_temp*0.9, SQ_size_temp*0.55))

    # Se genera un rectangulo para poner la imagen encima
    rectangulo1 = p.Rect(15, 65, SQ_size_temp, SQ_size_temp)

    # Se generan dos rectangulos para pintar el fondo
    rectangulo2 = p.Rect(0, 0, SQ_size_temp, SQ_size_temp)
    rectangulo3 = p.Rect(SQ_size_temp, 0, SQ_size_temp, SQ_size_temp)
    p.draw.rect(screen1, "white", rectangulo2)
    p.draw.rect(screen1, "blue", rectangulo3)

    # Pinta las imágenes
    screen1.blit(img1, rectangulo3)
    screen1.blit(img2, rectangulo1)

    # Se le hace flip a la pantalla
    reloj1.tick(max_FPS)
    p.display.flip()
    corriendo = True

    # Se obtiene cuál fue la selección del usuario y se retorna
    while corriendo:
        ubicacion_mouse1 = p.mouse.get_pos()
        colum = int(ubicacion_mouse1[0]//SQ_size_temp)
        for e in p.event.get():
            if e.type == p.QUIT:
                corriendo = False
            elif e.type == p.MOUSEBUTTONDOWN:
                colum = int(ubicacion_mouse1[0]//SQ_size_temp)
                corriendo = False
    screen1 = p.display.set_mode((ancho, alto))
    return colum


# Función encargada de realizar la coronación del pawn.
# Recibe a los atributos de la pieza actual para comprobar
# que cumple con las condiciones para realizar el promotion

def promotion(objeto2, mov):

    # Comprueba que la pieza se encuentre en las dos únicas filas posibles
    # para realizar la coronación, es decir, la última fila posible para
    # cada uno de los pawn de ambos lados del tablero.
    # La función, en caso de cumplirse las condiciones, retorna la pieza
    # seleccionada por el usuario y en caso de no cumplirse, se retorna
    # la pieza original y no se refleja ningún cambio.
    if objeto2.fila == 0 or objeto2.fila == 7:
        # Se comprueba que la pieza sea un pawn
        if objeto2.tipo == "P":
            # Variables definen el tamaño de la interfaz de selección temporal
            altotemp = 256
            anchotemp = 256

            screen1 = p.display.set_mode(
                (anchotemp, altotemp+64))  # Genera el display con las dimensiones dadas
            reloj1 = p.time.Clock()
            screen1.fill(white)

            p.font.init()
            font = p.font.Font('freesansbold.ttf', 16)
            texto = font.render(
                'Seleccione la pieza deseada', True, brown)
            screen1.blit(texto, (16, 288))

            # Determina el color de la pieza que está realizando la coronación,
            # para generar una interfaz de selección acorde al color.
            # Genera un "tablero" temporal de selección.
            if objeto2.color == "w":
                seleccion = Estado_promotion_w()
            else:
                seleccion = Estado_promotion_b()

            # Se inicializa el ciclo de estado que espera a la selección de la nueva pieza
            promoted = True
            dimension_temp = 2  # Es 2 ya que se va a generar una tablero de 2x2
            SQ_size_temp = anchotemp // dimension_temp  # Se define la escala

            # Carga las imágenes desde la carpeta y las escala
            imagenesG = {}
            piezas = ["wR", "wN", "wB", "wQ"]
            piezas += ["bR", "bN", "bB", "bQ"]
            for pieza in piezas:
                imagen = p.image.load("imagenes/" + pieza + ".png")
                imagenesG[pieza] = p.transform.scale(
                    imagen, (SQ_size_temp, SQ_size_temp))

            while promoted:

                # Detecta click del mouse
                ubicacion_mouse1 = p.mouse.get_pos()

                # Variables para obtener la fila y la columna donde está el
                # mouse y cual pieza se eligió
                colum = int(ubicacion_mouse1[0]//SQ_size_temp)
                fil = int(ubicacion_mouse1[1]//SQ_size_temp)

                for e in p.event.get():

                    # Espera a que el usuario dé click dentro del rango de selección
                    if e.type == p.MOUSEBUTTONDOWN and ubicacion_mouse1[1] <= 256:
                        # Regresa a la pantalla a las dimensiones originales y retorna
                        # la pieza del tablero temporal de selección
                        # que coincida con la fila y columna seleccionada por el usuario
                        screen1 = p.display.set_mode((ancho, alto))
                        return seleccion.board[fil][colum]

                colores = [white, brown]
                for f in range(dimension_temp):  # f: fila
                    for c in range(dimension_temp):  # c: columna
                        if colum == c and fil == f:
                            color = green
                        else:
                            color = colores[((f+c) % 2)]
                        left = c * SQ_size_temp
                        top = f * SQ_size_temp
                        p.draw.rect(screen1, color, p.Rect(
                            left, top, SQ_size_temp, SQ_size_temp))
                for f in range(dimension_temp):  # f:fila
                    for c in range(dimension_temp):  # c:columna
                        pieza1 = seleccion.board[f][c]
                        rectangulo1 = p.Rect(
                            c * SQ_size_temp, f * SQ_size_temp, SQ_size_temp, SQ_size_temp)
                        screen1.blit(imagenesG[pieza1], rectangulo1)
                reloj1.tick(max_FPS)
                p.display.flip()
        else:
            return mov
    else:
        return mov


# Función responsable de mostrar la interfaz
def Dibujo_Estado_Juego(screen, juego, cas_avail, cas_take, historial_clicks):
    # Dibuja los cuadros del tablero.
    Dibuja_Tablero(screen)

    # Si ya se seleccionó una casilla, se pintan los movimientos
    # válidos en verde o amarillo (si es posible comer) y los
    # inválidos en rojo.
    if len(historial_clicks) == 1:
        Posibles(screen, cas_avail, cas_take)
        Movimientos_Invalidos(screen, cas_avail, cas_take)

    # Dibuja las piezas encima del tablero pintado anteriormente.
    Dibuja_Piezas(screen, juego.board)


# Dibuja los cuadrados del tablero en el orden de aparición en la interfaz
def Dibuja_Tablero(screen):
    colores = [white, brown]
    for f in range(dimension):  # f: fila
        for c in range(dimension):  # c: columna
            color = colores[((f+c) % 2)]
            left = c * SQ_size
            top = f * SQ_size
            p.draw.rect(screen, color, p.Rect(left, top, SQ_size, SQ_size))


# Toma las casillas disponibles para moverse y comer, y pinta de rojo
# todas las que no son estas.
def Movimientos_Invalidos(screen, cas_avail, cas_take):
    colores = [red, darkred]
    for f in range(dimension):  # f: fila
        for c in range(dimension):  # c: columna
            color = colores[((f+c) % 2)]
            left = c * SQ_size
            top = f * SQ_size
            if not ((f, c) in cas_avail or (f, c) in cas_take):
                p.draw.rect(screen, color, p.Rect(left, top, SQ_size, SQ_size))


# Muestra las piezas en el tablero usando el Estado_Juego actual (class board)
def Dibuja_Piezas(screen, board):
    for f in range(dimension):  # f:fila
        for c in range(dimension):  # c:columna
            pieza = board[f][c]
            rectangulo = p.Rect(c * SQ_size, f * SQ_size, SQ_size, SQ_size)
            if pieza != "--":  # No es un espacio vacío.
                screen.blit(imagenes[pieza], rectangulo)


# Verifica que la combinación entre la primera posición escogida
# y la segunda sea válida, también se encarga de llevar los turnos puesto que
# sólo permite que sean intercalados y con blanco de primero.
def Valida(historial_clicks, juego_temporal, historial_mov, board, objeto):
    if historial_mov == []:
        noturno = "b"
    else:
        noturno = board[historial_mov[1][0]][historial_mov[1][1]][0]

    # Si la casilla escogida es una disponible, o una donde se puede comer y
    # además es el turno de las piezas de ese color, se permite el movimiento
    if (historial_clicks[1] in objeto.cas_avail or (historial_clicks[1] in objeto.cas_take)) and (noturno != objeto.color):
        # Verifica si es peón para corroborar una posible comida al paso
        if isinstance(objeto, pawn):
            if historial_clicks[1] == objeto.cuadro_alpaso:
                board[historial_mov[1][0]][historial_mov[1][1]] = "--"
        juego_temporal.board = copy.deepcopy(board)
        mov = Movimiento((objeto.fila, objeto.col),
                         (historial_clicks[1][0], historial_clicks[1][1]), juego_temporal.board)
        juego_temporal.Jugada(mov, objeto)
        if check(juego_temporal.board, historial_mov) == 1 and noturno == "b":
            return False
        elif check(juego_temporal.board, historial_mov) == 2 and noturno == "w":
            return False
        return True


# Esta función va a mostrar de color verde claro los posibles
# movimientos que pueden realizar las piezas
def Posibles(screen, cas_avail, cas_take):
    colores = [lightgreen, green]
    for f in range(dimension):  # f: fila
        for c in range(dimension):  # c: columna
            color = colores[((f+c) % 2)]
            left = c * SQ_size
            top = f * SQ_size
            if (f, c) in cas_avail or (f, c) in cas_take:
                p.draw.rect(screen, color, p.Rect(left, top, SQ_size, SQ_size))
    color = yellow
    for i in range(len(cas_take)):
        left = cas_take[i][1]*SQ_size  # Define la fila
        top = cas_take[i][0]*SQ_size  # Define la columna
        p.draw.rect(screen, color, p.Rect(left, top, SQ_size, SQ_size))


# Verifica cual pieza es la casilla escogida y crea un objeto
def CrearObjeto(Primer_click, board, historial_mov, primerMovimiento, ValidosenCheck, jaque):
    color = board[Primer_click[0]][Primer_click[1]][0]
    fila = Primer_click[0]
    col = Primer_click[1]
    # Cada uno de los condicionales revisa que tipo de pieza escogió el usuario
    # y crea un objeto con los atributos que pide dicha clase
    if board[Primer_click[0]][Primer_click[1]][1] == "P":
        objeto = pawn("P", color, fila, col, [], [], board, historial_mov)
    elif board[Primer_click[0]][Primer_click[1]][1] == "B":
        objeto = bishop("B", color, fila, col, [], [], board)
    elif board[Primer_click[0]][Primer_click[1]][1] == "R":
        objeto = rook("R", color, fila, col, [], [], board)
    elif board[Primer_click[0]][Primer_click[1]][1] == "Q":
        objeto = queen("Q", color, fila, col, [], [], board)
    elif board[Primer_click[0]][Primer_click[1]][1] == "N":
        objeto = knight("N", color, fila, col, [], [], board)
    elif board[Primer_click[0]][Primer_click[1]][1] == "K":
        objeto = king("K", color, fila, col, [], [], board, primerMovimiento)
    if (jaque == 1 and objeto.color == "w") or (jaque == 2 and objeto.color == "b"):
        quitar = []
        for i in objeto.cas_avail:
            j = ((objeto.fila, objeto.col), i)
            if j not in ValidosenCheck:
                quitar.append(i)
        for h in quitar:
            objeto.cas_avail.remove(h)
        quitar = []
        for i in objeto.cas_take:
            j = ((objeto.fila, objeto.col), i)
            if j not in ValidosenCheck:
                quitar.append(i)
        for h in quitar:
            objeto.cas_take.remove(h)
    return objeto


# Esta función simplemente revisa si alguna pieza está atacando al rey
def check(board, historial_mov):
    total_take = []
    a = 0
    b = 0
    # Define a cual rey se le va a consultar el jaque
    if historial_mov != ():
        color = board[historial_mov[1][0]][historial_mov[1][1]][0]
    else:
        color = "w"
    # Va casilla por casilla del tablero.
    for a in range(8):
        for b in range(8):
            # En caso de que la pieza sea del color que puede atacar al rey,
            # se procede a crear un objeto con dicha pieza y verificar si
            # dentro de las casillas en las que puede comer, está la del rey
            if color == board[a][b][0]:
                if board[a][b][1] == "P":
                    objeto = pawn("P", board[a][b][0],
                                  a, b, [], [], board, historial_mov)
                elif board[a][b][1] == "B":
                    objeto = bishop("B", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "R":
                    objeto = rook("R", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "Q":
                    objeto = queen("Q", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "N":
                    objeto = knight("N", board[a][b][0], a, b, [], [], board)
                if board[a][b][1] != "K" and board[a][b] != "--":
                    if objeto.cas_take != []:
                        for t in objeto.cas_take:
                            if t not in total_take:
                                total_take.append(t)
            # Se guardan las coordenadas del rey, para verificar si
            # en efecto está en jaque.
            elif board[a][b][1] == "K":
                fila_rey = a
                col_rey = b
    # Si alguna pieza lo ataca, se marca como Jaque.
    if (fila_rey, col_rey) in total_take:
        if color == "w":
            return 2
        elif color == "b":
            return 1
    else:
        return "-"


# Revisa el checkmate
def checkmate(board, historial_mov, ValidosenCheck):
    # Si el rey está siendo atacado y no se puede salvar sólo, jaque mate.
    if (check(board, historial_mov) != "-") and ValidosenCheck == []:
        print("Jaque mate")
        return True
    # Nota: falta agregar que otras piezas lo puedan salvar del
    # jaque y que no necesariamente sea un jaque mate.


def MovValidosCheck(board, juego_temporal, historial_mov, ValidosenCheck, primerMovimiento):
    ValidosenCheck = []
    a = 0
    b = 0
    if historial_mov != ():
        color = board[historial_mov[1][0]][historial_mov[1][1]][0]
    else:
        color = "b"
    # Va casilla por casilla del tablero.
    for a in range(8):
        for b in range(8):
            if color != board[a][b][0]:
                if board[a][b][1] == "P":
                    objeto = pawn("P", board[a][b][0],
                                  a, b, [], [], board, historial_mov)
                elif board[a][b][1] == "B":
                    objeto = bishop("B", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "R":
                    objeto = rook("R", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "Q":
                    objeto = queen("Q", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "N":
                    objeto = knight("N", board[a][b][0], a, b, [], [], board)
                elif board[a][b][1] == "K":
                    objeto = king("K", board[a][b][0], a, b, [
                    ], [], board, primerMovimiento)
                if board[a][b] != "--":
                    for disponible in objeto.cas_avail:
                        juego_temporal.board = copy.deepcopy(board)
                        mov = Movimiento(
                            (objeto.fila, objeto.col), disponible, juego_temporal.board)
                        juego_temporal.Jugada(mov, objeto)
                        if not (check(juego_temporal.board, historial_mov) != "-"):
                            jugada = ((objeto.fila, objeto.col), (disponible))
                            ValidosenCheck.append(jugada)
                    for disponible in objeto.cas_take:
                        juego_temporal.board = copy.deepcopy(board)
                        mov = Movimiento(
                            (objeto.fila, objeto.col), disponible, juego_temporal.board)
                        juego_temporal.Jugada(mov, objeto)
                        if not (check(juego_temporal.board, historial_mov) != "-"):
                            jugada = ((objeto.fila, objeto.col), (disponible))
                            ValidosenCheck.append(jugada)
    return ValidosenCheck

# La función se encarga de definir si el usuario desea que el 
# tablero se inicie de la forma tradicional o que pueda asignar 
# manualmente las posiciones de tablero.

def AsignarTablero(board):
    altotemp = 256
    anchotemp = 512
    dimension_temp = 2
    SQ_size_temp = anchotemp // dimension_temp
    screen1 = p.display.set_mode((anchotemp, altotemp))  # Genera el display
    reloj1 = p.time.Clock()
    screen1.fill(white)

    # Carga las imágenes desde la carpeta y las escala
    img1 = p.image.load("imagenes/" + "Asignar" + ".png")
    img2 = p.image.load("imagenes/" + "Basic" + ".png")
    img1 = p.transform.scale(img1, (SQ_size_temp//2, SQ_size_temp//2))
    img2 = p.transform.scale(img2, (SQ_size_temp//2, SQ_size_temp//2))

    # Se genera un rectangulo para poner la imagen encima
    rectangulo1 = p.Rect(64, 64, SQ_size_temp, SQ_size_temp)
    rectangulo2 = p.Rect(320, 64, SQ_size_temp, SQ_size_temp)

    # Se generan dos rectangulos para pintar el fondo
    rectangulo3 = p.Rect(0, 0, SQ_size_temp, SQ_size_temp)
    rectangulo4 = p.Rect(SQ_size_temp, 0, SQ_size_temp, SQ_size_temp)
    p.draw.rect(screen1, "white", rectangulo3)
    p.draw.rect(screen1, "blue", rectangulo4)

    # Pinta las imágenes
    screen1.blit(img1, rectangulo2)
    screen1.blit(img2, rectangulo1)

    # Se le hace flip a la pantalla
    reloj1.tick(max_FPS)
    p.display.flip()
    corriendo = True

    # Se obtiene cuál fue la selección del usuario y se retorna
    while corriendo:
        ubicacion_mouse1 = p.mouse.get_pos()
        colum = int(ubicacion_mouse1[0]//SQ_size_temp)
        for e in p.event.get():
            if e.type == p.QUIT:
                corriendo = False
            elif e.type == p.MOUSEBUTTONDOWN:
                colum = int(ubicacion_mouse1[0]//SQ_size_temp)
                corriendo = False
    screen1 = p.display.set_mode((ancho, alto))
    if colum == 1:
        board = cambiarBoard(board)
    return board


def cambiarBoard(board):
    load_images()
    altotemp = 640 
    anchotemp = 512
    dimension_temp = 10 # Se define una matriz de 10x10, para 
    # adjuntar el área de selección de piezas
    SQ_size_temp = altotemp // dimension_temp
    screen1 = p.display.set_mode((anchotemp, altotemp))  # Genera el display
    reloj1 = p.time.Clock()
    screen1.fill(white)
    cuadro_selec_temp = ()
    historial_clicks_temp = []
    asignando = True
    
    # Se inicializan las variables que 
    # que controlan la cantidad máxima de cada tipo de pieza que
    #  se puede colocar.
    num_pawns = 0 
    num_bishops = 0
    num_rook = 0
    num_knights = 0
    num_queen = 0
    num_king_w = 0
    num_king_b = 0

    # Se genera un elemento de clase cambiar_board
    tablero_temporal = cambiar_board()

    # Se entra al ciclo infinito
    while asignando:
        for e in p.event.get():
            if e.type == p.QUIT:
                # El usuario solamente puede continuar si ya fueron colocados 
                # ambos reyes en el tablero. El juego no puede iniciar 
                # sin la presencia de ambos
                if num_king_b == 1 and num_king_w == 1: 
                    asignando = False
                    return board
            elif e.type==p.KEYDOWN:
                    if e.key == p.K_SPACE:
                        if num_king_b == 1 and num_king_w == 1:
                            asignando = False
                            return board
            elif e.type == p.MOUSEBUTTONDOWN:
                ubicacion_mouse = p.mouse.get_pos()  # Posición (x,y) del mouse

                # Variables para obtener la fila y la columna donde está el
                # mouse y cual pieza se eligió
                columna = ubicacion_mouse[0]//SQ_size_temp
                fila = ubicacion_mouse[1]//SQ_size_temp

                # Caso en que haya seleccionado la misma pieza 2 veces
                if cuadro_selec_temp == (fila, columna):
                    tablero_temporal.board[fila][columna] = "--" # Se elimina del tablero dicha pieza
                    cuadro_selec_temp = ()  # Se "deselecciona" el cuadro (Vacío)
                    historial_clicks_temp = []  # Se limpia el historial de clicks

                # Caso en el que se seleccione un cuadro diferente, o no
                # se haya seleccionado ninguno aún.
                else:
                    cuadro_selec_temp = (fila, columna)

                    # Si se escoge una casilla no vacía o ya se tenía un
                    # click, se procede a guardar el cuadro en el
                    # historial de clicks
                    if tablero_temporal.board[fila][columna] != "--" or len(historial_clicks_temp) == 1:
                        historial_clicks_temp.append(cuadro_selec_temp)

                    # Si sólo se tiene seleccionada la pieza con el 1er click
                    # Se define que el origen será la pieza en la fila y columna
                    # seleccionadas 
                    if len(historial_clicks_temp) == 1:
                        origen = tablero_temporal.board[historial_clicks_temp[0][0]][historial_clicks_temp[0][1]]

                    if len(historial_clicks_temp) == 2:

                        mov_in = historial_clicks_temp[0]
                        mov_fin = historial_clicks_temp[1]

                        # Se define que en condiciones normales, 
                        # el destino será igual al origen
                        destino = origen

                        # Evita una sobreescritura en el caso en que el primer click del usuario 
                        # se dio en el área del seleccionador y su segundo click intenta 
                        # sobreescribir alguna de las piezas del seleccionador
                        if mov_in[0] > 8:
                            if mov_fin[0] == 8 or mov_fin[0] == 9:
                                destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]

                        
                        if mov_in[0] < 8:
                            # Evita una sobreescritura en el caso en que el primer click del usuario 
                            # se dio en el área del tablero y su segundo click intenta 
                            # sobreescribir alguna de las piezas del seleccionador
                            if mov_fin[0] == 8 or mov_fin[0] == 9:
                                destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                            
                            # Si el usario da su segundo click en algún cuadro del tablero(esté vacío o no), 
                            # se sobrepone y limpia el cuadro en el que estaba anteriormente
                            if (mov_fin[0] < 8):
                                origen = "--"

                        # Define las variables según el tipo y color de la pieza
                        # que se está tratando de colocar desde el seleccionador.   
                        if tablero_temporal.board[mov_in[0]][mov_in[1]] == "wP":
                            pw = "wP" 
                        else:
                            pw = "bP"
                        if tablero_temporal.board[mov_in[0]][mov_in[1]] == "wB":
                            bs = "wB" 
                        else:
                            bs = "bB"
                        if tablero_temporal.board[mov_in[0]][mov_in[1]] == "wR":
                            rk = "wR" 
                        else:
                            rk = "bR"
                        if tablero_temporal.board[mov_in[0]][mov_in[1]] == "wN":
                            nt = "wN" 
                        else:
                            nt = "bN"
                        if tablero_temporal.board[mov_in[0]][mov_in[1]] == "wQ":
                            qn = "wQ" 
                        else:
                            qn = "bQ"

                        # Se realizam varias condiciones. Inicialmente, que la pieza de origen provenga de 
                        # seleccionador y se comprueba que el número de piezas del color definido 
                        # anteriormente no exceda la cantidad posible dentro del juego (No más de 8 pawns, no 
                        # más de 2 bishops, etc) 
                    
                        if num_pawns > 7 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == pw:
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        if num_bishops > 1 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == bs:
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        if num_rook > 1 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == rk:
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        if num_knights > 1 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == nt:
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        if num_queen > 0 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == qn:
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        if num_king_w > 0 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == "wK":
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        if num_king_b > 0 and mov_in[0] > 7 and tablero_temporal.board[mov_in[0]][mov_in[1]] == "bK":
                            destino = tablero_temporal.board[mov_fin[0]][mov_fin[1]]
                        
                        
                        # Se actualiza el tablero con la jugada
                        tablero_temporal.Jugada(mov_in, mov_fin, origen, destino)
                        
                        # Se reinicia el contador de la cantidad de piezas; 
                        # esto para que no se acumule con los de la iteración anterior
                        num_pawns = 0
                        num_bishops = 0
                        num_rook = 0
                        num_knights = 0
                        num_queen = 0
                        num_king_w = 0
                        num_king_b = 0 

                        # Se lee la cantidad de piezas del color definido
                        # dentro de la matriz del tablero 8x8, sin contar, a las
                        # piezas presentes en el seleccionador
                        for f in range(dimension_temp-2):
                            num_pawns += tablero_temporal.board[f].count(pw)
                            num_bishops += tablero_temporal.board[f].count(bs)
                            num_rook += tablero_temporal.board[f].count(rk)
                            num_knights += tablero_temporal.board[f].count(nt)
                            num_queen += tablero_temporal.board[f].count(qn)
                            num_king_w += tablero_temporal.board[f].count("wK")
                            num_king_b += tablero_temporal.board[f].count("bK")
                    
                    
                        # Se resetean las variables que guardan el último click
                        # del usuario y el historial de clicks.
                        cuadro_selec_temp = ()
                        historial_clicks_temp = []

                        # Se copia cada elemento dentro del tablero temporal
                        # y se actualiza en el board del juego.
                        for f in range(dimension_temp-2):  # f: fila
                            for c in range(dimension_temp-2):  # c: columna
                                board[f][c] = tablero_temporal.board[f][c]


        colores = [white, brown]
        for f in range(dimension_temp):  # f: fila
            for c in range(dimension_temp-2):  # c: columna
                if f == 8:
                    color = brown
                elif f == 9:
                    color = white
                else:
                    color = colores[((f+c) % 2)]
                left = c * SQ_size
                top = f * SQ_size
                p.draw.rect(screen1, color, p.Rect(
                    left, top, SQ_size_temp, SQ_size_temp))
        for f in range(dimension_temp):  # f:fila
            for c in range(dimension_temp-2):  # c:columna
                pieza = tablero_temporal.board[f][c]
                rectangulo = p.Rect(c * SQ_size, f * SQ_size, SQ_size, SQ_size)
                if pieza != "--":  # No es un espacio vacío.
                    screen1.blit(imagenes[pieza], rectangulo)
        reloj1.tick(max_FPS)
        p.display.flip()


# Para que se ejecute solo cuando corro este archivo.py
if __name__ == "__main__":
    main()
