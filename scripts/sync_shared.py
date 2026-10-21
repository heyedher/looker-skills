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

"""Synchronizes canonical files from _shared/ into skills declaring metadata.shared-refs."""

import argparse
import glob
import os
import re
import shutil
import sys


def parse_shared_refs(skill_md_path):
    with open(skill_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not match:
        return []
    frontmatter = match.group(1)
    ref_match = re.search(r"^\s*shared-refs:\s*(.+)$", frontmatter, re.MULTILINE)
    if not ref_match:
        return []
    raw_val = ref_match.group(1).strip().strip("'\"")
    return [tok.strip() for tok in raw_val.split() if tok.strip()]


def main():
    parser = argparse.ArgumentParser(description="Sync _shared/ assets into skill directories.")
    parser.add_argument("--check", action="store_true", help="Verify shared refs are in sync without modifying files.")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shared_refs_dir = os.path.join(repo_root, "_shared", "references")
    shared_scripts_dir = os.path.join(repo_root, "_shared", "scripts")

    skill_md_files = (
        glob.glob(os.path.join(repo_root, "plugins", "*", "skills", "*", "SKILL.md"))
        + glob.glob(os.path.join(repo_root, "experimental", "*", "SKILL.md"))
    )

    out_of_sync = []
    synced_count = 0

    for skill_md in sorted(skill_md_files):
        skill_dir = os.path.dirname(skill_md)
        refs = parse_shared_refs(skill_md)
        for ref_name in refs:
            src_md = os.path.join(shared_refs_dir, f"{ref_name}.md")
            src_sh = os.path.join(shared_scripts_dir, f"{ref_name}.sh")
            if os.path.exists(src_md):
                src_path = src_md
                dest_dir = os.path.join(skill_dir, "references")
                dest_path = os.path.join(dest_dir, f"{ref_name}.md")
            elif os.path.exists(src_sh):
                src_path = src_sh
                dest_dir = os.path.join(skill_dir, "scripts")
                dest_path = os.path.join(dest_dir, f"{ref_name}.sh")
            else:
                print(f"[ERROR] {skill_md}: shared-ref '{ref_name}' not found in _shared/.", file=sys.stderr)
                sys.exit(1)

            if args.check:
                if not os.path.exists(dest_path):
                    out_of_sync.append(dest_path)
                else:
                    with open(src_path, "rb") as f1, open(dest_path, "rb") as f2:
                        if f1.read() != f2.read():
                            out_of_sync.append(dest_path)
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src_path, dest_path)
                synced_count += 1
                print(f"Synced: {os.path.relpath(dest_path, repo_root)}")

    if args.check and out_of_sync:
        print("[ERROR] The following shared references are out of sync (run 'python3 scripts/sync_shared.py'):", file=sys.stderr)
        for p in out_of_sync:
            print(f"  - {os.path.relpath(p, repo_root)}", file=sys.stderr)
        sys.exit(1)

    print(f"Shared reference sync complete ({synced_count} files updated).")


if __name__ == "__main__":
    main()
