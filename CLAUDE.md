@AGENTS.md

## Claude-only notes

- Use Superpowers skills where they help. Din's request or an approved plan is the go-ahead. Specs and plans go in `docs/PRD.md`, `docs/PLAN.md`, `docs/TASKS.md`, never in `docs/superpowers/`.
- Codex image generation: run `codex exec` from an empty scratch directory with the prompt inline and stdin closed (`< /dev/null`), otherwise it loads this AGENTS.md and stops to ask instead of generating.
