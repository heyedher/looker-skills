#!/usr/bin/env node
/**
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const fs = require('fs');
const path = require('path');
const diff = require('diff');
const prompts = require('prompts');
const pc = require('picocolors');

const args = process.argv.slice(2);
const overrideAll = args.includes('--override');

const repoRoot = path.resolve(__dirname, '..');
const pluginsRoot = path.resolve(repoRoot, 'plugins');
const legacySkillsRoot = path.resolve(repoRoot, 'skills');
const targetDir = path.resolve(process.cwd(), '.agents/skills');

async function getFiles(dir) {
  const dirents = await fs.promises.readdir(dir, { withFileTypes: true });
  const files = await Promise.all(dirents.map((dirent) => {
    const res = path.resolve(dir, dirent.name);
    return dirent.isDirectory() ? getFiles(res) : res;
  }));
  return Array.prototype.concat(...files);
}

function discoverSkillDirectories() {
  const discovered = new Map();

  // 1. Discover domain-scoped skills under plugins/<domain>/skills/<skill-name>
  if (fs.existsSync(pluginsRoot)) {
    for (const pluginDirent of fs.readdirSync(pluginsRoot, { withFileTypes: true })) {
      if (!pluginDirent.isDirectory()) continue;
      const pluginSkillsDir = path.join(pluginsRoot, pluginDirent.name, 'skills');
      if (!fs.existsSync(pluginSkillsDir)) continue;
      for (const skillDirent of fs.readdirSync(pluginSkillsDir, { withFileTypes: true })) {
        if (!skillDirent.isDirectory()) continue;
        const skillPath = path.join(pluginSkillsDir, skillDirent.name);
        if (fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
          discovered.set(skillDirent.name, skillPath);
        }
      }
    }
  }

  // 2. Fallback for any legacy unmigrated skills under skills/<skill-name>
  if (fs.existsSync(legacySkillsRoot)) {
    for (const skillDirent of fs.readdirSync(legacySkillsRoot, { withFileTypes: true })) {
      if (!skillDirent.isDirectory() || discovered.has(skillDirent.name)) continue;
      const skillPath = path.join(legacySkillsRoot, skillDirent.name);
      if (fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
        discovered.set(skillDirent.name, skillPath);
      }
    }
  }

  return discovered;
}

async function start() {
  const skillDirs = discoverSkillDirectories();
  if (skillDirs.size === 0) {
    console.error(pc.red(`Error: No skills found under ${pluginsRoot} or ${legacySkillsRoot}`));
    process.exit(1);
  }

  for (const [skillName, skillRoot] of skillDirs.entries()) {
    const allSkillFiles = await getFiles(skillRoot);

    for (const srcFile of allSkillFiles) {
      const relWithinSkill = path.relative(skillRoot, srcFile);
      const relativePath = path.join(skillName, relWithinSkill);
      const destFile = path.resolve(targetDir, relativePath);

      const destDir = path.dirname(destFile);
      if (!fs.existsSync(destDir)) {
        fs.mkdirSync(destDir, { recursive: true });
      }

      if (!fs.existsSync(destFile)) {
        console.log(pc.green(`Creating: .agents/skills/${relativePath}`));
        fs.copyFileSync(srcFile, destFile);
        continue;
      }

      const srcContent = fs.readFileSync(srcFile, 'utf8');
      const destContent = fs.readFileSync(destFile, 'utf8');

      if (srcContent === destContent) {
        console.log(pc.gray(`Skipped (identical): .agents/skills/${relativePath}`));
        continue;
      }

      if (overrideAll) {
        console.log(pc.yellow(`Overriding: .agents/skills/${relativePath}`));
        fs.copyFileSync(srcFile, destFile);
        continue;
      }

      console.log(pc.cyan(`\nDiff for .agents/skills/${relativePath}:`));
      const diffResult = diff.diffLines(destContent, srcContent);

      diffResult.forEach((part) => {
        const color = part.added ? pc.green :
                      part.removed ? pc.red : pc.gray;
        const prefix = part.added ? '+ ' :
                       part.removed ? '- ' : '  ';

        const lines = part.value.split('\n');
        if (lines[lines.length - 1] === '') lines.pop();

        lines.forEach(line => {
          console.log(color(`${prefix}${line}`));
        });
      });

      const response = await prompts({
        type: 'confirm',
        name: 'value',
        message: `Overwrite .agents/skills/${relativePath}?`,
        initial: false
      });

      if (response.value) {
        console.log(pc.yellow(`Overriding: .agents/skills/${relativePath}`));
        fs.copyFileSync(srcFile, destFile);
      } else {
        console.log(pc.gray(`Skipped: .agents/skills/${relativePath}`));
      }
    }
  }

  console.log(pc.green('\nDone copying skills!'));
}

start().catch(err => {
  console.error(pc.red('An error occurred:'), err);
  process.exit(1);
});
