import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import { CATEGORY_LABELS } from "../config";
import { CARD_RISE } from "../motion";
import type { Resource } from "../types";
import { FALLBACK_TYPE, badgeStyle, domainOf } from "../utils";
import LogoMark from "./LogoMark";

interface ResourceCardProps {
  resource: Resource;
  index: number;
}

export default function ResourceCard({ resource, index }: ResourceCardProps) {
  return (
    <motion.article
      layout
      variants={CARD_RISE}
      custom={index}
      initial="hidden"
      animate="show"
      exit={{ opacity: 0, scale: 0.92, y: 22 }}
      className="resource-card"
      style={badgeStyle(resource.type || FALLBACK_TYPE)}
      whileHover={{ y: -7, scale: 1.016 }}
      whileTap={{ scale: 0.992 }}
    >
      <div className="card-head">
        <LogoMark url={resource.url} />
        <div>
          <h3>{resource.name}</h3>
          <a href={resource.url} target="_blank" rel="noreferrer">
            {domainOf(resource.url)}
          </a>
        </div>
        <span className="type">{resource.type || FALLBACK_TYPE}</span>
      </div>
      <p>{resource.description}</p>
      <div className="card-foot">
        <div>
          <span>{CATEGORY_LABELS[resource.category]}</span>
        </div>
        <a
          href={resource.url}
          target="_blank"
          rel="noreferrer"
          aria-label={`Visit ${resource.name}`}
        >
          Visit <ArrowUpRight />
        </a>
      </div>
    </motion.article>
  );
}
