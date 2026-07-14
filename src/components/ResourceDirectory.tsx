import { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ChevronDown, Filter, RefreshCcw, Search, X } from "lucide-react";
import {
  ALL_RESOURCES,
  CATEGORY_LABELS,
  CATEGORY_OF_GROUP,
  PAGE_SIZE,
} from "../config";
import { CONTAINER, RISE } from "../motion";
import type { CategoryFilter, CollectionFilter, SortKey } from "../types";
import { nextVisibleCount, relevanceRank } from "../utils";
import Filters from "./Filters";
import ResourceCard from "./ResourceCard";
import type { SearchControls } from "./SiteChrome";

export default function ResourceDirectory({ query, setQuery }: SearchControls) {
  const [collection, setCollection] = useState<CollectionFilter>("all");
  const [category, setCategory] = useState<CategoryFilter>("all");
  const [sort, setSort] = useState<SortKey>("relevance");
  const [drawer, setDrawer] = useState(false);
  const [pagination, setPagination] = useState({ key: "", visible: PAGE_SIZE });
  const drawerRef = useRef<HTMLDivElement>(null);
  const filterButtonRef = useRef<HTMLButtonElement>(null);
  const paginationKey = `${query}\u0000${collection}\u0000${category}\u0000${sort}`;
  const visible =
    pagination.key === paginationKey ? pagination.visible : PAGE_SIZE;
  const reduced = useReducedMotion();
  const results = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    let list = ALL_RESOURCES.filter((resource) => {
      const groupName = CATEGORY_OF_GROUP[resource.category];
      const collectionMatch = collection === "all" || collection === groupName;
      const categoryMatch =
        category === "all" || category === resource.category;
      const searchMatch =
        !normalizedQuery ||
        [
          resource.name,
          resource.description,
          resource.type,
          CATEGORY_LABELS[resource.category],
          groupName,
        ].some((value) => value?.toLowerCase().includes(normalizedQuery));
      return collectionMatch && categoryMatch && searchMatch;
    });
    if (sort === "relevance" && normalizedQuery)
      list = [...list].sort(
        (a, b) =>
          relevanceRank(a, normalizedQuery) - relevanceRank(b, normalizedQuery),
      );
    if (sort === "name")
      list = [...list].sort((a, b) => a.name.localeCompare(b.name));
    if (sort === "newest")
      list = [...list].sort((a, b) =>
        (b.date_added || "").localeCompare(a.date_added || ""),
      );
    return list;
  }, [query, collection, category, sort]);
  useEffect(() => {
    if (!drawer) return undefined;
    const previous = document.body.style.overflow;
    const trigger = filterButtonRef.current;
    const focusable = () => [
      ...(drawerRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), a[href], select, input, [tabindex]:not([tabindex="-1"])',
      ) ?? []),
    ];
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDrawer(false);
        return;
      }
      if (event.key !== "Tab") return;
      const items = focusable();
      const first = items[0];
      const last = items[items.length - 1];
      if (!first || !last) return;
      const active = document.activeElement;
      const outside = !drawerRef.current?.contains(active);
      if (event.shiftKey && (active === first || outside)) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && (active === last || outside)) {
        event.preventDefault();
        first.focus();
      }
    };
    document.body.style.overflow = "hidden";
    focusable()[0]?.focus();
    window.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previous;
      window.removeEventListener("keydown", onKeyDown);
      trigger?.focus();
    };
  }, [drawer]);
  const shown = Math.min(visible, results.length);
  return (
    <motion.section
      id="directory"
      className="directory"
      variants={CONTAINER}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.02 }}
      aria-label="Resource directory"
    >
      <motion.button
        ref={filterButtonRef}
        variants={RISE}
        className="mobile-filter"
        onClick={() => setDrawer(true)}
        aria-haspopup="dialog"
        aria-expanded={drawer}
      >
        <Filter /> Filters{" "}
        {(collection !== "all" || category !== "all") && (
          <span>
            {Number(collection !== "all") + Number(category !== "all")}
          </span>
        )}
      </motion.button>
      <AnimatePresence>
        {drawer && (
          <>
            <motion.button
              className="drawer-backdrop"
              aria-label="Close filters"
              onClick={() => setDrawer(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
            <motion.div
              ref={drawerRef}
              className="filter-drawer"
              role="dialog"
              aria-modal="true"
              aria-label="Resource filters"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
            >
              <button
                className="drawer-close"
                onClick={() => setDrawer(false)}
                aria-label="Close filters"
              >
                <X />
              </button>
              <Filters
                collection={collection}
                category={category}
                setCollection={setCollection}
                setCategory={setCategory}
                close={() => setDrawer(false)}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
      <motion.div variants={RISE} className="desktop-filters">
        <Filters
          collection={collection}
          category={category}
          setCollection={setCollection}
          setCategory={setCategory}
        />
      </motion.div>
      <motion.div className="results" variants={CONTAINER}>
        <h2 className="visually-hidden">Resources</h2>
        <motion.div variants={RISE} className="result-bar">
          <p role="status" aria-live="polite" aria-atomic="true">
            <strong>{results.length}</strong> resources found
          </p>
          <label>
            Sort by:
            <motion.span
              className="sort-control"
              whileHover={{ y: -2, scale: 1.025 }}
              whileTap={{ scale: 0.97 }}
            >
              <select
                value={sort}
                onChange={(event) => setSort(event.target.value as SortKey)}
                aria-label="Sort resources"
              >
                <option value="relevance">Relevance</option>
                <option value="name">Name A–Z</option>
                <option value="newest">Newest</option>
              </select>
              <ChevronDown aria-hidden="true" />
            </motion.span>
          </label>
        </motion.div>
        {results.length ? (
          <motion.div
            id="resource-grid"
            layout={!reduced}
            className="card-grid"
          >
            {results.slice(0, visible).map((resource, index) => (
              <ResourceCard
                key={resource.id}
                resource={resource}
                index={index}
              />
            ))}
          </motion.div>
        ) : (
          <motion.div variants={RISE} className="empty">
            <Search />
            <h2>No resources found</h2>
            <p>Try a broader search or clear your filters.</p>
            <motion.button
              className="load-more empty-reset"
              whileTap={{ scale: 0.94 }}
              onClick={() => {
                setQuery("");
                setCollection("all");
                setCategory("all");
                setSort("relevance");
              }}
            >
              <RefreshCcw aria-hidden="true" />
              <span className="load-more-label">Clear search and filters</span>
            </motion.button>
          </motion.div>
        )}
        <motion.div variants={RISE} className="pagination-row">
          <div className="pagination-center">
            {visible < results.length && (
              <motion.button
                className="load-more"
                whileTap={{ scale: 0.94 }}
                onClick={() =>
                  setPagination({
                    key: paginationKey,
                    visible: nextVisibleCount(
                      visible,
                      results.length,
                      PAGE_SIZE,
                    ),
                  })
                }
                aria-controls="resource-grid"
              >
                <span className="load-more-label">
                  Show {Math.min(PAGE_SIZE, results.length - visible)} more
                </span>
                <span className="load-more-meta">
                  {shown} of {results.length}
                </span>
                <ChevronDown aria-hidden="true" />
              </motion.button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </motion.section>
  );
}
