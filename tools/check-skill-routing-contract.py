#!/usr/bin/env python3
"""校验正式 Skill 的单任务编排与跨 Skill 交接契约。"""

import json
import re
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT_DIR / ".claude-plugin" / "marketplace.json"
DBS_SKILL_PATH = ROOT_DIR / "skills" / "dbs" / "SKILL.md"
OFFICIAL_NAMES_PATH = (
    ROOT_DIR / "skills" / "dbs" / "references" / "official-skill-names.txt"
)

ROUTING_CONTRACT_MARKER = "## 跨 Skill 交接契约"
COMPOSITION_MARKERS = (
    "## 模式 B：任务编排",
    "1 个主 Skill 和最多 2 个辅助 Skill",
    "scripts/list-official-skills.py",
    "references/composition-contract.md",
)
CONDITIONAL_NAVIGATION_MARKER = (
    "只有用户明确询问下一步，且当前环境已经安装 `/dbs` 时"
)

DIRECT_HANDOFF_PATTERNS = (
    re.compile(r"(路由到|转到|交给|衔接)\s*[`*]*(/dbs-[a-z0-9-]+)"),
    re.compile(r"建议(?:你)?(?:先)?(?:用|去)\s*[`*]*(/dbs-[a-z0-9-]+)"),
    re.compile(r"试试\s*[`*]*(/dbs-[a-z0-9-]+)"),
)


def main() -> None:
    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    formal_names = [plugin["name"] for plugin in marketplace.get("plugins", [])]
    errors: list[str] = []

    snapshot_names = [
        line.strip()
        for line in OFFICIAL_NAMES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    expected_snapshot_names = [name for name in formal_names if name != "dbs"]
    if snapshot_names != expected_snapshot_names:
        errors.append(
            "skills/dbs/references/official-skill-names.txt "
            "与 Marketplace 正式条目顺序或内容不一致"
        )

    dbs_text = DBS_SKILL_PATH.read_text(encoding="utf-8")
    if ROUTING_CONTRACT_MARKER not in dbs_text:
        errors.append("skills/dbs/SKILL.md 缺少「跨 Skill 交接契约」")
    for marker in COMPOSITION_MARKERS:
        if marker not in dbs_text:
            errors.append(f"skills/dbs/SKILL.md 缺少单任务编排标记：{marker}")
    if "## 模式 B：任务后导航" in dbs_text or "### 导航地图" in dbs_text:
        errors.append("skills/dbs/SKILL.md 仍含旧版任务后静态导航")

    for name in formal_names:
        skill_path = ROOT_DIR / "skills" / name / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"正式 Skill 缺少定义文件：skills/{name}/SKILL.md")
            continue

        text = skill_path.read_text(encoding="utf-8")
        if name != "dbs" and CONDITIONAL_NAVIGATION_MARKER not in text:
            errors.append(f"skills/{name}/SKILL.md 缺少条件式 /dbs 导航规则")

        if name == "dbs":
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in DIRECT_HANDOFF_PATTERNS:
                match = pattern.search(line)
                if match:
                    errors.append(
                        f"skills/{name}/SKILL.md:{line_number} "
                        f"直接指定了下一站 {match.group(2)}：{line.strip()}"
                    )
                    break

    save_text = (ROOT_DIR / "skills" / "dbs-save" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    if "只有用户已经明确选择下一个 Skill" not in save_text:
        errors.append("dbs-save 的 next_skill 字段缺少「用户明确选择」约束")

    restore_text = (ROOT_DIR / "skills" / "dbs-restore" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    if "用户说「就接着上次确认的下一步走」" not in restore_text:
        errors.append("dbs-restore 缺少用户明确确认 next_skill 后再接续的规则")

    guide_text = (ROOT_DIR / "docs" / "新手入门.md").read_text(encoding="utf-8")
    if "**常见衔接：**" in guide_text:
        errors.append("docs/新手入门.md 仍含直接指定下一站的「常见衔接」")
    repeated_guide_navigation = "**继续推进：** 完成本 Skill 后输入 `/dbs`。"
    if repeated_guide_navigation in guide_text:
        errors.append(
            "docs/新手入门.md 仍在每个 Skill 条目后重复动态导航提示"
        )
    shared_guide_navigation = (
        "完成任何 Skill 后，可以继续补充事实或直接说明下一步。"
    )
    if guide_text.count(shared_guide_navigation) != 1:
        errors.append("docs/新手入门.md 应且只能保留 1 处统一动态导航说明")

    readme_text = (ROOT_DIR / "README.md").read_text(encoding="utf-8")
    if "常见衔接方式" in readme_text:
        errors.append("README.md 仍把文档描述为「常见衔接方式」")

    route_map_text = (ROOT_DIR / "docs" / "skill-link-map.mmd").read_text(
        encoding="utf-8"
    )
    if "没有完成／有新反馈" not in route_map_text or "回到 /dbs" not in route_map_text:
        errors.append("docs/skill-link-map.mmd 未体现任务未完成或有新反馈时回到 /dbs")

    route_svg_text = (ROOT_DIR / "docs" / "skill-link-map-4x3.svg").read_text(
        encoding="utf-8"
    )
    view_box_match = re.search(r'viewBox="([^"]+)"', route_svg_text)
    if view_box_match is None:
        errors.append("docs/skill-link-map-4x3.svg 缺少 viewBox")
    else:
        _, _, width, height = map(float, view_box_match.group(1).split())
        if abs(width / height - 4 / 3) > 0.001:
            errors.append(
                "docs/skill-link-map-4x3.svg 画布比例为 "
                f"{width / height:.3f}，应为横版 4:3"
            )

    if errors:
        print("Skill 编排契约校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        sys.exit(1)

    leaf_count = len([name for name in formal_names if name != "dbs"])
    print(
        "Skill 编排契约校验通过："
        f"{len(formal_names)} 个正式 Skill，"
        f"{leaf_count} 个叶子 Skill 已使用条件式 /dbs 导航"
    )


if __name__ == "__main__":
    main()
