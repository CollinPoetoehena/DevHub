---
name: adr
description: 'Drafts Architecture Decision Records for significant technical choices, including context, decision, consequences, and alternatives. Use when asked to create, write, review, or refine an ADR or architecture decision; follow an existing project convention and the bundled ADR template.'
---

# Draft Architecture Decision Records

Create evidence-based ADRs with enough detail for a future maintainer to understand why a significant architectural choice was made and what it means for the system. Be concise by removing repetition, not by omitting decision-relevant reasoning.

## When to Use This Skill

- **Explicit request**: The user asks to create, write, review, or refine an ADR.
- **Durable decision**: A consequential architectural decision needs a lasting record.
- **Structured comparison**: A project needs options, trade-offs, and a decision captured in its established ADR format.

Do not create an ADR for routine implementation details or decisions that are easy to reverse and have no meaningful impact beyond the immediate change.

## Workflow

1. **Find the project convention.** Look for existing ADRs, naming and numbering rules, status conventions, and the expected directory. Reuse those conventions. If none exist, use the bundled [ADR template](./references/ADR-TEMPLATE.md); do not invent a project-specific storage location or numbering scheme.
2. **Ground the context.** Read relevant project guidance and implementation. Separate verified facts from assumptions, and identify the problem, constraints, and decision drivers. Ask for missing information when it could change the decision.
3. **Compare viable options.** Include the recommended choice and realistic alternatives. Present alternatives in a comparison table with columns for technique/tool, advantages, drawbacks and risks, reason not selected, and reconsider when. The first column must name the option, briefly describe how it works, and link to official documentation. For a project-defined workflow without its own official documentation, label it as such and link to the relevant documented mechanisms rather than imply external endorsement. Support claims with project evidence or authoritative sources; do not fabricate measurements or benefits.
4. **Draft the record.** Use the project's template or the bundled template, retaining the comparison table where the project format permits it. Record one specific significant decision; separate independently changeable choices into focused ADRs and connect related records through the project's topic folders, index, and links. Keep the title specific, the decision unambiguous, and consequences tied to the actual system. Explain the chosen option's rationale and boundaries, and include positive and negative consequences. Format prose bullets as `- **Short summary**: details`: the bold label makes the point scannable, and the following text supplies its reasoning. Keep labels brief and meaningful, not whole sentences. Write substantive table cells that explain concrete trade-offs, not one-sentence dismissals or generic labels. Add supporting prose only when needed for clarity; the table is the primary alternatives view.
5. **Set status and date accurately.** Use the project's status vocabulary. A draft awaiting approval is not accepted; record it as Proposed when that status is supported. Use the actual decision date, and do not imply approval that has not occurred.
6. **Return or save appropriately.** Return a draft for review unless the user asks for a file and its location is established. Do not modify an existing ADR unless asked. For an explicitly requested revision, preserve the original decision date and existing history; append a dated entry to the optional same-document changelog rather than silently rewriting or replacing the recorded decision. If independent decisions are extracted or moved, preserve each decision's original date, status, and reasoning, add a dated explanation of the split or move and its rationale, and cross-link the source and resulting records. Do not add a changelog for initial creation. For a substantially changed decision, follow project supersession conventions instead of using the changelog to replace the prior decision. Follow any applicable agent role boundaries, approval requirements, and file-editing permissions.
7. **Review the result.** Confirm the decision follows from the stated context, alternatives are fairly represented, links work, and the status, date, and numbering match project conventions. Check that a reader can reconstruct the trade-offs without the original conversation, that each substantial alternative explains both its appeal and its rejection, and that prose bullets use a short bold summary followed by details.

For revisions, separate the optional changelog from the record with `---` and a level-one `# Changelog` heading. Add dated entries in `YYYY-MM-DD` format with a short explanation of what changed and why; use the [template](./references/ADR-TEMPLATE.md) for the layout.

## Scope and Organization

- **One ADR, one significant decision**: Give each record one specific decision with its own rationale, consequences, and alternatives. Combining independent decisions makes records harder to read and maintain, and couples their histories so that changing one choice can make the rest confusing or misleading.
- **Split by independence, not length**: Separate choices only when they can be changed independently, have distinct decision drivers, or can be reconsidered on different timelines. Keep related details together when they are boundaries or consequences of the same decision; do not split a coherent decision to meet an arbitrary word count.
- **Group related records**: When several focused ADRs belong to one topic, place them in topic subfolders where project conventions allow, and connect them through the established index, README, and cross-links. Follow existing paths and numbering; do not invent a competing index or convention.
- **Preserve history when extracting**: When splitting or moving decisions out of an existing ADR, preserve each decision's original date, status, and reasoning. Add a dated explanation of the split or move, why it was needed, and links between the original and resulting records. Do not silently replace the recorded choices. For a substantially changed choice, use the project's supersession convention and retain the prior record.

## Gotchas

- **Explicit approval**: An ADR recommendation or draft does not become an accepted decision without the responsible person's approval.
- **Existing conventions**: Discover the project's ADR location, numbering, and lifecycle vocabulary before writing a file; ask if a consequential convention is missing.
- **Durable reasoning**: Record the rationale and consequences that future maintainers need, not a step-by-step account of code changes.
- **Complete comparisons**: Scale detail to the decision's complexity. Explain concrete effects on the project instead of labels such as "simpler" or "more complex"; avoid both thin table rows and filler added to meet a sentence count. Table formatting must preserve the reasoning, not compress it away. Use "Not applicable" with a brief explanation when reconsideration does not apply, rather than invent a condition.
- **Grounded evidence**: Label assumptions and uncertainty; avoid unsupported performance, cost, security, or operational claims.
- **Proportionate records**: Record significant choices, not every design detail or routine code-level decision.

## References

- **Template and examples**: Use the [ADR template](./references/ADR-TEMPLATE.md) when no project format exists.