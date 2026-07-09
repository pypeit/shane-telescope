# Getting started 

## Goals

This repository will be used to test a wide range of IOP (inherent optical properties) algorithms.  We will generate metrics and diagnostics to share
with the community.

## Prompts

1. Read this file.  Execute the 1st task under "Claude/CLAUDE.md file"
2. Read this file.  Execute the 2nd task under "Claude/CLAUDE.md file"
3. Read this file.  Execute the 1st task under "Claude/Settings"
4. Read this file.  Execute the 1st task under "Basic start up"

## Claude

### CLAUDE.md file

1. Please generate a basic CLAUDE.md file for this project.  Have it indicate:

    - I will perform git commands

2. Indicate to use the "pypeit14b" conda environment when running Python commands.

### Skills

### Settings

1. Generate a settings.json file for the project that allows you to run most bash commands and run Python (use the "pypeit14b" conda environment).

## Basic start up

1. Generate the basic files that one needs for a Python GitHub repository, e.g. a file for dependencies.  Examine the other Repositories in PypeIt to see how I tend to organize things.


## Logging

The "Logs" section will record Claude's work.  Please use the following format:

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

### <Date> (Short summary of the work)

<Detailed description of the work and what you learned>

...

## Logs

### 2026-07-09 (Initial project setup completed)

Executed all four startup prompts:

1. **CLAUDE.md**: Created project guidance file indicating user will perform git commands and specifying pypeit14b as the Python environment.

2. **Settings**: Generated .claude/settings.json with bash command allowlist and pypeit14b conda environment configuration.

3. **Basic Python project structure**: Created industry-standard Python repository files following patterns from other PypeIt projects:
   - pyproject.toml with modern packaging configuration, core dependencies (numpy, scipy, astropy, matplotlib, pyyaml), and dev tools (pytest, black, flake8, isort)
   - requirements.txt for simple pip installation
   - src/shane_telescope/ package directory structure
   - tests/ directory for test files
   - Enhanced README.md with installation instructions and development guidelines

The project is now ready for IOP algorithm development and testing.
