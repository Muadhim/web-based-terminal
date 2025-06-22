const term = new Terminal();
term.open(document.getElementById('terminal'));

const socket = new WebSocket("ws://localhost:8000");

socket.onopen = () => {
  term.focus();
  term.write("Connected to WebShell\r\n");
  console.log('connect to web shell')
};

socket.onmessage = (event) => {
  term.write(event.data);
};

term.onData(data => {
  socket.send(data);
});