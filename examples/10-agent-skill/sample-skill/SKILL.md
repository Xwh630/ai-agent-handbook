---
name: sample-skill
description: >
  A minimal, spec-compliant example skill used as a starting template.
  Use when someone needs a clean skeleton for authoring a new skill, or when
  demonstrating the SKILL.md format and its optional resources.
license: MIT
metadata:
  author: Xwh630
  version: "1.0"
---

# Sample Skill

A deliberately minimal template. Copy this directory, rename it, and replace
every field — then run the validator from `examples/10-agent-skill/` before
publishing.

## What this template demonstrates

- Required frontmatter fields (`name`, `description`)
- Optional fields (`license`, `metadata`)
- All three optional resource directories (`scripts/`, `references/`, `assets/`)
- A description that states **both** what it does and when to use it

## Workflow

1. Read `assets/template.md` for the output skeleton.
2. If the request involves counting or formatting, **run
   `scripts/count_words.py`** rather than doing it in your head — it is exact
   and costs no context.
3. Only consult `references/rules.md` when you hit an edge case.

## Edge cases

- Empty input → return an empty result, do not invent content.
- Input larger than the task needs → summarize rather than echoing it back.
