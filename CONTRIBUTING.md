# Contributing to DESKILL

Thanks for your interest! This repo is a community-driven data engineering skill framework.

## How to contribute

### 1. Report issues
- Bug: unexpected behavior in skill files, broken links, outdated patterns
- Feature request: new implementation pattern, missing phase coverage, tool addition

### 2. Submit changes
- Fork the repo
- Create a feature branch
- Make your changes
- Run quality checks: `node tools/validate-skills.js`
- Submit a PR

### 3. Content guidelines

**For methodology (phases/):**
- Tool-agnostic — focus on concepts, not specific tools
- Include feedback loop triggers
- Include AI usage tips

**For implementation patterns (implementation/):**
- Include complete, runnable code examples
- Follow the existing format (Pattern 1, Pattern 2, etc.)
- Add comments for clarity
- Test your examples

**For skill assets (skills/*/assets/):**
- Machine-verifiable YAML preferred over free-form markdown
- Include all required fields with descriptions
- Add example values

### 4. Code of conduct
Be respectful, constructive, and assume good faith. See `CODE_OF_CONDUCT.md`.
