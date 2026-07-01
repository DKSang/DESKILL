#!/usr/bin/env node
const { program } = require('commander');
const path = require('node:path');
const fs = require('node:fs');
const os = require('node:os');
const packageJson = require('../../package.json');

const prompts = require('./prompts');

const DESKILL_DIR = '.deskill';
const ROOT = path.resolve(__dirname, '../..');

// ─── Logo ────────────────────────────────────────────────────────

async function displayLogo() {
  const color = await prompts.getColor();
  const termWidth = process.stdout.columns || 80;

  const logoWide = [
    ' ██████╗ ███████╗███████╗██████╗ ██╗██╗     ██╗         ██████╗ ███████╗',
    ' ██╔══██╗██╔════╝██╔════╝██╔══██╗██║██║     ██║         ██╔══██╗██╔════╝',
    ' ██║  ██║█████╗  ███████╗██║  ██║██║██║     ██║         ██║  ██║█████╗  ',
    ' ██║  ██║██╔══╝  ╚════██║██║  ██║██║██║     ██║         ██║  ██║██╔══╝  ',
    ' ██████╔╝███████╗███████║██████╔╝██║███████╗███████╗    ██████╔╝███████╗',
    ' ╚═════╝ ╚══════╝╚══════╝╚═════╝ ╚═╝╚══════╝╚══════╝    ╚═════╝ ╚══════╝',
  ];

  const logoNarrow = [
    ' ██████╗ ███████╗███████╗██████╗ ██╗██╗     ██╗',
    ' ██╔══██╗██╔════╝██╔════╝██╔══██╗██║██║     ██║',
    ' ██║  ██║█████╗  ███████╗██║  ██║██║██║     ██║',
    ' ██║  ██║██╔══╝  ╚════██║██║  ██║██║██║     ██║',
    ' ██████╔╝███████╗███████║██████╔╝██║███████╗███████╗',
    ' ╚═════╝ ╚══════╝╚══════╝╚═════╝ ╚═╝╚══════╝╚══════╝',
  ];

  const logoLines = termWidth >= 90 ? logoWide : logoNarrow;
  const logo = logoLines.map(line => color.blue(line)).join('\n');
  const tagline = color.white('    Data Engineering Project Roadmap\n    \u00A9 DESKILL');

  await prompts.box(`${logo}\n${tagline}`, '', {
    contentAlign: 'center',
    rounded: true,
    formatBorder: color.blue,
  });
}

// ─── File ops ────────────────────────────────────────────────────

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const entries = fs.readdirSync(src, { withFileTypes: true });
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of entries) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyRecursive(s, d);
    else fs.copyFileSync(s, d);
  }
}

// ─── Scaffolding ─────────────────────────────────────────────────

function scaffoldProject(targetDir, config) {
  const { outputFolder } = config;
  const dirs = [
    'docs',
    path.join(outputFolder, 'planning'),
    path.join(outputFolder, 'implementation'),
    path.join(outputFolder, 'learning'),
  ];
  for (const dir of dirs) {
    fs.mkdirSync(path.join(targetDir, dir), { recursive: true });
  }
}

function writeProjectConfig(targetDir, config) {
  const deskillPath = path.join(targetDir, DESKILL_DIR);
  const configDir = path.join(deskillPath, '_config');
  fs.mkdirSync(configDir, { recursive: true });

  const content = [
    '# DESKILL project configuration',
    '',
    '[project]',
    `name = "${config.projectName}"`,
    `user_name = "${config.userName}"`,
    `communication_language = "${config.commLang}"`,
    `document_output_language = "${config.docLang}"`,
    `output_folder = "${config.outputFolder}"`,
    '',
  ].join('\n') + '\n';

  fs.writeFileSync(path.join(configDir, 'config.toml'), content);
}

// ─── Tool integration files ──────────────────────────────────────

function writeIntegrationConfig(targetDir, tools, config) {
  const deskillPath = path.join(targetDir, DESKILL_DIR);
  const configDir = path.join(deskillPath, '_config');
  fs.mkdirSync(configDir, { recursive: true });

  const content = [
    '# DESKILL tool/IDE integration',
    '',
    '[integration]',
    ...tools.map(t => `${t} = true`),
    '',
  ].join('\n') + '\n';

  fs.writeFileSync(path.join(configDir, 'integration.toml'), content);
}

function writeClaudeDotMd(targetDir, config) {
  const content = [
    '# DESKILL Data Engineering Framework',
    '',
    `This project uses **DESKILL** (v${packageJson.version}) — a Data Engineering Project Roadmap.`,
    '',
    '## Available Skills',
    '',
    '### Lifecycle Commands (run in order)',
    '| Command | Purpose |',
    '|---------|---------|',
    '| `/spec` | Define business problem, data sources, contracts |',
    '| `/plan` | Design architecture, choose tools, set up environment |',
    '| `/build` | Implement ingestion + transformation + tests |',
    '| `/validate` | Run data quality checks, validate contracts |',
    '| `/review` | Review architecture, code, security |',
    '| `/ship` | Deploy, orchestrate, document, hand off |',
    '',
    '### Agent Personas',
    '- **data-engineer**: Use for hands-on pipeline building',
    '- **backend-architect**: Use for system design and architecture decisions',
    '',
    '## How to Use',
    '',
    '1. Read `.deskill/SKILL.md` for the full methodology.',
    '2. Start with `/spec` to define the business problem.',
    '3. Work through lifecycle commands in order.',
    '4. Use agent personas for specialized tasks.',
    '',
    `## Configuration`,
    `- Agent name: ${config.userName}`,
    `- Communication language: ${config.commLang}`,
    `- Document language: ${config.docLang}`,
    `- Output folder: ${config.outputFolder}`,
  ].join('\n') + '\n';

  fs.writeFileSync(path.join(targetDir, 'CLAUDE.md'), content);
}

function writeGithubCopilotInstructions(targetDir, config) {
  const githubDir = path.join(targetDir, '.github');
  fs.mkdirSync(githubDir, { recursive: true });

  const content = [
    '# DESKILL Data Engineering Framework — Copilot Instructions',
    '',
    'This project follows the DESKILL Data Engineering Project Roadmap.',
    '',
    '## Project Structure',
    '- `.deskill/` — DESKILL framework files (commands, phases, templates, agents)',
    '- `docs/` — Project documentation and architecture decisions',
    '- `' + config.outputFolder + '/` — Planning, implementation, and learning artifacts',
    '',
    '## Lifecycle Commands',
    `When the user mentions any of these commands, reference .deskill/commands/ for guidance:`,
    '- /spec: Define business problem, sources, contracts',
    '- /plan: Design architecture, choose tools, set up environment',
    '- /build: Implement ingestion + transformation + tests',
    '- /validate: Run data quality checks, validate contracts',
    '- /review: Review architecture, code, security',
    '- /ship: Deploy, orchestrate, document, hand off',
    '',
    '## Key Principles',
    '- Data contracts are first-class deliverables',
    '- Testing validates transformation logic; Data Quality validates actual data at runtime',
    '- Tools are choices, not requirements',
    '- Always check for feedback loops between phases',
    '',
  ].join('\n') + '\n';

  fs.writeFileSync(path.join(githubDir, 'copilot-instructions.md'), content);
}

function writeCursorRules(targetDir, config) {
  const rulesDir = path.join(targetDir, '.cursor', 'rules');
  fs.mkdirSync(rulesDir, { recursive: true });

  const content = [
    '---',
    'description: DESKILL Data Engineering Framework — lifecycle commands and methodology',
    'globs: *.md, *.yaml, *.py, *.sql',
    '---',
    '',
    '# DESKILL Data Engineering Framework',
    '',
    'This project uses DESKILL (v' + packageJson.version + ').',
    '',
    '## Capabilities',
    '- Lifecycle commands: /spec, /plan, /build, /validate, /review, /ship',
    '- Agent personas: data-engineer, backend-architect',
    '- Methodology: 10-phase DE lifecycle (discover → governance)',
    '',
    '## Reference',
    '- Full methodology: .deskill/SKILL.md',
    '- Commands: .deskill/commands/',
    '- Templates: .deskill/templates/',
    '- Agent prompts: .deskill/agents/',
    '',
  ].join('\n') + '\n';

  fs.writeFileSync(path.join(rulesDir, 'deskill.mdc'), content);
}

function writeOpenCodeConfig(targetDir, config) {
  const opencodeDir = path.join(targetDir, '.opencode');
  fs.mkdirSync(opencodeDir, { recursive: true });

  const content = '{}\n';

  fs.writeFileSync(path.join(opencodeDir, 'opencode.json'), content);

  const deskillSkillDir = path.join(opencodeDir, 'skills', 'deskill');
  fs.mkdirSync(deskillSkillDir, { recursive: true });

  const srcSkill = path.join(ROOT, 'SKILL.md');
  const destSkill = path.join(deskillSkillDir, 'SKILL.md');
  if (fs.existsSync(srcSkill)) fs.copyFileSync(srcSkill, destSkill);

  const opencodeCommandsDir = path.join(opencodeDir, 'commands');
  fs.mkdirSync(opencodeCommandsDir, { recursive: true });

  const deskillCommandsDir = path.join(ROOT, 'commands');
  if (fs.existsSync(deskillCommandsDir)) {
    const entries = fs.readdirSync(deskillCommandsDir);
    for (const entry of entries) {
      if (entry.endsWith('.md')) {
        const src = path.join(deskillCommandsDir, entry);
        const dest = path.join(opencodeCommandsDir, entry);
        if (!fs.existsSync(dest)) fs.copyFileSync(src, dest);
      }
    }
  }
}

// ─── Install logic ───────────────────────────────────────────────

async function doInstall(targetDir, components, config) {
  const deskillPath = path.join(targetDir, DESKILL_DIR);

  const s = await prompts.spinner();

  const dirMap = {
    commands: 'commands',
    phases: 'phases',
    implementation: 'implementation',
    templates: 'templates',
    agents: 'agents',
    references: 'references',
    assets: 'assets',
  };

  for (const [key, dir] of Object.entries(dirMap)) {
    if (!components.includes(key)) continue;
    s.message(`Installing ${dir}...`);
    copyRecursive(path.join(ROOT, dir), path.join(deskillPath, dir));
  }

  if (components.includes('root-files')) {
    s.message('Installing root files...');
    for (const file of ['SKILL.md', 'README.md', 'plugin.json', 'LICENSE']) {
      const src = path.join(ROOT, file);
      const dest = path.join(deskillPath, file);
      if (fs.existsSync(src)) fs.copyFileSync(src, dest);
    }
  }

  s.message('Scaffolding project directories...');
  scaffoldProject(targetDir, config);

  s.message('Writing project configuration...');
  writeProjectConfig(targetDir, config);

  s.stop('DESKILL installed successfully!');
  return deskillPath;
}

// ─── Display welcome ─────────────────────────────────────────────

async function displayWelcome() {
  const color = await prompts.getColor();

  const lines = [
    'Agile AI-Driven Data Engineering. Powered by DESKILL\'s lifecycle framework.',
    'Install the components you need to design, engineer, ship, and learn.',
    '',
    `  ${color.green('\u2605')} 100% free. 100% open source. Always.`,
    '    No paywalls. No gated content. Knowledge shared, not sold.',
    '',
    `  ${color.cyan('\u25CF')} CONNECT:`,
    '    GitHub:    https://github.com/anomalyco/DESKILL',
    `    Issues:    ${packageJson.bugs?.url || 'https://github.com/anomalyco/DESKILL/issues'}`,
    '',
    `  ${color.yellow('\u2605')} SUPPORT THE PROJECT:`,
    '    Star us:   https://github.com/anomalyco/DESKILL',
    '',
    `  Docs and latest updates at: ${packageJson.homepage || 'https://github.com/anomalyco/DESKILL'}`,
  ];

  await prompts.note(lines.join('\n'), '');
}

// ─── Directory prompt ────────────────────────────────────────────

async function promptDirectory(targetDir) {
  const color = await prompts.getColor();

  await prompts.log.info(`Installation directory: ${color.cyan(targetDir)}`);

  let dirInfo = '';
  try {
    const items = fs.readdirSync(targetDir);
    dirInfo = `  Directory exists and contains ${items.length} item(s)`;
  } catch {
    dirInfo = '  Directory does not exist yet — will be created';
  }
  await prompts.log.info(dirInfo);

  const ok = await prompts.confirm({
    message: 'Install to this directory?',
    default: true,
  });

  if (!ok) {
    const customDir = await prompts.text({
      message: 'Enter installation directory:',
      placeholder: process.cwd(),
      validate: (input) => {
        if (!input || !input.trim()) return 'Directory path is required';
        return undefined;
      },
    });
    return path.resolve(customDir.trim());
  }

  return targetDir;
}

// ─── Component selection ─────────────────────────────────────────

async function promptComponents() {
  const choices = [
    { name: 'Lifecycle Commands', value: 'commands', hint: '/spec, /plan, /build, /validate, /review, /ship', checked: true },
    { name: '10-Phase Methodology', value: 'phases', hint: 'Deep-dive DE lifecycle docs', checked: true },
    { name: 'Implementation Patterns', value: 'implementation', hint: 'Airflow, dbt, Spark, Great Expectations patterns', checked: true },
    { name: 'AI Agent Personas', value: 'agents', hint: 'data-engineer, backend-architect prompts', checked: true },
    { name: 'YAML Templates', value: 'templates', hint: 'Contracts, backfill, release gate', checked: true },
    { name: 'Reference Guides', value: 'references', hint: 'Anti-patterns, legacy docs', checked: true },
    { name: 'Asset Templates', value: 'assets', hint: 'Fill-in-the-blank templates', checked: true },
    { name: 'Root Files', value: 'root-files', hint: 'SKILL.md, plugin.json, README', checked: true },
  ];

  const selected = await prompts.multiselect({
    message: 'Select components to install:',
    choices,
    required: true,
  });

  if (selected && selected.length > 0) {
    await prompts.log.message(
      'Selected components:\n' + selected.map(c => `  \u2022 ${choices.find(ch => ch.value === c)?.name || c}`).join('\n')
    );
  }

  return selected;
}

// ─── Tool integration selection ──────────────────────────────────

async function promptTools() {
  const toolOptions = [
    { label: 'Claude Code (Anthropic)', value: 'claude-code', hint: 'CLAUDE.md — terminal AI agent' },
    { label: 'GitHub Copilot \u2B50', value: 'copilot', hint: '.github/copilot-instructions.md' },
    { label: 'OpenCode', value: 'opencode', hint: '.opencode/opencode.json — AI coding CLI' },
    { label: 'Cursor', value: 'cursor', hint: '.cursor/rules/ — AI-native editor' },
  ];

  const selected = await prompts.multiselect({
    message: 'Integrate with AI tools (skills auto-discoverable immediately):',
    options: toolOptions,
    required: false,
  });

  if (selected && selected.length > 0) {
    await prompts.log.message(
      'Selected tools:\n' + selected.map(c => `  \u2022 ${toolOptions.find(t => t.value === c)?.label || c}`).join('\n')
    );
  } else {
    const skip = await prompts.confirm({
      message: 'No tools selected. Continue without AI integration? (Skills still available via .deskill/)',
      default: false,
    });
    if (!skip) return promptTools();
  }

  return selected || [];
}

// ─── Configuration prompts ───────────────────────────────────────

async function promptConfig(targetDir) {
  let safeUsername;
  try { safeUsername = os.userInfo().username; } catch { safeUsername = process.env.USER || process.env.USERNAME || 'User'; }
  const defaultName = safeUsername.charAt(0).toUpperCase() + safeUsername.slice(1);
  const defaultProject = path.basename(targetDir);

  await prompts.log.step('Configuring DESKILL');

  const userName = await prompts.text({
    message: 'What should agents call you? (Use your name or a team name)',
    default: defaultName,
  });

  const projectName = await prompts.text({
    message: 'What is your project called?',
    default: defaultProject,
  });

  const commLang = await prompts.select({
    message: 'What language should agents use when chatting with you?',
    choices: [
      { name: 'English', value: 'English' },
      { name: 'Vietnamese', value: 'Vietnamese' },
    ],
    default: 'English',
  });

  const docLang = await prompts.select({
    message: 'Preferred document output language?',
    choices: [
      { name: 'English', value: 'English' },
      { name: 'Vietnamese', value: 'Vietnamese' },
    ],
    default: 'English',
  });

  const outputFolder = await prompts.text({
    message: 'Where should output files be saved?',
    default: '_deskill-output',
  });

  return { userName, projectName, commLang, docLang, outputFolder };
}

// ─── Write tool integration ──────────────────────────────────────

async function applyToolIntegration(targetDir, tools, config) {
  if (!tools || tools.length === 0) return;

  const s = await prompts.spinner();
  s.message('Configuring AI tool integration...');

  writeIntegrationConfig(targetDir, tools, config);

  let count = 0;
  for (const tool of tools) {
    switch (tool) {
      case 'claude-code':
        writeClaudeDotMd(targetDir, config);
        count++;
        break;
      case 'copilot':
        writeGithubCopilotInstructions(targetDir, config);
        count++;
        break;
      case 'cursor':
        writeCursorRules(targetDir, config);
        count++;
        break;
      case 'opencode':
        writeOpenCodeConfig(targetDir, config);
        count++;
        break;
    }
  }

  s.stop(`Configured ${count} AI tool integration file(s).`);
}

// ─── Main install command ────────────────────────────────────────

async function installAction(options) {
  if (process.stdin.isTTY) {
    try {
      process.stdin.resume();
      process.stdin.setEncoding('utf8');
      if (process.platform === 'win32') process.stdin.on('error', () => {});
    } catch {}
  }
  if (process.stdin?.setMaxListeners) {
    process.stdin.setMaxListeners(Math.max(process.stdin.getMaxListeners(), 50));
  }

  await displayLogo();
  await displayWelcome();

  const targetDir = options.directory
    ? path.resolve(options.directory)
    : process.env.INIT_CWD || process.cwd();

  await prompts.log.step('Installation directory');
  await prompts.log.info(`Resolved installation path: ${targetDir}`);

  const confirmedDir = options.yes ? targetDir : await promptDirectory(targetDir);

  const components = options.yes
    ? ['commands', 'phases', 'implementation', 'templates', 'agents', 'references', 'assets', 'root-files']
    : await promptComponents();

  const tools = options.yes ? [] : await promptTools();

  const config = options.yes
    ? {
        userName: 'User',
        projectName: path.basename(confirmedDir),
        commLang: 'English',
        docLang: 'English',
        outputFolder: '_deskill-output',
      }
    : await promptConfig(confirmedDir);

  if (!options.yes) {
    const proceed = await prompts.confirm({
      message: 'Ready to install?',
      default: true,
    });
    if (!proceed) {
      await prompts.log.warn('Installation cancelled.');
      process.exit(0);
    }
  }

  const deskillPath = await doInstall(confirmedDir, components, config);

  if (tools.length > 0) {
    await applyToolIntegration(confirmedDir, tools, config);
  }

  const color = await prompts.getColor();
  const lines = [
    `  \u2713 Installed ${components.length} component(s) to ${color.cyan(deskillPath)}`,
    `  \u2713 Created project scaffolding (docs/, ${config.outputFolder}/)`,
    tools.length > 0 ? `  \u2713 Integrated ${tools.length} AI tool(s) — skills auto-discoverable` : '',
    `  \u2713 Configuration saved for ${color.green(config.userName)}`,
    '',
    `  ${color.green('\u25B6')} Get started:`,
    '    1. Open CLAUDE.md (or your AI tool\'s config) to begin',
    '    2. Ask your AI agent: "Read .deskill/SKILL.md and help me start"',
    '    3. Run lifecycle commands in order:',
    '       /spec \u2192 /plan \u2192 /build \u2192 /validate \u2192 /review \u2192 /ship',
  ];

  await prompts.note(lines.filter(Boolean).join('\n'), 'DESKILL is ready to use!');
  await prompts.outro(`Happy Data Engineering, ${config.userName}!`);
}

// ─── Commander setup ─────────────────────────────────────────────

program
  .name('deskill')
  .version(packageJson.version)
  .description('DESKILL Data Engineering CLI — install and manage the DESKILL framework');

program
  .command('install', { isDefault: true })
  .description('Install DESKILL components into your project')
  .option('-y, --yes', 'Accept all defaults, skip interactive prompts')
  .option('-d, --directory <path>', 'Target installation directory')
  .action(async (options) => {
    try {
      await installAction(options);
    } catch (error) {
      try {
        await prompts.log.error(`Installation failed: ${error.message}`);
        if (process.env.DESKILL_DEBUG) console.error(error.stack);
      } catch {
        console.error(error.message || error);
      }
      process.exit(1);
    }
  });

program.parse(process.argv);
