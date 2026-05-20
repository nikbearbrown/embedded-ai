#!/usr/bin/env node
// SCRIPTS/svg-to-png.mjs
// Convert every images/**/*.svg to a 300dpi PNG.
// Idempotent: skips PNG if newer than the SVG source.
// Usage: node SCRIPTS/svg-to-png.mjs

import { readdir, stat, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, dirname, basename, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), '..');
const IMAGES_DIR = join(ROOT, 'images');
const DPI = 300;

async function walk(dir) {
  const out = [];
  let entries;
  try {
    entries = await readdir(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const ent of entries) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) {
      out.push(...(await walk(p)));
    } else if (ent.isFile() && ent.name.toLowerCase().endsWith('.svg')) {
      out.push(p);
    }
  }
  return out;
}

async function needsRebuild(svgPath, pngPath) {
  if (!existsSync(pngPath)) return true;
  const [s, p] = await Promise.all([stat(svgPath), stat(pngPath)]);
  return s.mtimeMs > p.mtimeMs;
}

function getSvgDims(svgText) {
  const vb = svgText.match(/viewBox\s*=\s*"\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s*"/i);
  if (vb) return { w: parseFloat(vb[3]), h: parseFloat(vb[4]) };
  const w = svgText.match(/<svg[^>]*\swidth\s*=\s*"(\d+(?:\.\d+)?)/i);
  const h = svgText.match(/<svg[^>]*\sheight\s*=\s*"(\d+(?:\.\d+)?)/i);
  return { w: w ? parseFloat(w[1]) : 700, h: h ? parseFloat(h[1]) : 420 };
}

async function convert(svgPath) {
  const pngPath = svgPath.replace(/\.svg$/i, '.png');
  if (!(await needsRebuild(svgPath, pngPath))) {
    return { skipped: true, svgPath, pngPath };
  }
  const svg = await readFile(svgPath);
  const { w, h } = getSvgDims(svg.toString('utf8'));
  // 300dpi: 1 user unit = 1/96 inch in CSS pixels. Scale to (w * DPI / 96).
  const scale = DPI / 96;
  const outW = Math.round(w * scale);
  const outH = Math.round(h * scale);
  await sharp(svg, { density: DPI })
    .resize(outW, outH, { fit: 'fill' })
    .png({ compressionLevel: 9 })
    .toFile(pngPath);
  return { skipped: false, svgPath, pngPath, outW, outH };
}

async function main() {
  const files = await walk(IMAGES_DIR);
  let converted = 0, skipped = 0, failed = 0;
  for (const f of files) {
    try {
      const r = await convert(f);
      if (r.skipped) { skipped++; }
      else {
        converted++;
        console.log(`[png] ${basename(f).replace(/\.svg$/, '.png')}  ${r.outW}x${r.outH}`);
      }
    } catch (e) {
      failed++;
      console.error(`[fail] ${f}: ${e.message}`);
    }
  }
  console.log(`\nSummary: ${converted} converted, ${skipped} skipped (up to date), ${failed} failed`);
}

main().catch(e => { console.error(e); process.exit(1); });
