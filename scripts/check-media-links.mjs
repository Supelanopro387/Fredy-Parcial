import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const page = fs.readFileSync(path.join(root, 'web', 'index.html'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(root, 'web', 'media-links.json'), 'utf8'));
const slotIds = [...page.matchAll(/data-media-id="([^"]+)"/g)].map((match) => match[1]);
const configuredIds = Object.keys(config.products ?? {});
const errors = [];

if (slotIds.length !== 12) errors.push(`Expected 12 media slots; found ${slotIds.length}.`);

for (const id of slotIds) {
  if (!(id in (config.products ?? {}))) {
    errors.push(`No URL configured for media slot: ${id}`);
    continue;
  }

  const rawUrl = config.products[id];
  if (!rawUrl) {
    errors.push(`Media slot is still empty: ${id}`);
    continue;
  }

  let url;
  try {
    url = new URL(rawUrl);
  } catch {
    errors.push(`Invalid URL for media slot: ${id}`);
    continue;
  }

  if (url.protocol !== 'https:') errors.push(`Media URL must use HTTPS: ${id}`);
  const marker = '/Fredy-Parcial/';
  const markerIndex = url.pathname.indexOf(marker);
  if (markerIndex < 0) {
    errors.push(`Media URL must point to this published site: ${id}`);
    continue;
  }

  const relativeAssetPath = decodeURIComponent(url.pathname.slice(markerIndex + marker.length));
  const localAssetPath = path.join(root, 'web', relativeAssetPath);
  if (!fs.existsSync(localAssetPath)) errors.push(`Linked export is missing locally: ${id} -> ${relativeAssetPath}`);
}

for (const id of configuredIds) {
  if (!slotIds.includes(id)) errors.push(`Unexpected media URL key without a page slot: ${id}`);
}

if (config.driveFolderUrl) {
  try {
    if (new URL(config.driveFolderUrl).protocol !== 'https:') errors.push('Drive folder URL must use HTTPS.');
  } catch {
    errors.push('Drive folder URL is invalid.');
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log(`Validated ${slotIds.length} product links and ${configuredIds.length} configured media slots.`);
  if (!config.driveFolderUrl) console.log('Drive folder link is not set yet.');
}
