import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const appName = process.argv[2];

if (!appName) {
    console.error('Usage: node build-vite-app.mjs <app-name>');
    process.exit(1);
}

const appDir = path.join(__dirname, '..', 'apps', appName);
const distDir = path.join(__dirname, '..', 'dist', 'apps', appName);

console.log(`Building Vite app: ${appName}`);

// Install deps
console.log('Installing dependencies...');
try {
    execSync('npm install', { cwd: appDir, stdio: 'inherit' });
} catch (e) {
    console.error('npm install failed');
    process.exit(1);
}

// Build
console.log('Building...');
try {
    execSync('npm run build', { cwd: appDir, stdio: 'inherit' });
} catch (e) {
    console.error('npm run build failed');
    process.exit(1);
}

// Copy dist
console.log(`Copying build artifacts to ${distDir}...`);
if (fs.existsSync(distDir)) {
    fs.rmSync(distDir, { recursive: true, force: true });
}
fs.mkdirSync(distDir, { recursive: true });

const buildDir = path.join(appDir, 'dist');
if (fs.existsSync(buildDir)) {
    fs.cpSync(buildDir, distDir, { recursive: true });
    console.log('Done.');
} else {
    console.error(`Build directory not found: ${buildDir}`);
    process.exit(1);
}
