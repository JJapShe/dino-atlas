const { startReviewServer } = require("./backend");

try {
  startReviewServer();
} catch (error) {
  console.error(error?.stack || error);
  process.exitCode = 1;
}
