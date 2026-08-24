import { describe, expect, it } from "vitest";

import { activeProfileId, activeProfileName, enabledFeatures, hasFeature } from "./project-profile";

describe("active project profile", () => {
  it("exposes a valid frontend profile", () => {
    expect(activeProfileId).toMatch(/^[a-z][a-z0-9-]*$/);
    expect(activeProfileName.trim()).not.toBe("");
    expect(enabledFeatures).toContain("frontend");
  });

  it("answers feature checks from the generated feature set", () => {
    for (const feature of enabledFeatures) {
      expect(hasFeature(feature)).toBe(true);
    }
    expect(hasFeature("not-a-project-feature")).toBe(false);
  });

  it("keeps feature queries valid across generated profiles", () => {
    const backendEnabled: boolean = hasFeature("backend");

    expect(backendEnabled).toBe(new Set<string>(enabledFeatures).has("backend"));
  });
});
