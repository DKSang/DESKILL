let _clack = null;
let _clackCore = null;
let _picocolors = null;

async function getClack() {
  if (!_clack) _clack = await import('@clack/prompts');
  return _clack;
}

async function getClackCore() {
  if (!_clackCore) _clackCore = await import('@clack/core');
  return _clackCore;
}

async function getColor() {
  if (!_picocolors) _picocolors = (await import('picocolors')).default;
  return _picocolors;
}

async function handleCancel(value, message) {
  const clack = await getClack();
  if (clack.isCancel(value)) {
    clack.cancel(message || 'Operation cancelled');
    process.exit(0);
  }
}

async function intro(message) {
  const clack = await getClack();
  clack.intro(message);
}

async function outro(message) {
  const clack = await getClack();
  clack.outro(message);
}

async function note(message, title) {
  const clack = await getClack();
  clack.note(message, title);
}

async function box(content, title, options) {
  const clack = await getClack();
  clack.box(content, title, options);
}

async function spinner() {
  const clack = await getClack();
  const s = clack.spinner();
  let spinning = false;
  return {
    start: (msg) => {
      if (spinning) s.message(msg);
      else { spinning = true; s.start(msg); }
    },
    stop: (msg) => { if (spinning) { spinning = false; s.stop(msg); } },
    message: (msg) => { if (spinning) s.message(msg); },
  };
}

async function select(options) {
  const clack = await getClack();
  const clackOptions = options.choices
    .filter(c => c.type !== 'separator')
    .map(c => {
      if (typeof c === 'string' || typeof c === 'number') return { value: c, label: String(c) };
      return { value: c.value === undefined ? c.name : c.value, label: c.name || c.label || String(c.value), hint: c.hint };
    });
  const result = await clack.select({ message: options.message, options: clackOptions, initialValue: options.default });
  await handleCancel(result);
  return result;
}

async function multiselect(options) {
  const clack = await getClack();
  const clackOptions = (options.options || options.choices || [])
    .filter(c => c.type !== 'separator')
    .map(c => {
      if (typeof c === 'string' || typeof c === 'number') return { value: c, label: String(c) };
      return { value: c.value === undefined ? c.name : c.value, label: c.name || c.label || String(c.value), hint: c.hint };
    });
  const initialValues = (options.initialValues || (options.choices ? options.choices.filter(c => c.checked).map(c => c.value === undefined ? c.name : c.value) : []));
  const result = await clack.multiselect({ message: options.message, options: clackOptions, initialValues: initialValues.length > 0 ? initialValues : undefined, required: options.required || false });
  await handleCancel(result);
  return result;
}

async function confirm(options) {
  const clack = await getClack();
  const result = await clack.confirm({ message: options.message, initialValue: options.default === undefined ? true : options.default });
  await handleCancel(result);
  return result;
}

async function text(options) {
  const core = await getClackCore();
  const color = await getColor();
  const placeholder = options.placeholder === undefined ? options.default : options.placeholder;
  const prompt = new core.TextPrompt({
    defaultValue: options.default,
    validate: options.validate,
    render() {
      const title = `${color.gray('\u25C6')}  ${options.message}`;
      const bar = color.gray('\u2502');
      let valueDisplay;
      if (this.state === 'error') valueDisplay = color.yellow(this.userInputWithCursor);
      else if (this.userInput) valueDisplay = this.userInputWithCursor;
      else valueDisplay = `${color.inverse(color.hidden('_'))}${color.dim(placeholder || '')}`;
      if (this.state === 'submit') return `${color.gray('\u25C7')}  ${options.message}\n${bar}  ${color.dim(this.value || options.default || '')}`;
      if (this.state === 'cancel') return `${color.gray('\u25C7')}  ${options.message}\n${bar}  ${color.strikethrough(color.dim(this.userInput || ''))}`;
      if (this.state === 'error') return `${color.yellow('\u25B2')}  ${options.message}\n${bar}  ${valueDisplay}\n${color.yellow('\u2502')}  ${color.yellow(this.error)}`;
      return `${title}\n${bar}  ${valueDisplay}\n${bar}`;
    },
  });
  prompt.on('key', (char) => {
    if (char === '\t' && placeholder && !prompt.userInput) prompt._setUserInput(placeholder, true);
  });
  const result = await prompt.prompt();
  await handleCancel(result);
  return result;
}

const log = {
  info: async (m) => { const c = await getClack(); c.log.info(m); },
  success: async (m) => { const c = await getClack(); c.log.success(m); },
  warn: async (m) => { const c = await getClack(); c.log.warn(m); },
  error: async (m) => { const c = await getClack(); c.log.error(m); },
  message: async (m) => { const c = await getClack(); c.log.message(m); },
  step: async (m) => { const c = await getClack(); c.log.step(m); },
};

module.exports = { getColor, handleCancel, intro, outro, note, box, spinner, select, multiselect, confirm, text, log };
