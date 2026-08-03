import { createRequire } from "node:module";
import { resolve } from "node:path";

const require = createRequire(import.meta.url);
const sharp = require("sharp");

const [backgroundArg, outputArg, modeArg = "full"] = process.argv.slice(2);

if (!backgroundArg || !outputArg) {
  console.error("Usage: node compose_trackway_evidence_plate.mjs <background.png> <output.png> [full|theropod-only]");
  process.exit(1);
}

const width = 1672;
const height = 941;
const corridorCenters = [190, 620, 1050, 1480];
const leftStrideY = [74, 294, 514, 734];
const rightStrideY = [184, 404, 624, 844];
const theropodSteps = [
  [58, 84, 114],
  [250, 218, 116],
  [424, 304, 117],
  [620, 350, 118],
  [804, 458, 118],
  [1050, 568, 118],
  [1232, 652, 117],
  [1480, 780, 116],
  [1630, 862, 114],
];

function pesImpression(x, y, rotation, scale = 1) {
  return `
    <g transform="translate(${x} ${y}) rotate(${rotation}) scale(${scale})" filter="url(#soft-impression)">
      <path d="M -34 -47 C -50 -28 -49 17 -34 38 C -22 54 19 55 33 37 C 48 18 49 -23 34 -43 C 20 -59 -20 -61 -34 -47 Z"
        fill="#1d1814" fill-opacity="0.58" stroke="#d7cbb2" stroke-opacity="0.34" stroke-width="5"/>
      <path d="M -23 35 Q -12 48 -3 37 Q 7 51 16 37 Q 24 45 31 31"
        fill="none" stroke="#0d0b09" stroke-opacity="0.38" stroke-width="6" stroke-linecap="round"/>
      <ellipse cx="-8" cy="-11" rx="20" ry="28" fill="#0f0d0b" fill-opacity="0.16"/>
    </g>`;
}

function manusImpression(x, y, rotation, scale = 1) {
  return `
    <g transform="translate(${x} ${y}) rotate(${rotation}) scale(${scale})" filter="url(#soft-impression)">
      <path d="M -26 5 Q 0 -22 26 5 Q 18 23 0 25 Q -18 23 -26 5 Z"
        fill="#211b16" fill-opacity="0.55" stroke="#dacdb4" stroke-opacity="0.32" stroke-width="4"/>
      <path d="M -18 6 Q 0 -10 18 6" fill="none" stroke="#0f0c0a" stroke-opacity="0.28" stroke-width="5" stroke-linecap="round"/>
    </g>`;
}

function sauropodRail(x, ys, railIndex) {
  return ys.map((y, stepIndex) => {
    const nudge = ((railIndex * 3 + stepIndex * 5) % 9) - 4;
    const rotation = ((railIndex * 7 + stepIndex * 3) % 11) - 5;
    const scale = 0.94 + (((railIndex + stepIndex) % 4) * 0.025);
    return [
      pesImpression(x + nudge, y, rotation, scale),
      manusImpression(x + nudge + (railIndex % 2 === 0 ? 7 : -7), y + 69, rotation * 0.65, scale),
    ].join("");
  }).join("");
}

function theropodImpression(x, y, rotation, index) {
  const scale = 1.02 + ((index % 3) * 0.04);
  return `
    <g transform="translate(${x} ${y}) rotate(${rotation}) scale(${scale})" filter="url(#soft-impression)">
      <path d="M 0 23 C -10 22 -14 11 -10 2 L -25 -17 C -31 -24 -25 -31 -18 -26 L -5 -11 L -5 -35 C -5 -45 5 -45 5 -35 L 5 -10 L 18 -26 C 25 -31 31 -24 25 -17 L 10 2 C 14 11 10 22 0 23 Z"
        fill="#18130f" fill-opacity="0.58" stroke="#d8cbb2" stroke-opacity="0.24" stroke-width="3" stroke-linejoin="round"/>
      <ellipse cx="0" cy="9" rx="9" ry="10" fill="#0e0b09" fill-opacity="0.16"/>
    </g>`;
}

const sauropodTracks = corridorCenters.map((center, corridorIndex) => {
  const leftX = center - 62;
  const rightX = center + 62;
  return `
    <g data-trackway="${corridorIndex + 1}">
      ${sauropodRail(leftX, leftStrideY, corridorIndex * 2)}
      ${sauropodRail(rightX, rightStrideY, corridorIndex * 2 + 1)}
    </g>`;
}).join("");

const theropodTrack = theropodSteps
  .map(([x, y, rotation], index) => theropodImpression(x, y, rotation, index))
  .join("");

const overlay = Buffer.from(`
  <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
    <defs>
      <filter id="soft-impression" x="-35%" y="-35%" width="170%" height="170%">
        <feTurbulence type="fractalNoise" baseFrequency="0.028" numOctaves="2" seed="41" result="noise"/>
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.4" xChannelSelector="R" yChannelSelector="G" result="rough"/>
        <feDropShadow in="rough" dx="5" dy="6" stdDeviation="4" flood-color="#090705" flood-opacity="0.42"/>
        <feDropShadow in="rough" dx="-3" dy="-3" stdDeviation="3" flood-color="#e6dcc5" flood-opacity="0.26"/>
      </filter>
    </defs>
    <g style="mix-blend-mode:multiply">
      ${modeArg === "theropod-only" ? "" : sauropodTracks}
      ${theropodTrack}
    </g>
  </svg>`);

const outputPath = resolve(outputArg);
await sharp(resolve(backgroundArg))
  .resize(width, height, { fit: "cover" })
  .composite([{ input: overlay, blend: "over" }])
  .png({ compressionLevel: 9 })
  .toFile(outputPath);

const metadata = await sharp(outputPath).metadata();
console.log(JSON.stringify({ output: outputPath, width: metadata.width, height: metadata.height }));
