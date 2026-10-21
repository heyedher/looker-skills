#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Validates plugin manifests and skills under plugins/ and experimental/."""

import glob
import json
import os
import re
import sys


REQUIRED_PLUGINS = [
    "looker-base",
    "looker-lookml-modeling",
    "looker-onboarding-migration",
    "looker-operations",
    "looker-apps-viz",
    "looker-analytics-agents",
]


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = []
    warnings = []

    # 1. Verify all 6 domain plugin directories and plugin.json manifests exist
    for p_name in REQUIRED_PLUGINS:
        p_json_path = os.path.join(repo_root, "plugins", p_name, "plugin.json")
        if not os.path.exists(p_json_path):
            errors.append(f"Missing plugin manifest: plugins/{p_name}/plugin.json")
            continue
        try:
            with open(p_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("name") != p_name:
                errors.append(f"plugins/{p_name}/plugin.json 'name' must be '{p_name}'.")
        except Exception as exc:
            errors.append(f"Invalid JSON in plugins/{p_name}/plugin.json: {exc}")

    # 2. Validate any migrated/created skills under plugins/*/skills/* and experimental/*
    skill_dirs = [
        d for d in (
            glob.glob(os.path.join(repo_root, "plugins", "*", "skills", "*"))
            + glob.glob(os.path.join(repo_root, "experimental", "*"))
        )
        if os.path.isdir(d)
    ]

    seen_names = {}
    for s_dir in sorted(skill_dirs):
        s_name = os.path.basename(s_dir)
        rel_dir = os.path.relpath(s_dir, repo_root)
        if s_name in seen_names:
            errors.append(f"Duplicate skill name '{s_name}' in {rel_dir} and {seen_names[s_name]}.")
        seen_names[s_name] = rel_dir

        skill_md = os.path.join(s_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            errors.append(f"{rel_dir}: Missing SKILL.md.")
            continue

        if os.path.exists(os.path.join(s_dir, "README.md")):
            warnings.append(f"{rel_dir}: Root README.md detected inside skill folder (move to references/guide.md).")

        with open(skill_md, "r", encoding="utf-8") as f:
            lines = f.readlines()
            content = "".join(lines)

        if len(lines) > 150:
            warnings.append(f"{rel_dir}/SKILL.md is {len(lines)} lines (recommended <= 150 lines).")

        fm_match = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
        if not fm_match:
            errors.append(f"{rel_dir}/SKILL.md: Missing YAML frontmatter.")
            continue

        fm = fm_match.group(1)
        for req_key in ["name:", "description:", "license:", "metadata:"]:
            if req_key not in fm:
                errors.append(f"{rel_dir}/SKILL.md: Missing required frontmatter field '{req_key}'.")

    for w in warnings:
        print(f"[WARNING] {w}")
    for e in errors:
        print(f"[ERROR] {e}", file=sys.stderr)

    if errors:
        print(f"Validation failed with {len(errors)} error(s) and {len(warnings)} warning(s).", file=sys.stderr)
        sys.exit(1)

    print(f"Validation passed ({len(REQUIRED_PLUGINS)} plugins verified, {len(skill_dirs)} migrated skills checked, {len(warnings)} warning(s)).")


if __name__ == "__main__":
    main()
