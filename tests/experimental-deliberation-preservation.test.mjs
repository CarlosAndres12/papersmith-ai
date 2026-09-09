// The experimental domain's preservation gate: which atoms an experiments
// document declares (lost ones must be acknowledged by id before a successor
// publishes), and the canonical-form rules that block outright because they are
// never intentional.
//
// Loaded IN PROCESS rather than through a spawned child, and that is a property
// of the module under test rather than a convenience: `preservation-experimental.ts`
// imports only `types.js` (for `sha256`), never `domain-profile.js`, so nothing
// here touches the single `DELIBERATION_DOMAIN_PROFILE` the whole suite run is
// fixed to. The sibling file `experimental-deliberation-domain-profile.test.mjs`
// spawns a child for the parts that DO need this skill's profile installed.
import assert from 'node:assert/strict';
import path from 'node:path';
import test from 'node:test';
import { pathToFileURL } from 'node:url';

const repoRoot = process.cwd();
const piRoot = '/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent';
const { createJiti } = await import(pathToFileURL(path.join(piRoot, 'node_modules/jiti/lib/jiti.mjs')).href);
const jiti = createJiti(import.meta.url, { alias: {
    '@earendil-works/pi-coding-agent': path.join(piRoot, 'dist/index.js'),
    '@earendil-works/pi-ai': path.join(piRoot, 'node_modules/@earendil-works/pi-ai/dist/index.js'),
    typebox: path.join(piRoot, 'node_modules/typebox/build/index.mjs'),
} });
const { extractAtoms, violations } = await jiti.import(
    path.join(repoRoot, '.claude/skills/experimental-deliberation/preservation-experimental.ts'));

const kinds = (source) => [...extractAtoms(source).values()].map((atom) => atom.kind).sort();
const rules = (source) => violations(source).map((entry) => entry.rule).sort();

// A document carrying one of every atom kind and violating nothing. The protocol
// paragraph deliberately carries three numbers (a learning rate, a seed count and a
// year) OUTSIDE any table, because the fabricated-value rule below must not see them.
const RICH = `# Experiments

## Protocol

Training runs use a learning rate of 3e-4 over 5 seeds, reported on the 2018 split.

- **Success criterion:** the adapted model matches the source-only baseline on the held-out split.

## Baselines

| Baseline | Repository | Venue |
| --- | --- | --- |
| Alpha-Net | https://example.org/alpha-net [pending-verification] | ICML 2015 |
| Beta-Net | https://example.org/beta-net [pending-verification] | NeurIPS 2019 |

## Reported results

| Arm | Accuracy | F1 |
| --- | --- | --- |
| Source only |  |  |
| Adapted |  |  |

![Accuracy against the number of labelled examples](figures/accuracy-vs-labels.png)
`;

// The same protocol prose with every experimental structure removed: no table, no
// figure, no declared criterion, no cited URL. Nothing for this gate to check.
const PLAIN = `# Experiments

## Protocol

Training runs use a learning rate of 3e-4 over 5 seeds, reported on the 2018 split.
`;

// ---------------------------------------------------------------------------
// Atoms
// ---------------------------------------------------------------------------

test('every atom kind is extracted from a document that genuinely contains it', () => {
    assert.deepEqual(kinds(RICH), [
        'baseline', 'baseline',
        'figure',
        'report-table', 'report-table',
        'success-criterion',
        'url', 'url',
    ]);
});

test('a report-table atom is keyed on the header row, so losing the skeleton is a loss', () => {
    const atoms = [...extractAtoms(RICH).values()].filter((atom) => atom.kind === 'report-table');
    assert.deepEqual(atoms.map((atom) => atom.text).sort(), [
        '| Arm | Accuracy | F1 |',
        '| Baseline | Repository | Venue |',
    ]);
});

test('a baseline atom names the model in the first cell of a baselines table body row', () => {
    const atoms = [...extractAtoms(RICH).values()].filter((atom) => atom.kind === 'baseline');
    assert.deepEqual(atoms.map((atom) => atom.text).sort(), ['Alpha-Net', 'Beta-Net']);
});

test('a success-criterion atom carries the criterion text, not the label', () => {
    const atoms = [...extractAtoms(RICH).values()].filter((atom) => atom.kind === 'success-criterion');
    assert.equal(atoms.length, 1);
    assert.equal(atoms[0].text, 'the adapted model matches the source-only baseline on the held-out split.');
});

test('a url atom is keyed on the URL itself, and the verification marker is not part of it', () => {
    const atoms = [...extractAtoms(RICH).values()].filter((atom) => atom.kind === 'url');
    assert.deepEqual(atoms.map((atom) => atom.text).sort(), [
        'https://example.org/alpha-net',
        'https://example.org/beta-net',
    ]);
    assert.deepEqual(atoms.map((atom) => atom.id).sort(), [
        'url:https://example.org/alpha-net',
        'url:https://example.org/beta-net',
    ]);
});

test('a URL ending a sentence is cited without the sentence punctuation', () => {
    const source = '# Experiments\n\nSee https://example.org/alpha-net.\n';
    assert.deepEqual([...extractAtoms(source).values()].map((atom) => atom.id), ['url:https://example.org/alpha-net']);
    // The stripped period stays in the trailing text, where it correctly fails the tag
    // rule: an untagged URL is untagged whether or not a sentence ended on it.
    assert.deepEqual(rules(source), ['url-without-verification-marker']);
});

test('a figure placeholder standing alone on its line is an atom; an inline image reference is not', () => {
    const inline = '# Experiments\n\nSee ![a chart](figures/chart.png) in the appendix.\n';
    assert.deepEqual(kinds(inline), []);
    assert.deepEqual(kinds('# Experiments\n\n![a chart](figures/chart.png)\n'), ['figure']);
});

test('atoms are presence-based: repeating an atom does not multiply it', () => {
    const twice = `${PLAIN}\n![a chart](figures/chart.png)\n\n![a chart](figures/chart.png)\n`;
    assert.deepEqual(kinds(twice), ['figure']);
});

// ---------------------------------------------------------------------------
// applicable:false vs a genuine pass
// ---------------------------------------------------------------------------

test('a document with none of these declares no atoms, which the core reports as not applicable', () => {
    assert.equal(extractAtoms(PLAIN).size, 0, 'core computes preservationApplicable as `atoms(before).size > 0`');
    assert.deepEqual(violations(PLAIN), []);
});

test('a document that HAS atoms and breaks no rule is a genuine pass, distinct from the vacuous one', () => {
    assert.ok(extractAtoms(RICH).size > 0, 'a pass over an empty atom set is the vacuous pass this gate exists to avoid');
    assert.deepEqual(violations(RICH), []);
});

// ---------------------------------------------------------------------------
// Canonical form: no fabricated value in a report table's body
// ---------------------------------------------------------------------------

const REPORT_TABLE = (rows) => `# Experiments

## Reported results

| Arm | Accuracy | F1 |
| --- | --- | --- |
${rows}
`;

test('an empty report-table body cell is not a violation', () => {
    assert.deepEqual(violations(REPORT_TABLE('| Source only |  |  |')), []);
});

test('a number in a report-table body cell is a violation naming the row line', () => {
    const found = violations(REPORT_TABLE('| Source only | 0.91 |  |'));
    assert.deepEqual(found.map((entry) => entry.rule), ['report-table-fabricated-value']);
    assert.equal(found[0].line, 7, 'the violation must point at the offending body row');
    assert.match(found[0].detail, /0\.91/);
});

test('a number in a report-table row LABEL (column one) is not a violation', () => {
    assert.deepEqual(violations(REPORT_TABLE('| Adapted (k=3) |  |  |')), []);
});

test('a number in prose outside any table is never a fabricated value', () => {
    assert.deepEqual(violations(PLAIN), []);
});

test('a number in a baselines table body is legitimate: it is a reference table, not a report table', () => {
    const baselines = `# Experiments

| Baseline | Repository | Venue |
| --- | --- | --- |
| Alpha-Net | https://example.org/alpha-net [pending-verification] | ICML 2015 |
`;
    assert.deepEqual(violations(baselines), []);
});

// ---------------------------------------------------------------------------
// Canonical form: a baseline carries a repository URL and a venue/year
// ---------------------------------------------------------------------------

const BASELINES = (header, row) => `# Experiments

| ${header} |
| ${header.split('|').map(() => '---').join(' | ')} |
| ${row} |
`;

test('a baseline row with a repository URL and a venue year is not a violation', () => {
    assert.deepEqual(
        rules(BASELINES('Baseline | Repository | Venue', 'Alpha-Net | https://example.org/alpha-net [pending-verification] | ICML 2015')),
        []);
});

test('a baseline named without a repository URL is a violation', () => {
    assert.deepEqual(
        rules(BASELINES('Baseline | Venue', 'Alpha-Net | ICML 2015')),
        ['baseline-missing-repository-url']);
});

test('a baseline named without a venue year is a violation', () => {
    assert.deepEqual(
        rules(BASELINES('Baseline | Repository', 'Alpha-Net | https://example.org/alpha-net [pending-verification]')),
        ['baseline-missing-venue-year']);
});

test('a verified-on date does not stand in for a missing venue year', () => {
    assert.deepEqual(
        rules(BASELINES('Baseline | Repository', 'Alpha-Net | https://example.org/alpha-net [verified: 2026-09-08]')),
        ['baseline-missing-venue-year'],
        'the verification marker carries a year of its own and must be stripped before the venue check');
});

test('an empty first cell is not a baseline, so an empty spacer row raises nothing', () => {
    assert.deepEqual(rules(BASELINES('Baseline | Repository | Venue', ' |  | ')), []);
});

// ---------------------------------------------------------------------------
// Canonical form: every external URL carries a verification marker
// ---------------------------------------------------------------------------

test('a bare URL is a violation: nothing in the bytes says a search ever reached it', () => {
    const found = violations('# Experiments\n\nSee https://example.org/alpha-net for the reference implementation.\n');
    assert.deepEqual(found.map((entry) => entry.rule), ['url-without-verification-marker']);
    assert.equal(found[0].line, 3);
});

test('a URL marked pending verification is accepted', () => {
    assert.deepEqual(violations('# Experiments\n\nSee https://example.org/alpha-net [pending-verification] for it.\n'), []);
});

test('a URL marked verified with a run date is accepted', () => {
    assert.deepEqual(violations('# Experiments\n\nSee https://example.org/alpha-net [verified: 2026-09-08] for it.\n'), []);
});

test('a Markdown link carries its tag after the closing paren', () => {
    // Citing a repository as a Markdown link is the ordinary way to write one, so the
    // tag rule has to reach past the link syntax the URL is wrapped in.
    assert.deepEqual(violations('# Experiments\n\nSee [the repository](https://example.org/alpha-net) [pending-verification].\n'), []);
});

test('a marker that is not one of the two spellings does not satisfy the rule', () => {
    assert.deepEqual(
        rules('# Experiments\n\nSee https://example.org/alpha-net [checked] for it.\n'),
        ['url-without-verification-marker']);
});

test('a verified marker without a full date does not satisfy the rule', () => {
    assert.deepEqual(
        rules('# Experiments\n\nSee https://example.org/alpha-net [verified: 2026] for it.\n'),
        ['url-without-verification-marker']);
});

test('a marker written before the URL does not vouch for it', () => {
    assert.deepEqual(
        rules('# Experiments\n\n[pending-verification] was written before https://example.org/alpha-net here.\n'),
        ['url-without-verification-marker']);
});

test('a marker further along the same line does not vouch for an earlier URL', () => {
    // One tagged URL must not cover an untagged neighbour: the tag has to be the next
    // thing after the URL it speaks for, not merely present somewhere on the line.
    const found = violations('# Experiments\n\nSee https://example.org/alpha-net and https://example.org/beta-net [pending-verification] here.\n');
    assert.deepEqual(found.map((entry) => entry.rule), ['url-without-verification-marker']);
    assert.match(found[0].detail, /alpha-net/, 'the untagged URL is the first one, not the tagged neighbour');
});

// ---------------------------------------------------------------------------
// Shape
// ---------------------------------------------------------------------------

test('violations are returned in line order', () => {
    const source = `# Experiments

See https://example.org/one and https://example.org/two.

| Arm | Accuracy |
| --- | --- |
| Adapted | 0.42 |
`;
    const found = violations(source);
    assert.deepEqual(found.map((entry) => entry.line), [3, 3, 7]);
    assert.deepEqual(found.map((entry) => entry.rule), [
        'url-without-verification-marker',
        'url-without-verification-marker',
        'report-table-fabricated-value',
    ]);
});
