# Work ledger

Decisions and why, work done, verification results, approvals, blockers, handoff status. Newest entries first.

## 2026-10-21

### Domain bought, Wrangler installed, commit rule (Din, Claude, 2026-10-21)

- **Done (Din):** bought `dins.dev` on Cloudflare (task 0.6). Verified: the .dev RDAP record shows Cloudflare as registrar, registered 2026-10-21, expiring 2027-10-21, so the term is 1 year rather than the planned 4; auto-renew is not visible from outside. Nameservers are Cloudflare's (`tom`, `paloma`). `wrangler login` succeeded. This clears the domain risk in the site plan; Email Routing (task 0.8) is next for the contact form.
- **Done (Claude):** installed Wrangler 4.151.2, Cloudflare's CLI, with Homebrew (independent of the mise-managed Node), and started `wrangler login` in Din's terminal. The site will pin its own Wrangler as a dev dependency in M0.
- **Changed (Din):** local commits need no approval; pushing, PRs, merges and deploys still do. `AGENTS.md` updated to match, with the no-attribution rule added.

### Site PRD and plan written (Claude, 2026-10-21)

- **Section 8 agreed (Din):** milestones M0 Foundation (Oct 22 to 26), M1 Pages and content (Oct 27 to Nov 6), M2 Ottie on the site (Nov 2 to 12), M3 Ask Ottie (Nov 6 to 22), M4 Set pieces (Nov 13 to 29), a content track for Din (Nov 1 to Dec 1, freeze Dec 1), M5 Hardening and launch (Dec 1 to 12, live by Dec 12), then the performance pass. Fallbacks: a set piece not approved by Dec 1 ships as its calm version; unready projects stay drafts. Din's dependencies: Workers Builds authorization (M0), the domain and Email Routing by about Nov 12, Anthropic keys before M3, the interview in early November.
- **Done:** `docs/site/PRD.md` (sections 1 to 8 with acceptance criteria) and `docs/site/PLAN.md` (layout, environments, milestones with verification, dependencies, fallbacks), kept separate from the setup PRD, which says the site gets its own. TASKS rows 2.10 to 2.17.
- **Reconciled while writing:** section 1's project `placeholder` or `real` status became section 5's `draft` or `published`; library entry fields merge both sections (question or topic, approved text, audience tags, sources, language, `approved_on`).
- **Open:** Din's review of both files. Nothing is built yet.
- **Working rule (Din):** "local commits are fine as you go. Only pushing to github requires permission." `AGENTS.md` updated to match (see the entry above).

### Site brainstorm, section 7: testing and CI (Din and Claude, 2026-10-21)

- **Agreed (Din):** Vitest for unit tests (player logic, search, budget, answer renderer, schemas), Vitest inside the Workers runtime with a local D1 for `/api/ask` and `/api/contact` on the fake backend, pytest for the RAG build, retrieval evals on every PR (recall@6 at least 0.9), answer evals on demand and before release (faithfulness at least 0.95, 100 percent correct refusals, language match), Playwright with axe end to end, a budget script (Ottie sheets and manifest; home page JavaScript at most 100 KB gzipped as a gate), Lighthouse CI (accessibility and SEO gates, performance as a warning) and lychee. Set-piece screenshots are attached to PRs for review, not pixel-compared. pre-commit, `check.sh` under 2 minutes, GitHub Actions on every PR as required checks, Workers Builds previews on the fake backend, production from `main` with a pre-launch checklist. Tests first for logic; visual set pieces are reviewed by Din in the preview.
- **Version note:** Cloudflare's Vitest pool (0.23.0) supports Vitest 4 only, so Vitest is pinned to 4.1, not 5.
- **Decided (Din):** answer evals run in GitHub Actions on manual trigger with a separate eval key (own spend cap of about $5) stored as a GitHub secret ("Use the GitHub secret").

### Site brainstorm, section 6: quality (Din and Claude, 2026-10-21)

- **Agreed (Din):** WCAG 2.2 AA, with a calm version of every set piece under reduced motion, full keyboard access, Ottie hidden from screen readers and answers announced once complete; axe at zero violations plus one manual VoiceOver pass before launch. Smoothness budget instead of the Lighthouse performance gate: no layout shift (reserved boxes, metric-matched font fallbacks, two preloaded self-hosted WOFF2 fonts), animate only transform, opacity and canvas, 60 fps and no main-thread task over 50 ms through the set pieces on a 2020 laptop and a mid-range phone, about 100 KB of first-party JavaScript on the home page before interaction, and a still Ottie with no lens intro on Save-Data or low-memory devices. SEO baseline as locked, Lighthouse SEO 100 as a gate. Privacy: no cookies or banner, only Turnstile and Cloudflare Web Analytics as outside scripts, anonymous question log deleted after 30 days, contact messages emailed and not stored. Security: the Anthropic key as a Worker secret per environment, a strict CSP, HSTS, `security.txt`, answers rendered as plain text with simple formatting. Failure modes: readable without JavaScript, Ottie "resting" when the API or budget is out, keyword-only search when Workers AI is down, the still Ottie when a sheet fails, a 404 with Ottie.

### Site brainstorm, section 5: content and the library (Din and Claude, 2026-10-21)

- **Agreed (Din):** typed Astro content collections for `projects`, `writing`, `library` (Ottie-only, never rendered as pages) and `suggested`; drafts never render in production, so the placeholder projects cannot ship. Library pipeline: raw sources (GitHub READMEs, resume, LinkedIn export, thesis) and the interview transcript stay in `handbook`; Claude drafts short entries citing their sources; entries reach this repo only through a PR Din reviews, and only Din sets `approved_on`. CI fails on an unapproved entry or a deny-list topic (keyword scan, backed by refusal evals). The interview questions and Din's approved answers become `rag/evals/golden.yaml`; deny-list, off-topic and injection questions go in `adversarial.yaml`. Suggested answers are generated by a script, reviewed in a PR and served as static text, so builds never call the API. Content freeze around December 1.
- **Decided (Din):** the library is public in this repo ("Keep it public"). Why: Ottie can repeat anything in it, so it is effectively public anyway, and reviewers can see exactly what Ottie knows; keeping it in `handbook` would add a private dependency to every deploy.

### Site brainstorm, section 4: the stack (Din and Claude, 2026-10-21)

- **Decided (Din):** Astro with Svelte islands ("Let's go with Astro and Svelte"), after comparing it with Next.js and Vue. Why: pages ship as finished HTML and only Ask Ottie, Ottie and the scroll set pieces load JavaScript, so the lens intro and Ottie get the main thread on first load; Astro deploys to Cloudflare without an extra adapter layer. Next.js would suit an app with heavy cross-page state; React islands inside Astro remain the route if a React resume signal is ever wanted.
- **Rest of the stack (proposed by Claude, not vetoed):** Astro 7.4, Svelte 5, plain CSS on `brand/tokens/tokens.css`, GSAP with ScrollTrigger for the set pieces and no smooth-scroll library, an in-house canvas Ottie player, Cloudflare Workers with static assets through Workers Builds (Astro's adapter dropped Pages), D1 for the daily budget and the anonymous question log, Email Routing's `send_email` binding for the contact form, a Python `rag/` project with uv for chunking, bge-m3 embeddings and evals, Node 24 LTS, pnpm, TypeScript 6.0 (`@astrojs/check` does not support TypeScript 7 yet), Vitest, Playwright with axe. Versions checked on npm and nodejs.org on 2026-10-21; pin to minor versions and let Renovate bring patches.
- **Ottie loading (Din's requirement: "make sure Ottie loads good and the website is smooth"):** the neutral still is inline and sized in advance; the idle sheet loads when the page is idle and wave is preloaded; other states are fetched just before they are needed; decoding happens off the main thread; playback pauses off screen and in hidden tabs.
- **Free-plan calls:** the search index is a binary file in static assets (no JSON parse inside the 10 ms CPU limit), and a test checks that build-time bge-m3 embeddings (open weights) match Workers AI's.
- **Changed from section 2:** the "Claude Code on Din's membership" answer backend is dropped (a subscription is unlikely to be licensed to power a website, an assumption not yet checked, and it is a third code path). Backends: a fake for tests and local work, the Anthropic API for live checks, staging and production.
- **Changed from section 3:** no cursor-following eyes, since the 3D Ottie's eyes are rendered into the frames.
- **Changed in the plan (Din):** Lighthouse performance is a warning, not a gate, for now ("Let's mark it for optimization later"). Accessibility 100 and SEO 100 stay as gates.

### Ottie: 3D look locked, 3D source made private (Din, Claude, 2026-10-21)

- **Decided (Din):** the 3D Ottie is the final look for now: "The way Ottie is right now is the final decision for now. We went thru every stage of testing and this was the best looking one." `docs/BRAND.md` now names the 3D render as the full Ottie, with `brand/reference/ottie-3d-neutral.webp` (idle drawing 0 at full render size) as the reference. The 2D art stays as the character reference and the source of the seal. `BRIEF.md` gets a status note instead of a rewrite.
- **Decided (Din):** "I don't think we should push the 3d modelling. We only need what's enough to be able to animate Ottie on the website. Anything we need can also use git lfs."
- **Done:** the full branch history (37 commits) plus the untracked `.blend` files and rendered frames went into a new local repo, `~/Develop/dins-ottie` (cloned from `feat/ottie-puppet`, checked file for file against the worktree). `feat/ottie-puppet` was then rebuilt from `docs/site-prd` with only the sheets, manifest, preview player, a public README and these docs. Removed from this repo: the Tripo export, the cleaned model and textures, the Codex inputs and views, the Blender and packing tools, `RESEARCH.md` and the look and rig review renders. `.gitignore` now blocks those paths and `*.blend`, `*.fbx` and `*.glb`. Paths to `tools3d/`, `source/` and `docs/design/ottie/*.jpg` in the entries below now point into `dins-ottie`.
- **Why:** the old branch added about 248 MB of files to history, mostly dead TRELLIS meshes and four versions of a 40 MB `.blend`. A squash merge would not help, because pushing the branch uploads every object. A public 3D model would also let anyone lift Ottie, while the site only needs the sheets (2.4 MB, small enough that Git LFS is not needed here).
- **Private remote (Din's go):** created `dinsdev/dins-ottie` (private) and pushed it. Its history was converted to Git LFS for `*.blend`, `*.glb`, `*.fbx`, `*.png`, `*.jpg` and `*.webp` first (commit messages unchanged), and the look and rig `.blend` files and the full rendered frames are now tracked too, because the frames take hours to render again. Only the quick test renders stay untracked. The free plan includes 10 GiB of LFS storage and 10 GiB of bandwidth a month; this uses about 0.5 GB. The repo has its own README, AGENTS.md and CLAUDE.md.
- **Open:** the brief's crop and from-scratch rebuild checks were not recorded during the build and remain unverified.

### Ottie milestone 2 accepted (Din, 2026-10-21)

- **Accepted (Din):** "All approved: run-in, think, nod, point, shrug, poke, jump, nap, wake and talk", after reviewing the preview at commit `7f5737c` (all at q45, total 2,404.4 KB). Tasks 2.4 and 2.4a are Accepted. Celebrate (optional) was not built.

## 2026-10-20

### Ottie milestone 2: the mouth, talk, and the remaining states (Claude, 2026-10-20)

- **Decided (Din):** talk uses option A, an opening mouth built into the look ("Go with A: cut the mouth open along the lip crease in build_look.py, add a mouth interior and shape keys, rebuild look and rig, and check idle and wave for drift"), over a separate mouth piece (B) or a jaw-only mumble (C).
- **Found:** no cut was needed. Tripo modelled a real mouth cavity behind the closed lips (it runs back to y -0.17); the lips only meet inside the cavity and at the corners. So the mouth opens by moving existing vertices, which keeps every face, the fur layout and `hair_uv` exactly as accepted.
- **Done (`build_look.py`, `build_mouth()`):** three shape keys on the skin: `jaw` (the lower lip, chin and cavity floor swing 20 degrees about a hinge behind the mouth, fading to the corners and down the chin), `round` (oh: corners in and forward) and `wide` (ee: corners out and up). The lower jaw is found by growing from the chin through the mesh, stopped by the cavity's upper half and the corners (a height threshold pulled the upper lip down over the teeth). Inside the mouth: vertices hidden at rest (every frontal ray hits the skin or the teeth, eroded by one ring) darken with depth and get a tongue on the floor; the lips, which Tripo painted cream like the teeth, tint toward a lip colour through a driver on the jaw key, so they change only while the mouth is open. 2,885 fur strands rooted on hidden cavity skin are dropped after every random draw, so the other 170,289 strands are the same strands as before. `OTTIE_MOUTH=0` builds the look without the mouth.
- **Lesson:** in Blender 5.2 a new shape key starts at value 1. The first rebuild rendered the rest pose with the mouth open until the keys were set to 0.
- **Drift check:** re-rendered idle drawings 0 and 10 and wave drawing 8 on the new rig against the accepted frames: mean difference 0.026, 0.318 and 0.403 (of 255). The old rig re-rendered against its own frames gives the same numbers (0.026 and 0.403), so the difference is render noise in posed fur, and idle, wave and the states already rendered did not need re-rendering.
- **Done (`build_anim.py`):** `pose(mouth=(jaw, round, wide))`, keyed on the skin's shape keys per state. New states: **point** (2 s, eyes lead, arm out to screen right with an overshoot, an "over there" nod, settle), **shrug** (1.5 s, shoulders and open paws up, head tilt, half-lowered lids), **poke** (0.8 s, blink, squash, small hop, squashy landing), **jump** (1.5 s, crouch, launch, paws up in a V, squashed landing), **nap** (dozes off once, then a slow sleeping breath on a loop; leaves through wake), **wake** (1.5 s from the sleeping pose: ear twitch, startled hop, a look each way, blink, settle), **talk** (2 s loop: syllables ah, ee, closed, oh with head bobs, a small open-palm paw gesture and a blink). Hops and the jump use travel, so their sheets stay compact. Celebrate (optional) is not built: the budget has 96 KB left.
- **Verified:** `pack.py`, all twelve states at q45 except wave (q80, accepted): idle 243.1, wave 367.4, run-in 258.2, think 271.0, nod 111.8, point 198.9, shrug 144.6, poke 91.3, jump 172.1, nap 221.9, wake 113.8, talk 210.2 KB; total 2,404.4 KB of 2,500 KB, each state under 400 KB. The preview plays every state on paper and charcoal with no console errors; asking for another state during nap plays wake first; the chain runs run-in 2.3 s, wave 2.0 s, idle 4.0 s, think 4.0 s, nod 1.0 s and back to idle.
- **Changed since batch 1:** sharing the budget with nine more states moved run-in, think and nod from q55 to q45 (idle's accepted quality).
- **Open:** none of the milestone 2 states is accepted by Din yet. The point is drawn toward screen right only. Pupils are rendered, so states cannot look at the cursor.

### Ottie milestone 2, batch 1: run-in, think, nod (Claude, 2026-10-20)

- **Done (`build_anim.py`):** new posing tools beside the accepted idle and wave (whose output is unchanged): `pose()` now also takes root and bone moves, `plant` (moves the root so the lower foot stays on the floor in crouches), `glasses` (tilts the glasses empty about the ear line, a push-up), `eyes` (turns both eyeballs for glances), `travel` (a whole-body offset the player applies, so runs and jumps do not widen the sheets) and `reach` (a two-bone reach that puts a paw on a point of the head). The glasses and eyes get their own actions per state. Timing can vary inside a state (twos for fast moves, fours to eights for holds). `--keys` renders each key pose small and quick for contact sheets.
  - *Run-in (2.3 s):* four scurrying steps turned three-quarters toward the stage (arms pumping, tail streaming, a bounce), a brake with a lean back while the arms and tail fly forward, a turn to the front with an overshoot, a blink and a settle.
  - *Think (4 s loop):* the paw comes up and pushes the glasses up by the bottom of the rim (the head dips to meet it, since the arm is 25 cm long), drops under the chin, glances up and aside, two chin taps, a blink, a glance the other way, then home while the glasses slide back down.
  - *Nod (1 s):* a small chin lift, two nods (the second smaller) with a half-blink, ears and tail late.
- **Packing (`pack.py`):** idle and wave keep their accepted budgets and encodings. The other states share what is left of 2.5 MB at one common quality (the highest that fits), each capped at 400 KB, with reserves for states not rendered yet. Why: per-state guesses starved think (q20 at its first budget, visibly smeared fur at 2x). New manifest fields: per-drawing `shift`, and per-state `loop_start`, `exit_via`, `enter_from` (for nap and wake).
- **Preview:** applies `shift` (the stage grows to hold the run-in's entry), loops from `loop_start`, leaves through `exit_via`, skips the crossfade for an entrance from off stage, and in the chain demo lets each loop play one full pass (before, idle and think were cut at once by the crossfade).
- **Verified:** run-in 25 drawings q55 281.7 KB, think 28 drawings q55 298.2 KB, nod 12 drawings q55 123.2 KB; total 1313.6 KB with 1150 KB reserved. The preview plays all five states and the chain (run-in, wave, idle, think, nod, back to idle) on paper and charcoal with no console errors.
- **Open:** not yet reviewed by Din. Talk needs an open mouth (proposal to Din). Point, shrug, poke, jump, nap and wake are keyed and rendering.

### Ottie: 3D idle and wave accepted (Din, 2026-10-20)

- **Accepted (Din):** "idle approved, wave approved", after watching the preview with the hands-at-sides pose and the bright studio lighting (commit `ebfef67`; idle 243.1 KB, wave 367.4 KB). Task 2.3b is Accepted. Milestone 2 (task 2.4) can start when Din says so.


### Ottie: hands at the sides and brighter lighting (Din, 2026-10-20)

- **Asked (Din):** "Hands down on the side would look nicer" for the idle pose, and brighter lighting like the bright reference (`brand/ottie/source/views/front.png`).
- **Done:**
  - *Pose:* the neutral pose hangs the arms about 30 degrees out from vertical so they clear the belly, with the paws turned a little forward (candidate B of three test renders). The idle gains an arm sway trailing the weight shift. The wave's anticipation and settle keys are re-keyed around the hanging arms: the arm drops with the forearm trailing, swings slightly past rest and settles. `pose()` now applies aims before turns, so a turn sways an aimed arm.
  - *Light (`build_look.py`):* a bright neutral studio world, a big soft key from the front and above, a broad fill, a bounce from below and softer warm rims. The key and fill are hidden from glossy rays (they fogged the wrapped lenses), and a small catch light above the camera gives the eyes their highlight.
  - *Grade:* exposure -0.75, gamma 1.3 (separates the brown sides from the cream belly), saturation 0.92, gain 1.0/0.94/0.86 to take out Tripo's pink. A new paw mask tints the hands and feet dark brown on both the skin and the fur.
- **Verified:** `pack.py`: idle 243.1 KB (q45), wave 367.4 KB (q80), total 610.6 KB, all within budget. The preview plays both on paper and charcoal with no console errors.
- **Open:** the reference's darker eye mask and crown come from its painting; Tripo's texture spreads colour differently. The `look-tripo-v1` and `rig-tripo-v1` renders in `docs/design/ottie/` show the earlier lighting.


### Ottie: 3D idle and wave rendered and packed (Din's go, Claude, 2026-10-20)

- **Accepted (Din, 2026-10-20):** the cleaned base ("Base looks good"), the look ("The look is good") and the rig ("The rig passes").
- **Done:** `brand/ottie/tools3d/build_anim.py` keys and renders the states from `ottie_rig.blend`, and `tools/pack.py` packs them into `brand/ottie/dist/`.
  - *Neutral pose:* paws held in front of the belly, like the reference. Every state starts and ends on it.
  - *Idle:* a 4 s loop with two breaths (chest swell), a weight shift with the spine and head following late, a tail sway trailing the hips, an ear twitch and one blink.
  - *Wave:* a 2 s one-shot. Anticipation (tuck and dip), an overshooting raise, three waves that shrink while the paw trails the forearm, a blink as the arm drops past neutral, then a settle. The head tilts toward the paw and the tail flicks a beat late.
  - *Method:* poses are built on the neutral pose (world-axis turns through bone heads, arm aims, chest scale, lid roll) and keyed as quaternions kept on one hemisphere, with auto-clamped Bezier curves. The idle loops through a Cycles modifier.
- **Rig fixes found while animating:** Smart UV Project had left overlapping faces in `hair_uv` on the right arm, so 924 strands stayed behind when the arm moved. `hair_uv` now uses lightmap packing, and 0 strands are left off the skin. The lids lost their orientation when parented to the head, so `build_rig.py` adds `lid.L`/`lid.R` bones at the eye centres and a blink is a 140-degree roll. The fill light no longer shows in glossy reflections, because it fogged the lens nearest the camera.
- **Render and pack:** Cycles at 96 samples with a fixed seed, transparent, 720 by 880, about 23 s a drawing. Idle is drawn on fours (6 drawings a second) to fit its budget, as the approved 2D idle was; wave is drawn on twos.
- **Verified:** `pack.py`: idle 24 drawings, 219 by 390, q45, 242.0 KB (budget 250 KB); wave 24 drawings, 234 by 389, q80, 369.3 KB (budget 400 KB); total 611.3 KB. Exits: idle at drawing 0 (the player crossfades when more than 12 ticks away), wave at 0 and 23. The preview plays both on paper and charcoal with no console errors, and switching from idle to wave works.
- **Open:** only one clean idle exit, so switching mid-loop uses the crossfade. Look and motion not yet accepted by Din.


### Ottie: rig and wave test pose (Din's go, Claude, 2026-10-20)

- **Done:** `brand/ottie/tools3d/build_rig.py` rigs `ottie_look.blend` in about 15 seconds.
  - *Armature:* 25 bones (root, hips, spine, chest, neck, head, two ears, upper arm, forearm and hand per side, thigh, shin and foot per side, five tail bones), with joints read off calibrated front and side views of the A-pose.
  - *Weights:* Blender's automatic (bone heat) weights, which now work because the body is one closed skin. This replaces the hand-rolled inverse-distance weights behind the earlier deformation problems. The head is then blended to fully rigid between z 0.70 and 0.76, with the ear weights kept, so the face never distorts.
  - *Attachments:* the eyes, lids, teeth, glasses and whiskers ride the head bone, and the fur rides the skin through Deform Curves on Surface on `hair_uv`.
  - *Glasses:* the temples now stop just in front of the ear roots (`TEMPLE_END` in `build_look.py`) instead of poking into the ears.
- **Verified (renders, `docs/design/ottie/rig-tripo-v1-*.jpg`):** in the wave, the arm stays attached with a smooth armpit and even thickness. The torso and belly do not move with the arm. The head tilts as one piece with everything on it, and the fur follows the skin. Every vertex received weights.
- **Not tracked:** `ottie_rig.blend` (13 MB, a build output).
- **Open:** a bone-heat-only rig has no controls or IK yet (fine for keyed animation from scripts). The lids are not yet furred. No animation is keyed yet (idle and wave are next, task 2.3b). Not yet accepted by Din.


### Ottie: look development on the Tripo base (Din's go, Claude, 2026-10-20)

- **Done:** `brand/ottie/tools3d/build_look.py` builds the look on `ottie_base.blend` in about 30 seconds (plus about 30 seconds of Cycles renders on the Mac's GPU). It reuses the shaders and the fur approach from the TRELLIS build (history up to `6df5e51`), refitted to the Tripo model:
  - *Eyes:* Tripo's eyeballs were rounded boxes (radius 0.047 to 0.077), so they are replaced by spheres (r 0.0615) at the same centres. The procedural iris reads from each eye's forward axis, so the eyes can turn. The upper lids rest hidden under the brow and close for a blink (checked in a render).
  - *Nose:* a soft mask on the skin makes dark, glossy leather with fine bumps; the teeth get an enamel material.
  - *Glasses:* each rim's plane is fitted to the face around the eye (wrap and tilt capped at 16 and 12 degrees), moved forward to clear the skin, with a bridge over the nose and temples running straight back to the ears. The lens faces are forced to point forward, since a backward-facing lens mirrors everything through the Fresnel term.
  - *Fur and whiskers:* 173,174 strands coloured from the texture under each root (patches use their own colour), short on the face and paws, bare on the nose, mouth and eye openings. They are attached through a fresh non-overlapping UV map (`hair_uv`) for the rig, plus 12 whiskers.
  - *Grade and light:* the same grade on the skin and fur (gamma 1.2, saturation 0.82, gain 0.86/0.88/0.86), because Tripo's texture reads lighter and pinker than the reference. Standard view at -1.1 exposure, a warm key placed so the wrapped lenses do not mirror it, a fill and two warm rims.
- **Renders:** `docs/design/ottie/look-tripo-v1-{portrait,three_quarter,full,eyes,blink}.jpg`.
- **Not tracked:** `ottie_look.blend` (12 MB) is a build output, rebuilt by the script.
- **Open:** the lids are plain brown shells (no fur yet); the fur has no clumping or grooming passes beyond combing; the glasses are separate objects, not yet rigged. Look not yet accepted by Din.


### Ottie: Tripo model cleaned in Blender (Din's go, Claude, 2026-10-20)

- **Found:** the export is two nearly coincident skins crossing each other (about 5,600 faces each, 0 to 3 mm apart), not one surface with a few faults. The inner skin is smooth and almost closed; the outer one carries the crown spikes, most of the holes and the doubled edges. The paw "overlaps" were the same doubling. Separate parts: two eyeballs, the teeth, 12 whisker strips and one closed part hidden inside the muzzle.
- **Done:** `brand/ottie/tools3d/clean_model.py` rebuilds `brand/ottie/source/3d/ottie_base.blend` from the export in about 15 seconds. It keeps the inner skin, relaxes a fold under the chin, trims rims that touch themselves, fills the 13 holes (crown, chin, muzzle, finger tips, soles) with concentric quad rings faired by a bi-Laplacian solve (the rim and one ring outside held fixed), and colours each patch by harmonic interpolation of the texture around its rim (outlier rim colours replaced by the patch median, converted to linear). Tripo's UVs and texture are kept (scaled to 4K, 3.7 MB); its stale custom normals are dropped. The eyeballs and teeth are their own objects; whisker strips and the hidden part are removed.
- **Tried and dropped:** peeling hidden faces by ray visibility (tore the mouth and feet), baking from the doubled original (smeared the face), grid fill (one-strip patches with no inner vertices, so streaks).
- **Verified:** body 4,291 vertices and 4,700 faces with no open edges and no edges shared by more than two faces; eyeballs closed; teeth closed (5 doubled edges, invisible). Renders from the front, side, back, crown, face, chin and paws show no holes or spikes.
- **Open:** the nose bridge is now muzzle brown, not dark leather (the nose gets its own material in look dev); the crown and chin patches have flat colour (covered by the groom); hair attachment should use a fresh UV map, since patch faces reuse nearby UVs. Not yet accepted by Din.


### Ottie: Tripo base model in hand (Din, Claude, 2026-10-20)

- **Done (Din):** subscribed to Tripo Studio Max and generated Smart Mesh P2.0, quad, multi-view from `brand/ottie/source/views/` (four polycounts, private), texture with Remove Lighting at 8K. Exported the 12,454-face result as FBX to `brand/ottie/source/ottie-3d-model/` (Tripo named it "meerkat"). The Tripo CLI is also installed and signed in to the API account (separate pay-as-you-go billing, 0 credits); Studio is what we use.
- **Checked in Blender (Claude):** 1.0 m tall, feet at the origin, facing -Y, one 8K base colour texture. 70 percent quads with real edge loops around the eyes, nose and mouth, a clean body grid, arms apart in A-pose, closed smile. Eyeballs, nose and teeth are separate closed parts, so the eyes can take our own shader.
- **Faults to fix:** two holes with dark texture patches under the chin; a fringe of loose spike cards and small holes across the top of the head; thin whisker strips (12 loose pieces); overlapping geometry at the paws (most of the 1,427 edges shared by more than two faces). The texture is 16 MB (8K JPEG); a 4K copy is enough for rendering.


### Ottie: Tripo researched as the base-model service (Claude, 2026-10-20)

- **Done:** Din asked about Tripo (tripo3d.ai) and its free tier. Findings, credit costs and a workflow are in `docs/design/ottie/RESEARCH.md` (Tripo section). Added `brand/ottie/tools/split_views.py`, which cuts the turnaround into front, left, back and mirrored right views (`brand/ottie/source/views/`) for multi-view to 3D.
- **Key facts:** the free tier (200 credits) is public and non-commercial and has no multi-view to 3D, so it is for testing only; the shipped model needs a paid plan (Pro, $20 a month). Smart Mesh P2.0 gives quad topology, which addresses the TRELLIS.2 rigging problems.
- **Free test (Din):** a Tripo free-tier turntable generated from the 3D reference holds the face (eyes, glasses, open smile, teeth, whiskers) and a consistent body and tail from every side. It is not a usable rig base as is: the open mouth, glasses and probably the eyes are fused into one mesh and texture, the paws rest on the belly instead of an A-pose, the fur in the video may be the viewer's effect rather than exported geometry, and free output is public and non-commercial. Plan: Din subscribes to Pro, then the hero model is regenerated from the A-pose views in `brand/ottie/source/views/` (no glasses, closed mouth), with the turntable as the look target.
- **Proposed:** run the free test on Tripo, then pay for one month of whichever of Tripo or Meshy keeps the face and deforms cleanly. Din's call.

### Ottie: modelling cleared for a fresh start with Meshy (Din, 2026-10-20)

- **Decided (Din):** remove everything no longer needed for modelling and start fresh tomorrow with a Meshy model. Removed: the 2D puppet (painted parts, Codex sheets and masters, 2D sheets in `dist/`, its tools and `.blend`) including the accepted 2D idle and wave, the TRELLIS.2 meshes, texture, `.blend` and Blender build script (`tools3d/`), the look-test images, and the stopped milestone 2 session's uncommitted edits. All of it stays in git history on `feat/ottie-puppet` up to `6df5e51`.
- **Kept:** the brief, `RESEARCH.md`, the 3D reference, the Codex mesh input and turnaround (the Meshy inputs), `tools/pack.py` (now independent of the 2D parts: no contact-shadow pass, no lid colour or live-eye fields; optional ground, look, mouth and head fields pass through) and the preview player (rewritten without live pupils, which Din dropped for rendered 3D eyes; keeps ground anchoring, clean exits with a crossfade fallback, the chain demo and the reduced-motion still).
- **Verified:** packed two synthetic states with `pack.py` and played them in the preview (state switching works, no console errors); the test output was deleted.

### Ottie 3D route: first model, paused for Meshy (2026-10-20)

- **Done:** Codex mesh input and turnaround (approved by Din); TRELLIS.2 on a rented Vast.ai RTX A6000 (about $0.60): six meshes, the 1536 seed 4 kept for shape and the 1024 seed 3 for colour (`brand/ottie/source/3d/`). DINOv3 is gated with manual approval, so it was rebuilt from the ungated timm copy and verified identical (max difference 2.8e-6); RMBG-2.0 (non-commercial licence) was never used. In Blender (`brand/ottie/tools3d/ottie3d_build.py`, rebuilds the scene in seconds): colour matched, the painted TRELLIS eyes repainted out of the texture, modelled eyes with rendered pupils (Din's call), lids, procedural glasses, a 15 percent bigger head and rounder belly, darker limb markings, about 150,000 groomed fur strands bound to the skin, and a 24-bone rig with computed weights. Look tests in `docs/design/ottie/` (look-test-3d-*, rig-test-3d-*).
- **Lessons:** TRELLIS.2 meshes collapse under Decimate and shred under voxel remesh (not a closed shell); keep full density and smooth instead. Its painted eyes must be removed when modelling real ones.
- **Decided (Din):** pause here; Din will get a Meshy membership so the base model can come from Meshy (stylised characters, auto-rigging, Blender plugin). This is a paid third-party service for modelling, which Din has chosen; the animation stays in-house. The Codex mesh input and turnaround are ready as Meshy inputs, and the eyes, glasses, fur, markings and rig tooling should carry over to a Meshy mesh.
- **Open:** whether to keep committing `ottie3d.blend` (40.6 MB, near the brief's 50 MB line; the script rebuilds it); the open mouth for talk (the mesh has a closed mouth); the stopped milestone 2 session's uncommitted 2D edits are still in the worktree, untouched.

## 2026-10-19

### Ottie restart: route A, real 3D (Din)

- **Decided (Din):** after milestone 1 Din shared a new reference (`docs/design/ottie/reference-3d-2026-10-19.jpg`, a Pixar-style 3D render) and chose route A from `docs/design/ottie/RESEARCH.md`: a real 3D Ottie in Blender. Base mesh from a free open model (TRELLIS.2 first) on a GPU Din rents on Vast.ai, from a Codex mesh-input image and turnaround (both approved by Din). Glasses, eyes and teeth are modelled in Blender; fur by Geometry Nodes hair; Rigify rig; the animation, packing and preview tooling carry over.
- **Still open:** live pupils versus rendered eyes, and whether the new reference replaces the storybook style in BRAND.md (both Din's call). The 2D milestone 1 stays in history as the fallback. This changes the route locked in the brief; the brief is updated once the 3D pipeline is proven.

### Ottie puppet, milestone 1 (branch feat/ottie-puppet)

- **Accepted (Din, 2026-10-19):** "idle approved, wave approved", after reviewing the live preview.

- **Art route changed twice, both with Din's go:** a first Codex parts sheet drifted off model (orange, mouse ears, tube body). A master pose (A) plus a matching parts sheet (B) fixed the face, but separately painted parts never met at the neck and shoulders; Din saw a floating head and detached hands. Final route: a front-facing master (C) with the head, arms and tail cut straight from it, and a Codex edit of C (D) that paints the body hidden underneath. The rest pose is C (mean difference 0.6/255). Five Codex images in total, each approved by Din.
- **Pipeline:** `brand/ottie/tools/` (see `brand/ottie/README.md`): layers, Blender rig with computed smooth weights and procedural eyes, Bezier key poses with per-joint overlap, a spring pass for secondary motion, contact shadows from extra alpha masks, WebP packing to budget, manifest with per-drawing eye anchors, openness, head angle and measured exit drawings.
- **Budget:** a 2x drawing costs about 10 to 16 KB in WebP, so idle is timed on fours (6 drawings a second) with 24 drawings; wave is on twos. Idle 241 KB (q30), wave 388 KB (q70).
- **Verified:** preview loads with no console errors and draws light and dark at real size and 2x with live pupils.
- **Second pass (Din: keep going):** idle now comes home to neutral at 2 s (clean exits at drawings 0, 13, 23) and the preview switches at once with a 3-tick crossfade when a clean exit is more than 0.5 s away; all states share one stage anchored at the rest ground point (the trimmed sheets differ in size, which would have made Ottie jump). Seam fixes found with 2x joint crops: the right arm's region overlapped the tail tip, the arm feather showed D's narrower torso outline, and D's keyed edge carried a grey fringe. Sheets now encode with cwebp (sharp YUV); idle still lands at q30 because 24 drawings fill 250 KB.
- **Verified:** clean-state rebuild (`brand/ottie/tools/build.sh` after deleting parts, layout, .blend, build and dist) ran end to end in about 2 minutes; idle 244 KB, wave 386 KB, total 630 KB; seam crops of shoulders, elbows, neck and tail on paper and charcoal show no seams; preview has no console errors.
- **Wave arm reattached (Din, after approving):** in the wave the raised arm read as detached from the body. The body's shoulders are now weighted up to 65 percent to the upper arms (fading over 130 px), so a raised arm pulls the shoulder fur into a continuous armpit, and the arm's cut edge (its underside when raised) is crisper with a darker band like the painted outline. Clean rebuild re-run.
- **Wave body and arm proportions (Din):** the shoulder pull bulged the torso side and the raised upper arm read thinner than the forearm. The pull now stops 45 px below the shoulder joint (cap only, 60 percent over 120 px), the chest holds only the very top of each arm, the wave no longer stretches the upper arm lengthwise, and the raised upper arm thickens 14 percent with forearms set not to inherit that scale. Wave sheet 399 KB (q70).
- **Wave elbow and waist (Din):** the 14 percent upper-arm thickening made the bent elbow bulge, and D's painted waist under the arms showed the torso curving in. The thickening is gone; the raised forearm and paw slim to 88 percent instead (C paints them hanging toward the viewer). `layers.py` straightens each torso side between rows 720 and 1040 by pushing only the outer fur (beyond 165 px from the centre line), which the arms cover at rest.
- **Wave arm as one arc (Din):** the arm still folded into an L at the elbow (60 to 70 degrees), which read as uneven. The raise is re-aimed with the upper arm on a diagonal and at most about 40 degrees at the elbow, the arms' joint weights blend over 46 px instead of 26, and the body layer gets fur under the arm tops and the chin (hidden at rest) so the overshoot no longer shows a notch at the shoulder.
- **Wave re-approved (Din, 2026-10-19):** "wave approved" after the arm fixes above. Milestone 1 stands Accepted with this version (commit 2934302).
- **Open:** idle q30 is slightly soft at 4x zoom (fewer idle drawings would buy quality); milestone 2.

### Ottie puppet route (Din)

- **Locked:** Ottie is built in Blender: layered painted parts (complete underneath, so nothing reveals a seam), mesh deformation with an armature so the fur bends instead of hinging, animation authored as curves with anticipation, overlap, follow-through and secondary motion, rendered to WebP sprite sheets, with live pupils and glint drawn in the browser from a per-frame eye manifest. Spec: `docs/design/ottie/BRIEF.md`.
- **Why:** the earlier cut-out spike looked cheap (rigid pasted-on arms, a metronome wave). Din ruled out third parties (Rive animators) and AI video (not reliable enough on a live site). Blender keeps the painted canonical look, is free, and its sprite-sheet output plays the same in every browser. A redrawn vector rig was the lighter alternative, but its quality ceiling is lower and it drifts from the brand art.
- **Gate:** no Ottie state ships until Din approves it side by side in the preview page. Idle and wave come first. If Ottie is not approved by launch, the site uses a still Ottie.
- **Next:** a separate session builds it from a `/goal` prompt, on branch `feat/ottie-puppet` in its own worktree. This session continues the site PRD and plan.

### Site brainstorm: direction and home page skeleton (Din and Claude)

The site PRD and plan are still being written; these are the decisions locked so far.

- **Purpose:** a portfolio for a US master's in data science or ML/data engineering (primary) and data engineer, then AI/LLM engineer roles. The ML and AI skill shows through the work itself, not through claims.
- **Home page (approach A, chosen over a chat-only site and a classic portfolio with a widget):** Ask Ottie is the hero (name, role line, suggested questions written for recruiters and admissions, Resume/Email/GitHub/LinkedIn visible on first paint), with real crawlable pages underneath. A chat-only page would be invisible to search, to `llms.txt` and to screen readers, and would lose readers who don't type.
- **Ask Ottie:** a RAG pipeline over Din's approved library, answered by Claude Haiku. One answer-provider interface with three backends: a fake (tests and CI), Claude Code on Din's membership (local development, terms to be checked first), the Anthropic API (staging and production). Budget: a $100 spend cap, rate limits and Turnstile. Answers in English, and in French when asked in French; the site itself stays English for v1.
- **Library:** sources are GitHub repos, resume, LinkedIn, the undergrad thesis, and an in-depth interview by a Claude agent. Nothing reaches Ottie without Din's sign-off; raw transcripts stay in `handbook`; a deny-list (visa status, finances, personal life) gets a polite decline. The interview question bank plus Din's approved answers doubles as the eval set.
- **Pushbacks Din accepted:** a brand-native "Look closer" lens intro instead of the React Bits Hyperspeed effect (heavy WebGL, delays the first 30 seconds, and its neon glow breaks the calm brand); React Bits is inspiration only, we write our own versions; one quiet motion budget (letter field, small teal click sparks, scroll reveals, Ottie); Ottie is a 2D cut-out puppet in the canonical style, not pixel art, and stays quiet while someone types or reads; writing lives at `dins.dev/writing`, not a `blog.` subdomain, so everything ranks for Din's name on one domain.
- **Content timing:** real projects (ML, pipelines, data science, each with a visual demo) and the interview come later. `passfx`, `claude-runner` and `claudehome` are placeholders until then. A content freeze around December 1 is proposed.
- **Routes and content model (section 1, locked):** `/`, `/work`, `/work/<project>` (with an "Ask Ottie about this project" bar that only searches that project), `/writing` and posts with RSS, `/about`, `/contact`, `/privacy`, a 404 with Ottie, plus the agreed SEO files. Typed content collections for projects, writing and the Ottie-only library; Ottie's corpus is the library plus the pages. Not in v1: a French site, comments, a newsletter, `/uses`.
- **Home page skeleton (Accepted by Din):** one visual family. Lens: the intro pulls the page into focus through Ottie's right lens, and a faint mono letter field resolves into real library words near the cursor (and sweeps while Ottie retrieves). Windows: projects on a scroll-pinned center stage, each tilting in and landing in focus with its demo inside a browser window. Paper: writing as floating cards that drift in and settle. Studio: About as a dark studio where a laptop unfolds, a terminal types `whoami`, and the camera dollies into the screen (CSS 3D first; a Blender-rendered frame sequence is an optional upgrade). Letter: contact as a sheet of paper that folds into an envelope, gets an Ottie wax seal and is carried off by Ottie.
- **Sketch:** `docs/design/sketches/home-sketch.html` (built by `build.py` from `home.template.html`, the real tokens and logo). A rough reference for layout and motion, not final design or copy.
- **Verification:** rendered with headless Chrome in light and dark at 1440 px, including forced scroll states for the stage, studio and letter. Limits: headless Chrome will not go below about 500 px wide, so phone layouts are unchecked, and it stops its clock mid-animation, so the full letter fold was only checked by Din live.

### Going public (Din)

- **Decision:** `dins.dev` is public from today instead of at launch, so progress is visible as it happens.
- **Before the first push:** a scan found account-security details and personal plans in the docs. Din had them moved to a new private `handbook` repo, and the unpushed history was rewritten so they never appear here. The public repo starts from one initial commit; the earlier local history is archived privately.
- **Repo setup:** squash merge only, branches deleted after merge, secret scanning and push protection on, Dependabot alerts on, and a ruleset on `main` (pull request required, no force push or deletion, linear history).

### Brand guide page (Claude)

- Built `brand/brand-guide.html` from `brand/tools/brand-guide.template.html` with `brand/tools/guide.py` (inlines tokens.css and theme-following marks, embeds every image) and published it privately: https://claude.ai/artifact/R8qLpurwsRu6PHmZzeDy2t. Sections: logo (with clear space, minimum sizes and don'ts), icons, social cards, color (live contrast ratios, click to copy), typography (live fluid scale), Ottie, voice, space and motion, files. The page runs on the dins tokens themselves.
- New defaults introduced and recorded in BRAND.md: clear space and minimum sizes.
- Pose sheet embedded as a 1400 px WebP (`brand/concepts/ottie-poses-web.webp`, 110 KB) instead of the 1.8 MB PNG. `brand/tools/sheet.py` now embeds PNG and WebP too.
- Verification: script syntax check; one Quick Look render (dark theme) looked right. Quick Look does not run scripts, so the swatches and spacing scale were not seen rendered; check them on the live page.

### Checklist sync

- Read the live checklist first, kept every tick Din had made, marked the finished brand work done and republished. Fixed the self-save baking the "Saving..." status into the page.

### Ottie pose sheet

- Din approved one Codex image (reference: canonical Ottie). Result `brand/concepts/ottie-poses.png`: five poses on white, on model (same glasses, proportions and style), each separable for cutouts. First try, no second image used. Din approved it. With this, every brand item is locked: type guidelines and scale, color, logo, style rules, tokens, icons, social cards and Ottie's poses.

### Social cards (Din)

- **Locked:** A (Paper) is the default card for every page; C (Paper with Ottie) for devlogs and game posts. B (Charcoal) dropped for thumbnail legibility. Why: recruiters and admissions see these in LinkedIn and email, where a clean title wins; Ottie belongs on the playful content. `brand/tools/sheet.py` now embeds SVGs into any template, which the cards page uses.

### Type scale, tokens and icons

- **Type scale locked (Din):** ten steps from Display (48 to 76 px) to Data (12.5 to 13 px), fluid between 375 and 1280 px, headings at weight 500 below the 600 wordmark, H4 in the sans, body capped at 66 characters. Rules added: curly quotes in display text, tabular digits. Specimen rows are static HTML because Quick Look does not run scripts.
- **Tokens (Claude):** `brand/tokens/tokens.json` plus generated `tokens.css`. Spacing, radius, layout and motion values are Claude's defaults, recorded in BRAND.md.
- **Icons (Claude):** `brand/tools/icons.py` rasterizes with cairosvg (needs Homebrew cairo; run with `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`). 16 px check, enlarged on light and dark tab colors: the solid tile reads as glasses; the earlier transparent, theme-following `favicon.svg` was about 4 px tall and faded on both, so `favicon.svg` is now the same solid tile. Din approved the solid-tile favicon.

### First commit (Din's go)

- First local commit of the fresh repo: brand files, tools and docs.

### Launch checklist (Claude)

- Published a private, self-saving checklist page of every task in order. It covers private tasks too, so its source and builder live in the private `handbook` repo.

### Apple and game conventions (Din)

- **Locked:** `dev.dins.<game>` bundle IDs, `support@dins.dev`, one game page template (landing, support, privacy, press kit), collect-nothing privacy by default, TestFlight-first release flow, and a first-paid-game checklist (Small Business Program, banking and tax forms, EU trader status, encryption flag). Monetization, age rating and countries are decided per game.

### SEO and analytics (Din)

- **Locked:** baseline built around ranking for Din's name (Person structured data with `sameAs` links), Search Console domain property plus Bing, branded social cards, `llms.txt`, Cloudflare Web Analytics instead of Google Analytics (no cookies, no banner), a free uptime monitor. No keyword strategy.

### Tracking and docs (Din)

- **Locked:** TASKS.md stays the single plan and board; GitHub Issues only for bugs, ideas and outside feedback; README in every repo; the ledger is the decision log; changelogs for games only; shared conventions live in `handbook`. Why: two to-do lists drift apart, and Din's global rules already make the docs the source of truth.
- **Added:** `README.md` with the lockup (light and dark via `<picture>`), contents, regeneration commands and license notes.

### Checks, CI and dependencies (Din)

- **Locked:** one `check.sh` shared by laptop and CI; pre-commit hooks with gitleaks (GitHub secret scanning does not cover private repos on the free plan); GitHub Actions; Cloudflare Git integration for previews (no Cloudflare token in GitHub); Renovate weekly; Unity tests local-only until a game nears release.

### Branching, PRs and commits (Din)

- **Locked:** trunk-based with short-lived branches, a PR for every change, squash merge, Conventional Commits, SemVer tags for games only. Why: PRs give checks, preview links and a written record that doubles as portfolio evidence. Branch protection comes from a GitHub ruleset now that the repo is public.

### Repo map (Din)

- **Locked:** `dins.dev` (made public right away on 2026-10-19, see below), `handbook` (private), `.github` (public), one private repo per new game, `template-site` and demos (public when ready). SuperOttie's code stays in Din's personal account, with a showcase page at `superottie.dins.dev` in this repo. Nothing is created on GitHub yet.

### Logo (Din and Claude)

- **Approved (Din):** wordmark, lens, lockup, app icon and favicon, then the Ottie seal. The brand files are complete.
- **Seal built:** Din approved one Codex image (`brand/concepts/ottie-seal-draft.png`, prompt beside it, references: canonical Ottie and the logo direction sheet). `brand/tools/seal.py` snaps it to five Ottie colors, keys out the background, traces it with vtracer, snaps the traced fills again and wraps the art in a ring drawn in code. Outputs: `seal-light.svg`, `seal-dark.svg`, `avatar.svg` (no ring, for platforms that crop to a circle). First fit clipped the ears and whiskers on the ring; the art is now scaled to 0.84 and dropped so the shoulders run off the bottom.
- **Tooling note:** vtracer segfaults on Python 3.14, so `seal.py` runs on Python 3.12 through uv.
- **Logo sheet:** `brand/tools/sheet.py` builds `brand/logo/logo-sheet.html` from `brand/tools/logo-sheet.template.html` with every SVG embedded, because the browser pane's local-file view cannot load linked images and the preview server list only reads the shared `~/Develop/.claude/launch.json` (outside this project, left untouched).
- **Verification:** seal and avatar rendered with Quick Look and checked by eye at 600, 300 and 48 px.

- **Wordmark spec (Din):** Fraunces weight 600, SOFT 50, picked from a 3 x 3 weight and softness sheet (`brand/logo/explorations/wordmark-variants.html`).
- **Built:** `brand/tools/wordmark.py final` shapes "dins." with HarfBuzz (kerning on) and writes true vector paths, so the SVGs need no font. Outputs in `brand/logo/`: wordmark (display and small masters), lens, lockup, each in light, dark and mono; app icon (paper lens on ink, 1024 canvas); favicon (follows the system theme). Fraunces is vendored in `brand/fonts/` with its OFL license.
- **Lens iteration:** a rim matching the Fraunces stem (0.24 of the lens diameter) read as two donuts and pushed the glint onto the rim. Final rim is 0.14 of the diameter (0.19 for the favicon so it survives 16 px), with the glint inside the right lens.
- **Verification:** rendered the logo sheet, app icon and favicon with Quick Look and checked them by eye. The favicon was only checked at 64 px so far; 16 px needs a check in a real browser tab.

### Typography (Din)

- **Fonts locked:** Fraunces (display), Instrument Sans (text and UI), JetBrains Mono (mono). Chosen from four systems compared side by side in light and dark (`brand/specimen/type-options.html`). Next: draw the wordmark from Fraunces outlines.

### Repo map and reopened items (Din)

- **SuperOttie stays personal** in Din's own GitHub account and is not part of dins. Every new game goes in the `dinsdev` org with a `dev.dins.<game>` bundle ID.
- **Repo map revised (still Proposed):** `dins.dev` private until launch, then public; demos public when ready.
- **Reopened:** Din considers the fonts, typography and the real logo not decided yet. The earlier type trio and the logo sheet are now candidates and direction, not final. Next: compare font options side by side, then draw the real logo in the chosen font.

### Fresh start

- **Din's call:** the earlier repo held website concepts that are not finalized, so it was renamed to `~/Develop/dins.dev-concepts` (kept intact, with its own git history) and this repo was started clean with only what was decided in the brainstorm. Carried over: the approved logo direction sheet and its prompt, the Ottie reference art, and the type specimen Din approved. Nothing was pushed anywhere.
- Note: the shared `~/Develop/.claude/launch.json` entry `dins-puppet-spike` still points at the old path and needs updating if that spike is ever previewed again.

### Brand and identity decisions (Din)

- **Brand:** "dins" for everything. dins.dev is the hub; games live on subdomains such as `superottie.dins.dev`.
- **Handles:** `dinsdev` on GitHub (organization), YouTube, TikTok and X. `dins` was taken on GitHub by an active personal account since 2011. `dinsdev` beat `dins-dev` because X and Instagram do not allow hyphens.
- **Platforms:** GitHub, YouTube, TikTok, X. LinkedIn stays personal.
- **Email addresses:** `din@`, `dinesh@` (alias), `hello@`, `support@`, catch-all, forwarded to Din's personal inbox. Sending through "Send mail as" on a free provider to start.
- **Domain:** buy `dins.dev` for 4 years on Cloudflare. Already have a Cloudflare account and an Apple Developer account.
- **Timeline:** applications open mid-January 2027, so the portfolio goes live by mid-December 2026.
- **Brand system:** logo system, palette, warm charcoal dark mode, type trio, Ottie rules and voice with tagline "Look closer." All locked; details in `docs/BRAND.md`.

### Why some brand calls went the way they did

- **Logo:** of four directions (`brand/concepts/logo-directions.png`), the wordmark matches the site's serif headline, the lens holds up at favicon size where the seal does not, and the seal keeps Ottie's charm for game and social use. The d-lens monogram read as a broken letter and was dropped.
- **Dark mode:** Din preferred a calm, Claude Code style dark over a glowing ink-teal look. The accent stays dins teal rather than Claude orange, so it borrows the feel without imitating Anthropic's brand.
- **Voice:** "I", never "we", because Din is one person and a fake "we" costs trust with admissions and clients.

### Verification

- Contrast ratios computed with the WCAG formula for every text color on its background (numbers in `docs/BRAND.md`). Amber fails as text on the light background (2.0:1), so it is decoration only there.
- `dins.dev` availability: the .dev registry RDAP returned 404 (not registered) on 2026-10-19.
