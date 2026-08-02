---
date: 2026-08-02
type: process
scope: process
status: active
stance: monitor
delta: unchanged
conviction: high
next_trigger: weekly_update_generation
source_from: 투자 종목 주간 Consensus Tracking Rule.md; 변수 변화 추적 프롬프트_V1.md
tags:
  - "#System/Agent_Instructions"
  - "#Process/Consensus_Tracking"
---

# Consensus Tracking Agent Instructions

## Markdown Rules

Every Markdown file starts with YAML frontmatter. Use the repository YAML standard and populate only fields supported by the document.

## Weekly Update Workflow

For every `YYMMDD_섹터_update.md`, follow this sequence without exception.

1. Read `투자 종목 주간 Consensus Tracking Rule.md`, `변수 변화 추적 프롬프트_V1.md`, and `tag_rules.json` before analyzing or writing.
2. Read `G:\내 드라이브\2. Sector_Analysis\섹터\YYMMDD_섹터_consensus.md`, the relevant `G:\내 드라이브\2. Sector_Analysis\섹터\리포트\` TXT files, and `G:\내 드라이브\4. Market_Monitoring\Market Price\` CSV files.
3. Start from `templates/weekly_sector_update_template.md`. Do not replace, rename, reorder, or omit sections 1 through 5.
4. Add market data only in `#### 3-1. 주간 시황 및 가격 해석` under section 3. Market prices are supporting evidence, not the sole basis for the industry-stage decision.
5. Write only changes versus prior market expectations. Avoid report/news summaries, copied text, and unsupported facts.
6. Save the final file as `G:\내 드라이브\2. Sector_Analysis\섹터\YYMMDD_섹터_update.md` and record all source inputs in `source_from`.
7. Populate `tags` as a YAML list. Apply the sector's mandatory level-2 tag and `Update` level-3 tag from `tag_rules.json`. Because section 4 analyzes related companies, add `#Stocks/종목명` for each Korean company and `#Stocks/TICKER` for each U.S. company mentioned there.
8. Run `python validate_weekly_updates.py --date YYMMDD` after all sector updates are written. Fix every failure before staging, committing, or pushing.

## Git Gate

Weekly outputs are published through Google Drive synchronization and must not be staged from the Drive path. Use Git only for repository code, rules, templates, and configuration changes.
