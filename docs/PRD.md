# dins: Setup Requirements

Status: Draft from the 2026-10-19 brainstorm, for Din's review
Owner: Din

## 1. Purpose

Set up "dins" as a professional one-person studio before building anything on it: a brand, a domain, email, accounts, a development workflow and the business basics. Think of it as a startup built from scratch, at the scale of one person, with structure that never gets ahead of the actual work.

The website, the games and the client demos are planned separately once this foundation is in place.

## 2. Audiences

| Audience                                                                     | What they need from dins                                                 |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Master's admissions committees (primary, applications open mid-January 2027) | Credibility: who Din is, what Din has built, how Din works               |
| Hiring managers and recruiters                                               | The same, in about 30 seconds                                            |
| Clients (later)                                                              | Trust: sample sites, a clear way to get in touch, professional paperwork |
| Players (later)                                                              | Fun: a page per game, support and privacy pages for the App Store        |

## 3. Goals and success criteria

| Goal                                                       | How we know                                                                                                        |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| The portfolio is live at dins.dev in time for applications | Live by mid-December 2026, leaving a month of buffer before mid-January 2027                                       |
| Every public touchpoint looks like one brand               | Site, social profiles, game pages and email all follow `docs/BRAND.md`                                             |
| Din never loses access to anything                         | Every account has 2FA, saved recovery codes and a non-dins.dev recovery email                                      |
| Email from dins.dev reaches inboxes                        | SPF, DKIM and DMARC pass for mail sent as `din@dins.dev`                                                           |
| Work is reproducible and reviewable                        | Every repo has project docs, checks that run locally and in CI, and preview deploys                                |
| The setup stays proportionate                              | Nothing is built before it is needed (for example the business registration waits for the first client or revenue) |

## 4. Scope

### In scope

1. **Identity and accounts:** password manager, account security, consistent handles, a GitHub organization.
2. **Domain and DNS:** dins.dev on Cloudflare, DNS hygiene (DNSSEC, CAA, `security.txt`).
3. **Email:** addresses on dins.dev that forward to Din's personal inbox and can send from it.
4. **Brand system:** logo, color, type, mascot rules, voice. Locked in `docs/BRAND.md`.
5. **Dev workflow:** repo map, branching and PR flow, checks, issue tracking, docs conventions.
6. **SEO and analytics baseline:** search console, sitemaps, structured data, privacy-friendly analytics.
7. **Apple and games conventions:** bundle IDs, per-game support and privacy pages.
8. **Business basics (Ontario):** sole proprietorship, business name, bank account, bookkeeping, templates.

### Non-goals (for now)

- The website's content and design. That gets its own PRD once the foundation is done.
- Building or publishing games.
- Incorporating. A sole proprietorship comes first. Note: Apple organization accounts need a legal entity, so the App Store seller name stays Din's legal name until there is a corporation.
- Paid email, paid analytics or any other paid service before there is a real need.
- A LinkedIn company page. LinkedIn stays personal.

## 5. Acceptance criteria

Din accepts each area when:

- **Foundation:** the domain is registered with auto-renew; all accounts in the inventory have 2FA and saved recovery codes; handles are claimed; email forwarding and sending work from the personal inbox.
- **Brand:** SVG wordmark, lens and seal exist and match `docs/BRAND.md`; design tokens exist as a file the site can import.
- **Workflow:** the repo map is set up on GitHub, `main` is protected, and a test PR shows checks plus a preview deploy.
- **SEO baseline:** dins.dev is verified in Google Search Console and Bing Webmaster Tools, with a sitemap submitted.

## 6. Open questions

- Outgoing mail provider for "Send mail as" (free tier to start).
- Whether to use `@dins.dev` as a Bluesky handle.
- When to register the business name "dins" in Ontario (details in the private handbook).
