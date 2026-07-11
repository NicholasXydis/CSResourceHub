import siteJson from "../generated/site.json";

export type Category = keyof (typeof siteJson)["labels"];

export type GroupName = keyof (typeof siteJson)["groups"];

export interface Resource {
  id: string;
  name: string;
  url: string;
  description: string;
  category: Category;
  type?: string;
  location?: string;
  month?: string;
  date_added?: string;
  last_verified?: string;
}

export interface Group {
  name: GroupName;
  icon: string;
  categories: Category[];
  total: number;
}

export interface SiteData {
  generated: string;
  total: number;
  labels: Record<Category, string>;
  types: string[];
  allowedTypes: Record<Category, string[]>;
  groups: Record<GroupName, Omit<Group, "name">>;
  categories: Record<Category, Resource[]>;
}

export type SortKey = "relevance" | "name" | "newest";

export type CollectionFilter = "all" | GroupName;

export type CategoryFilter = "all" | Category;
