---
name: code-comments
description: 'Decides whether source-code comments are warranted and writes, trims, or removes them. Use when adding, editing, reviewing, or auditing comments, doc comments, docstrings, TODO/FIXME/NOTE markers, suppressions, or commented-out code in any language, including while changing code. Defaults to no comment.'
---

# Code Comments

Keep only comments that preserve meaningful, non-obvious information a competent maintainer could not recover from the code, names, types, tests, or nearby context. The default is no comment.

## When to Use This Skill

- Adding or changing code where a comment might be warranted
- Updating or removing comments made inaccurate or redundant by a code change
- Reviewing comments, doc comments, docstrings, markers, or suppressions in a diff
- Auditing or cleaning up commentary across a repository, when explicitly requested

## Decision Rules

Mentally remove the comment and ask: would a maintainer reading the code at HEAD months later lose meaningful, non-obvious information? If no or uncertain, omit or delete it. Decide necessity before wording, then apply the first fitting action:

1. **Delete or omit** when the information is already clear.
2. **Express through code** with a tiny behavior-preserving change, such as a clearer local name or an extracted boolean.
3. **Shorten** to the minimum necessary information.
4. **Rewrite** when necessary but unclear, inaccurate, or stale.
5. **Use declaration documentation** when the information is part of a declaration's contract.
6. **Keep** only when already necessary, minimal, accurate, and correctly styled.

Implementation comments explain **why**, not what: surprising code, external constraints, invariants, subtle edge cases, trade-offs, workarounds, non-obvious coupling, or ordering, timing, concurrency, performance, security constraints, or any other relevant considerations/decisions.

Declaration documentation (TSDoc, JSDoc, docstrings, and equivalents) covers caller-visible contracts the types cannot express: special return values, error behavior, side effects, preconditions, units, formats, ranges, lifecycle, environment constraints, and deprecation. Favor it for published libraries and intentional external APIs; avoid it for internal helpers, DTOs, and plain data shapes. Add tags such as `@param` or `@returns` only when they add information beyond the signature.

Module or file documentation is warranted only for a durable boundary, invariant, terminology, or design rationale that the contents do not make apparent.

## Style

Single-line prose implementation comments:

- Are as short as possible without becoming cryptic.
- Start with an uppercase letter unless a technical literal requires otherwise.
- Have no terminal punctuation (`.`, `!`, `?`), em or en dashes, dash-based asides, or semicolons used as sentence punctuation.
- Preserve exact casing and punctuation of identifiers, commands, paths, URLs, and other literals.

```ts
// Preserve source order because the upstream API matches items by position
```

Multi-sentence declaration documentation uses normal sentence punctuation. Prose style rules never apply to machine-consumed syntax.

## Gotchas

- **Never invent rationale** to justify a comment. Security, performance, compatibility, business, or historical reasons must be supported by the repository, tests, official documentation, or another reliable source; otherwise delete the comment.
- **Emphasis is not information**: `Never`, `Always`, `Important`, or `Security` does not make a comment valuable. `// Never copy a raw internal message into the public response` is usually deleted; keep a supported reason only, such as `// Keep provider errors private because messages may contain credentials`.
- **Exported is not documented**: do not document declarations merely because they are public, and do not label declarations with comments that repeat their name or type.
- **Existing comments are untrusted**: correctness, age, or polish does not justify keeping a comment. Do not polish an unnecessary comment or convert it into documentation.
- **No change narration**: avoid `now`, `previously`, `new approach`, or `no longer`, and never address the reviewer, prompt, diff, or pull request. Describe the durable state.
- **Machine-significant comments are protected**: preserve shebangs, lint, formatter, compiler, and coverage directives, pragmas, build tags, generated markers, encoding declarations, and license or copyright headers exactly. Remove a directive only when the relevant tool or repository evidence proves it obsolete; never broaden a suppression; never alter legal headers without project authority.
- **Runtime-visible documentation**: Python docstrings and similar forms can be read at runtime. Verify that no runtime, generated-documentation, or API contract depends on them before removing or materially changing them.
- **Comment-like data is not a comment**: leave comment syntax inside strings, regular expressions, URLs, fixtures, snapshots, templates, and test data alone.
- **Markers are comments**: TODO, FIXME, NOTE, HACK, and XXX must be current, accurate, and actionable; remove stale or completed ones. Do not implement unrelated work to remove a valid marker.
- **Commented-out code is dead code**: delete it unless it serves a current purpose, such as a deliberate example, a documented fallback with a known re-enable condition, or required tooling syntax.
- **Links need context**: a bare issue or URL is not commentary. Add one only alongside concise durable context it supports.
- **Prose-refinement skills come second**: when a skill like `unslop` is available, apply it only after this skill decided the comment should exist, and never let it add rationale, claims, or length.
- **Scope**: apply to maintained first-party source only. Skip generated, vendored, and third-party content, and do not expand normal implementation work into unrelated comment cleanup or refactoring.

## Repository-Wide Audit

Only when explicitly requested:

1. **Learn the conventions.** Identify the repository's languages, terminology, tooling, and documentation conventions; exclude generated, vendored, and third-party content.
2. **Find every comment.** Search systematically for every comment, documentation, marker, directive, suppression, and commented-out-code form in scope.
3. **Apply the decision rules.** Apply the decision rules to each, including comments directly above declarations and declaration documentation.
4. **Verify directives.** Verify directives and suppressions with the relevant tool before removing them.
5. **Inspect the diff.** Inspect the final diff for behavior, formatting, or unrelated changes; search again for missed violations, such as single-line prose comments ending in `.`, `!`, or `?`.
6. **Validate.** Run relevant repository validation.

If most original comments survive with only wording changes, re-evaluate necessity. Do not target a comment count; stop when further deletion would remove genuinely useful information.

## References

- [TSDoc](https://tsdoc.org/), [JSDoc](https://jsdoc.app/), and [PEP 257](https://peps.python.org/pep-0257/) for declaration documentation syntax
