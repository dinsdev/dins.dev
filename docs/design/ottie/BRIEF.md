# Ottie puppet: build brief

Status: route locked by Din on 2026-10-19. This brief is the spec for building Ottie, the animated mascot on dins.dev. Read `docs/BRAND.md` (Ottie section) and `docs/WORK_LEDGER.md` first.

**Update (2026-10-21): built, with a different route.** Ottie was built and both milestones were accepted by Din, but not as the layered 2D puppet below. Din moved Ottie to a real 3D character: a Tripo base model, then eyes, glasses, fur, rig, animation and rendering in Blender. The pupils are rendered into the frames, so there are no live eyes and the manifest has no eye anchors. Still true from this brief: the states (celebrate not built), the size budgets, the WebP sheets with a manifest, every state starting and ending on the neutral pose, and the approval gate. The 3D source and tools are private (`~/Develop/dins-ottie`); `brand/ottie/README.md` describes what this repo holds. The ledger has the full history. The route section below is kept as the original plan.

## Why this exists

Ottie greets visitors on the home page, reacts while Ask Ottie answers, naps, shrugs and celebrates. An earlier spike (`~/Develop/dins.dev-concepts/spikes/puppet/`, reference only, do not copy code from it) proved the idea but looked cheap for two reasons:

1. **Rigid cut-outs of painted art.** Stiff parts rotated on hinges, so the arms looked pasted on and the shoulder caps showed.
2. **Motion without animation.** The wave was a constant back-and-forth rotation with an abrupt arm swap: no anticipation, overlap, follow-through or secondary motion. It read as a metronome.

The bar is a portfolio aimed at design-literate reviewers. Ottie has to look hand-animated and alive. A mechanical Ottie never ships; if a state isn't approved, the site uses a still Ottie instead.

## The locked route

Blender, free and in-house. No third-party animation services, no AI video.

1. **Layered painted art.** Ottie in the canonical clean-outline storybook style (`brand/reference/ottie-canonical-2d.png`, poses in `brand/concepts/ottie-poses.png`), split into layers that are complete underneath: the body painted fully behind the arms, arms drawn full length including the shoulder that tucks under the fur, so moving a part never reveals a hole or a seam. Expected layers: body and belly, head, ear left and right, tail, upper arm, forearm and hand per side (or one deformable arm per side), eye whites, upper lids, mouth shapes (smile, open, "oh", grin), whiskers, glasses. Pupils and the glasses glint are drawn live in the browser (see 5).
2. **Mesh deformation.** Each layer sits on a finely subdivided plane, deformed by an armature with smooth weights, so the painted fur bends at shoulders, elbows, neck and tail instead of hinging. Suggested bones: root, hips, spine, chest, neck, head, ears, a 3 to 4 bone tail chain, upper arm, forearm and hand per side. Glasses are rigid and follow the head.
3. **Animation authored as curves**, through Blender's Python API, with the classic principles: anticipation, squash and stretch (subtle), overlap and offset timing, follow-through and settle, arcs, secondary motion in ears, tail, belly and whiskers. No constant-speed oscillation anywhere. Every state starts and ends on the same neutral pose so states chain without a pop.
4. **Rendered to sprite sheets.** Transparent frames (Eevee, flat shading so the painted art looks exactly like the art) packed into WebP sprite sheets. Default 12 drawings per second (animating on twos); the wave may compare 12 vs 24 for Din. Frames are 2x the display size (display about 160 to 220 CSS px tall). Clean alpha edges with no white or dark fringe on paper `#F4F1EA` or charcoal `#1F1E1C`.
5. **Live eyes.** A manifest records, for every frame, the left and right eye centres, eye openness (lids) and the head angle, so the browser draws pupils that follow the cursor and a glasses glint on top of the pre-rendered motion.

## States

Milestone 1 (the approval gate): **idle** (loop, breathing, blink handled by lid frames or live, tiny weight shifts, 3 to 5 s) and **wave** (one-shot, about 1.5 to 2 s, returns to idle). Nothing else starts until Din approves both.

Milestone 2: **run-in** (enters from the right, settles into idle), **think** (pushes glasses up, glances aside, loop), **nod** (answer landed), **point** (toward the side, for sources and the contact form), **talk** (mouth shapes, loop, for speech bubbles), **shrug**, **nap** (dozes off, loop) and **wake** (startled hop back to idle), **excited jump** (contact send), **poke** (small hop when clicked). Optional: **celebrate**.

## Deliverables (in this repo)

- `brand/ottie/source/`: layered parts (PNG), the `.blend` file (saved compressed; if it would exceed 50 MB, stop and ask Din about Git LFS), and the Codex prompts used, saved next to the images.
- `brand/ottie/tools/`: Python scripts that build the rig, apply animation, render and pack sprite sheets, re-runnable end to end. Document the commands in `brand/ottie/README.md`.
- `brand/ottie/dist/`: WebP sprite sheets and `manifest.json` (per state: frame size, count, fps, loop or one-shot, and per-frame eye anchors, lid openness, head angle). Rendered frame folders are build output and go in `.gitignore`.
- `brand/ottie/preview/index.html`: a standalone player (plain HTML and JS, no framework, no network) used for approval. It shows every state on buttons, light and dark side by side, real size and 2x zoom, live pupils following the cursor, a state-chaining demo (run-in, wave, idle, think, nod), a reduced-motion still pose, and the file size of each state.

Budgets: idle at most 250 KB, any other state at most 400 KB, everything together at most 2.5 MB. Playback at 60 fps on a 2020 laptop with no dropped frames in the preview.

## Process

- Work in your own git worktree on branch `feat/ottie-puppet`, created from `docs/site-prd` (this brief lives there). Never switch branches in Din's main checkout. Commit locally at each checkpoint; never push.
- **Codex images:** ask Din before every image generation (it uses Din's quota). Generate one look-test first, show it, then the rest. Run `codex exec` from an empty scratch directory with the prompt inline and stdin closed (`< /dev/null`); run inside the repo it reads AGENTS.md and stops to ask.
- **Blender connector:** the `blender` MCP talks to the official Blender Lab add-on on port 9876. If calls hang, the community "MCP for Blender" add-on may have grabbed the port: check with `lsof -nP -iTCP:9876` and disable the community add-on.
- Show Din renders early and often: a contact sheet of key poses before animating, then the preview page. Expect several rounds per state; that is the plan, not a failure.
- Record decisions, verification and Din's approvals in `docs/WORK_LEDGER.md`, and add the Ottie rows in `docs/TASKS.md` (Phase 2) with honest statuses. Only Din sets Accepted.
- Writing style for docs, comments and commits: no em dashes, no AI buzzwords (see `AGENTS.md`).

## Verification to print in the chat

For each milestone: the list of files in `brand/ottie/dist/` with sizes, a manifest summary (states, frames, fps), 2x crops of shoulders, elbows, neck and tail on both backgrounds showing no seams or fringe, a screenshot of the preview page in light and dark, and Din's explicit approval message.
