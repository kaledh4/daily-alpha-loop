#!/usr/bin/env node

/**
 * Simple build script for static dashboard apps
 * Copies app files to dist directory
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const appName = process.argv[2];

if (!appName) {
    console.error('Usage: node build-app.mjs <app-name>');
    process.exit(1);
}

const sourceDir = path.join(__dirname, '..', 'apps', appName);
const distDir = path.join(__dirname, '..', 'dist', 'apps', appName);

// Check if source directory exists
if (!fs.existsSync(sourceDir)) {
    console.error(`Error: App directory not found: ${sourceDir}`);
    process.exit(1);
}

// Create dist directory
if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
}

// Copy files recursively
function copyRecursive(src, dest) {
    const stats = fs.statSync(src);

    if (stats.isDirectory()) {
        // Skip certain directories
        const dirName = path.basename(src);
        if (dirName === 'node_modules' || dirName === '.git' || dirName === '__pycache__' || dirName === '.github' || dirName === 'briefs') {
            return;
        }

        if (!fs.existsSync(dest)) {
            fs.mkdirSync(dest, { recursive: true });
        }

        const files = fs.readdirSync(src);
        files.forEach(file => {
            copyRecursive(path.join(src, file), path.join(dest, file));
        });
    } else {
        // Skip certain file types
        const ext = path.extname(src);
        const basename = path.basename(src);

        if (ext === '.py' || ext === '.txt' || ext === '.md' || ext === '.ps1' || basename === 'project.json' || basename.endsWith('.backup') || basename === 'package.json' || basename === 'package-lock.json') {
            return;
        }

        fs.copyFileSync(src, dest);
        console.log(`Copied: ${path.relative(sourceDir, src)}`);
    }
}

console.log(`Building ${appName}...`);
console.log(`Source: ${sourceDir}`);
console.log(`Destination: ${distDir}`);

copyRecursive(sourceDir, distDir);

// Also copy shared folder to dist/shared (only needs to be done once, but safe to do multiple times)
const sharedSrc = path.join(__dirname, '..', 'shared');
const sharedDest = path.join(__dirname, '..', 'dist', 'shared');

if (fs.existsSync(sharedSrc)) {
    console.log('Copying shared assets...');
    copyRecursive(sharedSrc, sharedDest);
}

console.log(`✓ Build complete for ${appName}`);
