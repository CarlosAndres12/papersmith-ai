// Phase 4.1 (change 8): the change header is its OWN resolved block span,
// gated on `profile.artifact.changeHeader` -- never a sidecar-only field,
// never an invariant exemption. `proposal-deliberation` declares none, so
// most scenarios here spawn a FRESH process with a profile that DOES declare
// one (the same technique `proposal-deliberation-sidecar-root-routing.test.mjs`
// and `proposal-deliberation-required-sources.test.mjs` already established:
// `domain-profile.ts` reads `DELIBERATION_DOMAIN_PROFILE` once per process).
import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { mkdtemp, mkdir, readFile, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { promisify } from 'node:util';
import { pathToFileURL } from 'node:url';

const execFileAsync = promisify(execFile);
const repoRoot = process.cwd();
const engineDir = path.join(repoRoot, '.claude/skills/_core/deliberation/engine');
const piRoot = '/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent';

const MARKER = '<!-- proposal-workspace:artifact:v1 -->\n';

// Declares `artifact.changeHeader` (heading "Changes", a two-field What/Why render) and a
// `preservation.extractAtoms` that recognizes any `\word`-shaped macro token -- self-contained
// domain knowledge, exactly parallel to how `preservation-math.ts` hardcodes its own canonical
// notation, with no engine-level file I/O (see `domain-profile.ts`'s `sourceAuthority` doc
// comment for the same reasoning applied to change 9).
const CUSTOM_PROFILE = `import type { DeliberationDomainProfile } from "${path.join(engineDir, 'domain-profile.js')}";
export const profile: DeliberationDomainProfile = {
	deriveBase: "base.md",
	baseLabel: "base",
	baseLabelLong: "base document",
	exampleSlug: "example-slug-r01",
	names: ["TESTDOMAIN"],
	proseReferencePattern: "\\\\(Ec\\\\. ([0-9]+)\\\\)",
	proseReferenceText: (value) => \`(Ec. \${value})\`,
	vocabulary: {
		conceptualTerms: [],
		expertPattern: "x",
		displayNounPattern: "x",
		displayNounStripPattern: "x",
		subjectPattern: "x",
		subjectTerms: [],
		subjectLocusDescription: "x",
		subjectEvidenceLabel: "x",
	},
	artifact: {
		directory: "proposals",
		stem: "research-concept",
		revisionPattern: "r",
		revisionLabel: (ordinal) => \`r\${String(ordinal).padStart(2, "0")}\`,
		sidecarRoot: ".other-deliberation",
		marker: ${JSON.stringify(MARKER)},
		changeHeader: {
			heading: "Changes",
			render: (s) => \`## Changes\\n\\n**What:** \${s.what}\\n\\n**Why:** \${s.why}\\n\\n\`,
		},
	},
	preservation: {
		extractAtoms: (source) => {
			const map = new Map();
			for (const m of source.matchAll(/\\\\[A-Za-z]+/g)) map.set(m[0], { id: m[0], kind: 'macro', text: m[0] });
			return map;
		},
		violations: () => [],
	},
	references: { declares: () => [], cites: () => [] },
	sources: [],
};
`;

function harness(body) {
	return `import path from 'node:path';
import { pathToFileURL } from 'node:url';
const piRoot = ${JSON.stringify(piRoot)};
const { createJiti } = await import(pathToFileURL(path.join(piRoot, 'node_modules/jiti/lib/jiti.mjs')).href);
const jiti = createJiti(import.meta.url, { alias: {
	'@earendil-works/pi-coding-agent': path.join(piRoot, 'dist/index.js'),
	'@earendil-works/pi-ai': path.join(piRoot, 'node_modules/@earendil-works/pi-ai/dist/index.js'),
	typebox: path.join(piRoot, 'node_modules/typebox/build/index.mjs'),
} });
const workspaceModule = await jiti.import(process.env.PROPOSAL_WORKSPACE_MODULE);
const v2 = await jiti.import(process.env.EXPORTS_MODULE);
const { mkdir, writeFile, readFile } = await import('node:fs/promises');
const root = process.env.PROJECT_ROOT;
const proposals = path.join(root, 'proposals');
await mkdir(proposals, { recursive: true });
${body}
`;
}

async function run(t, body, extraProfileSuffix = '') {
	const projectRoot = await mkdtemp(path.join(os.tmpdir(), 'pp-change-header-'));
	const profilePath = path.join(projectRoot, 'profile.ts');
	const harnessPath = path.join(projectRoot, 'harness.mjs');
	await writeFile(profilePath, CUSTOM_PROFILE + extraProfileSuffix, 'utf8');
	await writeFile(harnessPath, harness(body), 'utf8');
	const env = {
		...process.env,
		DELIBERATION_DOMAIN_PROFILE: profilePath,
		PROPOSAL_WORKSPACE_MODULE: path.join(engineDir, 'proposal-workspace.ts'),
		EXPORTS_MODULE: path.join(engineDir, 'exports.ts'),
		PROJECT_ROOT: projectRoot,
	};
	const { stdout } = await execFileAsync('node', [harnessPath], { env });
	return JSON.parse(stdout.trim().split('\n').pop());
}

const HEADER_BLOCK = '## Changes\n\n**What:** Initial revision.\n\n**Why:** First published version.\n';
const TARGET_BLOCK = '## Target Section\n\nOriginal content for the target section.\n';
const SEED_MARKDOWN = `# Test Document\n\n${HEADER_BLOCK}\n${TARGET_BLOCK}`;

test('4.1.1 CREATE_SUCCESSOR omitting changeSummary is refused CHANGE_SUMMARY_REQUIRED, no successor published', async (t) => {
	const result = await run(t, `
await writeFile(path.join(proposals, 'research-concept-r01.md'), ${JSON.stringify(MARKER)} + ${JSON.stringify(SEED_MARKDOWN)});
const guard = workspaceModule.createDocumentOperationGuard(root);
const workspace = workspaceModule.createProposalWorkspaceTool(root, { operationGuard: guard });
const adapter = new v2.ProposalWorkspaceAdapter(root, guard, workspace, () => 'change-header-required');
const planner = { async plan(input) { return { actions: [{ kind: 'replace', targetEntryId: input.target.entryId, replacementText: '## Target Section\\n\\nUpdated content.\\n' }], unresolvedQuestions: [] }; } };
const orchestrator = new v2.ProposalDeliberationOrchestrator(root, adapter, undefined, planner);
const result = await orchestrator.execute({ operation: 'CREATE_SUCCESSOR', sourceFilename: 'research-concept-r01.md', instruction: 'Modifica la sección Target Section.' });
let r02Exists = true;
try { await readFile(path.join(proposals, 'research-concept-r02.md')); } catch { r02Exists = false; }
console.log(JSON.stringify({ status: result.status, reason: result.reason, r02Exists }));
`);
	assert.equal(result.status, 'blocked');
	assert.equal(result.reason, 'CHANGE_SUMMARY_REQUIRED');
	assert.equal(result.r02Exists, false, 'no successor may be published when changeSummary is required and absent');
});

test('4.1.2/4.1.3 a present changeSummary publishes, the header is its own resolved block span, and blast-radius consumers all recount correctly', async (t) => {
	const result = await run(t, `
await writeFile(path.join(proposals, 'research-concept-r01.md'), ${JSON.stringify(MARKER)} + ${JSON.stringify(SEED_MARKDOWN)});
const guard = workspaceModule.createDocumentOperationGuard(root);
const workspace = workspaceModule.createProposalWorkspaceTool(root, { operationGuard: guard });
const adapter = new v2.ProposalWorkspaceAdapter(root, guard, workspace, () => 'change-header-publish');
const planner = { async plan(input) { return { actions: [{ kind: 'replace', targetEntryId: input.target.entryId, replacementText: '## Target Section\\n\\nUpdated content for the target section.\\n' }], unresolvedQuestions: [] }; } };
const orchestrator = new v2.ProposalDeliberationOrchestrator(root, adapter, undefined, planner);
const changeSummary = { what: 'Updated target section.', why: 'Testing change header.' };
const request = { operation: 'CREATE_SUCCESSOR', sourceFilename: 'research-concept-r01.md', instruction: 'Modifica la sección Target Section.', changeSummary };
const preview = await orchestrator.execute(request);

// Blast radius 4.1.11 (operation-spec.ts): successorTargetCount now accounts for the header as
// an ADDITIONAL resolved target -- by construction, since publish() appended it to
// plan.resolvedTargets BEFORE resolveEffectiveOperationProfile ever ran.
const effectiveProfile = v2.resolveEffectiveOperationProfile({ intent: 'MODIFY', cleanupLevel: 'NONE', successorCompositeTarget: true, successorTargetCount: preview.plan.resolvedTargets.length });

// Blast radius 4.1.12 (growth-threshold.ts): the advisory must NOT count the header as an
// approved section. Recompute the header-EXCLUDED verdict directly from the byte spans
// preview.compiled already resolved for BOTH loci (never a separate, re-materialized state
// load -- composite entries are never persisted back to a derived-state cache) and prove
// growthAdvisory matches it exactly, never the header-INCLUDED byte count.
const headerEntryId = preview.plan.resolvedTargets[preview.plan.resolvedTargets.length - 1];
const targetEntryId = preview.plan.resolvedTargets.find((id) => id !== headerEntryId);
const targetPatch = preview.compiled.patches.find((p) => p.selector.entryId === targetEntryId);
const headerPatch = preview.compiled.patches.find((p) => p.selector.entryId === headerEntryId);
const targetBytes = targetPatch.selector.endByte - targetPatch.selector.startByte;
const headerBytes = headerPatch.selector.endByte - headerPatch.selector.startByte;
const r01Before = await readFile(path.join(proposals, 'research-concept-r01.md'));
const documentBytes = r01Before.length;
const excludeHeaderVerdict = v2.evaluateSuccessorGrowthThreshold({ approvedSectionCount: 1, approvedBytes: targetBytes, documentBytes });

const published = await orchestrator.execute({ ...request, acceptSuccessor: true, successorAcceptanceToken: preview.acceptanceToken });
const r01 = (await readFile(path.join(proposals, 'research-concept-r01.md'))).toString('utf8');
const r02 = (await readFile(path.join(proposals, 'research-concept-r02.md'))).toString('utf8');
console.log(JSON.stringify({
	previewStatus: preview.status,
	previewResolvedTargetsLength: preview.plan.resolvedTargets.length,
	previewGrowthAdvisory: preview.growthAdvisory,
	excludeHeaderVerdict,
	headerBytesPositive: headerBytes > 0,
	effectiveMaxModelCalls: effectiveProfile.maxModelCalls,
	effectiveMaxPatchCount: effectiveProfile.maxPatchCount,
	publishedStatus: published.status,
	compiledPatchesLength: published.compiled.patches.length,
	// Blast radius 4.1.13 (successor-acceptance-registry.ts): compositeTargetIds is the same
	// preview.plan.resolvedTargets array threaded straight into the acceptance token.
	resolvedEntryIdsLength: published.receipt.resolvedEntryIds.length,
	resolvedEntryIdsIncludesHeader: published.receipt.resolvedEntryIds.includes(headerEntryId),
	receiptChangeSummary: published.receipt.changeSummary,
	titlePreserved: r01.startsWith(${JSON.stringify(MARKER)} + '# Test Document') && r02.includes('# Test Document'),
	r02HasNewHeader: r02.includes('**Why:** Testing change header.'),
	r02HasOldHeader: r02.includes('**Why:** First published version.'),
	r02HasNewTarget: r02.includes('Updated content for the target section.'),
}));
`);
	assert.equal(result.previewStatus, 'awaiting_acceptance');
	assert.equal(result.previewResolvedTargetsLength, 2, 'the header is one MORE resolved target alongside the real one');
	assert.equal(result.headerBytesPositive, true, 'sanity: the header locus must actually contribute bytes, or excluding it proves nothing');
	assert.deepEqual(result.previewGrowthAdvisory, result.excludeHeaderVerdict, 'growthAdvisory must be computed WITHOUT the header, never with it');
	assert.equal(result.effectiveMaxModelCalls, 2, 'operation-spec.ts must account for the header as an additional resolved target');
	assert.equal(result.effectiveMaxPatchCount, 2);
	assert.equal(result.publishedStatus, 'published');
	assert.equal(result.compiledPatchesLength, 2);
	assert.equal(result.resolvedEntryIdsLength, 2, 'the receipt resolvedEntryIds must recount with the extra header block');
	assert.equal(result.resolvedEntryIdsIncludesHeader, true);
	assert.deepEqual(result.receiptChangeSummary, { what: 'Updated target section.', why: 'Testing change header.' });
	assert.equal(result.titlePreserved, true, 'the byte-preservation invariant: bytes outside both resolved loci stay identical');
	assert.equal(result.r02HasNewHeader, true, 'the header locus was replaced with the new changeSummary');
	assert.equal(result.r02HasOldHeader, false);
	assert.equal(result.r02HasNewTarget, true);
});

test('4.1.5 a \\command-shaped macro token inside a previous header, once replaced, registers as a lost preservation atom', async (t) => {
	const seedWithMacro = `# Test Document\n\n## Changes\n\n**What:** Initial revision.\n\n**Why:** Uses \\legacyflag notation.\n\n${TARGET_BLOCK}`;
	const result = await run(t, `
await writeFile(path.join(proposals, 'research-concept-r01.md'), ${JSON.stringify(MARKER)} + ${JSON.stringify(seedWithMacro)});
const guard = workspaceModule.createDocumentOperationGuard(root);
const workspace = workspaceModule.createProposalWorkspaceTool(root, { operationGuard: guard });
const adapter = new v2.ProposalWorkspaceAdapter(root, guard, workspace, () => 'change-header-macro-loss');
const planner = { async plan(input) { return { actions: [{ kind: 'replace', targetEntryId: input.target.entryId, replacementText: '## Target Section\\n\\nUpdated content.\\n' }], unresolvedQuestions: [] }; } };
const orchestrator = new v2.ProposalDeliberationOrchestrator(root, adapter, undefined, planner);
const changeSummary = { what: 'Updated target section.', why: 'No macro reference this time.' };
const request = { operation: 'CREATE_SUCCESSOR', sourceFilename: 'research-concept-r01.md', instruction: 'Modifica la sección Target Section.', changeSummary };
const preview = await orchestrator.execute(request);
const lostIds = (preview.preservationDelta?.lost ?? []).map((atom) => atom.id);
const blockedWithoutAck = await orchestrator.execute({ ...request, acceptSuccessor: true, successorAcceptanceToken: preview.acceptanceToken });
console.log(JSON.stringify({ previewStatus: preview.status, lostIds, blockedWithoutAckStatus: 'unused', blockedReason: blockedWithoutAck.reason }));
`);
	assert.equal(result.previewStatus, 'awaiting_acceptance');
	assert.ok(result.lostIds.includes('\\legacyflag'), `expected \\legacyflag to register as a lost preservation atom, got ${JSON.stringify(result.lostIds)}`);
	assert.equal(result.blockedReason, 'MATH_REMOVALS_NOT_ACKNOWLEDGED', 'an unacknowledged lost header macro must still block accept, exactly like any other lost atom');
});

test('4.1.5b acknowledging the lost header macro completes the publish', async (t) => {
	const seedWithMacro = `# Test Document\n\n## Changes\n\n**What:** Initial revision.\n\n**Why:** Uses \\legacyflag notation.\n\n${TARGET_BLOCK}`;
	const result = await run(t, `
await writeFile(path.join(proposals, 'research-concept-r01.md'), ${JSON.stringify(MARKER)} + ${JSON.stringify(seedWithMacro)});
const guard = workspaceModule.createDocumentOperationGuard(root);
const workspace = workspaceModule.createProposalWorkspaceTool(root, { operationGuard: guard });
const adapter = new v2.ProposalWorkspaceAdapter(root, guard, workspace, () => 'change-header-macro-ack');
const planner = { async plan(input) { return { actions: [{ kind: 'replace', targetEntryId: input.target.entryId, replacementText: '## Target Section\\n\\nUpdated content.\\n' }], unresolvedQuestions: [] }; } };
const orchestrator = new v2.ProposalDeliberationOrchestrator(root, adapter, undefined, planner);
const changeSummary = { what: 'Updated target section.', why: 'No macro reference this time.' };
const request = { operation: 'CREATE_SUCCESSOR', sourceFilename: 'research-concept-r01.md', instruction: 'Modifica la sección Target Section.', changeSummary };
const preview = await orchestrator.execute(request);
const lostIds = (preview.preservationDelta?.lost ?? []).map((atom) => atom.id);
const published = await orchestrator.execute({ ...request, acceptSuccessor: true, successorAcceptanceToken: preview.acceptanceToken, acknowledgedRemovals: lostIds });
console.log(JSON.stringify({ publishedStatus: published.status, publishedReason: published.reason, publishedValidation: published.validation }));
`);
	assert.equal(result.publishedStatus, 'published', JSON.stringify(result));
});

test('4.1.15 a conceptual-revision CREATE_SUCCESSOR also carries the header block through without breaking the arity guards', async (t) => {
	const result = await run(t, `
await writeFile(path.join(proposals, 'research-concept-r01.md'), ${JSON.stringify(MARKER)} + ${JSON.stringify(SEED_MARKDOWN)});
const guard = workspaceModule.createDocumentOperationGuard(root);
const workspace = workspaceModule.createProposalWorkspaceTool(root, { operationGuard: guard });
const adapter = new v2.ProposalWorkspaceAdapter(root, guard, workspace, () => 'change-header-conceptual');
const planner = { async plan(input) { return { actions: [{ kind: 'replace', targetEntryId: input.target.entryId, replacementText: '## Target Section\\n\\nConceptually revised content.\\n' }], unresolvedQuestions: [] }; } };
const orchestrator = new v2.ProposalDeliberationOrchestrator(root, adapter, undefined, planner);
const changeSummary = { what: 'Conceptual revision.', why: 'Testing conceptual-planner.ts arity guards.' };
const request = { operation: 'CREATE_SUCCESSOR', editIntent: 'CONCEPTUAL_REVISION', sourceFilename: 'research-concept-r01.md', instruction: 'Modifica la sección Target Section.', changeSummary };
const preview = await orchestrator.execute(request);
const published = await orchestrator.execute({ ...request, acceptSuccessor: true, successorAcceptanceToken: preview.acceptanceToken });
console.log(JSON.stringify({ previewStatus: preview.status, previewReason: preview.reason, resolvedTargetsLength: preview.plan?.resolvedTargets?.length, publishedStatus: published.status, publishedReason: published.reason }));
`);
	assert.equal(result.previewStatus, 'awaiting_acceptance', JSON.stringify(result));
	assert.equal(result.resolvedTargetsLength, 2);
	assert.equal(result.publishedStatus, 'published', JSON.stringify(result));
});

test('4.1.4 CREATE_SUCCESSOR without a declared changeHeader never requires changeSummary and never adds a second resolved target', async () => {
	const piRootLocal = piRoot;
	const { createJiti } = await import(pathToFileURL(path.join(piRootLocal, 'node_modules/jiti/lib/jiti.mjs')).href);
	const jiti = createJiti(import.meta.url, { alias: {
		'@earendil-works/pi-coding-agent': path.join(piRootLocal, 'dist/index.js'),
		'@earendil-works/pi-ai': path.join(piRootLocal, 'node_modules/@earendil-works/pi-ai/dist/index.js'),
		typebox: path.join(piRootLocal, 'node_modules/typebox/build/index.mjs'),
	} });
	const workspaceModule = await jiti.import(path.resolve(engineDir, 'proposal-workspace.ts'));
	const v2 = await jiti.import(path.resolve(engineDir, 'exports.ts'));
	const root = await mkdtemp(path.join(os.tmpdir(), 'pp-change-header-undeclared-'));
	const proposals = path.join(root, 'proposals');
	await mkdir(proposals, { recursive: true });
	const bootstrap = workspaceModule.createProposalWorkspaceTool(root);
	await bootstrap.execute('seed', { action: 'write', resource: 'proposal', slug: 'r01', content: '# R01\n\n## Target Section\n\nOriginal content.\n' });
	const guard = workspaceModule.createDocumentOperationGuard(root);
	const workspace = workspaceModule.createProposalWorkspaceTool(root, { operationGuard: guard });
	const adapter = new v2.ProposalWorkspaceAdapter(root, guard, workspace, () => 'change-header-undeclared');
	const planner = { async plan(input) { return { actions: [{ kind: 'replace', targetEntryId: input.target.entryId, replacementText: '## Target Section\n\nUpdated content.\n' }], unresolvedQuestions: [] }; } };
	const orchestrator = new v2.ProposalDeliberationOrchestrator(root, adapter, undefined, planner);
	// No changeSummary supplied at all -- must not be required, since this DOMAIN (the default
	// math profile under normal npm test env) declares no `artifact.changeHeader`.
	const request = { operation: 'CREATE_SUCCESSOR', sourceFilename: 'research-concept-r01.md', instruction: 'Modifica la sección Target Section.' };
	const preview = await orchestrator.execute(request);
	assert.equal(preview.status, 'awaiting_acceptance', JSON.stringify(preview));
	assert.equal(preview.plan.resolvedTargets.length, 1, 'no header locus may be appended when changeHeader is undeclared');
	assert.equal(preview.growthAdvisory, undefined, 'growthAdvisory stays undefined on this path when changeHeader is undeclared, exactly as before this change');
	const published = await orchestrator.execute({ ...request, acceptSuccessor: true, successorAcceptanceToken: preview.acceptanceToken });
	assert.equal(published.status, 'published', JSON.stringify(published));
	assert.equal(published.receipt.resolvedEntryIds.length, 1);
	assert.equal('changeSummary' in published.receipt, false, 'the receipt must not carry a changeSummary key when changeHeader is undeclared');
});
