const BASE_PATHS = new Set(["/", "/index.html", ""]);

export function isKnownPath(pathname: string): boolean {
  return BASE_PATHS.has(pathname.replace(/\/+$/, "") || "/");
}
