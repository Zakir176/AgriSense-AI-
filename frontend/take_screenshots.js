import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const docsAssetsDir = path.resolve(__dirname, '../Docs/assets');
if (!fs.existsSync(docsAssetsDir)) {
  fs.mkdirSync(docsAssetsDir, { recursive: true });
}

(async () => {
  const launchOptions = {
    headless: true,
    defaultViewport: { width: 1280, height: 800 }
  };
  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  if (fs.existsSync(chromePath)) {
    launchOptions.executablePath = chromePath;
  }

  const browser = await puppeteer.launch(launchOptions);
  const page = await browser.newPage();
  
  console.log("Taking screenshot of Landing Page...");
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
  await page.evaluate(() => new Promise(r => setTimeout(r, 1500)));
  await page.screenshot({ path: path.join(docsAssetsDir, 'landing.jpg'), type: 'jpeg', quality: 90 });

  console.log("Navigating to login page...");
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });

  console.log("Submitting login credentials...");
  await page.type('#username', 'operator');
  await page.type('#password', 'prime_nest_2026');
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 5000 }).catch(() => {}),
    page.click('button[type="submit"]')
  ]);

  // Set tour as seen to prevent overlay tooltips in documentation screenshots
  await page.evaluate(() => {
    localStorage.setItem('agrisense_has_seen_tour', 'true');
  });

  // Wait extra time for dashboard data to load completely
  await page.evaluate(() => new Promise(r => setTimeout(r, 2000)));

  console.log("Taking screenshot of Dashboard...");
  await page.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle2' });
  await page.evaluate(() => new Promise(r => setTimeout(r, 2000)));
  await page.screenshot({ path: path.join(docsAssetsDir, 'dashboard.jpg'), type: 'jpeg', quality: 90 });

  console.log("Taking screenshot of Visual Monitor...");
  await page.goto('http://localhost:5173/inference', { waitUntil: 'networkidle2' });
  await page.evaluate(() => new Promise(r => setTimeout(r, 2000)));
  await page.screenshot({ path: path.join(docsAssetsDir, 'visual_monitor.jpg'), type: 'jpeg', quality: 90 });

  console.log("Taking screenshot of Analytics...");
  await page.goto('http://localhost:5173/analytics', { waitUntil: 'networkidle2' });
  await page.evaluate(() => new Promise(r => setTimeout(r, 2000)));
  await page.screenshot({ path: path.join(docsAssetsDir, 'analytics.jpg'), type: 'jpeg', quality: 90 });

  await browser.close();
  console.log("Screenshots captured successfully to Docs/assets!");
})();
