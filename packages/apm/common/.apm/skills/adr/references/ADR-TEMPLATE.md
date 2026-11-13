# ADR Template

Use this template when the project has no established ADR format. Follow existing naming and numbering conventions; the number placeholder does not establish a new numbering scheme.

## Scope and Organization

Record one specific significant decision per ADR. Combining independent decisions makes the record harder to read and maintain, and couples their histories: a change to one choice can leave the others confusing or misleading. Split choices only when they can be changed independently, have distinct decision drivers, or can be reconsidered on different timelines. Keep a coherent decision together, regardless of length; do not split by arbitrary word counts.

Group related focused ADRs in topic subfolders where project conventions allow. Link them through the established index, README, and relevant ADRs; follow existing paths and indexing conventions rather than creating a competing structure.

When extracting or moving decisions from an existing ADR, preserve each decision's original date, status, and reasoning. Add a dated explanation of what was split or moved and why in the source and resulting records' changelogs, with cross-links between the original and resulting records. Do not silently replace the original choices. A substantially changed choice should supersede the prior ADR according to project conventions.

Provide enough detail to reconstruct the decision without the original conversation. Use a comparison table as the primary alternatives view, with the former bullet categories as columns. The first column names the technique/tool, briefly describes it, and links to official documentation. Retain the option's appeal, concrete trade-offs, and reason for rejection; table formatting is not a reason to reduce an alternative to a one-sentence dismissal.

For a project-defined technique without official documentation, state that explicitly and link to the documented supporting mechanisms. Add prose outside the table only when a trade-off needs further explanation. Escape literal pipe characters inside cells so they do not create extra columns.

Format prose bullets as `- **Short summary**: details`. Use a brief, meaningful bold label for scanning and keep the explanation outside the bold text. Apply this to consequences, constraints, and other prose lists; alternatives remain in the comparison table.

For an initial ADR that is not extracted from an existing record, omit the changelog. When revising an existing ADR, preserve its original date and history, and append an entry stating briefly what changed and why. Do not silently rewrite or replace the recorded decision; for a substantial change, follow project supersession conventions. Use this optional section at the end of the document:

```markdown
---
# Changelog

- YYYY-MM-DD: <Briefly state what changed and why.>
```

---

## Template

```markdown
# ADR-<number>: <Title of the Decision>

## Context
<Describe the problem, relevant current state, constraints, and decision drivers. Separate verified facts from assumptions and unresolved questions.>

---

## Decision
<State the chosen option, its boundaries, and why it best meets the decision drivers. Describe the resulting architecture or responsibilities without turning this into an implementation plan.>

---

## Consequences

### Positive
- **<Benefit summary>**: <Explain a concrete benefit and how the chosen option produces it. Repeat for other material benefits.>

### Negative
- **<Drawback summary>**: <Explain a concrete cost, risk, or limitation and any necessary safeguards. Repeat for other material drawbacks.>

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [<Option name>](<Official documentation URL>): <Describe what it is and how it addresses the problem.> | <Explain its concrete appeal for this project.> | <Explain material costs, risks, and limitations against the decision drivers.> | <Explain why those trade-offs outweigh its advantages here.> | <Identify changed constraints that would make this preferable, or explain why reconsideration does not apply.> |

<Repeat for each substantial alternative. Keep enough detail in each row for a reader to reconstruct the comparison without the original conversation.>

---

## Status
<Use the project's status vocabulary. Otherwise use Accepted, Proposed, Deprecated, or Superseded. Use Proposed unless approval is explicit.>

---

## Date
<Actual decision date: YYYY-MM-DD.>
```

---

## Example 1: Vector Search Storage

This hypothetical scenario demonstrates decision reasoning, not measured product comparisons. A real ADR must verify capabilities, deployment compatibility, costs, and performance. Example dates and statuses are not defaults.

```markdown
# ADR-001: Use Redis for Semantic Search Vector Storage

## Context

The service needs similarity search over embeddings generated from canonical documents. The index is derived data and must be rebuildable; it is not the authoritative document store.

Assume the team already operates Redis and prefers extending an existing platform over introducing another service for a bounded initial corpus. Workload-specific search quality, capacity, and acceptable recovery time remain to be validated.

---

## Decision

Use [Redis Stack](https://redis.io/docs/stack/) for the derived vector-search index, subject to compatibility and workload validation. Retain canonical documents separately and a documented way to rebuild the index.

The deciding factor is the team's assumed operational familiarity, not a claim that Redis is universally faster or cheaper. Revisit this choice if validation shows that capacity or recovery time fails the service's requirements.

---

## Consequences

### Positive

- **Operational reuse**: Reusing a platform the team already operates avoids introducing a separate service lifecycle for the initial deployment.
- **Replaceable index**: Treating the index as derived data permits replacement without making the search backend the migration source for canonical documents.

### Negative

- **Workload validation**: Capacity, latency, and recovery behavior require workload-specific evidence; existing familiarity does not establish acceptable performance.
- **Recovery obligations**: The service needs explicit behavior for unavailable or stale search results and a tested rebuild procedure.
- **Migration effort**: A future backend replacement still requires integration changes and regression testing.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [PostgreSQL with pgvector](https://github.com/pgvector/pgvector): place vector search alongside data managed in PostgreSQL. | If PostgreSQL already owns the relevant data, this could reduce synchronization boundaries and reuse its operational practices. | For this hypothetical team, another database ownership decision would be needed. Sharing database resources with other workloads would also need validation. | The scenario prioritizes the team's existing platform for a derived index. This is an operational-fit judgment, not a claim that pgvector is slower. | PostgreSQL becomes the canonical data platform or workload evidence favors keeping search alongside it. |
| [Pinecone](https://docs.pinecone.io/): evaluate a separate search-service option. | A separate service is attractive if its verified capabilities and operating model better meet the team's search requirements. | Provider integration, pricing, data-handling requirements, and export or rebuild paths would need assessment. | The initial scope does not justify a new provider relationship before evaluating the existing platform. No comparative cost conclusion has been established. | Internal search operations become a larger burden and provider requirements have been verified. |
| [Weaviate](https://docs.weaviate.io/weaviate): evaluate a dedicated search platform with its own integration and ownership contract. | A dedicated platform may be preferable if its verified capabilities address requirements the existing deployment cannot meet. | The team would need to evaluate its operating model, compatibility, and migration path alongside the existing stack. | This scenario has not established a capability gap that warrants another platform. The availability of more options alone does not justify additional integration. | New requirements or validation failures expose a concrete gap in the selected backend. |

---

## Status
Proposed: validation remains outstanding and approval has not been recorded.

---

## Date
2025-01-15
```

---

## Example 2: Object Storage for Uploaded Reports

This generic hypothetical example demonstrates a single storage decision. The stated deployment and requirements are assumptions for the example, not product performance claims.

```markdown
# ADR-002: Store Uploaded Reports in Amazon S3

## Context

A web service accepts report files for later download. Assume the service runs in AWS and already stores each upload's identifier and ownership in PostgreSQL. The decision is where to store the file bytes; metadata design, authorization, retention, and download delivery are outside this ADR. The service has no established performance threshold that selects a storage option.

---

## Decision

Store report bytes in [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html). Keep the existing relational records as the source for upload identifiers and ownership. This choice aligns the file-storage service with the assumed AWS deployment; it does not prescribe a particular upload or download flow.

---

## Consequences

### Positive

- **Storage boundary**: File bytes reside in an object-storage service while the existing database continues to hold upload metadata.
- **Deployment alignment**: The selected storage service is in the assumed deployment provider, avoiding a second cloud-storage provider for this decision.

### Negative

- **Lifecycle coordination**: The service must keep object operations consistent with the metadata records, including handling failed or incomplete operations.
- **Provider coupling**: The service depends on Amazon S3 APIs and AWS configuration; moving file storage to another provider would require migration and integration work.

---

## Alternatives Considered

| Technique/tool (description and reference) | Advantages | Drawbacks and risks | Reason not selected | Reconsider when |
|---|---|---|---|---|
| [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html): store report bytes in AWS object storage. | Fits the assumed AWS-only deployment and keeps file bytes separate from the relational upload records. | Adds object-storage integration and requires the service to coordinate object and metadata operations. | Selected because the example assumes AWS deployment and a separate object-storage boundary. | Reconsider if the deployment provider or the requirement to keep bytes outside the relational database changes. |
| [PostgreSQL large objects](https://www.postgresql.org/docs/current/largeobjects.html): store report bytes in PostgreSQL large objects. | Keeps the file contents within the database system already holding upload metadata. | Places file bytes and metadata in the same persistence system, which does not match the example's preference for a separate object-storage boundary. | The scenario prefers a dedicated object-storage service for bytes rather than adding them to the relational persistence design. | Reconsider if keeping file contents with relational data becomes more important than a separate storage boundary. |
| [Azure Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction): store report bytes in Azure's object-storage service. | Provides an object-storage option with a distinct service boundary. | Under the assumed AWS-only deployment, it would introduce another cloud provider's storage service and configuration. | The scenario's deployment assumption favors storage in AWS. | Reconsider if the service moves to Azure or its deployment constraints otherwise change. |

---

## Status

Proposed: the example states a recommendation; no approval is implied.

---

## Date

2026-11-13
```