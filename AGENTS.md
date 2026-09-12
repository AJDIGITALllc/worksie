# AGENTS.md

Operating instructions for AI coding agents working on this repository. These
apply to Codex, Claude Code, and any other agent that picks up this file.

## DOX framework

DOX is the AGENTS.md hierarchy installed for this repository. Agents must
follow the nearest applicable `AGENTS.md` plus every parent `AGENTS.md` above
it for all edits.

### Core contract

- `AGENTS.md` files are binding work contracts for their subtrees.
- Work products, source materials, instructions, records, assets, and durable
  docs must stay understandable from the nearest applicable `AGENTS.md` plus
  every parent `AGENTS.md` above it.
- Do not rely on memory for DOX. Re-read the applicable DOX chain in the
  current session before editing.
- If docs conflict, the closer doc controls local work details, but no child
  doc may weaken DOX or this root contract.

### Read before editing

1. Read this root `AGENTS.md`.
2. Identify every file or folder you expect to touch.
3. Walk from the repository root to each target path.
4. Read every `AGENTS.md` found along each route.
5. If a parent `AGENTS.md` lists a child `AGENTS.md` whose scope contains the
   path, read that child and continue from there.
6. Use the nearest `AGENTS.md` as the local contract and parent docs for
   repo-wide rules.

### Update after editing

Every meaningful change requires a DOX pass before the task is done.

Update the closest owning `AGENTS.md` when a change affects:

- purpose, scope, ownership, or responsibilities
- durable structure, contracts, workflows, or operating rules
- required inputs, outputs, permissions, constraints, side effects, or artifacts
- user preferences about behavior, communication, process, organization, or
  quality
- `AGENTS.md` creation, deletion, move, rename, or index contents

Update parent docs when parent-level structure, ownership, workflow, or child
index changes. Update child docs when parent changes alter local rules. Remove
stale or contradictory text immediately. Small edits that do not change
behavior or contracts may leave docs unchanged, but the DOX pass still must
happen.

### Hierarchy

- Root `AGENTS.md` is the DOX rail: project-wide instructions, global
  preferences, durable workflow rules, and the top-level Child DOX Index.
- Child `AGENTS.md` files own domain-specific instructions and their own Child
  DOX Index.
- Each parent explains what its direct children cover and what stays owned by
  the parent.
- The closer a doc is to the work, the more specific and practical it must be.

### Child doc shape

Create a child `AGENTS.md` when a folder becomes a durable boundary with its
own purpose, rules, responsibilities, workflow, materials, or quality
standards.

Use this default section order:

1. Purpose
2. Ownership
3. Local Contracts
4. Work Guidance
5. Verification
6. Child DOX Index

Work Guidance must reflect current standards or user instructions. If there
are no specific standards yet, leave it empty. Verification must reflect an
existing check. If no verification framework exists yet, leave it empty and
update it when one exists.

### Style

- Keep docs concise, current, and operational.
- Document stable contracts, not diary entries.
- Put broad rules in parent docs and concrete details in child docs.
- Prefer direct bullets with explicit names.
- Do not duplicate rules across many files unless each scope needs a local
  version.
- Delete stale notes instead of explaining history.
- Trim obvious statements, repeated rules, misplaced detail, and warnings for
  risks that no longer exist.

### Closeout

1. Re-check changed paths against the DOX chain.
2. Update nearest owning docs and any affected parents or children.
3. Refresh every affected Child DOX Index.
4. Remove stale or contradictory text.
5. Run existing verification when relevant.
6. Report any docs intentionally left unchanged and why.

### User preferences

- When the user requests a durable behavior change, record it in this root
  contract or in the relevant child `AGENTS.md`.

## Remote iPhone workflow

The repo owner often reviews work from an iPhone via GitHub mobile. They
**cannot** open files written to `/tmp`, the sandbox filesystem, or any local
path. Surface visual progress in places that render on mobile.

### Rules

1. **Never report a local screenshot as "evidence."** Saving a PNG to `/tmp`
   does not count as a verifiable result.
2. **For every UI change, post screenshots to the PR** so they render inline
   on GitHub mobile:
   - Capture with Playwright at desktop (`1440x1200`) **and** iPhone
     (`390x844`) viewports.
   - Commit the PNGs to `docs/screenshots/<pr-or-branch>/` on the
     branch and reference them in the PR body / comment using raw GitHub URLs
     or relative markdown links (`![desktop](docs/screenshots/.../desktop.png)`).
   - Include hover, error, and empty states when relevant to the change.
3. **Prefer the Vercel preview URL when possible.** Vercel auto-deploys a
   preview for every PR. Grab the preview URL from the PR's checks (the
   "Visit Preview" link on the Vercel check) and paste it into the PR
   description with the exact route to verify
   (e.g. `https://<branch>-worksie.vercel.app/dashboard`). Confirm the
   Vercel check is green before declaring the task done. If the preview
   build failed, fix it — do not ship.
4. **Non-UI progress goes in the PR description, not chat-only output.**
   Update the PR body with: what changed, what was tested, trimmed
   command output (pass/fail + key lines), and links to screenshots or the
   preview URL.
5. **Maintain a checked test-plan checklist in the PR body** so the user can
   track progress from the PR view on mobile.
6. **If something blocks posting to the PR** (auth, missing tool, network),
   say so explicitly. Do not fall back to local-only artifacts and call the
   task done.

### Required commands before declaring done

Run from the repository root:

```bash
pnpm lint
pnpm build
```

If the local `pnpm` shim is unavailable or broken, `npm run lint` and
`npm run build` are acceptable validation fallbacks because they delegate to
the same root Turbo scripts. Do not use npm to install dependencies.

If you changed UI, also run a Playwright screenshot pass at both viewports
and follow rule 2 above.

## Branch and PR conventions

- Develop on the branch the user specifies; never push to a different branch
  without explicit permission.
- Open PRs as **draft** unless told otherwise.
- Keep PR titles under 70 characters; put detail in the body.
- Use a HEREDOC for multi-line commit messages and PR bodies to preserve
  formatting.

## Project layout

- `apps/web/` — Next.js web admin app.
- `apps/mobile/` — Expo mobile field app.
- `packages/` — Shared config, domain, database, types, and UI packages.
- `docs/` — Project documentation, including screenshots for PRs.
- `prompts/` — Reusable prompt templates.
- `supabase/` — Supabase config and migrations.

## Safety

- Never commit `.env`, credentials, or service-account JSON.
- Never run `git push --force`, `git reset --hard`, or other destructive ops
  without explicit confirmation.
- Never skip hooks (`--no-verify`) unless the user explicitly asks.

## Child DOX Index

- `.github/AGENTS.md` - CI workflow and repository automation contracts.
- `apps/AGENTS.md` - application workspace contracts.
  - `apps/web/AGENTS.md` - Next.js admin app.
  - `apps/mobile/AGENTS.md` - Expo field app.
- `dataset/AGENTS.md` - training and evaluation schema materials.
- `docs/AGENTS.md` - canonical product, architecture, GTM, and review docs.
- `packages/AGENTS.md` - shared workspace package contracts.
  - `packages/db/AGENTS.md` - Drizzle schema, database client, and migration
    ownership details.
- `prompts/AGENTS.md` - reusable agent prompt templates.
- `scripts/AGENTS.md` - repository scripts.
  - `scripts/verify-rls/AGENTS.md` - RLS verification harness.
- `supabase/AGENTS.md` - Supabase config, migrations, metadata, and seed SQL.

Root continues to own workspace-level files including `package.json`,
`pnpm-workspace.yaml`, `pnpm-lock.yaml`, `turbo.json`, `tsconfig.base.json`,
`.editorconfig`, `.npmrc`, `.nvmrc`, `.gitignore`, `CLAUDE.md`, `README.md`,
and this `AGENTS.md`.

## Tool Prerequisites

- graphifyy v0.8.36+ must be installed before working on any repo: `uv tool install graphifyy` (preferred) or `pip install graphifyy`. Run `uv tool list | grep graphify` to verify. Used for /graphify codebase analysis and knowledge graph generation.

## Independent review and human-only merge

Authority: the owner-approved AJ Digital policy (2026-09-12), maintained in
`G:/AJ-INTERNAL/AJ-DIGITAL-VAULT/00-CONTROL/GOVERNANCE/GLOBAL_MERGE_CRITERIA.md`
under `HUMAN_APPROVAL_MATRIX.md`. This entry point implements that policy; it
does not establish a competing authority. Preserve stricter local controls.

- Codex-authored changes require independent review by Claude or CodeRabbit.
- Claude-authored changes require independent review by Codex or CodeRabbit.
- If both Codex and Claude authored a PR, CodeRabbit must independently review it.
- Authors may test and self-check, but cannot satisfy their own independent-review requirement.
- Review must cover the current changes. Changes after review require independent review of those changes.
- Pending, skipped, failed, rate-limited, summary-only or walkthrough-only reviews do not count as completed review.
- Address blocking findings and resolve their conversations before merge.
- Agents may mark validated draft PRs ready for review without separate operator approval after verifying the current head and required checks. Readiness is not merge approval.
- The human performs merge or squash merge after independent review and all required validation pass. Agents must not execute merges, enable auto-merge, enqueue a merge, or use another tool/agent to perform a merge.
- These permissions do not authorize deployment, provider activation, credential changes, client-data mutations, or other separately gated actions.

Record authoring agents separately from GitHub account names, the reviewed head
SHA, reviewer system, review outcome and evidence link. A green bot check or an
account name alone proves neither authorship nor independent review. Unknown
authorship or ambiguous review evidence blocks a merge recommendation. For other
authoring harnesses, obtain owner clarification of reviewer eligibility; do not
invent a self-review exemption. This is an instruction contract, not verified
technical enforcement. If canonical context is unavailable, retain these
restrictions and report the verification gap.


### Authorship declaration and review routing

Record one explicit PR-body declaration: `authoring-agent:codex`,
`authoring-agent:claude`, `authoring-agent:codex+claude`,
`authoring-agent:human`, or `authoring-agent:unknown`, with provenance linking
the authoring session and contributed changes. These declarations are claims
to verify, not authenticated attestations. Preserve earlier agent contributions
when humans edit; another contributing agent must update the declaration to the
union of contributors. Conflicting or missing provenance blocks completion.

CodeRabbit is the default reviewer. For Codex-only authorship Claude is a
permitted fallback; for Claude-only authorship Codex is permitted. Mixed
Codex/Claude authorship requires CodeRabbit. Human-only and other harness
authorship retain applicable local review rules; do not invent an exemption.
Unknown authorship blocks review completion until established.

After current-head validation, request review by marking the draft ready.
New commits invalidate recorded review coverage; confirm renewed coverage of
the current SHA. A dispatch is only `review_requested`, never completion.
Record `review_running`, `review_completed`, `review_valid_for_head`,
`review_blocked`, or `review_unavailable` from actual evidence. Cancelled,
timed-out, skipped, unavailable, pending, failed, rate-limited, summary-only and
walkthrough-only runs cannot
satisfy review. Record reviewer system, exact SHA, event URL/time, findings and
thread resolution. Generic green checks and editable PR metadata cannot prove
reviewer independence. No agent may merge or enable automatic merge.
