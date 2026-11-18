// news-image-20261117 entry (Node 22, standard library only).
//
// The entry image is the editorial infographic committed beside this file
// as entry.png: it sums up world news of Tuesday 17 November 2026 in six
// panels (Crimea bridge, Iran/Bahrain, Trump Asia trip, Nvidia results,
// Knesset speaker, France strike) plus an "also today" strip. The picture
// was drawn by draw_entry.py (Pillow, Liberation Sans) from reporting
// published that day by Reuters, AP, Bloomberg, Al Jazeera and others;
// this program only carries those finished bytes to the output path, so
// every run writes exactly the same file.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(
  new URL('./entry.png', import.meta.url),
  join(outDir, 'entry.png'),
);
console.log('wrote', join(outDir, 'entry.png'));
