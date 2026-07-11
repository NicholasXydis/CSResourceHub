import { useEffect, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import { motion } from "framer-motion";
import { CA } from "country-flag-icons/react/3x2";
import {
  ArrowUp,
  BookOpen,
  Boxes,
  Github,
  Layers3,
  Menu,
  Search,
  X,
} from "lucide-react";
import { CATEGORY_LABELS, GITHUB_URL, GROUPS, SITE_DATA } from "../config";
import { CONTAINER, RISE } from "../motion";

export function Header() {
  const [open, setOpen] = useState(false);
  return (
    <motion.header variants={RISE} className="topbar">
      <motion.a
        className="brand"
        href="#top"
        aria-label="CS Resource Hub home"
        whileHover={{ y: -2, scale: 1.025 }}
        whileTap={{ scale: 0.975 }}
      >
        <span className="brand-mark">
          <img src="/favicon.svg" alt="" width="34" height="34" />
        </span>
        <span>
          CS<span>ResourceHub</span>
        </span>
      </motion.a>
      <button
        className="menu-button"
        onClick={() => setOpen((value) => !value)}
        aria-label="Toggle navigation"
        aria-expanded={open}
      >
        {open ? <X /> : <Menu />}
      </button>
      <nav
        className={open ? "nav open" : "nav"}
        aria-label="Primary navigation"
      >
        <motion.a
          href={`${GITHUB_URL}/blob/main/CONTRIBUTING.md`}
          target="_blank"
          rel="noreferrer"
          whileHover={{ y: -3, scale: 1.05 }}
          whileTap={{ scale: 0.96 }}
        >
          Contribute
        </motion.a>
        <motion.a
          className="github-pill"
          href={GITHUB_URL}
          target="_blank"
          rel="noreferrer"
          whileHover={{ y: -3, scale: 1.055 }}
          whileTap={{ scale: 0.96 }}
        >
          <Github size={17} /> GitHub
        </motion.a>
      </nav>
    </motion.header>
  );
}

export interface SearchControls {
  query: string;
  setQuery: Dispatch<SetStateAction<string>>;
}

export function Hero({ query, setQuery }: SearchControls) {
  const searchRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "/" && document.activeElement?.tagName !== "INPUT") {
        event.preventDefault();
        searchRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);
  return (
    <motion.section
      className="hero"
      variants={CONTAINER}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={RISE} className="eyebrow">
        <CA className="canada-flag" role="img" aria-label="Canadian flag" />{" "}
        Maintained directory for Canadian CS students
      </motion.div>
      <motion.h1 variants={RISE}>
        A practical starting point
        <br />
        for <span>CS students</span>
      </motion.h1>
      <motion.p variants={RISE}>
        Discover courses, communities, events, tools, and opportunities
        <br /> curated to help you learn, build, and grow
      </motion.p>
      <motion.label
        variants={RISE}
        className="search-box"
        whileHover={{ y: -3, scale: 1.012 }}
        whileTap={{ scale: 0.995 }}
      >
        <Search size={22} />
        <input
          ref={searchRef}
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search resources…"
          aria-label="Search resources"
        />
        {query ? (
          <button onClick={() => setQuery("")} aria-label="Clear search">
            <X size={17} />
          </button>
        ) : (
          <kbd>/</kbd>
        )}
      </motion.label>
      <motion.div variants={CONTAINER} className="stats">
        <motion.div variants={RISE}>
          <BookOpen />
          <strong>{SITE_DATA.total}+</strong>
          <span>Resources</span>
        </motion.div>
        <motion.div variants={RISE}>
          <Boxes />
          <strong>{Object.keys(CATEGORY_LABELS).length}</strong>
          <span>Categories</span>
        </motion.div>
        <motion.div variants={RISE}>
          <Layers3 />
          <strong>{GROUPS.length}</strong>
          <span>Collections</span>
        </motion.div>
        <motion.div variants={RISE} className="open-source-stat">
          <Github />
          <strong>Open Source</strong>
          <span>100% Free</span>
        </motion.div>
      </motion.div>
    </motion.section>
  );
}
export function Footer() {
  return (
    <motion.footer variants={RISE}>
      <motion.a className="back-to-top" href="#top" whileTap={{ scale: 0.94 }}>
        <ArrowUp aria-hidden="true" /> Back to top
      </motion.a>
    </motion.footer>
  );
}
