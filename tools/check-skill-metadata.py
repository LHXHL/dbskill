#!/usr/bin/env python3
"""校验正式 Skill 的 description 预算与本地 beta 的隐藏标记。"""

import json
import re
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT_DIR / "skills"
MARKETPLACE_PATH = ROOT_DIR / ".claude-plugin" / "marketplace.json"

SPEC_DESCRIPTION_MAX = 1024
PROJECT_DESCRIPTION_WARNING = 300
PROJECT_DESCRIPTION_MAX = 512
PROJECT_DESCRIPTION_TOTAL_MAX = 6000

# 超过项目单项预算时，必须在这里登记 Skill 名和具体理由。
DESCRIPTION_LENGTH_EXCEPTIONS: dict[str, str] = {}

USAGE_MARKERS = (
    "用户",
    "用于",
    "适用",
    "当",
    "需要",
    "要求",
    "希望",
    "提到",
    "请求",
    "use when",
)


def read_frontmatter(skill_path: Path) -> str:
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.DOTALL)
    if match is None:
        raise ValueError("缺少合法的 YAML frontmatter")
    return match.group(1)


def read_scalar(frontmatter: str, field: str) -> str:
    lines = frontmatter.splitlines()
    prefix = f"{field}:"

    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue

        value = line[len(prefix) :].strip()
        if value not in {"|", ">"}:
            return value.strip("\"'")

        content: list[str] = []
        for continuation in lines[index + 1 :]:
            if continuation and not continuation[0].isspace():
                break
            content.append(continuation[2:] if continuation.startswith("  ") else continuation)
        separator = "\n" if value == "|" else " "
        return separator.join(content).strip()

    return ""


def is_internal(frontmatter: str) -> bool:
    return bool(
        re.search(
            r"(?ms)^metadata:\s*\n"
            r"(?:(?:[ \t]+[^\n]*)\n)*?"
            r"^[ \t]+internal:\s*(?:true|['\"]true['\"])\s*$",
            frontmatter,
        )
    )


def main() -> None:
    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    formal_names = [plugin["name"] for plugin in marketplace.get("plugins", [])]
    errors: list[str] = []
    warnings: list[str] = []
    description_lengths: dict[str, int] = {}

    for name in formal_names:
        skill_path = SKILLS_DIR / name / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"正式 Skill 缺少定义文件：skills/{name}/SKILL.md")
            continue

        try:
            frontmatter = read_frontmatter(skill_path)
        except ValueError as error:
            errors.append(f"skills/{name}/SKILL.md：{error}")
            continue

        declared_name = read_scalar(frontmatter, "name")
        description = read_scalar(frontmatter, "description")
        length = len(description)
        description_lengths[name] = length

        if declared_name != name:
            errors.append(
                f"skills/{name}/SKILL.md 的 name 为 {declared_name!r}，应为 {name!r}"
            )
        if not description:
            errors.append(f"skills/{name}/SKILL.md 的 description 不能为空")
            continue
        if length > SPEC_DESCRIPTION_MAX:
            errors.append(
                f"skills/{name}/SKILL.md 的 description 为 {length} 个字符，"
                f"超过 Agent Skills 规范上限 {SPEC_DESCRIPTION_MAX}"
            )
        if length > PROJECT_DESCRIPTION_MAX:
            reason = DESCRIPTION_LENGTH_EXCEPTIONS.get(name, "").strip()
            if not reason:
                errors.append(
                    f"skills/{name}/SKILL.md 的 description 为 {length} 个字符，"
                    f"超过项目预算 {PROJECT_DESCRIPTION_MAX}，且未登记例外理由"
                )
        elif length > PROJECT_DESCRIPTION_WARNING:
            warnings.append(
                f"skills/{name}/SKILL.md 的 description 为 {length} 个字符，"
                f"超过建议值 {PROJECT_DESCRIPTION_WARNING}"
            )

        lowered = description.casefold()
        if not any(marker.casefold() in lowered for marker in USAGE_MARKERS):
            errors.append(
                f"skills/{name}/SKILL.md 的 description 缺少明确使用条件；"
                "应同时说明做什么和什么时候使用"
            )

    total_length = sum(description_lengths.values())
    if total_length > PROJECT_DESCRIPTION_TOTAL_MAX:
        errors.append(
            f"正式 Skill description 总量为 {total_length} 个字符，"
            f"超过项目预算 {PROJECT_DESCRIPTION_TOTAL_MAX}"
        )

    beta_paths = sorted(SKILLS_DIR.glob("*beta*/SKILL.md"))
    for skill_path in beta_paths:
        try:
            frontmatter = read_frontmatter(skill_path)
        except ValueError as error:
            errors.append(f"{skill_path.relative_to(ROOT_DIR)}：{error}")
            continue
        if not is_internal(frontmatter):
            errors.append(
                f"{skill_path.relative_to(ROOT_DIR)} 缺少 metadata.internal: true，"
                "可能被通用安装器公开发现"
            )

    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if errors:
        print("Skill 元数据校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        sys.exit(1)

    longest_name = max(description_lengths, key=description_lengths.get)
    print(
        "Skill 元数据校验通过："
        f"{len(description_lengths)} 个正式 Skill 的 description 共 "
        f"{total_length} 个字符，最长为 {longest_name} "
        f"（{description_lengths[longest_name]} 个字符）；"
        f"{len(beta_paths)} 个 beta Skill 已标记为 internal"
    )


if __name__ == "__main__":
    main()
