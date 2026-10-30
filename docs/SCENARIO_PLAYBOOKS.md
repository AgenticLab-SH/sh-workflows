# Unseen task practice playbooks / 미지 과제 훈련

These are **synthetic, reusable exercise prompts**, not leaked or reconstructed exam tasks. Use fictional data. Each scenario intentionally leaves out some requirements; ask the stakeholder before implementing.

## Workflow template used for every scenario

1. Summarize the actual goal and who will use the result.
2. Identify missing input format, business rules, exception policy, required output, and success examples.
3. Ask 3-5 high-impact clarifying questions, then state remaining assumptions.
4. Implement a runnable minimum slice with an AI agent **only where the environment permits**.
5. Test valid, invalid, boundary, duplicate, and ambiguous inputs relevant to the task.
6. Record what actually ran, changed files, known limits, and one safe next improvement.
7. Without AI, explain architecture, why this design, one observed failure/fix, and one limitation.

| Synthetic brief | Clarifications to seek | Minimum demonstrable output | Adversarial check |
| --- | --- | --- | --- |
| Campus event RSVP sorter | Capacity, duplicate names, waitlist rules | Summary of accepted/waitlisted/invalid RSVP records | Duplicate ID with different email |
| School library book returns | Due dates, timezone, lost item rules | Local overdue report from synthetic CSV | Null return date, DST boundary |
| Fictional e-commerce refund requests | Eligibility window, partial refund, disputed claim | Reviewer-oriented decision with reasons | Same order in two records |
| QA sensor daily summary | Units, missing sample handling, calibration version | Validated aggregation and anomaly flags | Celsius versus Fahrenheit |
| Internal helpdesk inbox | Categories, escalation urgency, private data | Draft categories and review queue | Conflicting labels or urgent safety case |
| Translation of product notices | Regional English variant, legal guarantees | Korean/English copy aligned by meaning | Placeholder and currency unchanged |
| Multi-version SOP comparison | Which document has authority, effective date | Conflicts and questions before decisions | Same rule with conflicting dates |
| Local feedback dashboard | Valid event records, time interval, privacy | Counts and charts using fake data | Duplicate events inflate total |
| Broken payment-free demo app | Expected command, regression scope, error log | Narrow bug fix, before/after test evidence | Old passing behavior regresses |
| Appointment request API | Required fields, duplicates, invalid date policy | Tested JSON API endpoints | Same request submitted twice |
| Policy-safe recommendations | Data sources, exclusions, quality threshold | Explainable and testable shortlist | Missing category or conflicting rules |
| Project handoff summary | Implemented versus intended, owner, next action | Reproducible README and risk list | Claiming nonexistent tests passed |

## Example generic acceptance table

| ID | Input | Expected policy | Observed result | Status |
| --- | --- | --- | --- | --- |
| A | Valid synthetic record | Produce documented result | Fill after execution | Not run |
| B | One missing required field | Do not silently accept | Fill after execution | Not run |
| C | Conflicting rules | Flag conflict for human review | Fill after execution | Not run |
| D | Edge just below/above boundary | Separate acceptance outcomes | Fill after execution | Not run |

Do not assume all 12 types will appear in any real test. Always defer to the actual task instructions. No sample counts or weights are official.

