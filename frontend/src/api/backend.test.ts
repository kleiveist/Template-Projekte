import { describe, expect, it, vi } from "vitest";

import { fetchBackendHealth } from "./backend";

describe("fetchBackendHealth", () => {
  it("returns the backend health payload", async () => {
    const fetcher = vi.fn(async () =>
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

    await expect(fetchBackendHealth(fetcher, "http://api.example.test")).rejects.toThrow(
      "HTTP 503"
    );
  });
});
