---
troy-doc: "architecture"
lang: "en"
version: "1.0"
updated: "2026-11-07"
status: "Approved by Troy for troy-init's trial (troy-pstack F06 design 11.4)."
mirror: "architecture.zh-CN.md"
---

# troy-mode-trial architecture

troy-mode-trial is a scratch project for trying troy-mode out. It counts the words of a text.

## 1. Background and constraints

- None beyond troy-mode's own rules.

## 2. Tech stack

| Part | Choice | Reason |
| --- | --- | --- |
| Language | Python 3.13 | troy-mode's Python pack. |

## 3. Modules

| Module | Owns | External interfaces | May depend on |
| --- | --- | --- | --- |
| counting | `src/troy_mode_trial/**`. Counts the words of a text. | `src/troy_mode_trial/__init__.py` | None |
