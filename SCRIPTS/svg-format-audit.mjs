#!/usr/bin/env node
// svg-format-audit.mjs — FORMAT-conformance gate for generated SVGs.
//
// Complements svg-layout-audit.mjs (which checks how a figure LOOKS).
// This checks whether the file is a VALID, ANIMATABLE vector asset — the
// thing cajal produced "reliably" but nothing was actually enforcing.
//
//   FAIL  NO_SVG       no <svg> root element
//   FAIL  NO_VIEWBOX   root <svg> has no viewBox (not resolution-independent)
//   FAIL  RASTER       contains <image> (a bitmap smuggled inside an SVG)
//   FAIL  NO_VECTOR    no path/shape/text element to draw or animate
//   warn  NO_XMLNS     root <svg> missing xmlns (some renderers choke)
//   warn  NO_TITLE     no <title> (accessibility / searchability)
//   warn  FLAT         no <g> groups (harder to animate clusters)
//
// Usage:
//   node SCRIPTS/svg-format-audit.mjs [dir|file ...]   # default: scan cwd for *.svg
//   STRICT=1 node SCRIPTS/svg-format-audit.mjs ...      # warnings also fail the gate
//
// Exit code = number of FAILING files (0 = all clean). A real gate: it blocks.

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const STRICT = process.env.STRICT === "1" || process.argv.includes("--strict");
const roots = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const SKIP = /(^|\/)(node_modules|output|\.git)(\/|$)/;
const VECTOR = /<(path|rect|circle|ellipse|line|polyline|polygon|text)\b/i;

function walk(dir, out = []) {
  let entries;
  try { entries = readdirSync(dir); } catch { return out; }
  for (const e of entries) {
    const p = join(dir, e);
    if (SKIP.test(p)) continue;
    let st; try { st = statSync(p); } catch { continue; }
    if (st.isDirectory()) walk(p, out);
    else if (e.toLowerCase().endsWith(".svg")) out.push(p);
  }
  return out;
}

function audit(file) {
  const s = readFileSync(file, "utf8");
  const fails = [], warns = [];
  const root = s.match(/<svg\b[^>]*>/i);
  if (!root) { fails.push("NO_SVG       no <svg> root element"); return { fails, warns }; }
  const tag = root[0];
  if (!/\bviewBox\s*=/.test(tag)) fails.push("NO_VIEWBOX   root <svg> has no viewBox");
  if (/<image\b/i.test(s))        fails.push("RASTER       contains <image> (embedded bitmap)");
  if (!VECTOR.test(s))            fails.push("NO_VECTOR    no path/shape/text to draw");
  if (!/\bxmlns\s*=/.test(tag))   warns.push("NO_XMLNS     root <svg> missing xmlns");
  if (!/<title\b/i.test(s))       warns.push("NO_TITLE     no <title> (accessibility)");
  if (!/<g\b/i.test(s))           warns.push("FLAT         no <g> groups (harder to animate clusters)");
  return { fails, warns };
}

const targets = (roots.length ? roots : ["."]).flatMap((r) => {
  let st; try { st = statSync(r); } catch { console.log(`svg-format-audit: skip missing path '${r}'`); return []; }
  return st.isDirectory() ? walk(r) : (r.toLowerCase().endsWith(".svg") ? [r] : []);
});

if (!targets.length) { console.log("svg-format-audit: no .svg files found."); process.exit(0); }

let failed = 0, warned = 0;
for (const f of [...new Set(targets)].sort()) {
  const { fails, warns } = audit(f);
  const rel = relative(".", f);
  if (fails.length) { failed++; for (const m of fails) console.log(`FAIL  ${rel}\n        ${m}`); }
  if (warns.length) { warned++; for (const m of warns) console.log(`warn  ${rel}\n        ${m}`); }
}

console.log(`\nsvg-format-audit: ${targets.length} files · ${failed} failed · ${warned} with warnings${STRICT ? " (strict: warnings fail)" : ""}`);
process.exit(Math.min(failed + (STRICT ? warned : 0), 255));
