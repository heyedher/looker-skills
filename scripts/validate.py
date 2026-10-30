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

"""Validates plugin manifests, marketplace registries, flat symlinks, and skills."""

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

MARKETPLACE_MANIFESTS = [
    os.path.join(".claude-plugin", "marketplace.json"),
    os.path.join(".cursor-plugin", "marketplace.json"),
    os.path.join(".github", "plugin", "marketplace.json"),
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

    # 2. Verify multi-client marketplace manifests if present
    for rel_mp in MARKETPLACE_MANIFESTS:
        mp_path = os.path.join(repo_root, rel_mp)
        if not os.path.exists(mp_path):
            warnings.append(f"Missing marketplace manifest: {rel_mp} (run 'python3 scripts/build_release.py').")
            continue
        try:
            with open(mp_path, "r", encoding="utf-8") as f:
                mp_data = json.load(f)
            mp_plugins = mp_data.get("plugins", [])
            mp_names = [entry.get("name") for entry in mp_plugins]
            if mp_names != REQUIRED_PLUGINS:
                errors.append(f"{rel_mp}: 'plugins' list {mp_names} does not match {REQUIRED_PLUGINS}.")
            for entry in mp_plugins:
                expected_src = f"./plugins/{entry.get('name')}"
                if entry.get("source") != expected_src:
                    errors.append(f"{rel_mp}: plugin '{entry.get('name')}' source must be '{expected_src}'.")
        except Exception as exc:
            errors.append(f"Invalid JSON in {rel_mp}: {exc}")

    # 3. Verify .agents/skills symlinks resolve cleanly without broken targets
    agents_skills = os.path.join(repo_root, ".agents", "skills")
    if os.path.isdir(agents_skills) and not os.path.islink(agents_skills):
        for entry in sorted(os.listdir(agents_skills)):
            if entry.startswith("."):
                continue
            full_entry = os.path.join(agents_skills, entry)
            if not os.path.exists(full_entry):
                errors.append(f"Broken symlink in .agents/skills/{entry} -> {os.readlink(full_entry)}")

    # 4. Validate any migrated/created skills under plugins/*/skills/* and experimental/*
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
        for req_key in ["name", "description", "license", "metadata"]:
            if not re.search(rf"^\s*{req_key}\s*:", fm, re.MULTILINE):
                errors.append(f"{rel_dir}/SKILL.md: Missing required frontmatter field '{req_key}:'.")

    for w in warnings:
        print(f"[WARNING] {w}")
    for e in errors:
        print(f"[ERROR] {e}", file=sys.stderr)

    if errors:
        print(f"Validation failed with {len(errors)} error(s) and {len(warnings)} warning(s).", file=sys.stderr)
        sys.exit(1)

    print(
        f"Validation passed ({len(REQUIRED_PLUGINS)} plugins verified, "
        f"{len(skill_dirs)} migrated skills checked, {len(warnings)} warning(s))."
    )


if __name__ == "__main__":
    main()
