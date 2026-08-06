export interface HealthResponse {
  status: string;
  service: string;
}

function configuredApiBaseUrl(): string {
  const value = import.meta.env.VITE_API_BASE_URL;
  if (!value) {
    throw new Error("VITE_API_BASE_URL is required when the backend feature is enabled");
  }
  return value;
}

export async function fetchBackendHealth(
  fetcher: typeof fetch = fetch,
  baseUrl = configuredApiBaseUrl()
): Promise<HealthResponse> {
  const response = await fetcher(`${baseUrl.replace(/\/$/, "")}/api/health`);
  if (!response.ok) {
    throw new Error(`Backend health check failed with HTTP ${response.status}`);
  }
  return (await response.json()) as HealthResponse;
}
