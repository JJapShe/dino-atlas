const { chromium } = require("playwright");

const baseUrl = process.argv[2] || "http://127.0.0.1:8020/";
const sceneId = process.argv[3] || "tyrannosaurus-edmontosaurus-kpg-dim-sky";
const expectedTitle = process.argv[4] || "충돌 뒤 흐려지는 헬크리크의 하늘";
const expectedSource =
  process.argv[5] ||
  "assets/dinosaurs/tyrannosaurus-rex-edmontosaurus-annectens-kpg-dim-sky-separated-context-imagegen-v1.png";
const expectedWidth = Number(process.argv[6] || 1122);
const expectedHeight = Number(process.argv[7] || 1402);
const chromeExecutable =
  process.env.CHROME_PATH || "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

if (!Number.isInteger(expectedWidth) || expectedWidth <= 0 || !Number.isInteger(expectedHeight) || expectedHeight <= 0) {
  throw new Error("Expected image dimensions must be positive integers");
}

const profiles = [
  { name: "desktop", context: { viewport: { width: 1440, height: 1000 } } },
  {
    name: "mobile-portrait",
    context: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true },
  },
  {
    name: "mobile-compact",
    context: { viewport: { width: 320, height: 700 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true },
  },
  {
    name: "mobile-landscape",
    context: { viewport: { width: 844, height: 390 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true },
  },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function waitForImage(page, selector) {
  await page.waitForFunction((target) => {
    const image = document.querySelector(target);
    return Boolean(image?.complete && image.naturalWidth > 0 && image.naturalHeight > 0);
  }, selector);
}

async function runTouchChecks(page) {
  const tap = await page.evaluate(() => {
    const image = document.querySelector("#lightboxImage");
    const rect = image.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const fire = (type, buttons) =>
      image.dispatchEvent(
        new PointerEvent(type, {
          bubbles: true,
          cancelable: true,
          pointerType: "touch",
          pointerId: 71,
          isPrimary: true,
          clientX: x,
          clientY: y,
          buttons,
        }),
      );
    fire("pointerdown", 1);
    fire("pointerup", 0);
    return {
      hidden: document.querySelector("#imageLightbox").classList.contains("nav-temporarily-hidden"),
      prevAriaHidden: document.querySelector(".lightbox-nav.prev").getAttribute("aria-hidden"),
      nextAriaHidden: document.querySelector(".lightbox-nav.next").getAttribute("aria-hidden"),
    };
  });
  assert(tap.hidden, "image tap did not hide the lightbox navigation");
  assert(tap.prevAriaHidden === "true" && tap.nextAriaHidden === "true", "hidden navigation remained focusable");

  await page.evaluate(() => {
    setLightboxNavigationHidden(false);
    resetLightboxView();
  });

  const pinch = await page.evaluate(() => {
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
    fire(image, "pointerdown", 81, centerX - 34, centerY, 1, true);
    fire(image, "pointerdown", 82, centerX + 34, centerY, 1, false);
    fire(stage, "pointermove", 81, centerX - 86, centerY - 8, 1, true);
    fire(stage, "pointermove", 82, centerX + 86, centerY + 8, 1, false);
    const result = {
      scale: state.lightboxView.scale,
      imageTransform: getComputedStyle(image).transform,
      stageTransform: getComputedStyle(stage).transform,
      navHidden: document.querySelector("#imageLightbox").classList.contains("nav-temporarily-hidden"),
      zoomed: document.querySelector("#imageLightbox").classList.contains("image-zoomed"),
    };
    fire(stage, "pointerup", 81, centerX - 86, centerY - 8, 0, true);
    fire(stage, "pointerup", 82, centerX + 86, centerY + 8, 0, false);
    return result;
  });
  assert(pinch.scale > 1.2, `pinch scale stayed at ${pinch.scale}`);
  assert(pinch.zoomed && pinch.navHidden, "pinch did not enter the expected zoom/navigation state");
  assert(pinch.imageTransform !== "none", "pinch did not transform the image");
  assert(pinch.stageTransform === "none", "pinch transformed the stage instead of only the image");
  return { tap, pinch };
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
    if (new URL(request.url()).origin === new URL(baseUrl).origin) localFailedRequests.push(failure);
    else externalFailedRequests.push(failure);
  });

  const targetUrl = new URL(baseUrl);
  targetUrl.searchParams.set("ecosystemPreview", "draft");
  targetUrl.searchParams.set("qa", `${Date.now()}-${profile.name}`);
  const response = await page.goto(targetUrl.href, { waitUntil: "domcontentloaded" });
  assert(response?.ok(), `${profile.name} page returned ${response?.status()}`);
  await page.click('[data-view="ecosystems"]');
  await page.fill("#ecosystemSearchInput", expectedTitle);

  const cardSelector = `[data-ecosystem-card="${sceneId}"]`;
  const cardImageSelector = `${cardSelector} img`;
  await page.waitForSelector(cardSelector);
  await page.locator(cardSelector).scrollIntoViewIfNeeded();
  await waitForImage(page, cardImageSelector);
  const card = await page.evaluate(({ cardSelector, cardImageSelector }) => {
    const element = document.querySelector(cardSelector);
    const image = document.querySelector(cardImageSelector);
    const elementRect = element.getBoundingClientRect();
    const imageRect = image.getBoundingClientRect();
    return {
      title: element.querySelector("h4")?.textContent,
      tags: [...element.querySelectorAll(".ecosystem-diversity-tag")].map((tag) => tag.textContent),
      source: decodeURIComponent(new URL(image.src).pathname).replace(/^\//, ""),
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      objectFit: getComputedStyle(image).objectFit,
      cardRect: { left: elementRect.left, right: elementRect.right, width: elementRect.width },
      imageRect: { left: imageRect.left, right: imageRect.right, width: imageRect.width, height: imageRect.height },
      bodyOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      resultSummary: document.querySelector("#ecosystemResultSummary")?.textContent,
    };
  }, { cardSelector, cardImageSelector });
  assert(card.title === expectedTitle, `${profile.name} title mismatch`);
  const sourceMatches = card.source === expectedSource || card.source.endsWith(`/${expectedSource}`);
  assert(sourceMatches, `${profile.name} source mismatch: ${card.source}`);
  assert(card.naturalWidth === expectedWidth && card.naturalHeight === expectedHeight, `${profile.name} unexpected source dimensions`);
  assert(card.objectFit === "contain", `${profile.name} card object-fit is ${card.objectFit}`);
  assert(card.cardRect.left >= -1 && card.cardRect.right <= profile.context.viewport.width + 1, `${profile.name} card escaped the viewport`);
  assert(card.bodyOverflowX <= 1, `${profile.name} card page overflowed ${card.bodyOverflowX}px`);
  assert(card.resultSummary?.includes("현재 조건 1장"), `${profile.name} scene search was not isolated`);

  await page.click(`[data-ecosystem-scene="${sceneId}"]`);
  await page.waitForSelector("#imageLightbox.active:not([hidden])");
  await waitForImage(page, "#lightboxImage");
  const lightbox = await page.evaluate(() => {
    const image = document.querySelector("#lightboxImage");
    const stage = document.querySelector(".lightbox-stage");
    const panel = document.querySelector(".lightbox-panel");
    const imageRect = image.getBoundingClientRect();
    const stageRect = stage.getBoundingClientRect();
    return {
      title: document.querySelector("#lightboxTitle")?.textContent,
      count: document.querySelector("#lightboxCount")?.textContent,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      objectFit: getComputedStyle(image).objectFit,
      imageRect: { left: imageRect.left, top: imageRect.top, right: imageRect.right, bottom: imageRect.bottom },
      stageRect: { left: stageRect.left, top: stageRect.top, right: stageRect.right, bottom: stageRect.bottom },
      panelOverflowX: panel.scrollWidth - panel.clientWidth,
      bodyOverflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    };
  });
  assert(lightbox.title === expectedTitle && lightbox.count === "1 / 1", `${profile.name} lightbox scope mismatch`);
  assert(lightbox.naturalWidth === expectedWidth && lightbox.naturalHeight === expectedHeight, `${profile.name} lightbox source did not decode`);
  assert(lightbox.objectFit === "contain", `${profile.name} lightbox object-fit is ${lightbox.objectFit}`);
  assert(lightbox.imageRect.left >= lightbox.stageRect.left - 1 && lightbox.imageRect.right <= lightbox.stageRect.right + 1, `${profile.name} lightbox image escaped horizontally`);
  assert(lightbox.imageRect.top >= lightbox.stageRect.top - 1 && lightbox.imageRect.bottom <= lightbox.stageRect.bottom + 1, `${profile.name} lightbox image escaped vertically`);
  assert(lightbox.panelOverflowX <= 1 && lightbox.bodyOverflowX <= 1, `${profile.name} lightbox overflowed`);

  const touch = profile.context.hasTouch ? await runTouchChecks(page) : null;
  assert(pageErrors.length === 0, `${profile.name} page errors: ${pageErrors.join(" | ")}`);
  assert(localFailedRequests.length === 0, `${profile.name} local failed requests: ${localFailedRequests.join(" | ")}`);
  await context.close();
  return { profile: profile.name, card, lightbox, touch, externalFailedRequests, errors: [] };
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: chromeExecutable });
  try {
    const results = [];
    for (const profile of profiles) results.push(await runProfile(browser, profile));
    console.log(JSON.stringify({ baseUrl, sceneId, expectedSource, results, errors: [] }, null, 2));
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
