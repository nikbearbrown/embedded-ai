import sharp from 'sharp';
import { glob } from 'glob';
import { statSync } from 'fs';

const file = process.argv[2];

if (file) {
  // Single file mode
  const out = file.replace('.svg', '.png');
  await sharp(file, { density: 300 }).png().toFile(out);
  console.log(`${file} → ${out}`);
} else {
  // Batch mode: all SVGs under images/
  const files = await glob('images/**/*.svg');
  for (const f of files) {
    const out = f.replace('.svg', '.png');
    try {
      const svgMtime = statSync(f).mtimeMs;
      const pngMtime = statSync(out).mtimeMs;
      if (pngMtime > svgMtime) {
        console.log(`skipped (up to date): ${out}`);
        continue;
      }
    } catch {
      // PNG doesn't exist yet — proceed
    }
    await sharp(f, { density: 300 }).png().toFile(out);
    console.log(`${f} → ${out}`);
  }
}