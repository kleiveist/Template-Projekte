export interface HealthResponse {
  status: string;
  service: string;
}

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchBackendHealth(
  fetcher: typeof fetch = fetch,
  baseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
): Promise<HealthResponse> {
  const response = await fetcher(`${baseUrl.replace(/\/$/, "")}/api/health`);
  if (!response.ok) {
    throw new Error(`Backend health check failed with HTTP ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}
