# dbskill

[简体中文](README.md) | English | [日本語](README.ja.md) | [한국어](README.ko.md) | [繁體中文](README.zh-TW.md)

> A Chinese AI Skills toolkit for entrepreneurs and content creators. Give your Agent a real business, content, or execution problem, and get a clear judgment plus the next action you can take.

[![Version](https://img.shields.io/badge/version-2.17.13-111111.svg)](VERSION)
[![Skills](https://img.shields.io/badge/Skills-29-111111.svg)](docs/新手入门.md#skill-全目录)
[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-111111.svg)](LICENSE)

**Supported in Doubao, WorkBuddy, Claude Code, Codex, and other Agents that support Skills.**

Created by [dontbesilent](https://x.com/dontbesilent), dbskill distills 4,176 structured knowledge atoms and 29 directly callable Skills from 16,152 public posts.

[Quick start](#quick-start) · [Install](#install) · [Capabilities](#capabilities) · [Full guide](docs/新手入门.md) · [Releases](https://github.com/dontbesilent2025/dbskill/releases)

![dbskill routing map](docs/skill-link-map.svg)

## What dbskill helps you solve

You do not need to learn a complex methodology first, or know which tool to invoke. Give `/dbs` your current business situation, material, decision, or blocker. It selects the relevant Skill from the conversation context.

| Situation | What you get |
| --- | --- |
| Customers say your offer is expensive | Business diagnosis, risks, and validation actions |
| You have a topic but cannot turn it into watchable content | Content direction, hooks, titles, and script improvements |
| You know what to do but cannot move forward | Analysis of the blocker and one concrete starting action |
| You keep facing similar decisions without accumulating experience | Decision records, patterns, and snapshots |
| Your drafts, topics, and cases are scattered | A maintainable content-asset project |

## Quick start

After installation, enter this in your Agent:

```text
/dbs I run coding classes for children. I have 40 paid students, but renewals are low.
Help me determine whether the issue is the product, pricing, or customer segment.
```

`/dbs` reads the current conversation and selects an appropriate path. Add new facts or feedback after a round, then call `/dbs` again to determine what to work on next.

When you already know the task, call a Skill directly:

```text
/dbs-diagnosis I offer home-organization consulting for mothers. Clients say it is expensive. What should I change?
/dbs-content I want to discuss “ordinary people should not rush into building a personal brand.” How can I turn this into content?
/dbs-hook Here are the first 20 seconds of my video script. Improve the opening: …
/dbs-benchmark I want to study enterprise-service content accounts. Which benchmarks should I research?
```

## Capabilities

| Goal | Main Skills | Typical output |
| --- | --- | --- |
| Evaluate a business, product, price, or customer | `/dbs-diagnosis` | Diagnosis, risks, validation plan |
| Find and study benchmarks | `/dbs-benchmark` | Benchmark shortlist and research framework |
| Find recurring solutions in structurally analogous historical cases | `/dbs-standard-answer` | Case matrix, conditional answer, and failure boundaries |
| Create topics, content, titles, and videos | `/dbs-content`, `/dbs-hook`, `/dbs-xhs-title` | Direction and publishable copy |
| Review resonance, logic, and reach | `/dbs-resonate`, `/dbs-script-flow`, `/dbs-spread` | Prioritized edits |
| Clarify concepts, goals, and questions | `/dbs-deconstruct`, `/dbs-goal`, `/dbs-good-question` | Testable definitions and goals |
| Work through procrastination and execution blocks | `/dbs-action`, `/dbs-slowisfast` | Blocker analysis and next action |
| Record and review long-term decisions | `/dbs-decision`, `/dbs-save`, `/dbs-restore`, `/dbs-report` | Local decision archive and reports |
| Build content assets and multi-Agent workflows | `/dbs-content-system`, `/dbs-agent-migration`, `/dbs-bridge` | Local project, topic map, and bridge plan |
| Turn a local folder into a knowledge base | `/dbs-knowledge` | Knowledge navigation, version rules, and ready-to-use prompts |
| Audit local Skill risks | `/dbs-skill-cleaner` | Risk report and confirmed isolation |

See the [full guide and Skill directory](docs/新手入门.md#skill-全目录) for all 29 Skills, examples, and workflows.

## Install

### Recommended: Claude Code, Doubao, WorkBuddy, Codex, and other Agents supporting Skills

Run in a terminal:

```bash
npx -y skills add dontbesilent2025/dbskill -g --all
```

Return to your Agent and enter `/dbs 新手入门` to begin.

### Claude Code marketplace

You can also install the complete toolkit through the Claude Code marketplace:

```bash
claude plugin marketplace add dontbesilent2025/dbskill
claude plugin install dbs@dontbesilent-skills
```

The `dbs` plugin includes all 29 public business Skills plus the `dbs-update` system entry. Claude Code namespaces plugin Skills: use `/dbs:dbs` for the main router and commands such as `/dbs:dbs-diagnosis` for a specific capability.

To install only one capability, choose its marketplace plugin, for example `claude plugin install dbs-diagnosis@dontbesilent-skills`.

![Claude Code installation demo](demo.gif)

### Update

Ask your current Agent:

```text
更新 dbskill
```

This syncs the official dbskill and does not modify records, reports, or decisions under `~/.dbs/`. See [GitHub Releases](https://github.com/dontbesilent2025/dbskill/releases) for changes.

## How it works

```text
A real task
   ↓
/dbs reads context and selects the current entry point
   ↓
One Skill produces a diagnosis, output, or record
   ↓
Add results and feedback, then decide the next step
```

## Knowledge base and local records

The repository includes 4,176 structured knowledge atoms, methodology documents organized by Skill, and a high-frequency concept glossary.

- Read the [atom library guide](知识库/原子库/README.md) for data scope and fields.
- Use `知识库/原子库/atoms.jsonl` to build your own RAG.
- Browse the [Skill knowledge packs](知识库/Skill知识包) for the methods.
- Use `/dbs-save`, `/dbs-restore`, and `/dbs-report` for work across conversations. Data stays locally in `~/.dbs/`.

![dbskill knowledge pipeline](docs/knowledge-pipeline.svg)

## Project structure

```text
dbskill/
├── skills/                  # 29 published Skills + 1 update entry
├── 知识库/                   # Knowledge atoms, methods, and glossary
├── docs/                    # Guide, diagrams, and demo assets
├── .claude-plugin/          # Claude Code marketplace definition
└── tools/                   # Build and maintenance scripts
```

Build distribution packages locally:

```bash
bash tools/build-skills.sh
```

Packages are created in `dist/skills/`. Local experimental Skills whose names contain `beta` are excluded.

## Author and support

Author: [@dontbesilent](https://x.com/dontbesilent) · [Xiaohongshu](https://xhslink.com/m/637xuspR4iI) · [Douyin](https://v.douyin.com/pRUDhpBqOrc/)

For paid Q&A support, scan the QR code or see the [group details](https://mp.weixin.qq.com/s/RpwNjMo4M_er4GOrfCYt1g).

![Paid Q&A group QR code](docs/paid-qa-group-qrcode.png)

## License

Licensed under [CC BY-NC 4.0](LICENSE).

- Personal use, study, research, and non-commercial projects are welcome.
- Please attribute the source when you publish derivative work.
- Commercial use requires separate authorization. Contact the author.
