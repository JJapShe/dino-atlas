import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import fs from "node:fs";

const require = createRequire(import.meta.url);

function loadSharp() {
  try {
    return require("sharp");
  } catch (error) {
    const bundled = join(dirname(dirname(process.execPath)), "node_modules", "sharp");
    try {
      return require(bundled);
    } catch {
      throw error;
    }
  }
}

const sharp = loadSharp();
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");
const WIDTH = 1672;
const HEIGHT = 941;
const DEFAULT_SEED = 2026080701;

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    args[token.slice(2)] = argv[index + 1];
    index += 1;
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (!args.background || !args.output || !args.guide || !args.metrics) {
  console.error(
    "Usage: node compose_trackway_evidence_plate_v2.mjs --background <empty-mud.png> --output <preview.png> --guide <guide.svg> --metrics <review.json> [--seed 2026080701]",
  );
  process.exit(1);
}

const seed = Number(args.seed || DEFAULT_SEED);
if (!Number.isSafeInteger(seed) || seed <= 0) throw new Error(`Invalid seed: ${args.seed}`);

function mulberry32(initialSeed) {
  let state = initialSeed >>> 0;
  return () => {
    state += 0x6d2b79f5;
    let value = state;
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

const random = mulberry32(seed);
const range = (minimum, maximum) => minimum + (maximum - minimum) * random();
const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));
const radians = (degrees) => (degrees * Math.PI) / 180;
const degrees = (angle) => (angle * 180) / Math.PI;
const round = (value, precision = 3) => Number(value.toFixed(precision));

function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function standardDeviation(values) {
  const average = mean(values);
  return Math.sqrt(mean(values.map((value) => (value - average) ** 2)));
}

function coefficientOfVariation(values) {
  return standardDeviation(values) / mean(values);
}

function targetedSeries(average, count, targetCv) {
  const raw = Array.from({ length: count }, () => random() * 2 - 1);
  const rawMean = mean(raw);
  const centered = raw.map((value) => value - rawMean);
  const rawSd = standardDeviation(centered) || 1;
  return centered.map((value) => average * (1 + (targetCv * value) / rawSd));
}

function correlatedField(x, y, phase) {
  const low = Math.sin(x / 287 + y / 463 + phase);
  const cross = Math.sin(x / 641 - y / 331 + phase * 0.71);
  const patch = Math.cos(x / 419 + y / 229 - phase * 1.13);
  return clamp(0.5 + low * 0.22 + cross * 0.16 + patch * 0.12, 0, 1);
}

const corridorTemplates = [
  { center: 185, rail: 116, heading: -3.8, curve: 13.5, stride: 216, start: 52 },
  { center: 493, rail: 136, heading: 4.9, curve: -13, stride: 224, start: 76 },
  { center: 1032, rail: 125, heading: -2.7, curve: 11.5, stride: 221, start: 43 },
  { center: 1461, rail: 143, heading: 5.8, curve: -13.5, stride: 228, start: 66 },
];

const impressions = [];
const pairs = [];
const corridors = [];

function centerAt(corridor, y) {
  const normalized = (y - HEIGHT / 2) / (HEIGHT / 2);
  return corridor.center
    + Math.tan(radians(corridor.heading)) * (y - HEIGHT / 2)
    + corridor.curve * (normalized ** 2 - 0.34);
}

function railAt(corridor, y) {
  const field = correlatedField(corridor.center, y, corridor.phase + 0.8);
  return corridor.rail * (1 + (field - 0.5) * 0.12);
}

function tangentAt(corridor, y) {
  const delta = 4;
  return degrees(Math.atan2(centerAt(corridor, y + delta) - centerAt(corridor, y - delta), delta * 2));
}

function addPair(corridor, side, stepIndex, y, phaseRatio) {
  const railWidth = railAt(corridor, y);
  const sideSign = side === "left" ? -1 : 1;
  const x = centerAt(corridor, y) + sideSign * railWidth / 2;
  const pathYaw = tangentAt(corridor, y);
  const yawResidual = range(-6.8, 6.8) + (correlatedField(x, y, corridor.phase + 1.4) - 0.5) * 3.4;
  const rotation = pathYaw + yawResidual;
  const depth = clamp(0.55 + correlatedField(x, y, corridor.phase) * 0.43, 0.55, 0.98);
  const scaleX = range(0.91, 1.09);
  const scaleY = range(0.9, 1.1);
  const pairId = `s${corridor.index + 1}-${side[0]}${stepIndex + 1}`;
  const pes = {
    id: `${pairId}-pes`,
    type: "sauropod-pes",
    corridor: corridor.index + 1,
    side,
    stepIndex: stepIndex + 1,
    x,
    y,
    rotation,
    yawResidual,
    scaleX,
    scaleY,
    depth,
    radius: 43 * Math.max(scaleX, scaleY),
    visibility: 1,
    phaseRatio,
  };
  const headingAngle = radians(rotation);
  const forward = range(57, 70);
  const lateral = range(-5, 5);
  const manus = {
    ...pes,
    id: `${pairId}-manus`,
    type: "sauropod-manus",
    x: x + Math.sin(headingAngle) * forward + Math.cos(headingAngle) * lateral,
    y: y - Math.cos(headingAngle) * forward + Math.sin(headingAngle) * lateral,
    rotation: rotation + range(-3.5, 3.5),
    yawResidual: yawResidual + range(-2, 2),
    scaleX: scaleX * range(0.74, 0.84),
    scaleY: scaleY * range(0.68, 0.8),
    radius: 24 * Math.max(scaleX, scaleY),
    depth: clamp(depth + range(-0.08, 0.06), 0.48, 0.98),
  };
  pairs.push({ id: pairId, corridor: corridor.index + 1, side, stepIndex: stepIndex + 1, phaseRatio, railWidth });
  impressions.push(pes, manus);
}

for (let corridorIndex = 0; corridorIndex < corridorTemplates.length; corridorIndex += 1) {
  const template = corridorTemplates[corridorIndex];
  const corridor = {
    index: corridorIndex,
    center: template.center + range(-8, 8),
    rail: template.rail * range(0.975, 1.025),
    heading: template.heading + range(-0.45, 0.45),
    curve: template.curve + range(-1.35, 1.35),
    phase: range(0, Math.PI * 2),
  };
  const targetCv = range(0.072, 0.098);
  const strides = targetedSeries(template.stride, 3, targetCv);
  const leftY = [template.start + range(-7, 7)];
  for (const stride of strides) leftY.push(leftY.at(-1) + stride);
  const phaseRatios = Array.from({ length: 4 }, (_, index) => {
    const local = strides[Math.min(index, strides.length - 1)];
    const smooth = correlatedField(corridor.center, leftY[index], corridor.phase + 2.2);
    return clamp(0.43 + smooth * 0.14 + range(-0.015, 0.015), 0.42, 0.58);
  });
  const rightY = leftY.map((y, index) => y + phaseRatios[index] * strides[Math.min(index, strides.length - 1)]);
  corridor.leftY = leftY;
  corridor.rightY = rightY;
  corridor.strides = strides;
  corridor.phaseRatios = phaseRatios;
  corridors.push(corridor);
  leftY.forEach((y, index) => addPair(corridor, "left", index, y, phaseRatios[index]));
  rightY.forEach((y, index) => addPair(corridor, "right", index, y, phaseRatios[index]));
}

const sauropodImpressions = [...impressions];
const theropodStrideTarget = targetedSeries(218, 8, range(0.112, 0.142));

function clearanceFromSauropods(x, y, radius) {
  return Math.min(...sauropodImpressions.map((item) => Math.hypot(x - item.x, y - item.y) - radius - item.radius));
}

const theropodPrints = [];
let bestTheropodRoute = null;
const angleDifference = (a, b) => Math.abs((((a - b) + 540) % 360) - 180);
const directionDegrees = 23;
const direction = { x: Math.cos(radians(directionDegrees)), y: Math.sin(radians(directionDegrees)) };
const baseRoute = [];
let cumulativeStride = 0;
for (let index = 0; index < 9; index += 1) {
  if (index > 0) cumulativeStride += theropodStrideTarget[index - 1];
  baseRoute.push({
    x: 40 + direction.x * cumulativeStride,
    y: 92 + direction.y * cumulativeStride,
  });
}

for (let threshold = 20; threshold >= 15 && !bestTheropodRoute; threshold -= 1) {
  const layers = [];
  for (let pointIndex = 0; pointIndex < baseRoute.length; pointIndex += 1) {
    const point = baseRoute[pointIndex];
    const radius = 29 + (pointIndex % 2) * 1.5;
    let candidates = Array.from({ length: 81 }, (_, index) => -200 + index * 5).flatMap((normalOffset) => (
      Array.from({ length: 29 }, (_, index) => -140 + index * 10).map((alongOffset) => {
        const x = point.x - direction.y * normalOffset + direction.x * alongOffset;
        const y = point.y + direction.x * normalOffset + direction.y * alongOffset;
        const frameMargin = radius + 8;
        if (x < frameMargin || x > WIDTH - frameMargin || y < frameMargin || y > HEIGHT - frameMargin) return null;
        const clearance = clearanceFromSauropods(x, y, radius);
        if (clearance < threshold) return null;
        return { x, y, radius, clearance, normalOffset, alongOffset, cost: Infinity, previous: null };
      })
    )).filter(Boolean)
      .sort((a, b) => (Math.abs(a.normalOffset) + Math.abs(a.alongOffset) * 0.75) - (Math.abs(b.normalOffset) + Math.abs(b.alongOffset) * 0.75))
      .slice(0, 420);
    if (!candidates.length) break;

    if (pointIndex === 0) {
      for (const candidate of candidates) {
        candidate.cost = Math.abs(candidate.normalOffset) * 0.05 + Math.abs(candidate.alongOffset) * 0.04;
        candidate.heading = directionDegrees;
      }
    } else {
      const previousLayer = layers.at(-1);
      const targetStride = theropodStrideTarget[pointIndex - 1];
      for (const candidate of candidates) {
        for (const previous of previousLayer) {
          const deltaX = candidate.x - previous.x;
          const deltaY = candidate.y - previous.y;
          const actualStride = Math.hypot(deltaX, deltaY);
          const forwardTravel = deltaX * direction.x + deltaY * direction.y;
          if (deltaX <= 0 || forwardTravel < targetStride * 0.5 || forwardTravel > targetStride * 1.5) continue;
          if (actualStride < targetStride * 0.65 || actualStride > targetStride * 1.45) continue;
          const heading = degrees(Math.atan2(deltaY, deltaX));
          const headingChange = pointIndex > 1 ? angleDifference(heading, previous.heading) : angleDifference(heading, directionDegrees);
          if (headingChange > 48) continue;
          const strideError = Math.abs(actualStride - targetStride);
          const cost = previous.cost
            + Math.abs(candidate.normalOffset) * 0.02
            + Math.abs(candidate.alongOffset) * 0.015
            + Math.abs(candidate.normalOffset - previous.normalOffset) * 0.14
            + Math.abs(candidate.alongOffset - previous.alongOffset) * 0.1
            + strideError * 2.8
            + headingChange * 3.2;
          if (cost < candidate.cost) {
            candidate.cost = cost;
            candidate.previous = previous;
            candidate.heading = heading;
          }
        }
      }
      candidates = candidates.filter((candidate) => Number.isFinite(candidate.cost) && candidate.previous);
      if (!candidates.length) break;
    }
    layers.push(candidates);
  }
  if (layers.length !== 9) continue;

  for (const finalCandidate of [...layers.at(-1)].sort((a, b) => a.cost - b.cost)) {
    const route = [];
    let cursor = finalCandidate;
    while (cursor) {
      route.push(cursor);
      cursor = cursor.previous;
    }
    route.reverse();
    if (route.length !== 9) continue;
    const distances = route.slice(1).map((point, index) => Math.hypot(point.x - route[index].x, point.y - route[index].y));
    const strideCv = coefficientOfVariation(distances);
    if (strideCv < 0.1 || strideCv > 0.18) continue;
    const headings = route.slice(1).map((point, index) => degrees(Math.atan2(point.y - route[index].y, point.x - route[index].x)));
    const maximumHeadingChange = Math.max(...headings.slice(1).map((heading, index) => angleDifference(heading, headings[index])));
    if (maximumHeadingChange > 48) continue;
    const clearances = route.map((point) => point.clearance);
    bestTheropodRoute = {
      route,
      clearances,
      minimum: Math.min(...clearances),
      average: mean(clearances),
      score: -finalCandidate.cost,
      startY: route[0].y,
      alongShift: route[0].alongOffset,
      directionDegrees,
      maximumHeadingChange,
      threshold,
    };
    break;
  }
}
if (!bestTheropodRoute) throw new Error("Could not place a coherent nine-print theropod route with the required clearance and stride variation");

for (let index = 0; index < bestTheropodRoute.route.length; index += 1) {
  const best = bestTheropodRoute.route[index];
  const radius = best.radius;
  const previous = bestTheropodRoute.route[Math.max(0, index - 1)];
  const next = bestTheropodRoute.route[Math.min(bestTheropodRoute.route.length - 1, index + 1)];
  const localHeading = degrees(Math.atan2(next.y - previous.y, next.x - previous.x));
  const yawResidual = range(-6.2, 6.2) + (correlatedField(best.x, best.y, seed * 0.000002) - 0.5) * 4;
  const depth = clamp(0.54 + correlatedField(best.x, best.y, seed * 0.000003) * 0.44, 0.54, 0.98);
  const print = {
    id: `t1-${index + 1}`,
    type: "theropod-pes",
    trackway: 1,
    stepIndex: index + 1,
    x: best.x,
    y: best.y,
    rotation: localHeading - 90 + yawResidual,
    yawResidual,
    scaleX: range(0.91, 1.09),
    scaleY: range(0.9, 1.1),
    depth,
    radius,
    visibility: 1,
    corridorClearance: bestTheropodRoute.clearances[index],
    routeStartY: bestTheropodRoute.startY,
    routeAlongShift: bestTheropodRoute.alongShift,
  };
  theropodPrints.push(print);
  impressions.push(print);
}

const wearRank = impressions
  .map((item, index) => ({ index, score: correlatedField(item.x, item.y, seed * 0.000004 + item.x * 0.0001) + range(-0.08, 0.08) }))
  .sort((a, b) => a.score - b.score)
  .slice(0, 10);
const wearReasons = ["thin-water-film", "surface-crack", "slumped-silt", "firm-patch"];
wearRank.forEach(({ index }, wearIndex) => {
  impressions[index].visibility = wearIndex < 2 ? range(0.24, 0.31) : range(0.44, 0.69);
  impressions[index].occlusionReason = wearReasons[wearIndex % wearReasons.length];
});
impressions.forEach((item, index) => {
  item.shape = {
    shoulder: range(0.82, 1.16),
    leftDigit: range(23, 31),
    middleDigit: range(34, 42),
    rightDigit: range(24, 33),
  };
  if (item.visibility < 1) {
    item.maskShape = {
      angle: range(-35, 35),
      offsetX: (index % 2 === 0 ? -1 : 1) * range(11, 27),
      offsetY: range(-16, 19),
      rx: item.radius * range(0.62, 0.88),
      ry: item.radius * range(0.45, 0.78),
      darkness: clamp(1 - item.visibility, 0.3, 0.78),
    };
  }
});

function impressionShape(item, guide = false) {
  const opacity = guide ? clamp(0.32 + item.depth * 0.6, 0.4, 0.92) : clamp(0.18 + item.depth * 0.23, 0.28, 0.42);
  const mask = item.visibility < 1 ? ` mask="url(#mask-${item.id})"` : "";
  const filter = guide ? "" : ` filter="url(#depth-${item.depth < 0.67 ? "shallow" : item.depth < 0.84 ? "medium" : "deep"})"`;
  const transform = `translate(${round(item.x)} ${round(item.y)}) rotate(${round(item.rotation)}) scale(${round(item.scaleX)} ${round(item.scaleY)})`;
  if (item.type === "sauropod-pes") {
    return `<g transform="${transform}"${filter}${mask} opacity="${round(opacity)}"><path d="M 0 -48 C ${round(33 * item.shape.shoulder)} -48 43 -20 40 12 C 37 42 18 54 -2 52 C -27 52 -42 34 -40 7 C -40 -21 -29 -45 0 -48 Z" fill="${guide ? "#382f26" : "#50483f"}"/><path d="M -31 25 C -15 39 12 41 31 24" fill="none" stroke="${guide ? "#665747" : "#312820"}" stroke-opacity=".28" stroke-width="5" stroke-linecap="round"/></g>`;
  }
  if (item.type === "sauropod-manus") {
    return `<g transform="${transform}"${filter}${mask} opacity="${round(opacity)}"><path d="M -27 7 C -18 -19 14 -24 28 3 C 20 24 -16 29 -27 7 Z" fill="${guide ? "#4b4034" : "#5a5045"}"/><path d="M -18 7 C -6 -7 10 -8 19 4" fill="none" stroke="#312820" stroke-opacity=".22" stroke-width="4" stroke-linecap="round"/></g>`;
  }
  const leftDigit = round(item.shape.leftDigit);
  const middleDigit = round(item.shape.middleDigit);
  const rightDigit = round(item.shape.rightDigit);
  return `<g transform="${transform}"${filter}${mask} opacity="${round(opacity)}"><path d="M 0 22 C -10 22 -14 11 -9 1 L -${leftDigit} -19 C -31 -26 -24 -33 -17 -27 L -5 -11 L -4 -${middleDigit} C -4 -49 5 -49 6 -${middleDigit} L 6 -10 L ${rightDigit - 7} -27 C ${rightDigit} -32 ${rightDigit + 5} -24 ${rightDigit - 1} -18 L 10 2 C 14 11 10 22 0 22 Z" fill="${guide ? "#302820" : "#493d34"}"/></g>`;
}

function maskDefinitions() {
  return impressions
    .filter((item) => item.visibility < 1)
    .map((item) => {
      const angle = round(item.maskShape.angle);
      const offsetX = round(item.maskShape.offsetX);
      const offsetY = round(item.maskShape.offsetY);
      const rx = round(item.maskShape.rx);
      const ry = round(item.maskShape.ry);
      const darkness = round(item.maskShape.darkness);
      return `<mask id="mask-${item.id}" maskUnits="userSpaceOnUse" x="${item.x - item.radius * 2}" y="${item.y - item.radius * 2}" width="${item.radius * 4}" height="${item.radius * 4}"><rect x="${item.x - item.radius * 2}" y="${item.y - item.radius * 2}" width="${item.radius * 4}" height="${item.radius * 4}" fill="white"/><ellipse cx="${round(item.x + offsetX)}" cy="${round(item.y + offsetY)}" rx="${rx}" ry="${ry}" transform="rotate(${angle} ${round(item.x)} ${round(item.y)})" fill="black" opacity="${darkness}" filter="url(#occlusion-soft)"/></mask>`;
    })
    .join("");
}

function svgDocument({ guide = false } = {}) {
  const defs = `<defs>
    <filter id="occlusion-soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5"/></filter>
    <filter id="depth-shallow" x="-45%" y="-45%" width="190%" height="190%"><feTurbulence type="fractalNoise" baseFrequency=".034" numOctaves="2" seed="${seed % 997}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="2.2"/><feDropShadow dx="2" dy="3" stdDeviation="3" flood-color="#0c0806" flood-opacity=".24"/><feDropShadow dx="-2" dy="-2" stdDeviation="2" flood-color="#e1d4bb" flood-opacity=".17"/></filter>
    <filter id="depth-medium" x="-45%" y="-45%" width="190%" height="190%"><feTurbulence type="fractalNoise" baseFrequency=".031" numOctaves="2" seed="${(seed + 41) % 997}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="3.1"/><feDropShadow dx="4" dy="5" stdDeviation="4" flood-color="#0b0705" flood-opacity=".34"/><feDropShadow dx="-3" dy="-3" stdDeviation="3" flood-color="#e1d4bb" flood-opacity=".22"/></filter>
    <filter id="depth-deep" x="-50%" y="-50%" width="200%" height="200%"><feTurbulence type="fractalNoise" baseFrequency=".028" numOctaves="3" seed="${(seed + 83) % 997}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="4.2"/><feDropShadow dx="6" dy="7" stdDeviation="5" flood-color="#090604" flood-opacity=".44"/><feDropShadow dx="-4" dy="-4" stdDeviation="3" flood-color="#e5d8bf" flood-opacity=".27"/></filter>
    ${maskDefinitions()}
  </defs>`;
  const background = guide
    ? `<rect width="${WIDTH}" height="${HEIGHT}" fill="#8b826f"/><path d="M0 0H${WIDTH}V72C1350 50 1110 86 850 64C610 44 350 83 0 57Z" fill="#6f8985" opacity=".7"/><path d="M0 58C340 80 630 44 905 67C1170 88 1410 55 ${WIDTH} 73" fill="none" stroke="#b9ad8f" stroke-width="16" opacity=".48"/>`
    : "";
  const corridorGuides = guide
    ? corridors.map((corridor) => `<path d="M ${round(centerAt(corridor, 0))} 0 Q ${round(centerAt(corridor, HEIGHT / 2))} ${HEIGHT / 2} ${round(centerAt(corridor, HEIGHT))} ${HEIGHT}" fill="none" stroke="#d9d0b9" stroke-opacity=".18" stroke-width="4" stroke-dasharray="13 17"/>`).join("")
    : "";
  const tracks = impressions.map((item) => impressionShape(item, guide)).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}">${defs}${background}${corridorGuides}<g${guide ? " style=\"mix-blend-mode:multiply\"" : ""}>${tracks}</g></svg>`;
}

function minimumCrossClearance() {
  const clearances = [];
  let superimpositions = 0;
  for (const theropod of theropodPrints) {
    for (const sauropod of sauropodImpressions) {
      const clearance = Math.hypot(theropod.x - sauropod.x, theropod.y - sauropod.y) - theropod.radius - sauropod.radius;
      clearances.push(clearance);
      if (clearance < 0) superimpositions += 1;
    }
  }
  return { minimum: Math.min(...clearances), superimpositions };
}

function exactPeriod(values) {
  for (let period = 1; period <= Math.floor(values.length / 2); period += 1) {
    let repeats = true;
    for (let index = period; index < values.length; index += 1) {
      if (Math.abs(values[index] - values[index % period]) > 0.000001) {
        repeats = false;
        break;
      }
    }
    if (repeats) return period;
  }
  return null;
}

const corridorCenters = corridors.map((corridor) => centerAt(corridor, HEIGHT / 2));
const corridorGaps = corridorCenters.slice(1).map((value, index) => value - corridorCenters[index]);
const strideLengths = corridors.flatMap((corridor) => [
  ...corridor.leftY.slice(1).map((y, index) => Math.hypot(y - corridor.leftY[index], centerAt(corridor, y) - centerAt(corridor, corridor.leftY[index]))),
  ...corridor.rightY.slice(1).map((y, index) => Math.hypot(y - corridor.rightY[index], centerAt(corridor, y) - centerAt(corridor, corridor.rightY[index]))),
]);
const railWidths = pairs.map((pair) => pair.railWidth);
const phaseRatios = corridors.flatMap((corridor) => corridor.phaseRatios);
const yawResiduals = impressions.map((item) => item.yawResidual);
const depthValues = impressions.map((item) => item.depth);
const partial = impressions.filter((item) => item.visibility < 0.7);
const ghosts = impressions.filter((item) => item.visibility < 0.35);
const headingDrifts = corridors.map((corridor) => Math.abs(tangentAt(corridor, HEIGHT - 30) - tangentAt(corridor, 30)));
const theropodDistances = theropodPrints.slice(1).map((item, index) => Math.hypot(item.x - theropodPrints[index].x, item.y - theropodPrints[index].y));
const theropodForwardAxisStepCount = theropodPrints.slice(1).filter((item, index) => item.x > theropodPrints[index].x && item.y > theropodPrints[index].y).length;
const theropodHeadings = theropodPrints.slice(1).map((item, index) => degrees(Math.atan2(item.y - theropodPrints[index].y, item.x - theropodPrints[index].x)));
const theropodMaximumHeadingChange = Math.max(...theropodHeadings.slice(1).map((heading, index) => angleDifference(heading, theropodHeadings[index])));
const crossing = minimumCrossClearance();
const corridorGapRatio = Math.max(...corridorGaps) / Math.min(...corridorGaps);
const corridorGapCv = coefficientOfVariation(corridorGaps);
const railMedian = [...railWidths].sort((a, b) => a - b)[Math.floor(railWidths.length / 2)];
const largestMudGap = Math.max(...corridorGaps) - railMedian;
const metrics = {
  schemaVersion: 1,
  reviewStatus: "draft-candidate-not-promoted",
  generatedAt: new Date().toISOString(),
  seed,
  input: {
    background: resolve(args.background),
  },
  output: {
    preview: resolve(args.output),
    guide: resolve(args.guide),
  },
  macroTopology: {
    sauropodCorridors: 4,
    sauropodManusPesPairs: pairs.length,
    sauropodImpressions: sauropodImpressions.length,
    theropodTrackways: 1,
    theropodPrints: theropodPrints.length,
    bodiesShown: false,
    exactTrackmakerClaim: false,
    temporalOrderClaim: false,
  },
  layout: {
    corridorCentersPx: corridorCenters.map((value) => round(value)),
    corridorGapsPx: corridorGaps.map((value) => round(value)),
    corridorGapCv: round(corridorGapCv),
    corridorGapRatio: round(corridorGapRatio),
    largestMudGapPx: round(largestMudGap),
    largestMudGapFraction: round(largestMudGap / WIDTH),
    sauropodStrideCv: round(coefficientOfVariation(strideLengths)),
    sauropodStrideRangePx: [round(Math.min(...strideLengths)), round(Math.max(...strideLengths))],
    railWidthCv: round(coefficientOfVariation(railWidths)),
    railWidthRangePx: [round(Math.min(...railWidths)), round(Math.max(...railWidths))],
    phaseRatioRange: [round(Math.min(...phaseRatios)), round(Math.max(...phaseRatios))],
    headingDriftRangeDegrees: [round(Math.min(...headingDrifts)), round(Math.max(...headingDrifts))],
    yawResidualStdDegrees: round(standardDeviation(yawResiduals)),
    yawExactPeriod: exactPeriod(yawResiduals),
    theropodStrideCv: round(coefficientOfVariation(theropodDistances)),
    theropodStrideRangePx: [round(Math.min(...theropodDistances)), round(Math.max(...theropodDistances))],
    theropodForwardAxisStepCount,
    theropodMaximumHeadingChangeDegrees: round(theropodMaximumHeadingChange),
  },
  preservation: {
    depthRangeNormalized: [round(Math.min(...depthValues)), round(Math.max(...depthValues))],
    depthCv: round(coefficientOfVariation(depthValues)),
    partialCount: partial.length,
    partialFraction: round(partial.length / impressions.length),
    ghostCount: ghosts.length,
    occlusionReasons: Object.fromEntries([...new Set(partial.map((item) => item.occlusionReason))].map((reason) => [reason, partial.filter((item) => item.occlusionReason === reason).length])),
  },
  crossing: {
    superimpositionCount: crossing.superimpositions,
    minimumCrossTrackClearancePx: round(crossing.minimum),
    minimumClearanceInTheropodPrintWidths: round(crossing.minimum / (mean(theropodPrints.map((item) => item.radius)) * 2)),
  },
  perCorridor: corridors.map((corridor) => ({
    id: corridor.index + 1,
    centerPx: round(centerAt(corridor, HEIGHT / 2)),
    baseRailPx: round(corridor.rail),
    headingDegrees: round(corridor.heading),
    curvePx: round(corridor.curve),
    leftY: corridor.leftY.map((value) => round(value)),
    rightY: corridor.rightY.map((value) => round(value)),
    stridePx: corridor.strides.map((value) => round(value)),
    phaseRatios: corridor.phaseRatios.map((value) => round(value)),
  })),
  impressions: impressions.map((item) => ({
    id: item.id,
    type: item.type,
    corridor: item.corridor || null,
    side: item.side || null,
    stepIndex: item.stepIndex,
    x: round(item.x),
    y: round(item.y),
    rotation: round(item.rotation),
    scaleX: round(item.scaleX),
    scaleY: round(item.scaleY),
    depthClass: item.depth < 0.67 ? "shallow" : item.depth < 0.84 ? "medium" : "deep",
    depthNormalized: round(item.depth),
    visibility: round(item.visibility),
    occlusionReason: item.occlusionReason || null,
  })),
};

metrics.gates = {
  macroTopology4Plus1: metrics.macroTopology.sauropodCorridors === 4
    && metrics.macroTopology.sauropodManusPesPairs === 32
    && metrics.macroTopology.theropodTrackways === 1
    && metrics.macroTopology.theropodPrints === 9,
  sauropodStrideCv6To12Pct: metrics.layout.sauropodStrideCv >= 0.06 && metrics.layout.sauropodStrideCv <= 0.12,
  railWidthCv5To10Pct: metrics.layout.railWidthCv >= 0.05 && metrics.layout.railWidthCv <= 0.1,
  phase42To58Pct: metrics.layout.phaseRatioRange[0] >= 0.42 && metrics.layout.phaseRatioRange[1] <= 0.58,
  corridorGapNaturalized: metrics.layout.corridorGapCv >= 0.15 && metrics.layout.corridorGapRatio >= 1.4 && metrics.layout.corridorGapRatio <= 2.2,
  mudGap15To25Pct: metrics.layout.largestMudGapFraction >= 0.15 && metrics.layout.largestMudGapFraction <= 0.25,
  headingDrift2To8Degrees: metrics.layout.headingDriftRangeDegrees[0] >= 2 && metrics.layout.headingDriftRangeDegrees[1] <= 8,
  yawStd3To6Degrees: metrics.layout.yawResidualStdDegrees >= 3 && metrics.layout.yawResidualStdDegrees <= 6,
  noShortYawPeriod: metrics.layout.yawExactPeriod === null,
  partial10To20Pct: metrics.preservation.partialFraction >= 0.1 && metrics.preservation.partialFraction <= 0.2,
  ghostAtMost2: metrics.preservation.ghostCount <= 2,
  noSuperimposition: metrics.crossing.superimpositionCount === 0,
  crossingClearanceQuarterPrint: metrics.crossing.minimumClearanceInTheropodPrintWidths >= 0.25,
  theropodStrideCv10To18Pct: metrics.layout.theropodStrideCv >= 0.1 && metrics.layout.theropodStrideCv <= 0.18,
  theropodCoherentForwardRoute: metrics.layout.theropodForwardAxisStepCount === 8
    && metrics.layout.theropodMaximumHeadingChangeDegrees <= 30,
};
metrics.gates.allPassed = Object.values(metrics.gates).every(Boolean);

const backgroundPath = resolve(args.background);
const outputPath = resolve(args.output);
const guidePath = resolve(args.guide);
const metricsPath = resolve(args.metrics);
for (const path of [outputPath, guidePath, metricsPath]) fs.mkdirSync(dirname(path), { recursive: true });

const guideSvg = svgDocument({ guide: true });
fs.writeFileSync(guidePath, guideSvg, "utf8");
const overlay = Buffer.from(svgDocument(), "utf8");
await sharp(backgroundPath)
  .resize(WIDTH, HEIGHT, { fit: "cover" })
  .composite([{ input: overlay, blend: "over" }])
  .png({ compressionLevel: 9 })
  .toFile(outputPath);

const backgroundBytes = fs.readFileSync(backgroundPath);
const outputBytes = fs.readFileSync(outputPath);
const guideBytes = fs.readFileSync(guidePath);
metrics.input.backgroundBytes = backgroundBytes.length;
metrics.input.backgroundSha256 = createHash("sha256").update(backgroundBytes).digest("hex");
metrics.output.previewBytes = outputBytes.length;
metrics.output.previewSha256 = createHash("sha256").update(outputBytes).digest("hex");
metrics.output.guideBytes = guideBytes.length;
metrics.output.guideSha256 = createHash("sha256").update(guideBytes).digest("hex");
fs.writeFileSync(metricsPath, `${JSON.stringify(metrics, null, 2)}\n`, "utf8");

console.log(JSON.stringify({
  seed,
  output: outputPath,
  guide: guidePath,
  metrics: metricsPath,
  gates: metrics.gates,
}, null, 2));
