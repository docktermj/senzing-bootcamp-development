# `specs/`: the rule register and its ledgers

This directory holds live records only. New work is tracked as **GitHub issues**, and no
command writes a new file here.

| File | What it is |
| --- | --- |
| [`INVARIANTS.md`](INVARIANTS.md) | The canonical invariants. Machine-extended by design: `/review-invariants` appends to it after maintainer sign-off. |
| [`IMPLEMENTED.md`](IMPLEMENTED.md) | The implementation ledger, and the only completion signal the repository has (INV-182). It starts on 2026-11-14. |
| [`DECLINED.md`](DECLINED.md) | The declined-work record: decisions not to build, each with its reason and the condition for revisiting it (INV-217). |
| [`mcp-coverage.jsonl`](mcp-coverage.jsonl) | `/delegate-to-mcp-server`'s coverage ledger, appended on every run. |
| [`README.md`](README.md) | This notice. Its table is the one authoritative list of the files that belong here. |

## The archive

Until 2026-11-14 the bootcamp was developed as a Claude plugin in
`docktermj/senzing-bootcamp-claude-plugin-development`. Its `specs/` directory held the spec
file behind each change, frozen since 2026-09-15, and the ledger of everything implemented
there. That repository is the archive, pinned at the commit this one was imported from:

<https://github.com/docktermj/senzing-bootcamp-claude-plugin-development/tree/195c17dcc2fe6af7cf8097cc10cdc80f5da18eb2/specs>

An invariant cites its source by spec slug or by issue number: `(Source: write-gate-tests,
2026-07-24)`. A slug with no entry in this repository's ledger resolves in the archive, as a
spec file of that name or as an entry in the archived ledger. An issue number dated before
2026-11-14 is an issue in that repository.
