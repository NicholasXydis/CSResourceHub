import siteJson from "../generated/site.json";
import faviconsJson from "../generated/favicons.json";
import type { Category, Group, GroupName, Resource, SiteData } from "./types";

const siteData = siteJson as unknown as SiteData;

export const CATEGORY_LABELS: Record<Category, string> = siteData.labels;
export const RESOURCE_TYPES: string[] = siteData.types;
export const ALLOWED_TYPES: Record<Category, string[]> = siteData.allowedTypes;

export const GROUPS: Group[] = (
  Object.entries(siteData.groups) as [GroupName, Omit<Group, "name">][]
).map(([name, group]) => ({ name, ...group }));

export const ALL_RESOURCES: Resource[] = Object.values(
  siteData.categories,
).flat();

export const COUNTS = Object.fromEntries(
  Object.entries(siteData.categories).map(([key, value]) => [
    key,
    value.length,
  ]),
) as Record<Category, number>;

export const GROUP_COUNTS = Object.fromEntries(
  GROUPS.map((group) => [group.name, group.total]),
) as Record<GroupName, number>;

export const CATEGORY_OF_GROUP = Object.fromEntries(
  GROUPS.flatMap((group) =>
    group.categories.map((category) => [category, group.name]),
  ),
) as Record<Category, GroupName>;

export const GITHUB_URL = "https://github.com/NicholasXydis/CSResourceHub";
export const PAGE_SIZE = 18;
export const SITE_DATA: SiteData = siteData;

export const MISSING_FAVICON_DOMAINS = new Set<string>(faviconsJson.missing);
export const SITE_FAVICON_DOMAINS = new Set<string>(faviconsJson.siteOnly);
