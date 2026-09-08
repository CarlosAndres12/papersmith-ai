# Limitations

**Extent** 180–410 words · 1 paragraph, or 2 when the second carries a failure mode
**Items** 3 to 5
**Carries** at least one citation per item · no figure, no table, no equation, and no
new measurement

This subsection states what the reported results do **not** establish. Its source of
truth is the inverse of every other part of the results section: those are written
from what the artefacts show, this one from what they fail to show.

## The opening is a concession

*Although / While / Despite* **[a concrete achievement the results do support]**,
several limitations must be acknowledged.

The concession is mandatory and it names something specific, not a formula. It may
carry the bridge to future work in the same sentence — *which in turn open avenues
for future research*.

## The anatomy of an item

Five movements. The first four are required; reach the fifth wherever possible.

**1. Name the decision or the boundary.** A fixed value, a shared strategy, an
unexplored scale, a predefined grid, a chosen baseline, an approximation. **Never a
feeling.** *Performance may vary* is not a limitation; *the weighting coefficient is
static* is one.

**2. Concede its benefit.** *Although this design enables X* / *While this choice
promotes reproducibility and permits direct comparison*. This is what separates a
limitation from an oversight: the decision was made for a reason, and the reason is
stated.

**3. State the cost.** What it restricts, what it may overlook, what it precludes.

**4. State the consequence for the claim.** *Therefore the resolution of the result
is partly constrained by …* / *the estimated contributions may still depend on …* —
what the paper consequently cannot assert.

**5. State what the alternative would give, and what it would cost.** *… could
improve performance, albeit at an increased computational cost.* This answers the
question the reader asks unprompted: **if you knew it was a limitation, why did you
not fix it.**

### Every item carries at least one citation

The citation is what makes the limitation verifiable rather than confessional. It
lands in one of two places:

- **On the alternative that would fix it** — whoever already proposed it. This is the
  natural home when the item reaches movement 5.
- **On the fact that the problem is known** in the literature, when the item stops at
  movement 4.

## Two sweeps, two kinds of gap

Items come from two places, and both sweeps are made. Some papers have items from
only one, which usually means the other sweep was not done.

**Sweep the mathematical section for gaps in the proposal:**

- a fixed coefficient where an adaptive one is possible;
- a heuristic where a principled choice is possible;
- a predefined grid or partition that constrains the resolution of the result;
- a chosen baseline or reference the result depends on;
- an approximation that ignores a known dependency structure;
- a theoretical grounding the formulation does not incorporate;
- an operating regime where the method degrades;
- the generality of the formulation outside the problem type tested.

**Sweep the experimental design for gaps in the validation:**

- a single shared hyperparameter configuration, with no per-scenario search;
- evaluation on a single source, site, or cohort, with transferability untested;
- a scale left uncharacterized — tested at one only;
- a sample size that constrains generalization;
- data heterogeneity or harmonization left unresolved;
- dependence on the quality and completeness of the input data.

**The checkable rule:** every item names a decision in the formulation or a decision
in the experimental design. An item naming neither is a feeling, and it does not go
in.

## The second paragraph: the quantitative failure mode

Written when there is a regime worth isolating. Four movements:

1. **Name the concrete regime where the method is weakest.**
2. **Point at the worst cell of a table already reported**, by number. Never a new
   measurement.
3. **Bring the evidence that the regime is hard, not that the method is bad** —
   typically the baseline's own performance in that same regime.
4. **Give the mechanism**: which stage of the pipeline breaks, and what input breaks
   it.

The third movement is what separates *the method fails here* from *here nobody
succeeds*, and it does it with a number already in the paper.

## The closing

Optional. Either what addressing the limitations would give, or where the field is
moving, with a citation.

## Coupling with future work

Future work is the relevant subset of these items. The twin obligation lives here:
**an item is declared knowing it may be asked for a direction**, and an orphan
direction in the conclusions — one answering no item here — means an item is missing
from this list, not that the direction is unnecessary.

When an item reaches movement 5, the reference on its alternative is the same one the
corresponding future-work direction carries.

## Inputs

| What | Depends on |
|---|---|
| The proposal items | the mathematical section — its design decisions, one by one |
| The validation items | the experimental design — what was fixed instead of searched, what was tested at a single point |
| The quantitative failure mode | the results: the worst reported cell, and the baseline's performance there |
| The opening concession | the concrete achievement the results do support |
| Each item's citation | the alternative that would fix it, or the literature that already knows the problem |

## Disqualifiers

- An item naming no decision in the formulation and none in the experimental design.
- An item with no citation.
- An item that stops before movement 4 — the consequence for the claim left unstated.
- An item that concedes no benefit, which makes it read as an oversight rather than a
  decision.
- A new measurement, or a value not already in a reported table.
- A failure mode not visible in any reported table.
- A failure regime named without the baseline's performance in it.
- Only proposal items, or only validation items — one of the two sweeps was skipped.
- An item that no future-work direction may be built on, when the conclusions
  nonetheless carry a direction for it.
- Placement in the conclusions, or anywhere but the last subsection of the results.
- A worst-performing cell softened here while stated plainly in the results, or the
  reverse.
- A figure, a table, or an equation.
