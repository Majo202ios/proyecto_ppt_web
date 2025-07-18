import eventlet
eventlet.monkey_patch()  # ¡SIEMPRE antes de importar cualquier otro módulo!

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

jugadores = {}  # username: {'room': 'sala1', 'jugada': None, 'puntos': 0, 'rondas': 0}
salas = {}      # 'sala1': ['juan', 'maria']

def determinar_ganador(j1, j2):
    if j1 == j2:
        return 'empate'
    if (j1 == 'piedra' and j2 == 'tijeras') or \
       (j1 == 'papel' and j2 == 'piedra') or \
       (j1 == 'tijeras' and j2 == 'papel'):
        return 'jugador1'
    return 'jugador2'

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('unirse')
def on_unirse(data):
    username = data['username']
    room = 'sala1'
    join_room(room)

    if username in jugadores:
        jugadores[username]['jugada'] = None  # Reconectado
        emit('mensaje', 'Reconectado a la sala.', room=request.sid)
        return

    if room not in salas:
        salas[room] = []

    if len(salas[room]) >= 2:
        emit('mensaje', 'La sala está llena. Intenta más tarde.', room=request.sid)
        return

    salas[room].append(username)
    jugadores[username] = {'room': room, 'jugada': None, 'puntos': 0, 'rondas': 0}
    emit('mensaje', f'{username} se unió a la sala.', room=room)

    if len(salas[room]) == 2:
        emit('start', '¡Ambos jugadores conectados! Comiencen a jugar.', room=room)

@socketio.on('jugada')
def on_jugada(data):
    username = data.get('username')
    jugada = data.get('jugada')

    if username not in jugadores:
        emit('mensaje', 'Debes unirte primero.', room=request.sid)
        return

    room = jugadores[username]['room']
    jugadores[username]['jugada'] = jugada

    room_players = salas[room]
    jugadas = [jugadores[p]['jugada'] for p in room_players]

    if None not in jugadas:
        ganador = determinar_ganador(jugadas[0], jugadas[1])
        j1, j2 = room_players
        resultado = ""

        for p in room_players:
            jugadores[p]['rondas'] += 1

        if ganador == 'empate':
            resultado = f"¡Empate! Ambos eligieron {jugadas[0]}"
        elif ganador == 'jugador1':
            jugadores[j1]['puntos'] += 1
            resultado = f"Ganó {j1} ({jugadas[0]} vence a {jugadas[1]})"
        else:
            jugadores[j2]['puntos'] += 1
            resultado = f"Ganó {j2} ({jugadas[1]} vence a {jugadas[0]})"

        puntajes = {p: jugadores[p]['puntos'] for p in room_players}
        rondas = jugadores[j1]['rondas']

        emit('resultado', {
            'texto': resultado,
            'puntos': puntajes,
            'rondas': rondas
        }, room=room)

        for p in room_players:
            jugadores[p]['jugada'] = None

@socketio.on('salir')
def on_salir(data):
    username = data.get('username')
    if not username or username not in jugadores:
        return

    room = jugadores[username]['room']
    leave_room(room)
    if room in salas and username in salas[room]:
        salas[room].remove(username)
        if not salas[room]:
            del salas[room]

    del jugadores[username]
    emit('mensaje', f'{username} salió de la sala.', room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
