#!/usr/bin/env node

/**
 * Build all dashboard applications
 */

const { execSync } = require('child_process');

const apps = [
    'ai-race',
    'crash-detector',
    'dashboard-orchestrator',
    'economic-compass',
    'intelligence-platform',
    'hyper-analytical'
];

console.log('Building all dashboard applications...\n');

let failed = [];
let succeeded = [];

apps.forEach(app => {
    try {
        console.log(`\n=== Building ${app} ===`);
        execSync(`node scripts/build-app.mjs ${app}`, { stdio: 'inherit' });
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
