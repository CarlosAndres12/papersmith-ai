import type { DeliberationDomainProfile } from "../_core/deliberation/engine/domain-profile.js";
import { sha256 } from "../_core/deliberation/engine/types.js";
import { extractAtoms, violations } from "./preservation-experimental.js";
import { declares, cites } from "./reference-experimental.js";

/**
 * What the shared deliberation engine needs to know about THIS domain.
 *
 * The engine under `_core/` is domain-neutral and refuses to start without one of
 * these. It manages revisions of a Markdown document, indexes it, patches it
 * byte-exactly and transacts the result -- none of which cares whether the
 * document argues about mathematics or about which runs a machine will execute.
 * This file is the second such domain, and the engine gained no line of code to
 * accommodate it.
 *
 * An EXPERIMENTS document is a plan for work that has not happened. Everything
 * below follows from that one sentence: the tables are empty because a run fills
 * them, the URLs carry a verification tag because nobody has necessarily reached
 * them, and the data paper bounds what may be claimed because a claim the data
 * cannot support is not an experiment, it is a wish.
 */

/**
 * Sentences that assert an outcome. `detectConflicts` below is a pure function of
 * the candidate's bytes -- the profile knows what its own bound source asserts,
 * with no engine-level file I/O, exactly as `preservation.extractAtoms` knows its
 * own canonical form -- and what the data paper asserts, always, is that this
 * document plans work rather than reports it. So the detectable conflict is an
 * ACHIEVED result: an experiments document that says a model already won has
 * stepped past the one source that bounds it.
 */
const ACHIEVED_RESULT = /\b(?:outperform(?:s|ed)|beats|beat|surpass(?:es|ed)|achiev(?:es|ed)|obtain(?:s|ed)|state[- ]of[- ]the[- ]art|significantly better|reduces the error|wins against)\b/iu;

/** Where the data paper and dataset guidance live, and the one source that bounds every claim in this document. */
const DATA_PAPER = "guidance/data-paper";

export const profile: DeliberationDomainProfile = {
	deriveBase: "experimental_plan_base.md",
	baseLabel: "fixed experimental base",
	baseLabelLong: "fixed experimental plan base",
	exampleSlug: "domain-shift-baseline-sweep-v06",
	// This domain owns no proper noun -- it is a general layer, and naming one
	// research project here is the exact coupling the profile mechanism removes.
	// The one word it names ITSELF by is its own namespace, which no file under
	// `_core/` spells, so the core-scan lock stays meaningful rather than vacuous.
	names: ["experimental-deliberation"],
	// An experiments document numbers its experiments and cites them in prose as
	// `(Exp. E1)`. Unlike the mathematical sibling's `(Ec. N)`, the identifier is not
	// an ordinal: experiments are added, split and retired, and a positional number
	// would silently re-point every citation the first time one is removed.
	proseReferencePattern: "\\((?:Exp|Experiment)\\.\\s*([A-Za-z0-9][A-Za-z0-9._-]*)\\)",
	proseReferenceText: (value) => `(Exp. ${value})`,
	vocabulary: {
		conceptualTerms: ["experimental design", "baseline", "ablation", "evaluation protocol", "reported metric"],
		// The engine's intent matching is Spanish and shared; only the SUBJECT is this
		// domain's. These patterns therefore accept both spellings of each subject word:
		// a pattern that recognised only the English form would never fire on an
		// instruction written the way the rest of the engine expects to read it.
		expertPattern: "experiment|experimento|baseline|l[ií]nea base|protocol|protocolo|m[eé]trica|metric|ablation|ablaci[oó]n|benchmark",
		// This domain's numbered display is a report table or a figure, not an equation.
		displayNounPattern: "tabla|table|figura|figure",
		displayNounStripPattern: "\\b(?:tablas?|tables?|figuras?|figures?)\\b",
		subjectPattern: "baseline|l[ií]nea base|m[eé]trica|metric|partici[oó]n|split|protocol",
		subjectTerms: ["baseline", "línea base", "linea base"],
		subjectLocusDescription: "report table or figure related to a baseline",
		subjectEvidenceLabel: "nearby baseline/metric definition",
		// Optional, and declared because this domain genuinely has a second effect worth
		// naming: an instruction about removing a component to see what it was worth.
		requestedEffect: { terms: ["ablation", "ablaci"], label: "ablation study" },
	},
	artifact: {
		directory: "experiments",
		stem: "experiments",
		// `v` rather than `r`: a revision of an experiments document is a version of a
		// plan. The two-digit width is not free either -- the core's STRICT and LOOSE
		// matchers both require `\d{2,}` -- so `revisionLabel` pads, and the resulting
		// names are `experiments-<slug>-v01.md`, `experiments-<slug>-v02.md`.
		revisionPattern: "v",
		revisionLabel: (ordinal) => `v${String(ordinal).padStart(2, "0")}`,
		sidecarRoot: ".experimental-deliberation",
		// NOT free to change, and byte-identical to `proposal-deliberation`'s on purpose.
		// Three core files still SPELL this literal instead of reading it back out of the
		// profile -- `patch-compiler.ts`, `draft-materialization.ts` and
		// `revision-lifecycle-store.ts` -- so a domain that declared its own marker would
		// have its documents written with one string and validated against another, and
		// the failure would be silent. Copied exactly until those three read the profile.
		marker: "<!-- proposal-workspace:artifact:v1 -->\n",
		// Declared, unlike the mathematical sibling. A mathematical revision is answerable
		// to its own derivation, which is timeless; an experimental one is answerable to a
		// reader who has to know what changed between two plans before a run is launched
		// against the newer one. The block is its own resolved span each version, and the
		// receipt chain is where the full history lives.
		changeHeader: {
			heading: "Changes",
			// The FULL block, its own heading line included, and ending in a blank line:
			// `document-index.ts` folds the trailing blank line into a heading's span, so a
			// render that stopped one newline short would not fill the span it replaces and
			// `successor-markdown-block-safety` would refuse the candidate.
			render: (summary) => `## Changes\n\n**What:** ${summary.what}\n\n**Why:** ${summary.why}\n\n`,
		},
	},
	// The data paper is the bound. Advisory rather than `'refuse'`: an author who
	// genuinely means to restate a published result of somebody else's can acknowledge
	// the conflict by id on the accept turn, exactly as a lost atom is acknowledged --
	// whereas a hard block would make the document unable to quote its own sources.
	sourceAuthority: {
		names: [DATA_PAPER],
		severity: "advisory",
		detectConflicts: (candidateText) => {
			const conflicts: { id: string; sourceName: string; claim: string; evidence: string }[] = [];
			const seen = new Set<string>();
			for (const line of candidateText.split("\n")) {
				const evidence = line.replace(/\s+/gu, " ").trim();
				if (!evidence || !ACHIEVED_RESULT.test(evidence)) continue;
				const id = `claimed-result:${sha256(evidence).slice(0, 12)}`;
				if (seen.has(id)) continue;
				seen.add(id);
				conflicts.push({
					id,
					sourceName: DATA_PAPER,
					claim: "the data paper bounds what may be claimed, and this document plans runs that have not been executed, so no outcome may be asserted here",
					evidence,
				});
			}
			return conflicts;
		},
	},
	// The preservation gate: report-table skeletons, figure placeholders, baseline rows,
	// declared success criteria and cited URLs are what must never vanish in silence,
	// and the canonical form is what an honest plan looks like. Both live in
	// `preservation-experimental.ts`; the core's `preservation.ts` hardcodes neither.
	preservation: { extractAtoms, violations },
	// Reference integrity: an experiment declares an identifier, a claim reference cites
	// one. In `reference-experimental.ts`, for the same reason.
	references: { declares, cites },
	// Three sources, and which of them this domain cannot draft without.
	//
	//   1. The data paper / dataset guidance -- REQUIRED. It bounds what may be claimed;
	//      drafting without it produces a plan nothing can hold to account, which is why
	//      an absent one refuses `CREATE_INITIAL_REVISION` with `REQUIRED_SOURCE_MISSING`
	//      rather than rendering v1 silently.
	//   2. The latest managed proposal -- REQUIRED. The claims come from it; an
	//      experiments document with no proposal behind it is testing nothing. This is
	//      `proposal-deliberation`'s own managed directory, read here and never written.
	//   3. The area benchmark -- OPTIONAL. When present it is the source of truth for
	//      metrics, splits, protocol and baselines; when absent the document states its
	//      own, which is weaker but legal.
	sources: [
		{ path: DATA_PAPER, required: true },
		{ path: "proposals", required: true },
		{ path: "guidance/area-benchmark", required: false },
	],
};
