# openclaw-init

Initialize an OpenClaw project configuration and select feature modules.

- Creates `.openclaw/state.json` with project and Gateway settings
- Generates `CLAUDE.md` with OpenClaw API reference links
- Interactive CLI: AskUserQuestion tool for user input

## Usage

```bash
/openclaw-init               # interactive
/openclaw-init --output ~/my-project
```

## Output

- `.openclaw/state.json` - project configuration (sensitive)
- `CLAUDE.md` - development reference with OpenClaw docs

## Next steps

- `/openclaw-prd` - define product requirements
- `/openclaw-nextjs` - generate Next.js app (if web module selected)
- `/openclaw-generator` - one-stop generator
