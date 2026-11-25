# Chaos Experiments and Fault Environments for Agents

Use these experiments before raising an operations agent to L3, and during
the bake phase of a release.

## Fault environment qualification

Run the agent against injected faults before you trust it to act alone.
Public benchmarks show the shape: SREGym (Clark et al., arXiv 2605.07161,
CC BY 4.0) injects faults at several layers with background noise and
correlated failures, and scores diagnosis and mitigation separately. Agents
vary widely across failure types, so a single overall score is not enough.

1. Choose fault types that match the agent's real scope.
2. Score diagnosis and mitigation separately, per fault type.
3. Record the result as promotion evidence in `agent-autonomy-levels`.

## Experiment parameters

The Microsoft Agent SRE Governance 1.0 specification (MIT) defines chaos
experiments with these controls:

| Parameter | Rule |
| --- | --- |
| Blast radius | A fraction from 0 to 1 of agents or traffic affected; clamp to that range. |
| Duration | A default and a maximum; the experiment ends on its own. |
| Abort conditions | SLI thresholds that end the experiment at once. |
| Fault type | One named type per experiment. |

## Fault types to include

- Tool timeout, tool error and malformed tool output.
- Tool schema change without notice.
- Provider rate limiting and model outage.
- Reworded or ambiguous instructions.
- Stale or poisoned memory entries.
- A change to an agent's trust score or permissions during a run.

## Rules

1. Start with a blast radius of 0.01 or a single non-production agent.
2. Define abort conditions before you start.
3. Keep the stop control from `tool-blast-radius` ready during every run.
4. Add each failure found to the regression suite.
