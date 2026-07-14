import { useState } from "react";
import { MotionConfig, motion } from "framer-motion";
import NotFound from "./components/NotFound";
import ResourceDirectory from "./components/ResourceDirectory";
import { Footer, Header, Hero } from "./components/SiteChrome";
import { CONTAINER, SPRING } from "./motion";
import { isKnownPath } from "./routing";

export default function App() {
  const [query, setQuery] = useState("");
  const notFound = !isKnownPath(window.location.pathname);
  return (
    <MotionConfig transition={SPRING} reducedMotion="user">
      <motion.div
        id="top"
        className="app"
        variants={CONTAINER}
        initial="hidden"
        animate="show"
      >
        {!notFound && (
          <a className="skip-link" href="#directory">
            Skip to resource directory
          </a>
        )}
        <motion.div
          className="ambient one"
          animate={{
            x: [0, 35, -12, 0],
            y: [0, 24, -8, 0],
            scale: [1, 1.1, 0.96, 1],
          }}
          transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="ambient two"
          animate={{
            x: [0, -28, 16, 0],
            y: [0, -18, 12, 0],
            scale: [1, 0.95, 1.08, 1],
          }}
          transition={{ duration: 11, repeat: Infinity, ease: "easeInOut" }}
        />
        <div className="noise" />
        <motion.div className="shell" variants={CONTAINER}>
          <Header />
          <main>
            {notFound ? (
              <NotFound />
            ) : (
              <>
                <Hero query={query} setQuery={setQuery} />
                <ResourceDirectory query={query} setQuery={setQuery} />
              </>
            )}
          </main>
          {!notFound && <Footer />}
        </motion.div>
      </motion.div>
    </MotionConfig>
  );
}
