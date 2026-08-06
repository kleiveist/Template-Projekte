import { fetchBackendHealth } from "./api/backend";
import { activeProfileId, activeProfileName, enabledFeatures, hasFeature } from "./project-profile";
import "./styles/index.css";

const root = document.querySelector<HTMLDivElement>("#app");

if (!root) {
  throw new Error("Missing #app root element");
}

const backendEnabled = hasFeature("backend");

root.innerHTML = `
  <main class="page-shell">
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">Project profile</p>
      <h1 id="page-title">Template Project</h1>
      <p class="intro">
        The active template preset is <strong>${activeProfileName}</strong> (${activeProfileId}).
        Replace this starter surface with the first real feature and document acceptance work in
        the ATP area.
      </p>
    </section>

    <section class="status-card" aria-labelledby="profile-title">
      <div>
        <p class="eyebrow">Enabled features</p>
        <h2 id="profile-title">Profile summary</h2>
      </div>
      <p class="status status--ok" role="status">${["frontend", ...enabledFeatures.filter((feature) => feature !== "frontend")].join(", ")}</p>
    </section>

    ${
      backendEnabled
        ? `
    <section class="status-card" aria-labelledby="backend-title">
      <div>
        <p class="eyebrow">Integration check</p>
        <h2 id="backend-title">Backend</h2>
      </div>
      <p id="backend-status" class="status" role="status">Checking backend connection ...</p>
      <button id="retry-health" type="button">Check again</button>
    </section>
    `
        : `
    <section class="status-card" aria-labelledby="mode-title">
      <div>
        <p class="eyebrow">Local mode</p>
        <h2 id="mode-title">Backend disabled</h2>
      </div>
      <p class="status status--ok" role="status">
        This profile does not enable the FastAPI backend. Build the next local feature directly on
        the frontend or Tauri side.
      </p>
    </section>
    `
    }
  </main>
`;

const status = document.querySelector<HTMLParagraphElement>("#backend-status");
const retry = document.querySelector<HTMLButtonElement>("#retry-health");

async function updateBackendStatus(): Promise<void> {
  if (!status) return;
  status.className = "status";
  status.textContent = "Checking backend connection ...";
  try {
    const health = await fetchBackendHealth();
    status.classList.add("status--ok");
    status.textContent = `${health.service}: ${health.status}`;
  } catch (error) {
    status.classList.add("status--error");
    status.textContent = error instanceof Error ? error.message : "Backend is not reachable";
  }
}

if (backendEnabled) {
  retry?.addEventListener("click", () => void updateBackendStatus());
  void updateBackendStatus();
}
