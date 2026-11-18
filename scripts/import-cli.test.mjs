import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, copyFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { snapshotAt } from './diff-for-import.mjs';

test('import command entry points execute in paths containing spaces', () => {
  const directory = mkdtempSync(join(tmpdir(), 'catalogue CLI '));
  try {
    for (const name of ['diff-for-import.mjs', 'send-import.mjs']) {
      const target = join(directory, name);
      copyFileSync(new URL(name, import.meta.url), target);
      const args = name.startsWith('send') ? ['missing-input.json', 'result.json'] : [];
      const result = spawnSync(process.execPath, [target, ...args], { encoding: 'utf8', cwd: directory });
      assert.notEqual(result.status, 0, `${name} silently skipped execution`);
      assert.match(result.stderr, name.startsWith('send') ? /ENOENT/ : /Usage:/);
    }
  } finally { rmSync(directory, { recursive: true, force: true }); }
});

test('snapshotAt decodes its default repository path', () => {
  assert.ok(snapshotAt('HEAD').paints.length > 0);
});
