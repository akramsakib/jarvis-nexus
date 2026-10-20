const cpuValue = document.getElementById('cpu-value');
const ramValue = document.getElementById('ram-value');
const diskValue = document.getElementById('disk-value');
const uptimeValue = document.getElementById('uptime-value');
const messages = document.getElementById('messages');
const input = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');

async function loadStatus() {
  const response = await fetch('/api/system/status');
  const data = await response.json();
  const telemetry = data.telemetry || {};
  cpuValue.textContent = `${Math.round(telemetry.cpu_percent ?? 0)}%`;
  ramValue.textContent = `${Math.round(telemetry.ram_percent ?? 0)}%`;
  diskValue.textContent = `${Math.round(telemetry.disk_percent ?? 0)}%`;
  const uptime = Number(telemetry.uptime_seconds ?? 0);
  uptimeValue.textContent = `${Math.round(uptime / 60)}m`;
}

function appendMessage(sender, text) {
  const div = document.createElement('div');
  div.className = `message ${sender}`;
  div.textContent = text;
  messages.appendChild(div);
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  appendMessage('user', text);
  input.value = '';

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });

  const data = await response.json();
  const summary = data.summary || 'Task accepted.';
  appendMessage('assistant', summary);
}

sendButton.addEventListener('click', sendMessage);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') sendMessage();
});

loadStatus();
setInterval(loadStatus, 5000);
