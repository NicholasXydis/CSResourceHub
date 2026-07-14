import type { ComponentType } from "react";
import { motion } from "framer-motion";
import {
  BriefcaseBusiness,
  Code2,
  GraduationCap,
  Layers3,
  RefreshCcw,
  Trophy,
} from "lucide-react";
import {
  CATEGORY_LABELS,
  COUNTS,
  GROUP_COUNTS,
  GROUPS,
  SITE_DATA,
} from "../config";
import { CONTAINER, RISE } from "../motion";
import type { Category, CategoryFilter, CollectionFilter } from "../types";

const GROUP_ICONS: Record<string, ComponentType<{ size?: number }>> = {
  graduation: GraduationCap,
  trophy: Trophy,
  code: Code2,
  briefcase: BriefcaseBusiness,
};

const FILTER_MOTION = {
  whileHover: { x: 4, scale: 1.015 },
  whileTap: { scale: 0.965, x: 1 },
};

export interface FiltersProps {
  collection: CollectionFilter;
  category: CategoryFilter;
  setCollection: (value: CollectionFilter) => void;
  setCategory: (value: CategoryFilter) => void;
}

export default function Filters({
  collection,
  category,
  setCollection,
  setCategory,
}: FiltersProps) {
  const clearAll = () => {
    setCollection("all");
    setCategory("all");
  };
  const chooseCollection = (value: CollectionFilter) => {
    setCollection(value);
    setCategory("all");
  };
  const chooseCategory = (value: CategoryFilter) => {
    setCategory(value);
  };
  const activeGroup = GROUPS.find((group) => group.name === collection);
  const enabledCategories = activeGroup
    ? new Set(activeGroup.categories)
    : null;
  const categoryTotal = activeGroup
    ? GROUP_COUNTS[activeGroup.name]
    : SITE_DATA.total;
  const allCategories = Object.keys(CATEGORY_LABELS) as Category[];
  const categoryKeys = activeGroup
    ? [
        ...activeGroup.categories,
        ...allCategories.filter((key) => !enabledCategories?.has(key)),
      ]
    : allCategories;
  return (
    <motion.aside
      className="filters"
      variants={CONTAINER}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.02 }}
      aria-label="Resource filters"
    >
      <motion.div variants={RISE} className="filters-title">
        <strong>Filters</strong>
        <motion.button
          {...FILTER_MOTION}
          className="clear-filter"
          onClick={clearAll}
          whileHover={{ scale: 1.06, y: -2 }}
          whileTap={{ scale: 0.92 }}
          aria-label="Clear all resource filters"
        >
          <RefreshCcw aria-hidden="true" /> Clear all
        </motion.button>
      </motion.div>
      <motion.p variants={RISE} className="filter-label">
        Collections
      </motion.p>
      <motion.button
        {...FILTER_MOTION}
        variants={RISE}
        aria-pressed={collection === "all"}
        className={collection === "all" ? "filter-row active" : "filter-row"}
        onClick={() => chooseCollection("all")}
      >
        <Layers3 />
        <span>All collections</span>
        <em>{SITE_DATA.total}</em>
      </motion.button>
      {GROUPS.map((group) => {
        const Icon = GROUP_ICONS[group.icon] || Layers3;
        return (
          <motion.button
            {...FILTER_MOTION}
            variants={RISE}
            key={group.name}
            aria-pressed={collection === group.name}
            className={
              collection === group.name ? "filter-row active" : "filter-row"
            }
            onClick={() => chooseCollection(group.name)}
          >
            <Icon />
            <span>{group.name}</span>
            <em>{GROUP_COUNTS[group.name]}</em>
          </motion.button>
        );
      })}
      <motion.div variants={RISE} className="filter-divider" />
      <motion.p variants={RISE} className="filter-label">
        Categories
      </motion.p>
      <motion.button
        {...FILTER_MOTION}
        variants={RISE}
        aria-pressed={category === "all"}
        className={category === "all" ? "filter-row active" : "filter-row"}
        onClick={() => chooseCategory("all")}
      >
        <Code2 />
        <span>All categories</span>
        <em>{categoryTotal}</em>
      </motion.button>
      {categoryKeys.map((key) => {
        const disabled = enabledCategories
          ? !enabledCategories.has(key)
          : false;
        return (
          <motion.button
            {...FILTER_MOTION}
            variants={RISE}
            key={key}
            disabled={disabled}
            aria-disabled={disabled}
            aria-pressed={category === key}
            className={category === key ? "filter-row active" : "filter-row"}
            onClick={() => chooseCategory(key)}
          >
            <Code2 />
            <span>{CATEGORY_LABELS[key]}</span>
            <em>{COUNTS[key]}</em>
          </motion.button>
        );
      })}
    </motion.aside>
  );
}
