import type { DeliberationDomainProfile } from "../_core/deliberation/engine/domain-profile.js";
import { extractAtoms, violations } from "./preservation-math.js";
import { declares, cites } from "./reference-math.js";

/**
 * What the shared deliberation engine needs to know about THIS domain.
 *
 * The engine under `_core/` is domain-neutral and refuses to start without one of
 * these. Everything here was once spelled inside the engine itself, which is why
 * a sibling skill could not reuse it without inheriting a research project it has
 * nothing to do with.
 */
export const profile: DeliberationDomainProfile = {
	deriveBase: "matematica_propuesta_CREDA.md",
	baseLabel: "fixed CREDA base",
	baseLabelLong: "fixed CREDA proposal base",
	exampleSlug: "subject-bag-creda-integrated-r06",
	names: ["CREDA"],
	// These documents number with `\tag{N}` and cite as `(Ec. N)`; they do not
	// use `\label`/`\eqref`, so this is the only citation form that resolves.
	proseReferencePattern: "\\((?:Ec|Eq)\\.\\s*([0-9]+[a-z]?)\\)",
	proseReferenceText: (value) => `(Ec. ${value})`,
	vocabulary: {
		conceptualTerms: ["regularización", "motivación matemática", "múltiples dominios", "semi-supervisado"],
		expertPattern: "matem|ecuaci|regularización|semi-supervisado|teórico",
		displayNounPattern: "ecuaci[oó]n",
		displayNounStripPattern: "\\becuaci[oó]n(?:es)?\\b",
		subjectPattern: "one[- ]?hot|codificaci[oó]n|etiqueta|clase",
		subjectTerms: ["one-hot", "one hot"],
		subjectLocusDescription: "ecuación relacionada con one-hot",
		subjectEvidenceLabel: "nearby one-hot/coding definition",
		// Change 10: was a core-level unconditional literal in `intent-resolver.ts`. Opted in here,
		// with the exact same terms/label, so an instruction mentioning sparse/dispersed
		// representations keeps resolving to the exact same `requestedEffect` it always has --
		// this domain's own subject (regularisation, one-hot encoding) plausibly still needs it,
		// so the safer choice is preserving the signal explicitly rather than silently dropping it.
		requestedEffect: { terms: ["sparse", "dispers"], label: "representación sparse" },
	},
	// Exactly today's values: `directory`/`stem`/the `rNN` spelling/`sidecarRoot` (WITH its leading
	// dot)/`marker` were all previously hardcoded across core. This profile is now the only place
	// that names them, and core reads them back out through `artifact-naming.ts`.
	artifact: {
		directory: "proposals",
		stem: "research-concept",
		revisionPattern: "r",
		revisionLabel: (ordinal) => `r${String(ordinal).padStart(2, "0")}`,
		sidecarRoot: ".proposal-deliberation",
		marker: "<!-- proposal-workspace:artifact:v1 -->\n",
	},
	// The mathematical preservation gate (change 4): the atom extractor and canonical-form
	// rule set live in `preservation-math.ts`, wired through here so the shared core's
	// `preservation.ts` never hardcodes a single equation.
	preservation: { extractAtoms, violations },
	// Reference integrity (change 5): the declares/cites vocabulary lives in
	// `reference-math.ts`, wired through here so the shared core's `candidate-validator.ts`/
	// `reference-index.ts`/`document-index.ts` never hardcode `\label`/`\tag`/`\eqref`/`(Ec. N)`.
	references: { declares, cites },
	// Required sources (change 7): exactly today's single source, `guidance/paper-guide`,
	// declared NOT required -- an absent guide still renders v1 silently, identical to
	// pre-change behavior. A future source this domain cannot draft without would set
	// `required: true` instead.
	sources: [{ path: "guidance/paper-guide", required: false }],
};
