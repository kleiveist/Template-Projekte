import { fetchBackendHealth } from "./api/backend";
import "./styles/index.css";

const root = document.querySelector<HTMLDivElement>("#app");

if (!root) {
  throw new Error("Missing #app root element");
}

root.innerHTML = `
  <main class="page-shell">
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">Full-stack starter</p>
      <h1 id="page-title">Template Project</h1>
      <p class="intro">
        Vite, TypeScript, FastAPI und Tauri sind eingerichtet. Ersetze diese Startseite durch
        die erste fachliche Funktion und dokumentiere ihre Abnahme im ATP-Bereich.
      </p>
    </section>

    <section class="status-card" aria-labelledby="backend-title">
      <div>
        <p class="eyebrow">Integration check</p>
        <h2 id="backend-title">Backend</h2>
      </div>
      <p id="backend-status" class="status" role="status">Verbindung wird geprüft …</p>
      <button id="retry-health" type="button">Erneut prüfen</button>
    </section>
  </main>
`;

const status = document.querySelector<HTMLParagraphElement>("#backend-status");
const retry = document.querySelector<HTMLButtonElement>("#retry-health");

async function updateBackendStatus(): Promise<void> {
  if (!status) return;
  status.className = "status";
  status.textContent = "Verbindung wird geprüft …";
  try {
    const health = await fetchBackendHealth();
    status.classList.add("status--ok");
    status.textContent = `${health.service}: ${health.status}`;
  } catch (error) {
    status.classList.add("status--error");
    status.textContent = error instanceof Error ? error.message : "Backend ist nicht erreichbar";
  }
}

retry?.addEventListener("click", () => void updateBackendStatus());
void updateBackendStatus();
