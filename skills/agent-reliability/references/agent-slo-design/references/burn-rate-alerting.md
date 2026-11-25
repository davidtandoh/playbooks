# Burn-Rate Alerting and Error-Budget Policy

## Two-window burn-rate alerts

Burn rate is how fast the service spends its error budget relative to the
rate that would spend it exactly over the SLO window. A burn rate of 1 uses
the whole budget by the end of the window.

Fire an alert only when both a long window and a short window exceed the
threshold. The short window is about one twelfth of the long window. The long
window stops brief spikes from paging; the short window lets the alert clear
soon after recovery.

The SRE Workbook chapter "Alerting on SLOs" gives these starting points for a
99.9% target over 30 days. They are restated as facts; the Workbook text is
CC BY-NC-ND 4.0 and is not reproduced.

| Response | Burn rate | Long window | Short window | Budget spent before it fires |
| --- | --- | --- | --- | --- |
| Page | 14.4 | 1 hour | 5 minutes | 2% |
| Page | 6 | 6 hours | 30 minutes | 5% |
| Ticket | 1 | 3 days | 6 hours | 10% |

For a low-traffic agent, one failure can exceed these rates. Lengthen the
window, add synthetic probe tasks, or group similar workflows before paging.

The Microsoft Agent SRE Governance 1.0 defaults are a 30-day window, a warning
at burn rate 2 and a critical alert at burn rate 10. Its exhaustion actions are
alert, freeze deployments, open the circuit breaker, and throttle.

## Error-budget policy template

```text
Service / workflow: <name>        SLO: <link>        Owner: <role>
Approvers: <service owner>, <reliability owner>, <product owner>

While budget remains: release prompt, model, tool and harness changes
through eval-gated-releases.

When the 30-day budget is exhausted:
- Freeze non-reliability changes to this workflow until the budget recovers.
- Allowed during the freeze: security fixes, reliability fixes, rollbacks.
- Lower autonomy for affected action types by one level.

SLI accounting: count every customer-facing failure in the agreed SLO
scope, including dependency outages. Exclude only agreed out-of-scope test
traffic. Correct miscategorised events with an audit record; retain actual
customer failures.

Release-freeze exemptions require the policy approvers to record a reason.
They never remove customer failures from SLI accounting. Non-reliability
work may continue for a dependency outage only when its owning team has
frozen releases to address reliability. A separate dependency SLO and owner
alone do not qualify.

Postmortem rule: a single incident that consumes more than 20% of the budget
needs a postmortem with at least one highest-priority action item.

Escalation: disagreement about the budget or an exemption goes to <role>.
Review: revisit this policy every <quarter>.
```

The structure follows the SRE Workbook "Example Error Budget Policy"; the
wording is original.
