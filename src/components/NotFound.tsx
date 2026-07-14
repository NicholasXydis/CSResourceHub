import { motion } from "framer-motion";
import { ArrowLeft, CircleX, Search } from "lucide-react";
import { GITHUB_URL, SITE_DATA } from "../config";
import { CONTAINER, RISE } from "../motion";

export default function NotFound() {
  return (
    <motion.section
      className="hero not-found"
      variants={CONTAINER}
      initial="hidden"
      animate="show"
    >
      <motion.div variants={RISE} className="eyebrow">
        <CircleX className="not-found-icon" aria-hidden="true" />
        <span className="not-found-label">404 · Page not found</span>
      </motion.div>
      <motion.h1 variants={RISE}>
        This page took
        <br />a <span>wrong turn</span>
      </motion.h1>
      <motion.p variants={RISE}>
        The page you are looking for does not exist or has moved.
        <br />
        All {SITE_DATA.total} resources are still waiting on the home page.
      </motion.p>
      <motion.div variants={RISE} className="not-found-actions">
        <motion.a
          className="not-found-primary"
          href="/"
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
        >
          <ArrowLeft aria-hidden="true" /> Back to the directory
        </motion.a>
        <motion.a
          className="not-found-secondary"
          href={`${GITHUB_URL}/issues`}
          target="_blank"
          rel="noreferrer"
          whileHover={{ y: -3, scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
        >
          <Search aria-hidden="true" /> Report a broken link
        </motion.a>
      </motion.div>
    </motion.section>
  );
}
