export const activeProfileId = "full-platform";
export const activeProfileName = "Full platform";
export const enabledFeatures = ["frontend", "backend", "tauri", "cloud", "database", "postgres"] as const;
export type ProjectFeature = (typeof enabledFeatures)[number];

const featureSet = new Set<string>(enabledFeatures);

export function hasFeature(feature: string): boolean {
  return featureSet.has(feature);
}
