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

"""Generates multi-client marketplace manifests and refreshes flat .agents/skills/ symlinks."""

import argparse
import glob
import json
import os
import shutil
import sys


PLUGIN_ORDER = [
    "looker-base",
    "looker-lookml-modeling",
    "looker-onboarding-migration",
    "looker-operations",
    "looker-apps-viz",
    "looker-analytics-agents",
]

MARKETPLACE_TARGETS = [
    os.path.join(".claude-plugin", "marketplace.json"),
    os.path.join(".cursor-plugin", "marketplace.json"),
    os.path.join(".github", "plugin", "marketplace.json"),
]

MARKETPLACE_DESCRIPTION = (
    "Official Looker agentic skills organized into domain-specific plugins for "
    "LookML modeling, developer onboarding, operations, visualizations, and "
    "Conversational Analytics."
)


def build_marketplace_payload(repo_root):
    plugins_entries = []
    for plugin_name in PLUGIN_ORDER:
        manifest_path = os.path.join(repo_root, "plugins", plugin_name, "plugin.json")
        if not os.path.exists(manifest_path):
            print(f"[ERROR] Missing plugin manifest: plugins/{plugin_name}/plugin.json", file=sys.stderr)
            sys.exit(1)
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        plugins_entries.append({
            "name": manifest["name"],
            "description": manifest["description"],
            "source": f"./plugins/{plugin_name}",
        })

    return {
        "name": "looker-skills",
        "owner": {
            "name": "Google Looker",
            "url": "https://github.com/looker-open-source/looker-skills",
        },
        "metadata": {
            "description": MARKETPLACE_DESCRIPTION,
        },
        "plugins": plugins_entries,
    }


def compute_expected_symlinks(repo_root):
    """Maps skill_name -> relative symlink target from .agents/skills/<skill_name>."""
    expected = {}

    # 1. Canonical migrated skills inside plugins/<domain>/skills/<skill_name>
    for plugin_name in PLUGIN_ORDER:
        pattern = os.path.join(repo_root, "plugins", plugin_name, "skills", "*", "SKILL.md")
        for skill_md in sorted(glob.glob(pattern)):
            skill_dir = os.path.dirname(skill_md)
            skill_name = os.path.basename(skill_dir)
            expected[skill_name] = f"../../plugins/{plugin_name}/skills/{skill_name}"

    # 2. Transitional fallback for any legacy skills remaining in skills/<skill_name>
    legacy_pattern = os.path.join(repo_root, "skills", "*", "SKILL.md")
    for skill_md in sorted(glob.glob(legacy_pattern)):
        skill_dir = os.path.dirname(skill_md)
        skill_name = os.path.basename(skill_dir)
        if skill_name not in expected:
            expected[skill_name] = f"../../skills/{skill_name}"

    return expected


def main():
    parser = argparse.ArgumentParser(
        description="Build multi-client marketplace manifests and .agents/skills/ flat symlinks."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify manifests and symlinks are up to date without modifying files.",
    )
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    payload = build_marketplace_payload(repo_root)
    expected_json = json.dumps(payload, indent=2) + "\n"
    expected_symlinks = compute_expected_symlinks(repo_root)

    errors = []

    for rel_target in MARKETPLACE_TARGETS:
        abs_target = os.path.join(repo_root, rel_target)
        if args.check:
            if not os.path.exists(abs_target):
                errors.append(f"Missing marketplace manifest: {rel_target}")
            else:
                with open(abs_target, "r", encoding="utf-8") as f:
                    if f.read() != expected_json:
                        errors.append(f"Out-of-sync marketplace manifest: {rel_target}")
        else:
            os.makedirs(os.path.dirname(abs_target), exist_ok=True)
            with open(abs_target, "w", encoding="utf-8") as f:
                f.write(expected_json)
            print(f"Wrote: {rel_target}")

    agents_skills_dir = os.path.join(repo_root, ".agents", "skills")
    if args.check:
        if os.path.islink(agents_skills_dir) or not os.path.isdir(agents_skills_dir):
            errors.append(".agents/skills must be a directory containing flat skill symlinks.")
        else:
            existing_entries = sorted(os.listdir(agents_skills_dir))
            actual_map = {}
            for entry in existing_entries:
                if entry.startswith("."):
                    continue
                full_entry = os.path.join(agents_skills_dir, entry)
                if os.path.islink(full_entry):
                    actual_map[entry] = os.readlink(full_entry)
                else:
                    errors.append(f".agents/skills/{entry} is not a symlink.")
            if actual_map != expected_symlinks:
                errors.append(
                    ".agents/skills symlinks are out of sync with plugins/ and skills/ "
                    "(run 'python3 scripts/build_release.py')."
                )
    else:
        if os.path.islink(agents_skills_dir):
            os.unlink(agents_skills_dir)
        elif os.path.exists(agents_skills_dir) and not os.path.isdir(agents_skills_dir):
            os.remove(agents_skills_dir)
        os.makedirs(agents_skills_dir, exist_ok=True)

        for entry in os.listdir(agents_skills_dir):
            if entry.startswith("."):
                continue
            full_entry = os.path.join(agents_skills_dir, entry)
            if os.path.islink(full_entry) or os.path.isfile(full_entry):
                os.unlink(full_entry)
            elif os.path.isdir(full_entry):
                shutil.rmtree(full_entry)

        for skill_name, rel_dest in sorted(expected_symlinks.items()):
            link_path = os.path.join(agents_skills_dir, skill_name)
            os.symlink(rel_dest, link_path)

        print(f"Synced {len(expected_symlinks)} flat skill symlink(s) in .agents/skills/.")

    if errors:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(1)

    if args.check:
        print(
            f"Release packaging check passed ({len(MARKETPLACE_TARGETS)} manifests, "
            f"{len(expected_symlinks)} symlinks verified)."
        )


if __name__ == "__main__":
    main()
