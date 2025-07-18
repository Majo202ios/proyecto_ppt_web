const socket = io();
let username = "";

function unirse() {
  username = document.getElementById('username').value;
  if (!username) return alert("Ingresa un nombre");

  socket.emit('unirse', { username });
  document.getElementById('login').style.display = 'none';
  document.getElementById('juego').style.display = 'block';
}

function enviarJugada(jugada) {
  socket.emit('jugada', { username, jugada });
}

function salir() {
  socket.emit('salir', { username });
  document.getElementById('juego').style.display = 'none';
  document.getElementById('login').style.display = 'block';
}

socket.on('mensaje', msg => {
  document.getElementById('estado').innerText = msg;
});

socket.on('start', msg => {
  document.getElementById('estado').innerText = msg;
});

socket.on('resultado', data => {
  const resultado = `
    <p>${data.texto}</p>
    <p>Rondas: ${data.rondas}</p>
    <p>Puntos: ${Object.entries(data.puntos).map(([k, v]) => `${k}: ${v}`).join(', ')}</p>
  `;
  document.getElementById('resultado').innerHTML = resultado;
});
