# Vibecoding Playbook (Codex Edition)

Welcome to the icaly vibecoding guide. Follow these principles to keep collaborative flow with
OpenAI Codex smooth and consistent.

## 1. Communication cadance

- Start every request with the desired outcome and any hard constraints (security, stack, platform).
- Mention which files you already touched or want Codex to avoid.
- If the task involves deployment or credentials, share redacted examples so Codex can model the
  structure without seeing secrets.

## 2. Coding rhythm

- Use small, reviewable steps. Ask Codex for a plan when the work spans several files or concerns.
- Prefer declarative asks (“create a Flask route that…”) over imperative ones (“write code that does
  step 1, step 2…”); it gives Codex room to propose safer or cleaner patterns.
- When tweaking generated code, describe the intent (“tighten CSP”, “add retry with jitter”) so
  Codex can reason about edge cases rather than just patching lines.

## 3. Security & quality baseline

- Enforce linting or formatting tools relevant to the stack before large contributions.
- Keep secrets out of the repo; point Codex at environment variables or secret managers instead.
- Ask for threat-model checks after feature work so the assistant revisits potential regressions.
- Treat dependencies explicitly. If Codex introduces new packages, confirm their licence and update
  lockfiles.

## 4. Feedback loop

- Highlight what worked (“The UID sanitiser looks good”) and what needs revision (“events stopped
  rendering”). Positive signal sharpens future iterations.
- Provide logs or stack traces inline when reporting bugs; it helps Codex zero in on the fix.
- Close the loop: once changes are validated, note the results so Codex can archive the mental
  context.

Stay curious, keep the vibe constructive, and let Codex handle the heavy lifting while you steer the
vision.
