# Design Guidelines

## The process

Every good design passes through three phases. Know which one you're in.

1. **Naive.** The obvious simple solution. Stress test it; the edge cases will surface.
2. **Over-engineered.** The convoluted version that handles every edge case but is a mess. This is a draft, never the destination.
3. **Right.** Simple *and* durable. Correctness pops out of the natural shape of the design instead of being bolted on. If you're still patching edge cases, you haven't found it yet.

Don't ship phase 1 or phase 2. Don't optimise anything until you've reached phase 3.

## The principles

**1. Question every requirement.**
For each explicit and implicit requirement, ask: is this first-principles, or arbitrary? Keep only what survives the question.

**2. Delete relentlessly.**
Remove dead code, legacy paths, redundant logic, and speculative generality. If you're not occasionally forced to add something back, you're not deleting enough.

**3. Keep flow linear.**
One clean path through the code, top to bottom. Reach for early exits and null-check branches only when they're strictly necessary, not to save minor cycles.

**4. Let errors propagate.**
Trust the runtime. Write try/except only where you can genuinely handle the failure. Let natural errors surface naturally; raise manually only when the failure would otherwise be silent. Access arrays and attributes directly; if the contract guarantees presence, code like it.

**5. Make contracts strict.**
Require everything you can. Pass an empty data structure instead of making the parameter optional. Where something genuinely must be optional, use `Optional[X]`, not `X | None`.

**6. One concept, one implementation.**
One type per concept. One normalisation step (better: standardise so none is needed). Before writing a new pattern or abstraction, find the existing one in the codebase and align with it. Symmetry is a feature.

**7. Everything in its home.**
Constants live in `constants.py`. Types live in `types.py` and are pydantic models, like the rest of the codebase. Functions live in the file that matches their concern. If something's in the wrong place, move it.

**8. Keep it DRY, atomic, separated.**
Each function does one thing. Each concern lives in one place. Each piece of knowledge has exactly one representation.

**9. When in doubt, simplify.**
Complexity is the default failure mode. The burden of proof is always on the more complicated option.

## The test

Before merging, ask one question: *could this be simpler?* If yes, it's not done.
