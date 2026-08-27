// Node-side parser for Pokémon Showdown data.
//
// Reads TS data files from a cloned Showdown repo, transpiles them
// in-memory with esbuild (TS→JS, format=esm), writes each to a temp
// .mjs file, then dynamically imports it. The resulting JS objects are
// dumped to a single ``parsed.json`` file that the Python normalizer
// consumes.
//
// This script is intentionally dependency-light: it uses the system
// esbuild binary via ``esbuild`` npm package if available, and falls
// back to executing ``esbuild`` from PATH if the package is not
// installed. Every path is provided via argv — nothing is hardcoded.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import os from 'node:os';

const [repoDir, outFile] = process.argv.slice(2);
if (!repoDir || !outFile) {
    console.error('usage: parse.mjs <repo-dir> <out-file>');
    process.exit(2);
}

const FILES = {
    pokedex: 'data/pokedex.ts',
    moves: 'data/moves.ts',
    abilities: 'data/abilities.ts',
    items: 'data/items.ts',
    natures: 'data/natures.ts',
    typechart: 'data/typechart.ts',
    learnsets: 'data/learnsets.ts',
    formatsData: 'data/formats-data.ts',
    rulesets: 'data/rulesets.ts',
    formats: 'config/formats.ts',
    // Champions mod (VGC-focused)
    champions_formatsData: 'data/mods/champions/formats-data.ts',
    champions_rulesets: 'data/mods/champions/rulesets.ts',
    champions_abilities: 'data/mods/champions/abilities.ts',
    champions_items: 'data/mods/champions/items.ts',
    champions_moves: 'data/mods/champions/moves.ts',
    champions_learnsets: 'data/mods/champions/learnsets.ts',
    championsregma_formatsData: 'data/mods/championsregma/formats-data.ts',
    championsregma_rulesets: 'data/mods/championsregma/rulesets.ts',
};

// Transpile TS → JS using the ``esbuild`` binary on PATH.
// We write the TS to a temp file (esbuild's stdin mode caps output at
// 1MB which is not enough for learnsets.ts) and let esbuild read it
// from disk, capturing stdout via a larger maxBuffer.
function transpileTs(tsSrc, tsPath) {
    const res = spawnSync(
        'esbuild',
        [`--format=esm`, `--target=node20`, tsPath],
        { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 },
    );
    if (res.status !== 0) {
        throw new Error(`esbuild failed: ${res.stderr}`);
    }
    return res.stdout;
}

// Rewrite bare imports of Showdown internals to stubs. Data files import
// TYPES only from ``../sim/*``; esbuild strips those. We defensively
// null-out any leftover ``import ... from '../sim/...';`` runtime
// imports so we never leave the sandbox.
function neuterImports(jsSrc) {
    return jsSrc.replace(
        /^import\s+.*?from\s+['"][^'"]*?sim\/[^'"]*?['"];?$/gm,
        '// [stripped runtime sim import]',
    );
}

const tmpDir = path.join(
    os.tmpdir(),
    `showdown_parse_${process.pid}_${Date.now()}`,
);
mkdirSync(tmpDir, { recursive: true });

const result = {};
const errors = {};

for (const [key, rel] of Object.entries(FILES)) {
    const abs = path.join(repoDir, rel);
    if (!existsSync(abs)) {
        result[key] = null;
        errors[key] = 'file not present';
        continue;
    }
    try {
        let js = transpileTs(readFileSync(abs, 'utf8'), abs);
        js = neuterImports(js);
        const outPath = path.join(tmpDir, `${key}.mjs`);
        writeFileSync(outPath, js);
        const mod = await import(pathToFileURL(outPath).href);
        // Each file exports exactly one const named after its category.
        // Pick the first non-default named export.
        const namedExport = Object.keys(mod).find((n) => n !== 'default');
        result[key] = mod[namedExport];
    } catch (exc) {
        result[key] = null;
        errors[key] = String(exc);
    }
}

writeFileSync(outFile, JSON.stringify({ result, errors }, null, 0));
console.log(`wrote ${outFile}`);
