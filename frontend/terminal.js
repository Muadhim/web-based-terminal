let token = null;
let socket = null;

function login() {
  const u = document.getElementById("username").value;
  const p = document.getElementById("password").value;

  // Simulate login (use localStorage for now)
  if (u === "admin" && p === "password") {
    token = btoa(`${u}:${p}`);
    localStorage.setItem("token", token);
    document.getElementById("login").style.display = "none";
    startTerminal();
  } else {
    alert("Invalid credentials");
  }
}

function startTerminal() {
  const term = new Terminal();
  term.open(document.getElementById('terminal'));

  socket = new WebSocket("ws://localhost:8000?token=" + token);

  socket.onopen = () => {
    term.focus();
    term.write("Connected to WebShell\r\n");
  };

  socket.onmessage = (event) => {
    term.write(event.data);
  };

  term.onData(data => {
    socket.send(data);
  });
}
