import type { CSSProperties } from "react";
import { ALLOWED_TYPES, GROUPS } from "./config";

export const FALLBACK_TYPE = "resource";

const BASE_HUE = 214;

function typesSharingACollection(): Map<string, Set<string>> {
  const conflicts = new Map<string, Set<string>>();
  const add = (type: string) => {
    if (!conflicts.has(type)) conflicts.set(type, new Set());
    return conflicts.get(type) as Set<string>;
  };

  for (const group of GROUPS) {
    const types = new Set<string>([FALLBACK_TYPE]);
    for (const category of group.categories) {
      for (const type of ALLOWED_TYPES[category] ?? []) types.add(type);
    }
    for (const type of types) {
      const neighbours = add(type);
      for (const other of types) {
        if (other !== type) neighbours.add(other);
      }
    }
  }
  return conflicts;
}

function largestCollectionSize(): number {
  let largest = 1;
  for (const group of GROUPS) {
    const types = new Set<string>([FALLBACK_TYPE]);
    for (const category of group.categories) {
      for (const type of ALLOWED_TYPES[category] ?? []) types.add(type);
    }
    largest = Math.max(largest, types.size);
  }
  return largest;
}

function assignHueSlots(): Map<string, number> {
  const conflicts = typesSharingACollection();

  const ordered = [...conflicts.keys()].sort((a, b) => {
    const degree =
      (conflicts.get(b) as Set<string>).size -
      (conflicts.get(a) as Set<string>).size;
    return degree !== 0 ? degree : a.localeCompare(b);
  });

  const slots = new Map<string, number>();
  for (const type of ordered) {
    const taken = new Set<number>();
    for (const neighbour of conflicts.get(type) as Set<string>) {
      const slot = slots.get(neighbour);
      if (slot !== undefined) taken.add(slot);
    }
    let slot = 0;
    while (taken.has(slot)) slot += 1;
    slots.set(type, slot);
  }

  const highestSlot = Math.max(0, ...slots.values());
  const slotCount = Math.max(largestCollectionSize(), highestSlot + 1);
  const step = 360 / slotCount;
  const hues = new Map<string, number>();
  for (const [type, slot] of slots) {
    hues.set(type, Math.round((BASE_HUE + slot * step) % 360));
  }
  return hues;
}

const TYPE_HUES = assignHueSlots();

export function domainOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

export function originFavicon(url: string): string {
  try {
    return new URL("/favicon.ico", url).href;
  } catch {
    return "";
  }
}

export function badgeHue(type: string): number {
  return TYPE_HUES.get(type) ?? TYPE_HUES.get(FALLBACK_TYPE) ?? BASE_HUE;
}

type BadgeStyle = CSSProperties & {
  "--badge-color": string;
  "--badge-bg": string;
  "--badge-border": string;
  "--badge-glow": string;
};

export function badgeStyle(type: string = FALLBACK_TYPE): BadgeStyle {
  const hue = badgeHue(type || FALLBACK_TYPE);
  return {
    "--badge-color": `hsl(${hue} 92% 78%)`,
    "--badge-bg": `hsl(${hue} 82% 52% / .19)`,
    "--badge-border": `hsl(${hue} 88% 67% / .34)`,
    "--badge-glow": `hsl(${hue} 88% 58% / .2)`,
  };
}

export function nextVisibleCount(
  current: number,
  total: number,
  pageSize: number,
): number {
  return Math.min(current + pageSize, total);
}
