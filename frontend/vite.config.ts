import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";

import { enabledFeatures } from "./src/project-profile";

function parsePort(value: string | undefined, fallback: number): number {
  const port = Number(value ?? fallback);
  return Number.isInteger(port) && port >= 1 && port <= 65535 ? port : fallback;
}

function clientHost(host: string): string {
  return host === "0.0.0.0" || host === "::" ? "127.0.0.1" : host;
}

function readRootDotenv(path: string): Record<string, string> {
  if (!existsSync(path)) return {};
  const values: Record<string, string> = {};
  for (const [index, rawLine] of readFileSync(path, "utf8").split(/\r?\n/).entries()) {
    let line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    if (line.startsWith("export ")) line = line.slice(7).trimStart();
    const separator = line.indexOf("=");
    if (separator < 1) throw new Error(`Invalid dotenv entry at ${path}:${index + 1}`);
    const name = line.slice(0, separator).trim();
    let value = line.slice(separator + 1).trim();
    if (!/^[A-Z][A-Z0-9_]*$/.test(name)) {
      throw new Error(`Invalid dotenv variable name at ${path}:${index + 1}`);
    }
    if (value.startsWith('"') && value.endsWith('"')) {
      value = JSON.parse(value) as string;
    } else if (value.startsWith("'") && value.endsWith("'")) {
      value = value.slice(1, -1);
    } else {
      value = value.split(" #", 1)[0].trim();
    }
    values[name] = value;
  }
  return values;
}

export default defineConfig(() => {
  const projectRoot = fileURLToPath(new URL("..", import.meta.url));
  const env = {
    ...readRootDotenv(resolve(projectRoot, ".env")),
    ...process.env
  };
  const frontendHost = env.FRONTEND_HOST || "127.0.0.1";
  const frontendPort = parsePort(env.FRONTEND_PORT, 5173);
  const backendEnabled = enabledFeatures.some((feature) => feature === "backend");
  const backendHost = clientHost(env.BACKEND_HOST || "127.0.0.1");
  const backendPort = parsePort(env.BACKEND_PORT, 8000);
  const apiBaseUrl = backendEnabled ? env.VITE_API_BASE_URL || `http://${backendHost}:${backendPort}` : undefined;

  return {
    // Vite's implicit mode files are disabled so every adapter uses only the root .env contract.
    envDir: resolve(projectRoot, ".vite-env-disabled"),
    // Public values are explicitly defined below instead of exposing every process VITE_* value.
    envPrefix: [],
    define: apiBaseUrl ? { "import.meta.env.VITE_API_BASE_URL": JSON.stringify(apiBaseUrl) } : {},
    server: {
      host: frontendHost,
      port: frontendPort,
      strictPort: false
    },
    preview: {
      host: frontendHost,
      port: 4173
    }
  };
});
