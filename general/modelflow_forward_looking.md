# ModelFlow: Solving Forward-Looking Models, and Making It Fast

## Summary

A model with leaded endogenous variables cannot be solved one period at a time: what happens in 2030 depends on what is expected for 2031, which depends on 2032, and so on to the end of the horizon. ModelFlow solves such models by stacking every period into one system and applying Newton's method to it, as described in [Structure and solution](modelflow_structure_and_solution.md).

This chapter is about what that costs and how to bring the cost down. The stacked system has as many unknowns as variables times periods, and for a large model over a long horizon that is well over a million. At that size almost all the time, and all the memory, goes to the linear algebra of the Newton step, and the right choice of linear solver decides whether the model can be solved at all.

Two models are used throughout because they sit at opposite ends of the range. **FRB/US** with model-consistent expectations has a small stacked core (95,748 unknowns) that is badly conditioned. **MAKRO**, the Danish DREAM group's model translated from GAMS, has 20,474 equations solved over 100 years: 1.5 million unknowns in one system. What works best for one fails on the other, and the reasons show what to look for in a new model.

---

## Why leads change the problem

For a model with lags only, the periods form a chain: once 2029 is solved, 2030 is a self-contained system with 2029 as data. A lead breaks the chain. An equation such as

$$
c_t = \alpha\, c_{t+1} + \beta\, y_t
$$

makes period $t$ depend on $t+1$, and the lagged equations elsewhere make $t+1$ depend on $t$. The periods are simultaneous with each other, and the horizon needs an end: a **terminal condition** that pins down the last period, typically that the model is on its steady-state path.

Two approaches have been used for decades. **Fair-Taylor** iteration keeps the period-by-period solve, treats the leads as given, and repeats the sweep over the horizon until the expectations stop changing. It is simple and needs no new machinery, but it can need many sweeps and does not always converge. **Stacked Newton** solves all periods as one system. It converges in a handful of iterations when it converges, but each iteration solves a linear system of size variables times periods. That is the approach of TROLL {cite:p}`hollinger_beyond_2000`, of Dynare's perfect-foresight solver {cite:p}`adjemian_dynare_2011`, and of ModelFlow's `newtonstack_ng`.

The terminal condition matters in practice. The horizon of a stacked solve should end where the model's own terminal treatment applies. When MAKRO was solved over a span cut short, 2030–2039, Newton stalled at an equation error of about one per cent: the last solved year had no valid condition on what comes after it. The same model solved to its terminal year 2129 converged in 6–7 iterations.

---

## The stacked system

With $n$ endogenous variables and $T$ periods the stacked Jacobian has $nT$ rows. Each period's equations involve that period's variables and a few lags and leads, so the Jacobian is a **block band**: a diagonal of period blocks, with off-diagonal blocks only as far out as the longest lag and lead.

| | FRB/US MCE | MAKRO 2026 |
| --- | --- | --- |
| Equations | 285 | 20,474 |
| Periods solved together | 404 quarters | 100 years |
| Stacked unknowns | 95,748 (the core) | 1.5 million |

MAKRO's stacked Jacobian has 6.8 million non-zeros. FRB/US's is much smaller but far worse conditioned, with a condition number estimated at around $10^{18}$.

Each Newton iteration then has four parts:

1. **Evaluate the model** over the whole horizon to get the residuals.
2. **Build the Jacobian**: evaluate the derivatives and place them in the sparse matrix.
3. **Factorize** it.
4. **Solve** with the factors to get the Newton step.

How these costs compare depends almost entirely on the size of the system. For FRB/US the whole solve of a shock takes 0.2 seconds once the Jacobian exists. For MAKRO one factorization takes most of a minute and uses 16 GB.

---

## Making the system smaller

The first optimization is not to stack what does not need stacking. ModelFlow's graph analysis divides the model into prolog, simultaneous core and epilog (see [Structure and solution](modelflow_structure_and_solution.md)). For a stacked solve the same idea applies with one extra rule: a prolog or epilog variable can be solved period by period only if it never reads a lead of a variable in its own group.

With `split=1`, the default, `newtonstack_ng` solves the prolog as an ordinary forward loop over the periods, stacks only the core, and solves the epilog as a loop after convergence. In FRB/US that leaves 237 of the 285 variables in the core (29 prolog, 19 epilog):

| FRB/US MCE, `ljit=True` | New Jacobian | Later shocks |
| --- | --- | --- |
| `split=1` (default) | 1.8 s | 0.20–0.22 s |
| `split=0`, everything stacked | 2.5 s | 0.25–0.30 s |

Both give the same solution to within the convergence tolerance.

---

## Reusing work

Most of the cost of a stacked solve is in building and factorizing the Jacobian, and most of that work does not have to be repeated.

**Keep the Jacobian between shocks.** In a mildly nonlinear model the Jacobian at the baseline is a good enough approximation for a whole set of experiments. With `newton_reset=0` (the default after the first solve) ModelFlow keeps the factorization, and each further shock costs only model evaluations and back-substitutions with the existing factors. For FRB/US that is the difference between 1.8 seconds and 0.2 seconds per shock. The `nonlin` option decides when a fresh Jacobian is needed during the iterations.

**Keep the derivatives between sessions.** The symbolic derivatives of a large model take time to generate. `modeldump(derivatives=True)` stores them with the model, and the next session starts from them. For MAKRO this saves about two minutes on the first solve.

**Skip analysis the stacked solve does not use.** Loading MAKRO with the full structural analysis takes over two minutes, almost all of it in the search for feedback variables, which the stacked solver never uses. Loading with `straight=True` takes 1.5 seconds.

**Compile the model.** `ljit=True` compiles the model evaluations with Numba. It speeds up step 1 and the period loops of the split, but not the linear algebra. For a model the size of MAKRO the linear algebra dominates, so the gain is small.

**Solve large shocks in stages.** Newton takes the full step without a line search. For a large shock, starting from the baseline can be too far from the solution. DREAM's own procedure, which ModelFlow's MAKRO tools copy, is to solve with one per cent of the shock, scale the response up by a hundred, and use that as the starting point for the full shock. Only one of DREAM's eleven standard shocks, public investment, needed more: an extra stage at 30 per cent, and a Jacobian recalculated at the start of the last stage and every third iteration after that.

---

## Choosing the linear solver

The `factorizer` option selects the linear solver for the Newton step:

| `factorizer=` | Method | Strength | Weakness |
| --- | --- | --- | --- |
| default (SuperLU) | sparse LU with partial pivoting | robust, exact pivoting; very fast on a band | fill grows quickly beyond some 10^5 unknowns |
| `'umfpack'` | sparse LU, symbolic analysis reused | per-period Newton over many periods | no gain on one stacked system |
| `'pardiso'` | MKL PARDISO LU, multi-threaded | fast on large systems | static pivoting: inaccurate on a weak diagonal |
| `'normal'` | Cholesky of $J^\top J$ with PARDISO | no pivoting needed; handles very large systems | squares the condition number |
| `'mumps'` | MUMPS LU with real pivoting and METIS ordering | robust on large systems | slower |

The two example models need opposite choices.

**FRB/US: SuperLU with the natural ordering.** The stacked core is banded, and ordering the unknowns period by period (`permc_spec='NATURAL'`, the stacked default) keeps the fill inside the band. A fill-reducing ordering designed for general matrices scatters the band:

| FRB/US MCE | New Jacobian | Later shocks |
| --- | --- | --- |
| SuperLU, `NATURAL` (default) | 1.8 s | 0.20 s |
| SuperLU, `COLAMD` | 9.4 s | 0.25–0.30 s |
| UMFPACK | 2.5 s | 0.41–0.47 s |
| MUMPS | 4.4 s | 0.36–0.45 s |
| PARDISO, normal equations | fail | |

Because the FRB/US Jacobian is so badly conditioned, PARDISO's static pivoting and the squared conditioning of the normal equations both lose all accuracy, and ModelFlow raises an error rather than give Newton a wrong step.

**MAKRO: the normal equations.** At 1.5 million unknowns the picture reverses. SuperLU's fill makes it fail beyond 20–30 years. PARDISO's LU fails because 26,300 of the Jacobian's diagonal entries are zero, which static pivoting cannot handle. What works is to solve the Newton step as a least-squares problem:

$$
\min_{\Delta x} \lVert J \Delta x + F \rVert^2
\quad\Longleftrightarrow\quad
J^\top J\, \Delta x = -J^\top F
$$

$J^\top J$ is symmetric and positive definite, so PARDISO can factorize it by Cholesky without any pivoting. The cost is that the condition number is squared. ModelFlow counters this in two ways. It scales $J$ first (rows to a largest element of one, then columns to unit norm). And it refines the solution against $J$ itself, not against $J^\top J$:

$$
x_{k+1} = x_k + (J^\top J)^{-1} J^\top (b - J x_k)
$$

Each refinement step costs one solve with the factors, and the accuracy lost to the squaring comes back. MUMPS also solves MAKRO, but takes more than twice as long.

Neither choice is better in general. A **banded, badly conditioned** system wants an exact LU along the band. A **very large, reasonably scaled** system with structural zeros on the diagonal wants a method that needs no pivoting.

---

## Tuning the large solve

Once the normal equations make MAKRO solvable, the solve of one shock over the whole horizon takes about three minutes. About a quarter of the time goes to the factorization, half to solves with the factors, and the rest to model evaluation and Jacobian assembly. Three settings shorten the first two parts. All three are options of `modelfactorize.normal` (and `modelfactorize.pardiso`):

```python
import modelfactorize
FACT = modelfactorize.normal(iparm={1: 13}, refine_tol=1e-9)    # made once
result = mmakro(df, 2030, 2129, solver='newtonstack_ng', factorizer=FACT)
```

**A faster factorization (`iparm`).** oneMKL 2026 added an aggressive factorization mode for large matrices. It is selected by the tens digit of PARDISO's `iparm[1]`, which must be set before the reordering phase. On MAKRO, level 1 (`iparm[1]=13`) cuts the factorization from 54 to 37 seconds. Higher levels give nothing more on this machine, which has an AMD processor rather than the Intel Xeon of Intel's own benchmarks. The setting needs MKL 2026 or later.

**Fewer solves with the factors.** A single solve with MAKRO's factors takes 1.2 seconds, and almost none of that is arithmetic. The forward and back substitution must read all 16 GB of factors twice, so the speed is set by memory bandwidth, and no compiler or thread setting changes it. The only lever is the number of solves. Each Newton step refines until the relative residual is below a target, by default $10^{-11}$. Real Newton steps reach it in 2–8 refinements, and Newton converges just as well with a looser $10^{-9}$ (`refine_tol=1e-9`).

Two details matter here. First, a refinement can never get below the **rounding floor** of computing $b - Jx$ in double precision. For some right-hand sides that floor is above the target, so every refinement stops when the residual has stopped falling, rather than running to the step limit. Second, GMRES (`krylov=True`) can replace the plain refinement and needs fewer solves per step. It has to be preconditioned from the right, so that it minimizes the true residual. A left-preconditioned GMRES, such as scipy's, minimizes the preconditioned residual, and with the normal equations as preconditioner that residual reached $10^{-15}$ while the true residual was still $10^{-2}$.

Measured on one of DREAM's standard shocks (an increase in public purchases), solved 2030–2129:

| `factorizer=` | Total | Factorization | Solves with the factors |
| --- | --- | --- | --- |
| `'normal'` (before the changes) | 3.33 min | 54 s | 85 solves, 110 s |
| `normal(iparm={1: 13})` | 2.89 min | 37 s | 79 solves, 100 s |
| `normal(iparm={1: 13}, krylov=True)` | 2.75 min | 38 s | 68 solves, 88 s |
| `normal(iparm={1: 13}, refine_tol=1e-9)` | **2.65 min** | 44 s | 52 solves, 68 s |

All four give the same solution, with the same equation error and Newton iteration count. In all, the solve is 20 per cent faster, and nothing about the model changed.

None of these settings helps FRB/US. Its problem is accuracy, not size, and neither PARDISO nor the normal equations can solve it.

---

## A checklist

1. **Make sure the horizon ends at the model's terminal condition.** A stacked solve over a cut span may not converge.
2. **Keep `split=1`.** Only the simultaneous core is stacked.
3. **Solve many shocks with one Jacobian** (`newton_reset=0`). Store the derivatives with the model (`modeldump(derivatives=True)`), and load large models with `straight=True` when only the stacked solver is used.
4. **Start with the default linear solver.** If it is fast enough, stop there.
5. **Too large for SuperLU** (out of memory, or a factorization that never ends): try `factorizer='normal'`, and on MKL 2026 `modelfactorize.normal(iparm={1: 13}, refine_tol=1e-9)`. Make the factorizer once and pass the same object every time, because ModelFlow keeps the factorization only while the factorizer is unchanged.
6. **"Can not solve this linear system"** means the Jacobian is too badly conditioned for PARDISO or the normal equations. Use `'mumps'`, or SuperLU on a shorter problem.
7. **Large shocks:** solve a small fraction first and scale it up as the starting point.
8. **Before trusting a new setting,** compare its solution of one scenario with the default solver's. They should agree to within the convergence tolerance.
