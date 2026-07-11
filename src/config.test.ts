import { describe, expect, it } from "vitest";
import siteJson from "../generated/site.json";
import faviconsJson from "../generated/favicons.json";
import {
  ALL_RESOURCES,
  CATEGORY_LABELS,
  CATEGORY_OF_GROUP,
  COUNTS,
  GROUP_COUNTS,
  GROUPS,
  MISSING_FAVICON_DOMAINS,
  RESOURCE_TYPES,
  SITE_DATA,
  SITE_FAVICON_DOMAINS,
} from "./config";
import { domainOf } from "./utils";
import schema from "../schema/resource.schema.json";

const MAX_DESCRIPTION_LENGTH = schema.properties.description.maxLength;

describe("generated site data contract", () => {
  it("emits every field the frontend depends on", () => {
    expect(siteJson).toHaveProperty("labels");
    expect(siteJson).toHaveProperty("groups");
    expect(siteJson).toHaveProperty("types");
    expect(siteJson).toHaveProperty("categories");
    expect(typeof SITE_DATA.total).toBe("number");
    expect(RESOURCE_TYPES.length).toBeGreaterThan(0);
    expect(GROUPS.length).toBeGreaterThan(0);
  });

  it("labels exactly the categories it ships", () => {
    expect(Object.keys(CATEGORY_LABELS).sort()).toEqual(
      Object.keys(SITE_DATA.categories).sort(),
    );
  });

  it("assigns every category to exactly one collection", () => {
    const grouped = GROUPS.flatMap((group) => group.categories);
    expect([...grouped].sort()).toEqual(Object.keys(CATEGORY_LABELS).sort());
    expect(new Set(grouped).size).toBe(grouped.length);
  });

  it("names every collection it ships", () => {
    expect(GROUPS.map((group) => group.name)).toEqual(
      Object.keys(siteJson.groups),
    );
  });

  it("keeps every count consistent with the resources it ships", () => {
    expect(SITE_DATA.total).toBe(ALL_RESOURCES.length);
    for (const group of GROUPS) {
      const sum = group.categories.reduce(
        (total, category) => total + COUNTS[category],
        0,
      );
      expect(GROUP_COUNTS[group.name]).toBe(sum);
      expect(group.total).toBe(sum);
    }
  });

  it("files every resource under the category it claims", () => {
    for (const [category, resources] of Object.entries(SITE_DATA.categories)) {
      for (const resource of resources) {
        expect(resource.category).toBe(category);
        expect(CATEGORY_OF_GROUP[resource.category]).toBeTruthy();
      }
    }
  });

  it("gives every resource the fields a card renders", () => {
    for (const resource of ALL_RESOURCES) {
      expect(resource.id).toBeTruthy();
      expect(resource.name).toBeTruthy();
      expect(resource.description).toBeTruthy();
      expect(resource.url.startsWith("https://")).toBe(true);
    }
  });

  it("keeps every description within the length a card can show", () => {
    const overLong = ALL_RESOURCES.filter(
      (resource) => resource.description.length > MAX_DESCRIPTION_LENGTH,
    ).map((resource) => `${resource.id} (${resource.description.length})`);
    expect(overLong).toEqual([]);
  });

  it("ends every description with a period", () => {
    const malformed = ALL_RESOURCES.filter(
      (resource) => !resource.description.endsWith("."),
    ).map((resource) => resource.id);
    expect(malformed).toEqual([]);
  });

  it("issues every resource a unique id", () => {
    const ids = ALL_RESOURCES.map((resource) => resource.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("only uses types the schema declares", () => {
    for (const resource of ALL_RESOURCES) {
      if (resource.type) expect(RESOURCE_TYPES).toContain(resource.type);
    }
  });

  it("reserves the event type for the Experience collection", () => {
    const leaked = ALL_RESOURCES.filter(
      (resource) =>
        resource.type === "event" &&
        CATEGORY_OF_GROUP[resource.category] !== "Experience",
    ).map((resource) => resource.id);
    expect(leaked).toEqual([]);
  });

  it("uses no type other than event inside the Experience collection", () => {
    const wrong = ALL_RESOURCES.filter(
      (resource) =>
        CATEGORY_OF_GROUP[resource.category] === "Experience" &&
        resource.type !== undefined &&
        resource.type !== "event",
    ).map((resource) => resource.id);
    expect(wrong).toEqual([]);
  });

  it("lists no favicon domain that the dataset no longer contains", () => {
    const domains = new Set(ALL_RESOURCES.map((r) => domainOf(r.url)));
    for (const domain of MISSING_FAVICON_DOMAINS) {
      expect(domains).toContain(domain);
    }
    for (const domain of SITE_FAVICON_DOMAINS) {
      expect(domains).toContain(domain);
    }
    expect(faviconsJson.missing.length).toBeLessThan(domains.size);
  });

  it("keeps the missing and site-only favicon lists disjoint", () => {
    const overlap = [...SITE_FAVICON_DOMAINS].filter((domain) =>
      MISSING_FAVICON_DOMAINS.has(domain),
    );
    expect(overlap).toEqual([]);
  });
});
