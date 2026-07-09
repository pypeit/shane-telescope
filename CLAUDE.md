# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

This repository is used to test a wide range of IOP (inherent optical
properties) algorithms. We generate metrics and diagnostics to share with the
community.

## Workflow conventions

- **Git is handled by the user.** I (the user) will perform all git commands —
  staging, committing, branching, pushing, tagging, etc. Do not run `git add`,
  `git commit`, `git push`, or other state-changing git commands unless I
  explicitly ask. Read-only git inspection (`git status`, `git log`, `git diff`)
  is fine.

## Environment

- Python code runs in the `pypeit14b` conda environment.
