#!/usr/bin/env node
// DESKILL CLI Installer — install DE skills into your project

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '../..');
const DESKILL_DIR = '.deskill';

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const entries = fs.readdirSync(src, { withFileTypes: true });
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function install(targetDir) {
  const deskillPath = path.join(targetDir, DESKILL_DIR);
  console.log(`Installing DESKILL into ${deskillPath}...`);

  const dirsToCopy = ['commands', 'phases', 'implementation', 'templates', 'agents', 'references', 'assets'];
  for (const dir of dirsToCopy) {
    const src = path.join(ROOT, dir);
    const dest = path.join(deskillPath, dir);
    copyRecursive(src, dest);
  }

  // Copy root files
  for (const file of ['SKILL.md', 'README.md', 'plugin.json', 'LICENSE']) {
    const src = path.join(ROOT, file);
    const dest = path.join(deskillPath, file);
    if (fs.existsSync(src)) fs.copyFileSync(src, dest);
  }

  console.log(' DESKILL installed successfully!');
  console.log(`   Location: ${deskillPath}`);
  console.log('');
  console.log('   Next steps:');
  console.log('   1. Read .deskill/SKILL.md to understand the framework');
  console.log('   2. Run lifecycle commands in order: /spec → /plan → /build → /validate → /review → /ship');
  console.log('   3. For detailed methodology, see .deskill/phases/');
  console.log('   4. For code patterns, see .deskill/implementation/');
}

function setup(targetDir) {
  const deskillPath = path.join(targetDir, DESKILL_DIR);
  if (!fs.existsSync(deskillPath)) {
    console.log('DESKILL not installed. Run `npx deskill install` first.');
    process.exit(1);
  }
  console.log('DESKILL is ready at .deskill/');
}

function help() {
  console.log('DESKILL — Data Engineering Project Roadmap');
  console.log('');
  console.log('Usage:');
  console.log('  npx deskill install     Install DESKILL skills into project');
  console.log('  npx deskill setup       Verify installation');
  console.log('  npx deskill help        Show this help');
  console.log('');
  console.log('After installation, open SKILL.md in .deskill/ to get started.');
}

const args = process.argv.slice(2);
const command = args[0] || 'help';
const targetDir = process.env.INIT_CWD || process.cwd();

switch (command) {
  case 'install':
    install(targetDir);
    break;
  case 'setup':
    setup(targetDir);
    break;
  case '--yes':
    install(targetDir);
    break;
  default:
    help();
    break;
}
