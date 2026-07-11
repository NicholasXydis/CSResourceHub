import { useState } from "react";
import {
  googleFaviconUrl,
  initialFaviconSource,
  nextFaviconSource,
} from "../favicon";
import type { FaviconSource } from "../favicon";
import { domainOf, originFavicon } from "../utils";

export default function LogoMark({ url }: { url: string }) {
  const domain = domainOf(url);
  const [source, setSource] = useState<FaviconSource>(() =>
    initialFaviconSource(domain),
  );
  const imageUrl =
    source === "google" ? googleFaviconUrl(domain) : originFavicon(url);
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
          src={imageUrl}
          alt=""
          width="28"
          height="28"
          loading="lazy"
          decoding="async"
          referrerPolicy="no-referrer"
          onError={handleError}
        />
      )}
    </div>
  );
}
