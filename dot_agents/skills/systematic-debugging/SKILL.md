---
name: systematic-debugging
description: Reproduce a bug or failing test, isolate its root cause, make a minimal scoped fix when requested, and verify the result.
---

# Systematic Debugging

1. Capture the exact error, observed behavior, environment, and reproduction steps. Separate facts from hypotheses.
2. Reproduce the failure before changing code. If it cannot be reproduced, report what was tried and request the missing evidence rather than guessing.
3. Trace the failing path and inspect recent relevant changes. Form competing root-cause hypotheses and run the smallest experiment that distinguishes them.
4. Explain the root cause with concrete file/symbol/test evidence. Do not patch symptoms or broaden scope.
5. Implement a minimal fix only when implementation is requested and permitted. Add or update a regression test that fails before the fix where practical.
6. Run the focused regression test, then relevant broader checks. Report exact commands and outcomes; distinguish not-run checks from passing checks.
7. If blocked, return the reproduction, evidence, hypotheses ruled out, and next useful diagnostic. Never claim verification that did not happen.
