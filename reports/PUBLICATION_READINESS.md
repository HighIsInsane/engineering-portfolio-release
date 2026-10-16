# Release privacy review

**PRIVATE CANDIDATE — explicit publication approval pending.**

The candidate is prepared from an explicit set of reviewed files with a new Git root. Previous staging histories, workflow run records, private audit ledgers, source locators, and source-repository objects are excluded.

## Gates

| Gate | Requirement |
| --- | --- |
| Payload | Only allowlisted summaries, original synthetic examples, fixtures, tests, and release checks |
| Identity | Exact GitHub noreply author/committer addresses; no private contact details |
| Automation | Read-only CI permissions; no cleanup job or deletion permission |
| History | New independent root; no imported branches, tags, or prior staging objects |
| Verification | Synthetic tests and disclosure scan pass for the exact candidate |
| Destination | Fresh PRIVATE repository with reviewed owner and visibility |
| Publication | Explicit owner approval after exact remote commit and CI verification |

Keep every original research and earlier staging repository private. Clearing reachable history in an existing repository cannot establish erasure of unreferenced hosted objects. This release therefore requires a fresh destination; uploading a Git bundle or an entire prior repository would violate its disclosure boundary.

No purge, platform-cache deletion, legal clearance of private source, or independent device qualification is asserted. No third party has been contacted. The current task authorizes privacy preparation, not public visibility.
