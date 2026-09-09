// The north: why a deliberation session was invoked and where it has to arrive.
//
// Structure lives in the engine: its shape, its presence in `STATUS`, its
// presence on both CLI-level error paths -- pinned below, core-scoped, and
// independent of any one domain. Its TEXT does not: it is the host-chosen
// profile's own, declared in `<skill>/profile.ts`'s `objective` field. This
// suite discovers every profile that declares one, pairs it with its sibling
// `SKILL.md`, and checks the pair agrees by text -- rather than naming one
// skill's stages, which is what let a second domain silently inherit the
// first domain's destination (change 11, "a north a second domain can hold").
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import test from 'node:test';

const ENGINE_PATH = path.resolve('.claude/skills/_core/deliberation/engine/cli.mjs');
const CORE_DIR = path.resolve('.claude/skills/_core/deliberation/engine');
const SKILLS_DIR = path.resolve('.claude/skills');
const engine = await readFile(ENGINE_PATH, 'utf8');

/** Extracts the `<key>: { ... },` block at exactly one-tab indentation -- the
 * shape every `profile.ts` in this repo uses for its top-level object fields.
 * Nested closers (stage objects, arrays) sit at two-or-more tabs, so the
 * first one-tab `},` after the opening line is the block's own close. */
function extractBlock(source, key) {
	const openMarker = `\n\t${key}: {`;
	const openIdx = source.indexOf(openMarker);
	if (openIdx === -1) return null;
	const blockStart = openIdx + 1;
	const closeIdx = source.indexOf('\n\t},', blockStart);
	if (closeIdx === -1) return null;
	return source.slice(blockStart, closeIdx);
}

function parseObjective(block) {
	const stages = [...block.matchAll(/stage:\s*"([^"]+)"/g)].map((m) => m[1]);
	const behindWhens = [...block.matchAll(/behindWhen:\s*"([^"]*(?:\\.[^"]*)*)"/g)].map((m) => m[1]);
	const arrivalMatch = block.match(/\n\t+arrival:\s*"([^"]*(?:\\.[^"]*)*)"/);
	// `humanStops` is a string ARRAY, not an object -- `extractBlock` looks for `{`,
	// so it is parsed directly here instead.
	const humanStopsMatch = block.match(/\n\t+humanStops:\s*\[([\s\S]*?)\n\t+\],/);
	const humanStops = humanStopsMatch ? [...humanStopsMatch[1].matchAll(/"([^"]*(?:\\.[^"]*)*)"/g)].map((m) => m[1]) : [];
	const entrances = [...block.matchAll(/arrivesAt:\s*"([^"]+)"/g)].map((m) => m[1]);
	return { stages, behindWhens, arrival: arrivalMatch ? arrivalMatch[1] : null, humanStops, entrances };
}

async function discoverPairs() {
	const entries = await readdir(SKILLS_DIR, { withFileTypes: true });
	const pairs = [];
	for (const entry of entries) {
		if (!entry.isDirectory() || entry.name === '_core') continue;
		const profilePath = path.join(SKILLS_DIR, entry.name, 'profile.ts');
		const skillPath = path.join(SKILLS_DIR, entry.name, 'SKILL.md');
		const profileSource = await readFile(profilePath, 'utf8').catch(() => null);
		if (profileSource === null) continue;
		const objectiveBlock = extractBlock(profileSource, 'objective');
		if (objectiveBlock === null) continue;
		const skillSource = await readFile(skillPath, 'utf8').catch(() => null);
		pairs.push({ skillName: entry.name, profileSource, objective: parseObjective(objectiveBlock), skillSource });
	}
	return pairs;
}

const pairs = await discoverPairs();
const norm = (text) => text.replace(/\s+/g, ' ').trim();
// A stage whose closing condition is a person's word, not a byte the engine can
// read -- the honest gap this project's own doctrine insists on naming rather
// than papering over.
const REFUSES_MEASUREMENT = /the user said so|nothing (?:here )?measures/i;

test('exactly two profiles declare a north (a third is a decision)', () => {
	assert.equal(pairs.length, 2, `expected 2 profiles declaring objective, found ${pairs.length}: ${pairs.map((p) => p.skillName).join(', ')}`);
});

test('every error path carries the north', () => {
	// A blocked session is exactly the one that has lost the purpose. Both of
	// the engine's two output paths are pinned, so a third added later has to
	// be a decision rather than a drift.
	const paths = [...engine.matchAll(/status: 'error', message: [^}]*}/g)].map((m) => m[0]);
	assert.equal(paths.length, 2, 'the engine has two error paths; that count is what this pins');
	for (const emitted of paths) {
		assert.match(emitted, /objective: domainProfileModule\.DOMAIN\.objective/, 'an error reaches a reader without the north');
	}
});

test('STATUS reports it above the inventory', () => {
	assert.match(engine, /operation: 'STATUS',\n\t\t\/\/[\s\S]{0,700}?objective: domainProfileModule\.DOMAIN\.objective,/);
});

test('C-1: no core file declares a north\'s text, only its structure', async () => {
	// The absence layer (design.md, Decision C, C-1): would have caught the
	// original defect regardless of what any domain called its stages, because
	// it checks for a STRING LITERAL assigned to these keys -- not the type's
	// own field names (`readonly purpose: string;` has no literal after the
	// colon, and is not a leak).
	const coreEntries = await readdir(CORE_DIR, { recursive: true, withFileTypes: true });
	const coreFiles = coreEntries.filter((e) => e.isFile() && (e.name.endsWith('.ts') || e.name.endsWith('.mjs')));
	assert.ok(coreFiles.length > 40, `expected the whole engine, scanned ${coreFiles.length}`);
	const leaks = [];
	for (const entry of coreFiles) {
		const file = path.join(entry.parentPath ?? entry.path, entry.name);
		const source = await readFile(file, 'utf8');
		const rel = path.relative(CORE_DIR, file);
		if (/OBJECTIVE_FLOW/.test(source)) leaks.push(`${rel} still declares OBJECTIVE_FLOW`);
		if (/(?:purpose|arrival|behindWhen):\s*['"]/.test(source)) leaks.push(`${rel} spells a purpose/arrival/behindWhen string literal`);
	}
	assert.deepEqual(leaks, [], 'the north is reached only via DOMAIN.objective, never declared inline in core');
});

for (const { skillName, objective, skillSource } of pairs) {
	test(`${skillName}: the profile declares a non-empty ordered north`, () => {
		assert.ok(objective.stages.length > 0, `${skillName} declares no stages`);
		assert.ok(objective.arrival, `${skillName} declares no arrival`);
		assert.ok(objective.humanStops.length >= 1, `${skillName} declares no humanStops entry`);
	});

	test(`${skillName}: at least one stage refuses to claim it can be measured`, () => {
		// The honest gap. If every stage pretended to be byte-decidable, an agent
		// could close all of them on its own word -- a failure this project has
		// already seen once.
		assert.ok(objective.behindWhens.some((text) => REFUSES_MEASUREMENT.test(text)),
			`${skillName} declares no stage whose behindWhen names an unmeasurable, human-only condition`);
	});

	test(`${skillName}: the doctrine states the same stages, in the same order`, () => {
		assert.ok(skillSource, `${skillName}/SKILL.md is missing`);
		const start = skillSource.indexOf('## The objective flow');
		assert.ok(start >= 0, `${skillName}/SKILL.md has no objective-flow section`);
		const arrivalIdx = skillSource.indexOf('**Arrival:**', start);
		assert.ok(arrivalIdx >= 0, `${skillName}/SKILL.md's objective-flow section has no **Arrival:** line`);
		const table = skillSource.slice(start, arrivalIdx);
		const rows = table.split('\n').filter((line) => line.startsWith('| `')).map((line) => line.split('`')[1]);
		assert.deepEqual(rows, objective.stages, `${skillName}'s doctrine table does not match its profile's declared stages`);
	});

	test(`${skillName}: the doctrine's arrival text matches the profile's, whitespace-normalized`, () => {
		const start = skillSource.indexOf('**Arrival:**');
		assert.ok(start >= 0, `${skillName}/SKILL.md has no **Arrival:** line`);
		const rest = skillSource.slice(start + '**Arrival:**'.length);
		const docArrival = rest.slice(0, rest.indexOf('\n\n')).trim();
		assert.equal(norm(docArrival).toLowerCase().replace(/[.]$/, ''), norm(objective.arrival).toLowerCase(),
			`${skillName}'s doctrine arrival text does not match its profile's arrival, after whitespace normalisation`);
	});
}

test('every declared entrance names a stage its own profile actually declares', () => {
	let entranceCount = 0;
	for (const { skillName, objective } of pairs) {
		for (const arrivesAt of objective.entrances) {
			entranceCount += 1;
			assert.ok(objective.stages.includes(arrivesAt), `${skillName} declares an entrance arriving at "${arrivesAt}", which is not one of its own declared stages`);
		}
	}
	// Global vacuity guard: if no profile declared an entrance at all, the loop
	// above never ran a single assertion, and a check that never ran is not a
	// pass.
	assert.ok(entranceCount >= 1, 'no profile declares an entrance at all -- this check would otherwise be vacuous');
});
