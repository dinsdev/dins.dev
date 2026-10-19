# dins

The home of "dins", Din's brand: the brand system, the setup of accounts, domain, email and dev workflow, and later the dins.dev website itself. Games live on subdomains (for example `superottie.dins.dev`) and in their own repos. Din's global working agreements (in `~/.agents/AGENTS.md`) apply. This file adds what is specific to this project.

## Read first

`docs/PRD.md` (what and why), `docs/PLAN.md` (phases and how), `docs/TASKS.md` (status), `docs/WORK_LEDGER.md` (decisions and evidence) and `docs/BRAND.md` (the locked brand system). They are the source of truth. Keep them current while you work. If the work and the docs diverge, say so. Never quietly rewrite requirements to match the work.

Status vocabulary: Planned, In progress, Implemented, Verified (automated checks passed), Accepted (Din tested). Setup tasks Din does by hand are marked Done (Din). Only Din sets Accepted. Anything still under discussion is marked Proposed.

## Layout

- `brand/concepts/`: approved concept images (drafts, never shipped as final art).
- `brand/reference/`: canonical Ottie reference art.
- `brand/specimen/`: the type and color specimen Din approved.
- `docs/`: project documents.

Final brand assets live in `brand/logo/` (marks and icons) and `brand/tokens/` (design tokens); `brand/tools/` regenerates them, and `brand/brand-guide.html` shows them all.

Private notes (account security, business, the launch checklist) live in the private `dinsdev/handbook` repo, checked out at `~/Develop/dins-handbook`.

## Conventions

- The brand rules in `docs/BRAND.md` are locked. Changing one needs Din's approval and a ledger entry.
- This repo is public. No secrets, credentials, recovery codes or account inventories here, ever. The accounts inventory belongs in the private `handbook` repo.
- Earlier website concepts (comps, a draft site PRD and plan, a puppet spike) live in `~/Develop/dins.dev-concepts`. They are reference only and not finalized. Do not copy from them without Din's go-ahead.

## Writing style

In UI strings, docs, comments and commit messages: no em dashes, no en dashes as separators, no AI-tell buzzwords (elevate, seamless, unleash, journey, tapestry, "not just X but Y"). Use periods, commas, colons or parentheses. Brand copy follows the voice rules in `docs/BRAND.md`. Refer to Din by name rather than with pronouns.

## Stop and ask Din before

Generating images with Codex (it uses Din's quota), committing, creating a GitHub remote, pushing, deploying, adding a paid service, or deleting or overwriting anything unrelated to the task.
