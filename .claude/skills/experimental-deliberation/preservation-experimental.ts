import { sha256, type PreservationAtom, type PreservationViolation } from "../_core/deliberation/engine/types.js";

/**
 * This domain's preservation gate, wired through `profile.ts` as
 * `preservation.{extractAtoms, violations}`. The shared core knows only about
 * atoms, deltas and violations in the abstract; everything below is what an
 * EXPERIMENTS document is, and it is deliberately nothing like the mathematical
 * sibling's notation rules.
 *
 *   1. `extractAtoms` -- what does this document declare that must never vanish
 *      in silence? Reported on preview as `preservationDelta`, and refused on
 *      accept unless the caller acknowledges each lost one by id.
 *   2. `violations` -- does the candidate still spell an experiments document the
 *      one way that keeps it honest? Never intentional, so this blocks outright.
 *
 * Nothing here reads `DOMAIN`. That is a property worth keeping rather than an
 * accident: this module can then be exercised directly, in process, under a test
 * run whose single `DELIBERATION_DOMAIN_PROFILE` belongs to another domain.
 *
 * ## Why an experiments document needs its own gate at all
 *
 * The mathematical atom set is worthless here -- an experiments document has no
 * `$$`, no `\tag`, so that extractor returns an empty map and the gate passes
 * vacuously. A vacuous pass is worse than no gate, which is exactly why the core
 * distinguishes "nothing to check" (`preservationApplicable: false`) from
 * "checked and passed", and why the five atom kinds below are the things this
 * document is actually made of.
 */

const short = (value: string) => sha256(value).slice(0, 8);
const collapse = (value: string) => value.replace(/\s+/gu, " ").trim();

/**
 * A GFM table, fully pipe-delimited: a header row, its alignment separator, then
 * zero or more body rows.
 *
 * Byte-identical to `document-index.ts`'s own `GFM_TABLE`, on purpose and not by
 * coincidence: the core indexes a table as its own structural entry (so a table
 * can be a locus), and a gate that recognized a different set of tables would
 * report a loss inside a span the resolver cannot address, or miss one it can.
 * The core does not export it, so it is restated here with this note attached.
 */
const GFM_TABLE = /^\|[^\n]*\|[ \t]*\r?\n\|(?:[ \t]*:?-+:?[ \t]*\|)+[ \t]*\r?\n(?:\|[^\n]*\|[ \t]*(?:\r?\n|$))*/gm;

/** A declared figure placeholder: a Markdown image reference standing alone on its own line. Also restated from `document-index.ts`, same reason. An image reference used inline inside a sentence is prose, not a declared figure. */
const FIGURE_PLACEHOLDER = /^!\[[^\]\n]*\]\([^)\n]*\)[ \t]*$/gm;

/**
 * A declared success criterion: a bold `**Success criterion:**` label, optionally
 * carried by a list bullet, and the criterion itself as the rest of the line.
 *
 * A label rather than a heuristic over prose, because this is the sentence the
 * whole document is answerable to: an experiment whose criterion silently
 * disappeared between two revisions has stopped being falsifiable, and no
 * amount of reading the surrounding paragraph recovers what it used to say.
 */
const SUCCESS_CRITERION = /^[ \t]*(?:[-*+][ \t]+)?\*\*Success criteri(?:on|a):?\*\*[ \t]*(.+?)[ \t]*$/gmu;

/** An external URL. Stops at whitespace, at a closing paren (so a Markdown link target ends where the link does) and at a table cell boundary. */
const EXTERNAL_URL = /https?:\/\/[^\s|)\]]+/gu;

/**
 * The pending-verification convention, and the whole of it.
 *
 * The problem this solves is that the bytes cannot know whether a search ran.
 * "A URL that did not come from a search in the current run must be marked" is
 * only decidable if the ABSENCE of a mark is itself the violation -- so every
 * external URL in an experiments document carries exactly one of two tags,
 * immediately after it, on the same line:
 *
 *   - `[pending-verification]`      -- nobody has reached this URL yet.
 *   - `[verified: YYYY-MM-DD]`      -- a search in the run of that date reached it.
 *
 * An untagged URL is refused. That is the point: the default is the violation,
 * so a URL a model invented from memory cannot be published by saying nothing,
 * and the run date makes a stale verification visible instead of permanent. The
 * date must be a full `YYYY-MM-DD`; a bare year is not a run.
 *
 * "Immediately after" is load-bearing too. A tag anywhere on the line would let
 * one verified URL vouch for an unverified neighbour, so the tag must be the
 * next non-blank thing after the URL ends. The only bytes allowed to sit between
 * them are the ones the URL was wrapped in or ended by: a Markdown link's closing
 * paren and ordinary sentence punctuation. Citing a repository as
 * `[the repository](https://example.org/x) [pending-verification]` is the normal
 * way to write one, and a rule that refused it would be a rule nobody could obey.
 */
const VERIFICATION_TAG_SOURCE = "\\[pending-verification\\]|\\[verified: \\d{4}-\\d{2}-\\d{2}\\]";
const VERIFICATION_TAG_FOLLOWS = new RegExp(`^[)\\].,;:!?]*[ \\t]*(?:${VERIFICATION_TAG_SOURCE})`, "u");
const VERIFICATION_TAG_ANYWHERE = new RegExp(VERIFICATION_TAG_SOURCE, "gu");

/**
 * The first header cell that makes a table a BASELINES table rather than a report
 * table, and the distinction the fabricated-value rule below rests on.
 *
 * A report table is a promise about a future run: its body cells are slots, and a
 * number in one is a result nobody measured. A baselines table is a reference:
 * its cells legitimately carry a repository, a venue and a year. One header cell
 * tells them apart, and it is the only thing that does.
 */
const BASELINE_COLUMNS = new Set(["baseline", "baselines"]);

/** A venue year. Narrow on purpose: a four-digit year in the 1900s or 2000s, which is what a conference or journal citation carries. */
const VENUE_YEAR = /\b(?:19|20)\d{2}\b/u;

type TableRow = { readonly line: number; readonly cells: readonly string[] };
type ParsedTable = { readonly line: number; readonly header: string; readonly body: readonly TableRow[]; readonly baselines: boolean };

/** A pipe-delimited row split into its cells, with the outer pipes dropped and every cell trimmed. */
function cellsOf(row: string): string[] {
    return row.trim().replace(/^\|/u, "").replace(/\|$/u, "").split("|").map((cell) => cell.trim());
}

/** The 1-based line an index falls on. */
function lineAt(source: string, index: number): number {
    let line = 1;
    for (let at = 0; at < index; at += 1) if (source[at] === "\n") line += 1;
    return line;
}

/** Every GFM table in the source, already split into a header, its body rows and their line numbers. */
function tables(source: string): ParsedTable[] {
    const out: ParsedTable[] = [];
    for (const match of source.matchAll(GFM_TABLE)) {
        const start = match.index ?? 0;
        const lines = match[0].split(/\r?\n/u);
        const header = (lines[0] ?? "").trim();
        const headerCells = cellsOf(header);
        const body: TableRow[] = [];
        // Row 0 is the header and row 1 is the alignment separator; the body starts at 2.
        for (let offset = 2; offset < lines.length; offset += 1) {
            const raw = lines[offset] ?? "";
            if (!raw.trim()) continue;
            body.push({ line: lineAt(source, start) + offset, cells: cellsOf(raw) });
        }
        out.push({ line: lineAt(source, start), header, body, baselines: isBaselinesTable(headerCells) });
    }
    return out;
}

/** Whether this table's first header cell declares it a baselines table. */
function isBaselinesTable(headerCells: readonly string[]): boolean {
    return BASELINE_COLUMNS.has((headerCells[0] ?? "").toLowerCase());
}

type FoundUrl = { readonly value: string; readonly line: number; readonly trailing: string };

/** Every external URL, with the rest of its own line, so the tag rule can ask what immediately follows. */
function externalUrls(source: string): FoundUrl[] {
    const out: FoundUrl[] = [];
    for (const match of source.matchAll(EXTERNAL_URL)) {
        const start = match.index ?? 0;
        // Sentence punctuation is not part of a URL: `…/alpha-net.` cites `…/alpha-net`,
        // and the stripped character stays in `trailing`, where it correctly fails the tag rule.
        const value = match[0].replace(/[.,;:!?]+$/u, "");
        const end = start + value.length;
        const lineEnd = source.indexOf("\n", end);
        out.push({ value, line: lineAt(source, start), trailing: source.slice(end, lineEnd < 0 ? source.length : lineEnd) });
    }
    return out;
}

/**
 * Every atom this document declares, keyed by a stable id.
 *
 * Presence-based, never counted, exactly as the mathematical sibling argues:
 * an atom is lost only when it disappears entirely, so rewording a paragraph
 * that happened to repeat a figure reference is not a loss.
 *
 *   `report-table`     a table's header row -- the skeleton that declares what will be reported
 *   `baseline`         a model named in the first cell of a baselines table's body row
 *   `success-criterion` a declared criterion the document is answerable to
 *   `figure`           a figure placeholder standing alone on its own line
 *   `url`              a cited external URL, keyed by the URL itself
 */
export function extractAtoms(source: string): Map<string, PreservationAtom> {
    const atoms = new Map<string, PreservationAtom>();
    const add = (kind: string, key: string, text: string) => {
        const id = `${kind}:${key}`;
        if (!atoms.has(id)) atoms.set(id, { id, kind, text });
    };
    for (const table of tables(source)) {
        add("report-table", short(collapse(table.header)), collapse(table.header));
        if (!table.baselines) continue;
        for (const row of table.body) {
            const name = collapse(row.cells[0] ?? "");
            if (name) add("baseline", short(name), name);
        }
    }
    for (const [placeholder] of source.matchAll(FIGURE_PLACEHOLDER)) add("figure", short(collapse(placeholder)), collapse(placeholder));
    for (const [, criterion] of source.matchAll(SUCCESS_CRITERION)) add("success-criterion", short(collapse(criterion)), collapse(criterion));
    // Keyed by the URL itself rather than by a digest: the id is what a caller has
    // to echo back to authorise a removal, and a citation is legible where a hash is not.
    for (const found of externalUrls(source)) add("url", found.value, found.value);
    return atoms;
}

/** The canonical form: how this domain writes an experiments document so it stays honest about what has not happened yet. */
export function violations(source: string): PreservationViolation[] {
    const out: PreservationViolation[] = [];
    for (const table of tables(source)) {
        for (const row of table.body) {
            if (table.baselines) {
                baselineViolations(row, out);
                continue;
            }
            row.cells.forEach((cell, column) => {
                // Column one is the row LABEL -- what is being reported on, not a reported
                // value -- so `Adapted (k=3)` is a name and not a result. Everything past it
                // is a slot a future run fills, and a number in one is a fabricated result.
                if (column === 0 || !/\d/u.test(cell)) return;
                out.push({
                    rule: "report-table-fabricated-value",
                    line: row.line,
                    detail: `column ${column + 1} of this report table must stay empty until a run fills it; found ${JSON.stringify(cell)}`,
                });
            });
        }
    }
    for (const found of externalUrls(source))
        if (!VERIFICATION_TAG_FOLLOWS.test(found.trailing))
            out.push({
                rule: "url-without-verification-marker",
                line: found.line,
                detail: `${found.value} must be followed by [pending-verification] or [verified: YYYY-MM-DD]; an unmarked URL claims a search that left no trace`,
            });
    return out.sort((left, right) => left.line - right.line);
}

/** A named baseline owes a reader two things: where the code is, and where the work was published. */
function baselineViolations(row: TableRow, out: PreservationViolation[]): void {
    const name = collapse(row.cells[0] ?? "");
    if (!name) return;
    const text = row.cells.join(" | ");
    // The verification tag carries a date, and a date carries a year. Left in, a
    // freshly verified URL would satisfy the venue check on a row that names no venue.
    const withoutTags = text.replace(VERIFICATION_TAG_ANYWHERE, " ");
    if (!/https?:\/\//u.test(text))
        out.push({ rule: "baseline-missing-repository-url", line: row.line, detail: `the baseline ${JSON.stringify(name)} names no repository URL` });
    if (!VENUE_YEAR.test(withoutTags))
        out.push({ rule: "baseline-missing-venue-year", line: row.line, detail: `the baseline ${JSON.stringify(name)} names no venue year` });
}
