const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8020/";
const outputDirectory = path.resolve(process.argv[3] || "screenshots/brachiosaurus-gallery-qa");
const chromeExecutable = process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

const expectedSources = [
  "assets/dinosaurs/brachiosaurus-altithorax-nasal-mound-fullbody-imagegen-v18.png",
  "assets/dinosaurs/brachiosaurus-altithorax-nasal-mound-slate-moss-rearthreequarter-pattern-imagegen-v2.png",
  "assets/dinosaurs/brachiosaurus-altithorax-tailclear-canopy-window-habitat-ecology-imagegen-v2.png",
  "assets/dinosaurs/brachiosaurus-altithorax-nasal-mound-head-reference-imagegen-v19.png",
  "assets/dinosaurs/brachiosaurus-altithorax-tailclear-conifer-browse-longlens-ecology-imagegen-v2.png",
  "assets/dinosaurs/brachiosaurus-altithorax-two-individual-spacing-size-variation-imagegen-v2.png",
];

const profiles = [
  {
    name: "desktop",
    context: { viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 },
  },
  {
    name: "mobile-portrait",
    context: {
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2,
      hasTouch: true,
      isMobile: true,
    },
  },
  {
    name: "mobile-landscape",
    context: {
      viewport: { width: 844, height: 390 },
      deviceScaleFactor: 2,
      hasTouch: true,
      isMobile: true,
    },
  },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForLightboxImage(page, expectedSource) {
  await page.waitForFunction(
    (source) => {
      const image = document.querySelector("#lightboxImage");
      return Boolean(
        image &&
          image.complete &&
          image.naturalWidth > 0 &&
          decodeURIComponent(new URL(image.src).pathname).endsWith(`/${source}`),
      );
    },
    expectedSource,
  );
}

async function openBrachiosaurusGallery(page) {
  await page.evaluate(() => {
    const dino = getDinoById("brachiosaurus-altithorax");
    if (!dino) throw new Error("Brachiosaurus taxon is missing");
    openDinoGalleryLightbox(dino, getPrimaryImage(dino));
  });
  await page.waitForSelector("#imageLightbox.active:not([hidden])");
  await waitForLightboxImage(page, expectedSources[0]);
}

async function collectFrame(page) {
  return page.evaluate(() => {
    const lightbox = document.querySelector("#imageLightbox");
    const panel = document.querySelector(".lightbox-panel");
    const stage = document.querySelector(".lightbox-stage");
    const image = document.querySelector("#lightboxImage");
    const imageRect = image.getBoundingClientRect();
    const stageRect = stage.getBoundingClientRect();
    const imageStyle = getComputedStyle(image);
    const stageStyle = getComputedStyle(stage);
    return {
      source: decodeURIComponent(new URL(image.src).pathname).replace(/^\//, ""),
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      imageRect: {
        left: imageRect.left,
        top: imageRect.top,
        right: imageRect.right,
        bottom: imageRect.bottom,
        width: imageRect.width,
        height: imageRect.height,
      },
      stageRect: {
        left: stageRect.left,
        top: stageRect.top,
        right: stageRect.right,
        bottom: stageRect.bottom,
        width: stageRect.width,
        height: stageRect.height,
      },
      objectFit: imageStyle.objectFit,
      imageTransform: imageStyle.transform,
      stageTransform: stageStyle.transform,
      navHidden: lightbox.classList.contains("nav-temporarily-hidden"),
      zoomed: lightbox.classList.contains("image-zoomed"),
      scale: state.lightboxView.scale,
      panelOverflowX: panel.scrollWidth - panel.clientWidth,
      bodyOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });
}

async function runTouchChecks(page) {
  const tapResult = await page.evaluate(() => {
    const image = document.querySelector("#lightboxImage");
    const rect = image.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const fire = (type, pointerId, clientX, clientY, buttons) =>
      image.dispatchEvent(
        new PointerEvent(type, {
          bubbles: true,
          cancelable: true,
          pointerType: "touch",
          pointerId,
          isPrimary: true,
          clientX,
          clientY,
          buttons,
        }),
      );
    fire("pointerdown", 31, x, y, 1);
    fire("pointerup", 31, x, y, 0);
    return {
      hidden: document.querySelector("#imageLightbox").classList.contains("nav-temporarily-hidden"),
      prevAriaHidden: document.querySelector(".lightbox-nav.prev").getAttribute("aria-hidden"),
      nextAriaHidden: document.querySelector(".lightbox-nav.next").getAttribute("aria-hidden"),
    };
  });
  assert(tapResult.hidden, "mobile image tap did not hide navigation");
  assert(tapResult.prevAriaHidden === "true" && tapResult.nextAriaHidden === "true", "hidden navigation stayed exposed to accessibility focus");

  await page.evaluate(() => {
    setLightboxNavigationHidden(false);
    resetLightboxView();
  });

  const pinchResult = await page.evaluate(() => {
    const image = document.querySelector("#lightboxImage");
    const stage = document.querySelector(".lightbox-stage");
    const rect = image.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const fire = (target, type, pointerId, clientX, clientY, buttons, isPrimary) =>
      target.dispatchEvent(
        new PointerEvent(type, {
          bubbles: true,
          cancelable: true,
          pointerType: "touch",
          pointerId,
          isPrimary,
          clientX,
          clientY,
          buttons,
        }),
      );

    fire(image, "pointerdown", 41, centerX - 34, centerY, 1, true);
    fire(image, "pointerdown", 42, centerX + 34, centerY, 1, false);
    fire(stage, "pointermove", 41, centerX - 86, centerY - 8, 1, true);
    fire(stage, "pointermove", 42, centerX + 86, centerY + 8, 1, false);
    const during = {
      scale: state.lightboxView.scale,
      imageTransform: getComputedStyle(image).transform,
      stageTransform: getComputedStyle(stage).transform,
    };
    fire(stage, "pointerup", 41, centerX - 86, centerY - 8, 0, true);
    fire(stage, "pointerup", 42, centerX + 86, centerY + 8, 0, false);
    return {
      ...during,
      navHidden: document.querySelector("#imageLightbox").classList.contains("nav-temporarily-hidden"),
      zoomed: document.querySelector("#imageLightbox").classList.contains("image-zoomed"),
    };
  });

  assert(pinchResult.scale > 1.2, `pinch scale stayed at ${pinchResult.scale}`);
  assert(pinchResult.zoomed, "pinch did not enter image-zoomed state");
  assert(pinchResult.navHidden, "pinch did not temporarily hide navigation");
  assert(pinchResult.imageTransform !== "none", "pinch did not transform the image");
  assert(pinchResult.stageTransform === "none", "pinch transformed the lightbox stage instead of only the image");
  return { tap: tapResult, pinch: pinchResult };
}

async function runProfile(browser, profile) {
  const context = await browser.newContext(profile.context);
  const page = await context.newPage();
  const pageErrors = [];
  const localFailedRequests = [];
  const externalFailedRequests = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("requestfailed", (request) => {
    const failure = `${request.method()} ${request.url()} ${request.failure()?.errorText || "failed"}`;
    const requestUrl = new URL(request.url());
    const appUrl = new URL(baseUrl);
    if (requestUrl.origin === appUrl.origin) localFailedRequests.push(failure);
    else externalFailedRequests.push(failure);
  });

  const targetUrl = new URL(baseUrl);
  targetUrl.searchParams.set("qa", `${Date.now()}-${profile.name}`);
  targetUrl.hash = "catalog";
  const response = await page.goto(targetUrl.href, { waitUntil: "domcontentloaded" });
  assert(response && response.ok(), `${profile.name} page returned ${response?.status()}`);
  await page.waitForSelector("#catalogGrid .dino-card");
  await openBrachiosaurusGallery(page);

  const sources = await page.evaluate(() => state.lightboxItems.map((item) => item.src));
  assert(JSON.stringify(sources) === JSON.stringify(expectedSources), `${profile.name} gallery source order mismatch: ${JSON.stringify(sources)}`);
  assert((await page.textContent("#lightboxCount")) === "1 / 6", `${profile.name} did not report six slots`);

  const frames = [];
  for (let index = 0; index < expectedSources.length; index += 1) {
    await page.evaluate((nextIndex) => {
      state.lightboxIndex = nextIndex;
      resetLightboxView();
      setLightboxNavigationHidden(false);
      renderLightbox();
    }, index);
    await waitForLightboxImage(page, expectedSources[index]);
    const frame = await collectFrame(page);
    frame.slot = index + 1;
    assert(frame.naturalWidth > 0 && frame.naturalHeight > 0, `${profile.name} slot ${index + 1} did not decode`);
    assert(frame.objectFit === "contain", `${profile.name} slot ${index + 1} object-fit is ${frame.objectFit}`);
    assert(frame.panelOverflowX <= 1, `${profile.name} slot ${index + 1} panel overflowed ${frame.panelOverflowX}px`);
    assert(frame.bodyOverflowX <= 1, `${profile.name} slot ${index + 1} page overflowed ${frame.bodyOverflowX}px`);
    frames.push(frame);
  }

  const portraitFrame = frames[2];
  assert(portraitFrame.naturalHeight > portraitFrame.naturalWidth, "slot 3 is not a dedicated portrait asset");
  assert(
    portraitFrame.imageRect.left >= portraitFrame.stageRect.left - 1 &&
      portraitFrame.imageRect.right <= portraitFrame.stageRect.right + 1 &&
      portraitFrame.imageRect.top >= portraitFrame.stageRect.top - 1 &&
      portraitFrame.imageRect.bottom <= portraitFrame.stageRect.bottom + 1,
    `${profile.name} portrait asset escaped the stage at 1x`,
  );

  await page.evaluate(() => {
    state.lightboxIndex = 2;
    resetLightboxView();
    renderLightbox();
  });
  await waitForLightboxImage(page, expectedSources[2]);
  await page.screenshot({ path: path.join(outputDirectory, `${profile.name}-portrait-slot.png`), fullPage: false });

  const touch = profile.context.hasTouch ? await runTouchChecks(page) : null;
  assert(pageErrors.length === 0, `${profile.name} page errors: ${pageErrors.join(" | ")}`);
  assert(localFailedRequests.length === 0, `${profile.name} local failed requests: ${localFailedRequests.join(" | ")}`);

  await context.close();
  return {
    profile: profile.name,
    sources,
    portrait: {
      naturalWidth: portraitFrame.naturalWidth,
      naturalHeight: portraitFrame.naturalHeight,
      renderedWidth: Math.round(portraitFrame.imageRect.width),
      renderedHeight: Math.round(portraitFrame.imageRect.height),
    },
    touch,
    externalFailedRequests,
    errors: [],
  };
}

(async () => {
  fs.mkdirSync(outputDirectory, { recursive: true });
  const browser = await chromium.launch({ headless: true, executablePath: chromeExecutable });
  try {
    const results = [];
    for (const profile of profiles) results.push(await runProfile(browser, profile));
    console.log(JSON.stringify({ baseUrl, expectedSlots: expectedSources.length, results, errors: [] }, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
