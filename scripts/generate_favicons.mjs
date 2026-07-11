import { readFile, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import pngToIco from "png-to-ico";
import sharp from "sharp";

const svgPath = new URL("../public/favicon.svg", import.meta.url);
const icoPath = new URL("../public/favicon.ico", import.meta.url);
const svg = await readFile(svgPath);
const sizes = [16, 32, 48, 64];
const temporaryFiles = sizes.map((size) =>
  join(tmpdir(), `csresourcehub-favicon-${process.pid}-${size}.png`),
);

try {
  await Promise.all(
    temporaryFiles.map((file, index) =>
      sharp(svg).resize(sizes[index], sizes[index]).png().toFile(file),
    ),
  );
  const ico = await pngToIco(temporaryFiles);
  await writeFile(icoPath, ico);
} finally {
  await Promise.all(
    temporaryFiles.map((file) => unlink(file).catch(() => undefined)),
  );
}
