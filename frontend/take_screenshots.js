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
  const browser = await puppeteer.launch({ 
    defaultViewport: { width: 1280, height: 800 },
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  });
  const page = await browser.newPage();
  
  // Navigate to Dashboard (assuming login is bypassed or we go to public routes)
  console.log("Taking screenshot of Dashboard...");
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: path.join(docsAssetsDir, 'dashboard.jpg'), type: 'jpeg', quality: 80 });

  console.log("Taking screenshot of Visual Monitor...");
  await page.goto('http://localhost:5173/monitor', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: path.join(docsAssetsDir, 'visual_monitor.jpg'), type: 'jpeg', quality: 80 });

  console.log("Taking screenshot of Analytics...");
  await page.goto('http://localhost:5173/analytics', { waitUntil: 'networkidle2' });
  await page.screenshot({ path: path.join(docsAssetsDir, 'analytics.jpg'), type: 'jpeg', quality: 80 });

  await browser.close();
  console.log("Screenshots captured successfully!");
})();
