#!/usr/bin/env node

/**
 * Build all dashboard applications
 */

const { execSync } = require('child_process');

const apps = [
    'the-shield',
    'the-coin',
    'the-map',
    'the-frontier',
    'the-strategy',
    'the-library',
    'the-commander'
];

console.log('Building all dashboard applications...\n');

let failed = [];
let succeeded = [];

apps.forEach(app => {
    try {
        console.log(`\n=== Building ${app} ===`);
        // Use npm run build:<app> to ensure the correct script (standard or vite) is used
        execSync(`npm run build:${app}`, { stdio: 'inherit' });
        succeeded.push(app);
    } catch (error) {
        console.error(`✗ Failed to build ${app}`);
        failed.push(app);
    }
});

console.log('\n=== Build Summary ===');
console.log(`✓ Succeeded: ${succeeded.length}/${apps.length}`);
if (succeeded.length > 0) {
    succeeded.forEach(app => console.log(`  ✓ ${app}`));
}

if (failed.length > 0) {
    console.log(`✗ Failed: ${failed.length}/${apps.length}`);
    failed.forEach(app => console.log(`  ✗ ${app}`));
    process.exit(1);
}

console.log('\n✓ All builds completed successfully!');
