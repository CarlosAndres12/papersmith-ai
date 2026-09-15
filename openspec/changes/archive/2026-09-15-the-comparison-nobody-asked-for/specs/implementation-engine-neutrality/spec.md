# Delta for implementation-engine-neutrality

## ADDED Requirements

### Requirement: No Live Target's Own Name Appears Anywhere In This Forge, In Any Casing

This is a forge of papers, not of one paper. Every file under `.claude/`,
and every test's own commentary, fixture description, or string content not
meant as a neutral placeholder, MUST name no specific live target — neither
a target's package name (already guarded) nor its repository directory
name. This extends the existing engine-text and kit-agreement leak guards
to test commentary specifically, and MUST catch a live target's name
regardless of how that name happens to be cased where it leaks, so a
proper-noun-cased mention in prose is not structurally invisible to a
guard built from normalized words.

**Measured, not hypothetical.** A live target's repository directory name
appears once in `tests/test_proposal_implementation.py`, in a fixture
comment, while the existing vocabulary guards report 28/28 passing and the
same name appears nowhere under `.claude/`. The guard exists and mostly
works; this one instance is where it does not.

#### Scenario: A live target's repository name in a test comment is caught
- GIVEN a test file's comment names a specific live target's repository
  directory, in whatever casing it is naturally written
- WHEN the anti-leak guard runs
- THEN it fails, naming the file and the word

#### Scenario: A neutral placeholder is not mistaken for a leak
- GIVEN a fixture using a generic, invented name that is not any real
  target's own name
- WHEN the guard runs
- THEN it does not object

### Requirement: The Anti-Leak Guard's Word Comparison Does Not Depend On Matching Case

The step that compares a forge document's text against the words a live
target owns MUST NOT silently pass a match merely because the target's own
name is cased differently in the leaking text than in the guard's own
normalized vocabulary (for example, a title-cased repository name in prose
against a lowercased denylist entry). Closing the one measured instance by
hand, without making the comparison case-robust, would leave every future
target's own name free to leak the same way, in the same casing pattern.

#### Scenario: A repository name leaking in a different case than the denylist is caught
- GIVEN a live target's repository directory name appears in forge text in
  a different case than the guard's own derived vocabulary uses
- WHEN the leak check compares them
- THEN the leak is still caught

#### Scenario: The fix closes the class, not the one instance
- GIVEN a hypothetical second live target whose repository directory name
  has never appeared in any forge text before
- WHEN that name is planted, in any casing, into a forge file as a test
- THEN the guard catches it too, with no per-target exemption list required
