"""Validate the fixed structure and required source metadata for weekly sector updates."""

import argparse
import json
import re
import sys
from pathlib import Path
from project_paths import sector_updates_dir


REQUIRED_HEADINGS = [
    "### 1. 실적 추정치 모니터링 결과",
    "### 2. 핵심 모니터링 항목",
    "### 3. 시장 해석",
    "#### 3-1. 주간 시황 및 가격 해석",
    "### 4. 관련 기업",
    "### 5. 한줄 결론",
]

TAG_RULES_PATH = Path("tag_rules.json")


def parse_frontmatter(text):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def parse_frontmatter_list(text, key):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return []
    list_match = re.search(
        rf"(?m)^{re.escape(key)}:\s*\r?\n((?:[ \t]+-\s+.+\r?\n?)+)",
        match.group(1),
    )
    if not list_match:
        return []
    return [
        value.strip().strip('"').strip("'")
        for value in re.findall(r"(?m)^[ \t]+-\s+(.+?)\s*$", list_match.group(1))
    ]


def validate_file(path, date, sector, tag_rules):
    errors = []
    expected_name = f"{date}_{sector}_update.md"
    if path.name != expected_name:
        errors.append(f"filename must be {expected_name}")

    text = path.read_text(encoding="utf-8").lstrip("\ufeff")
    frontmatter = parse_frontmatter(text)
    if frontmatter is None:
        errors.append("YAML frontmatter is missing")
    else:
        for field in ("date", "type", "scope", "sector", "source_from"):
            if not frontmatter.get(field):
                errors.append(f"frontmatter field '{field}' is missing")
        if frontmatter.get("type") != "update":
            errors.append("frontmatter type must be 'update'")
        if frontmatter.get("scope") != "sector":
            errors.append("frontmatter scope must be 'sector'")
        if frontmatter.get("sector") != sector:
            errors.append(f"frontmatter sector must be '{sector}'")
        sources = frontmatter.get("source_from", "")
        if "consensus" not in sources.lower():
            errors.append("source_from must include the consensus source")
        if "data/market" not in sources and "Market Price" not in sources:
            errors.append("source_from must include market-data sources")

    tags = parse_frontmatter_list(text, "tags")
    if not tags:
        errors.append("tags must be a YAML list")
    else:
        sector_rule = tag_rules.get(sector)
        if sector_rule is None:
            errors.append(f"tag rule is missing for sector '{sector}'")
        else:
            for required_tag in (sector_rule["level_2"], sector_rule["update"]):
                if required_tag not in tags:
                    errors.append(f"required tag is missing: {required_tag}")
        if not any(tag.startswith("#Stocks/") for tag in tags):
            errors.append("at least one related-company #Stocks/ tag is required")

    positions = []
    for heading in REQUIRED_HEADINGS:
        position = text.find(heading)
        if position == -1:
            errors.append(f"required heading is missing: {heading}")
        positions.append(position)
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        errors.append("required headings are not in the fixed order")

    if "### 3. 시장 해석" in text and "#### 3-1. 주간 시황 및 가격 해석" in text:
        if text.find("#### 3-1. 주간 시황 및 가격 해석") < text.find("### 3. 시장 해석"):
            errors.append("market-data subsection must be inside section 3")
    if "### 5. 한줄 결론" in text and not re.search(r">\s*\*\*.+\*\*", text):
        errors.append("section 5 must contain a bold blockquote conclusion")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate weekly sector update files before Git publishing.")
    parser.add_argument("--date", required=True, help="Report date in YYMMDD format.")
    parser.add_argument("--sectors", nargs="*", help="Optional sector names. Defaults to stocks.json sectors.")
    args = parser.parse_args()

    if not re.fullmatch(r"\d{6}", args.date):
        parser.error("--date must use YYMMDD format")

    if args.sectors:
        sectors = args.sectors
    else:
        with Path("stocks.json").open(encoding="utf-8") as file:
            sectors = list(json.load(file).keys())

    with TAG_RULES_PATH.open(encoding="utf-8") as file:
        tag_rules = json.load(file)["sector_tags"]

    failures = []
    for sector in sectors:
        path = sector_updates_dir(sector) / f"{args.date}_{sector}_update.md"
        if not path.exists():
            failures.append((path, ["file is missing"]))
            continue
        errors = validate_file(path, args.date, sector, tag_rules)
        if errors:
            failures.append((path, errors))

    if failures:
        print("Weekly update validation failed:")
        for path, errors in failures:
            for error in errors:
                print(f"- {path}: {error}")
        sys.exit(1)

    print(f"Validated {len(sectors)} weekly update files for {args.date}.")


if __name__ == "__main__":
    main()
