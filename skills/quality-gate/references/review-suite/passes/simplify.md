# Pass: simplify

**id:** `simplify`  
**Maps to:** pr-review-toolkit `code-simplifier` · quality-gate-codex §6 simplifier · mattpocock/skills code-review smell baseline

## When

Run **after** correctness-oriented passes (code-correctness, silent-failures, tests). Still required for suite Pass on code diffs.

## Checklist

- Unnecessary abstraction, duplication, dead code
- Over-generalized config for a single use
- Conditionals or state machines that can be clearer without behavior change
- Local style churn that should be avoided (flag as Low or drop)
- Opportunities to reduce support burden without rewrite

## Smell baseline (Fowler, *Refactoring* ch.3)

Match against the diff. Each smell is a labelled heuristic ("possible Feature Envy"), never a
hard violation. A documented repo standard overrides the baseline; skip anything tooling enforces.

- **Mysterious Name** — name doesn't reveal what it does or holds → rename; if no honest name comes, the design's murky
- **Duplicated Code** — same logic shape in more than one hunk/file of the change → extract the shared shape
- **Feature Envy** — method reaches into another object's data more than its own → move it onto the data it envies
- **Data Clumps** — same few fields/params keep travelling together → bundle into one type
- **Primitive Obsession** — primitive standing in for a domain concept → give the concept its own small type
- **Repeated Switches** — same `switch`/`if`-cascade on the same type recurs across the change → polymorphism or one shared map
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff → gather into one module
- **Divergent Change** — one module edited for several unrelated reasons → split per reason
- **Speculative Generality** — abstraction/hooks for needs nothing has → delete; inline until a real need shows
- **Message Chains** — long `a.b().c().d()` navigation → hide the walk behind one method
- **Middle Man** — class/function that mostly delegates onward → cut it, call the target direct
- **Refused Bequest** — implementer ignores/overrides most of what it inherits → composition over inheritance

## Rules

- Do not suggest simplification that changes behavior or broadens scope
- Findings are often Medium/Low; rarely Critical
- Do not rewrite working code for taste alone
- Label baseline smells as judgement calls, citing the smell name and the hunk

## Artifact reminder

Emit `pass_id: simplify` with full artifact contract.
