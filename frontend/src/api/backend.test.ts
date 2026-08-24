import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchBackendHealth } from "./backend";

describe("fetchBackendHealth", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("returns the backend health payload", async () => {
    const fetcher = vi.fn(
      async () =>
        new Response(JSON.stringify({ status: "ok", service: "template-backend" }), {
          status: 200,
          headers: { "content-type": "application/json" }
        })
    );

    await expect(fetchBackendHealth(fetcher, "http://api.example.test/")).resolves.toEqual({
      status: "ok",
      service: "template-backend"
    });
    expect(fetcher).toHaveBeenCalledWith("http://api.example.test/api/health");
  });

  it("reports a non-success response", async () => {
    const fetcher = vi.fn(async () => new Response(null, { status: 503 }));

    await expect(fetchBackendHealth(fetcher, "http://api.example.test")).rejects.toThrow("HTTP 503");
  });

  it("uses the configured API base URL with the global fetch implementation", async () => {
    const fetcher = vi.fn(
      async () =>
        new Response(JSON.stringify({ status: "ok", service: "template-backend" }), {
          status: 200,
          headers: { "content-type": "application/json" }
        })
    );
    vi.stubEnv("VITE_API_BASE_URL", "http://configured.example.test/");
    vi.stubGlobal("fetch", fetcher);

    await expect(fetchBackendHealth()).resolves.toEqual({
      status: "ok",
      service: "template-backend"
    });
    expect(fetcher).toHaveBeenCalledWith("http://configured.example.test/api/health");
  });

  it("fails before making a request when the API base URL is absent", async () => {
    const fetcher = vi.fn();
    vi.stubEnv("VITE_API_BASE_URL", "");
    vi.stubGlobal("fetch", fetcher);

    await expect(fetchBackendHealth()).rejects.toThrow("VITE_API_BASE_URL is required");
    expect(fetcher).not.toHaveBeenCalled();
  });
});
