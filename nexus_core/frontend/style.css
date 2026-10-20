:root {
  --bg: #071018;
  --panel: rgba(14, 28, 39, 0.88);
  --panel-strong: rgba(9, 18, 26, 0.96);
  --border: rgba(116, 210, 255, 0.35);
  --text: #eaf7ff;
  --muted: #9fc7dc;
  --accent: #78d9ff;
  --accent-2: #9d8cff;
  --success: #7ef2c7;
  --warning: #ffd166;
  --danger: #ff6b6b;
}

* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  min-height: 100%;
  font-family: Inter, "Segoe UI", sans-serif;
  background: radial-gradient(circle at top left, rgba(120, 217, 255, 0.12), transparent 30%), var(--bg);
  color: var(--text);
}

body {
  min-height: 100vh;
  padding: 24px;
}

.hud-shell {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
  min-height: calc(100vh - 48px);
  padding: 20px;
  border: 1px solid var(--border);
  background: rgba(9, 16, 24, 0.82);
  border-radius: 18px;
  box-shadow: 0 0 32px rgba(34, 196, 255, 0.18);
}

.sidebar, .panel, .stat-card, .topbar, .system-mini {
  background: rgba(18, 35, 46, 0.82);
  border: 1px solid var(--border);
  border-radius: 14px;
}

.sidebar {
  padding: 18px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: #06141d;
  font-weight: 800;
  font-size: 1.4rem;
}

.label {
  font-size: 0.68rem;
  letter-spacing: 0.12rem;
  color: var(--muted);
  text-transform: uppercase;
}

.brand-block h1 {
  margin: 4px 0 0;
  font-size: 1.7rem;
}

nav {
  display: grid;
  gap: 8px;
}

.nav {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text);
  text-align: left;
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
}

.nav.active {
  background: rgba(120, 217, 255, 0.08);
  border-color: var(--border);
}

.system-mini {
  margin-top: 18px;
  padding: 12px;
}

.status-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 4px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  color: var(--muted);
}

.online {
  color: var(--success);
}

.main-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
}

.eyebrow {
  color: var(--muted);
  letter-spacing: 0.08rem;
  font-size: 0.7rem;
}

.topbar h2 {
  margin: 4px 0 0;
}

.core-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 999px;
  background: rgba(126, 242, 199, 0.08);
  border: 1px solid rgba(126, 242, 199, 0.25);
}

.pulse {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 12px rgba(126, 242, 199, 0.9);
  animation: pulse 1.8s infinite ease-in-out;
}

@keyframes pulse {
  0%, 100% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.2); opacity: 1; }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 14px;
}

.stat-card {
  padding: 16px;
}

.stat-title {
  color: var(--muted);
  margin-bottom: 10px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
}

.panel-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(260px, 1fr);
  gap: 18px;
}

.panel {
  padding: 16px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tag {
  background: rgba(157, 140, 255, 0.12);
  border: 1px solid rgba(157, 140, 255, 0.25);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 0.7rem;
}

.messages {
  min-height: 260px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.message {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(120, 217, 255, 0.04);
}

.message.user {
  align-self: flex-end;
  background: rgba(157, 140, 255, 0.12);
}

.composer {
  display: flex;
  gap: 8px;
}

input {
  flex: 1;
  background: rgba(9, 17, 24, 0.8);
  border: 1px solid var(--border);
  border-radius: 10px;
  color: var(--text);
  padding: 12px 14px;
}

button {
  background: linear-gradient(135deg, rgba(120, 217, 255, 0.18), rgba(157, 140, 255, 0.2));
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 16px;
  cursor: pointer;
}

.quest-list {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 10px;
  color: var(--muted);
}

.progress-row {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.meter {
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
  margin-top: 8px;
}

.meter span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-2));
}

@media (max-width: 900px) {
  .hud-shell {
    grid-template-columns: 1fr;
  }

  .panel-grid, .stats-grid {
    grid-template-columns: 1fr;
  }
}
