import type { Transition, Variants } from "framer-motion";
import { PAGE_SIZE } from "./config";

export const SPRING: Transition = {
  type: "spring",
  stiffness: 390,
  damping: 24,
  mass: 0.72,
};
export const CASCADE_STEP = 0.065;
export const CONTAINER: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: CASCADE_STEP, delayChildren: CASCADE_STEP },
  },
};
export const RISE: Variants = {
  hidden: { opacity: 0, y: 26, scale: 0.975, filter: "blur(10px)" },
  show: { opacity: 1, y: 0, scale: 1, filter: "blur(0px)", transition: SPRING },
};
export const CARD_RISE: Variants = {
  hidden: { opacity: 0, y: 54, scale: 0.94, rotateX: 5, filter: "blur(12px)" },
  show: (index: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    rotateX: 0,
    filter: "blur(0px)",
    transition: { ...SPRING, delay: (index % PAGE_SIZE) * CASCADE_STEP },
  }),
};
