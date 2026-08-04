const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8020/";
const expectedSamples = Number(process.argv[3] || 3);
const chromeExecutable =
  process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

if (!Number.isInteger(expectedSamples) || expectedSamples <= 0) {
  throw new Error("expectedSamples must be a positive integer");
}

const profiles = [
  { name: "desktop", columns: 2, context: { viewport: { width: 1440, height: 900 } } },
  {
    name: "mobile-portrait",
    columns: 1,
    context: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true },
  },
  {
    name: "mobile-compact",
    columns: 1,
    context: { viewport: { width: 320, height: 700 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true },
  },
  {
    name: "mobile-landscape",
    columns: 2,
    context: { viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true },
  },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function inspect(page, profile) {
  const lane = page.locator("#motionM2SampleLane");
  await lane.waitFor({ state: "visible" });
  const cards = lane.locator("article[data-motion-sample]");
  assert(await cards.count() === expectedSamples, `${profile.name}: expected ${expectedSamples} M2 cards`);

  const initial = await page.evaluate(() => {
    const laneElement = document.querySelector("#motionM2SampleLane");
    const grid = laneElement.querySelector(".motion-sample-grid");
    const cards = [...laneElement.querySelectorAll("article[data-motion-sample]")];
    const videos = [...laneElement.querySelectorAll("video[data-motion-video]")];
    const viewportWidth = document.documentElement.clientWidth;
    const gridColumns = getComputedStyle(grid).gridTemplateColumns
      .split(" ")
      .filter(Boolean).length;
    return {
      viewportWidth,
      scrollWidth: document.documentElement.scrollWidth,
      gridColumns,
      cards: cards.map((card) => {
        const rect = card.getBoundingClientRect();
        return { left: rect.left, right: rect.right, width: rect.width };
      }),
      videos: videos.map((video) => ({
        paused: video.paused,
        currentTime: video.currentTime,
        autoplay: video.autoplay,
        loop: video.loop,
        muted: video.muted,
        playsInline: video.playsInline,
        srcAttribute: video.getAttribute("src"),
        dataSrc: video.dataset.motionSrc,
      })),
    };
  });

  assert(initial.scrollWidth <= initial.viewportWidth + 1, `${profile.name}: horizontal overflow`);
  assert(initial.gridColumns === profile.columns, `${profile.name}: expected ${profile.columns} grid column(s)`);
  assert(initial.cards.every((card) => card.left >= -1 && card.right <= initial.viewportWidth + 1), `${profile.name}: card escaped viewport`);
  assert(initial.videos.length === expectedSamples, `${profile.name}: video count mismatch`);
  assert(initial.videos.every((video) => video.paused && video.currentTime === 0), `${profile.name}: video autoplayed`);
  assert(initial.videos.every((video) => !video.autoplay && !video.loop && video.muted && video.playsInline), `${profile.name}: playback policy mismatch`);
  assert(initial.videos.every((video) => !video.srcAttribute && /^assets\/motion\/m2\/.+-m2-v\d+\.mp4$/i.test(video.dataSrc)), `${profile.name}: lazy source policy mismatch`);

  const buttons = lane.locator("button[data-motion-play]");
  await buttons.nth(1).click();
  await page.waitForFunction(() => {
    const video = document.querySelectorAll("#motionM2SampleLane video[data-motion-video]")[1];
    return video && !video.paused && video.currentTime > 0;
  });
  await buttons.nth(2).click();
  await page.waitForFunction(() => {
    const videos = document.querySelectorAll("#motionM2SampleLane video[data-motion-video]");
    return videos[1]?.paused && videos[2] && !videos[2].paused && videos[2].currentTime > 0;
  });

  const switched = await page.evaluate(() => {
    const laneElement = document.querySelector("#motionM2SampleLane");
    const videos = [...laneElement.querySelectorAll("video[data-motion-video]")];
    const statuses = [...laneElement.querySelectorAll("[data-motion-status]")].map((node) => node.textContent.trim());
    return {
      firstPaused: videos[0].paused,
      secondPaused: videos[1].paused,
      thirdPlaying: !videos[2].paused,
      loadedSources: videos.map((video) => Boolean(video.getAttribute("src"))),
      statuses,
    };
  });
  assert(switched.firstPaused && switched.secondPaused && switched.thirdPlaying, `${profile.name}: cross-video pause failed`);
  assert(switched.loadedSources[0] === false && switched.loadedSources[1] === true && switched.loadedSources[2] === true, `${profile.name}: lazy loading state mismatch`);
  assert(switched.statuses[1] === "일시 정지됨", `${profile.name}: paused status missing`);
  assert(switched.statuses[2].startsWith("재생 중 · 소리 없음"), `${profile.name}: playing status missing`);

  await page.getByRole("button", { name: "도감" }).click();
  await page.waitForFunction(() => document.querySelectorAll("#motionM2SampleLane video")[2]?.paused === true);

  return {
    profile: profile.name,
    viewport: profile.context.viewport,
    gridColumns: initial.gridColumns,
    cardCount: initial.cards.length,
    noHorizontalOverflow: true,
    noAutoplayOrLoop: true,
    lazyLoading: true,
    crossVideoPause: true,
    viewExitPause: true,
  };
}

(async () => {
  const browser = await chromium.launch({ executablePath: chromeExecutable, headless: true });
  const results = [];
  try {
    for (const profile of profiles) {
      const context = await browser.newContext(profile.context);
      const page = await context.newPage();
      await page.goto(`${baseUrl}?qa=motion-m2-i2v-${Date.now()}#motion`, { waitUntil: "networkidle" });
      results.push(await inspect(page, profile));
      await context.close();
    }
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify({ expectedSamples, results }, null, 2));
})().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exitCode = 1;
});
