# Release privacy review

**PUBLIC RELEASE — publication authorized by the repository owner on 16 October 2026.**

The initial remote commit `7a97c0053c12fd73105433c825e3fe873d3ae123` was verified before publication: its 28 disclosed files matched the reviewed package, all 44 synthetic tests passed in GitHub CI, and the disclosure scanner reported no findings. The owner then approved public visibility. Later documentation changes have their own commit and CI records.

The candidate is prepared from an explicit set of reviewed files with a new Git root. Previous staging histories, workflow run records, private audit ledgers, source locators, and source-repository objects are excluded.

## Gates

| Gate | Requirement |
| --- | --- |
| Payload | Only allowlisted summaries, original synthetic examples, fixtures, tests, and release checks |
| Identity | GitHub users.noreply author addresses and the exact GitHub platform noreply committer address; no private contact details |
| Automation | Read-only CI permissions; no cleanup job or deletion permission |
| History | New independent root; no imported branches, tags, or prior staging objects |
| Verification | Synthetic tests and disclosure scan pass for the exact candidate |
| Destination | Fresh repository, initially PRIVATE, with reviewed owner and visibility |
| Publication | Owner approval received after remote commit and CI verification; public visibility verified |

Keep every original research and earlier staging repository private. Clearing reachable history in an existing repository cannot establish erasure of unreferenced hosted objects. This release therefore requires a fresh destination; uploading a Git bundle or an entire prior repository would violate its disclosure boundary.

No purge, platform-cache deletion, legal clearance of private source, or independent device qualification is asserted. Publication does not establish historical authenticity or guarantee the absence of every possible disclosure. The underlying research and earlier staging repositories remain private.
