import { useState } from "react";
import {
  initialFaviconSource,
  localLogoUrl,
  nextFaviconSource,
} from "../favicon";
import type { FaviconSource } from "../favicon";
import { domainOf } from "../utils";

export default function LogoMark({ url }: { url: string }) {
  const domain = domainOf(url);
  const [source, setSource] = useState<FaviconSource>(() =>
    initialFaviconSource(domain),
  );
  const handleError = () => setSource(nextFaviconSource);
  return (
    <div
      className={
        source === "fallback" ? "resource-logo fallback-logo" : "resource-logo"
      }
      aria-hidden="true"
    >
      {source === "fallback" ? (
        <img src="/favicon.svg" alt="" width="28" height="28" />
      ) : (
        <img
          src={localLogoUrl(domain)}
          alt=""
          width="28"
          height="28"
          loading="lazy"
          decoding="async"
          onError={handleError}
        />
      )}
    </div>
  );
}
