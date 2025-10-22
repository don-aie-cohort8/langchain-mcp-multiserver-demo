# Allowed Paths (Scope Guardrails)

This project uses **scope guardrails** so AI assistants and humans only write to safe documentation paths by default.

## Allowed (prefix-match for folders)
- `README.md`
- `PROJECT_CONTEXT.md`
- `ARCHITECTURE_OVERVIEW.md`
- `SLIDES.md`
- `VIDEO_SCRIPT.md`
- `LINKEDIN_POST.md`
- `LEARNING_REFLECTION.md`
- `docs/`, `docs/adr/`, `docs/diagrams/`
- `presentations/`, `slides/`
- `templates/`

If you need to touch code or configs, open a PR and update `scripts/allowed_paths.txt` **with rationale**.

### Pre-commit
Install the pre-commit hook to enforce scope locally:
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```
