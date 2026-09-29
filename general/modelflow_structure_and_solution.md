# ModelFlow: Model Structure and Solution

## Summary

Once ModelFlow has translated the economic specification into executable equations, the next question is how those equations are ordered and solved efficiently.

This chapter starts from the model's directed dependency graph. It uses strongly connected components to separate **prolog**, **simultaneous core** and **epilog**, and an approximate feedback vertex set to expose a smaller set of variables that drives the remaining cycles. That structure is then used by the numerical solvers: conventional Gauss-Seidel for many normalized macroeconomic models, Newton methods for harder simultaneous or implicit systems, reduced Newton on feedback variables, and stacked Newton when endogenous leads couple periods together.

The preceding chapter, [From model specification to executable code](modelflow_specification_to_code.md), explains how the equations reach executable form. The following chapter, [Local stability and model dynamics](modelflow_stability.md), reuses the Jacobian machinery to analyse the model rather than solve it.

---

## Model structure as a directed graph

A ModelFlow model can also be represented as a **directed dependency graph**. Each model variable is a node. For an equation with left-hand-side variable `Y`, every model variable on the right-hand side has a directed edge pointing to `Y`:

```text
RHS variable  ------>  LHS variable
```

The graph therefore describes the **computational dependency structure** implied by the normalized model equations. When the equations themselves have a structural economic interpretation, this ordering can also be read as causal in that model-specification sense; it should not be confused with a causal graph established independently by statistical identification. This is one of the reasons normalization matters: without a single left-hand-side variable per equation, the nodes of this graph would not be well defined.

### Dependencies and solving order

If the dependency graph contains no cycles, equations can be evaluated in topological order: upstream variables are calculated before variables that depend on them. Cycles identify feedback and simultaneous relationships.

ModelFlow can use this graph structure to establish an efficient solving order.

### Prolog, core and epilog

The ordered model is divided into three computational parts:

| Part | Graph interpretation | Role in solution |
| --- | --- | --- |
| **Prolog** | Variables upstream of the simultaneous core | Calculated once before iteration |
| **Core** | Simultaneously interdependent variables | Recalculated during iterative solution |
| **Epilog** | Variables downstream of the simultaneous core | Calculated after the core has converged |

:::{figure} diagrams/prolog_core_epilog.png
:alt: The ordered model: prolog once, core iterated, epilog after convergence.
:width: 92%
:name: fig-prolog-core-epilog

Prolog, core and epilog.
:::

This decomposition avoids repeatedly evaluating equations outside the simultaneous part. The prolog is evaluated before iteration, only the core must be repeatedly evaluated, and the epilog is evaluated after convergence.

### Strongly connected components

A **strongly connected component** is a set of nodes in which every node is reachable from every other node. In model terms, it represents variables connected through feedback.

A model can contain several simultaneous strongly connected components. For ModelFlow's computational representation, these are collected into one **core**. Equations that can be ordered before the core form the prolog; equations downstream of the core form the epilog.

Thus the overall computational structure remains:

```text
prolog  ->  core  ->  epilog
```

even when several strongly connected components occur inside the core.

### Feedback variables and the feedback vertex set

Even inside the core, it is often unnecessary to treat every endogenous variable as an independent feedback variable.

A **feedback vertex set** is a set of nodes which, if removed from the directed graph, breaks all directed cycles. If the feedback variables are held fixed at the beginning of an iteration, the remaining equations can be evaluated in an acyclic computational order. The feedback variables are then updated and convergence tested.

:::{figure} diagrams/feedback_set.png
:alt: Feedback variables are selected, the remaining equations evaluated in causal order, the feedback variables updated, and convergence tested.
:width: 58%
:name: fig-feedback-set

One pass over the feedback variables.
:::

Finding the **minimum feedback vertex set** is computationally hard for a general directed graph. It is not necessary, however, to find the mathematically smallest set to obtain most of the computational benefit. A good approximation can identify a relatively small feedback set and reduce the effective iterative problem.

None of this is new. {cite:t}`don_some_1990` sets out the argument for econometric models directly: a large sparse system can be solved efficiently if the equations are ordered so that the set of feedback variables is small, the reordering problem is the standard graph-theoretic one of finding a minimal feedback vertex set, that problem is NP-hard, and a heuristic in polynomial time is therefore used to produce small — though not necessarily minimal — feedback sets. He also notes what is claimed here: that the same reordering improves Gauss-Seidel convergence, not only Newton.

| Without feedback reduction | With feedback-set reduction |
| --- | --- |
| Large simultaneous core repeatedly evaluated | Smaller feedback set drives iteration |
| Less use of causal ordering within the core | Remaining equations use computational order |
| More work per iteration | Potentially substantially less work per iteration |

This splits the core into a small set of feedback equations and a larger acyclic remainder (`daglist`). The same split is just as useful for Newton, where it reduces the dimension of the linear system rather than the cost of an iteration; the Newton section returns to it.

### Graph analysis in ModelFlow

The dependency graph serves several purposes:

| Graph information | ModelFlow use |
| --- | --- |
| **Directed RHS-to-LHS edges** | Represent equation dependencies |
| **Topological ordering** | Establish causal/computational evaluation order |
| **Strongly connected components** | Identify simultaneous feedback structure |
| **Prolog/core/epilog decomposition** | Avoid unnecessary repeated evaluation |
| **Approximate feedback vertex set** | Reduce the effective iterative problem |
| **Lead/lag relationships** | Characterize dynamic dependencies across periods |

Graph analysis complements the numerical solvers. For Gauss-Seidel it provides equation ordering and feedback reduction. For Newton methods it exposes structural dependencies, reduces the system that has to be factorized, and helps explain the sparsity pattern of the Jacobian.

The directed graph is therefore an important intermediate representation connecting **model specification, causal structure and numerical solution**.

---

## Gauss-Seidel solution

For many economic models, the natural solution method is an iterative **Gauss-Seidel** solution.

The equations are arranged in computational order and evaluated repeatedly. As soon as a new value of an endogenous variable has been calculated, that updated value is available to subsequent equations in the same iteration.

Conceptually:

:::{figure} diagrams/gauss_seidel.png
:alt: Equations are evaluated in order, each updating its variable; the iteration repeats until the convergence test passes.
:width: 46%
:name: fig-gauss-seidel

A Gauss-Seidel sweep.
:::

For a dynamic model without leaded endogenous variables, periods can normally be solved sequentially:

:::{figure} diagrams/periods.png
:alt: Each period is solved to convergence before the next begins.
:width: 96%
:name: fig-periods

Sequential solution, period by period.
:::

Lagged variables are already known from earlier periods, so they fit naturally into this solution strategy.

The update can be damped. Instead of accepting a newly calculated value outright, the solver can move only part of the way towards it, which stabilizes oscillating feedback loops at the cost of more iterations.

Gauss-Seidel has important practical advantages:

- it is simple;
- it exploits the equation structure directly;
- it does not require construction or factorization of a Jacobian;
- and it works well for many traditionally specified macroeconomic models.

For more difficult nonlinear systems, implicit equations, or models where stronger simultaneous solution is required, ModelFlow can use Newton methods.

---

## Newton solution and the Jacobian

Newton solution requires the **Jacobian matrix**: the matrix of derivatives of model equations with respect to endogenous variables.

ModelFlow does not require the modeller to supply this matrix manually.

Instead, ModelFlow creates a new model instance whose purpose is to calculate the relevant Jacobian coefficients.

The process is:

:::{figure} diagrams/jacobian.png
:alt: Equations are differentiated symbolically, falling back to numerical differentiation where required; the derivative model produces the sparse Jacobian, which is factorized to give the Newton update.
:width: 62%
:name: fig-jacobian

From equations to a Newton update.
:::

### Symbolic differentiation

ModelFlow first attempts to differentiate the original equations **symbolically**, using SymPy.

This reuses the machinery already described under normalization. The equation is handed to SymPy in the same way: `LOG(` is lowercased to `log(` because SymPy uses lower-case function names, and a clash dictionary protects model variables whose names collide with SymPy's own symbols. The derivative is then taken with respect to each endogenous variable that actually occurs on the right-hand side.

The resulting derivative expressions are themselves equations. They can therefore be represented and evaluated using the same ModelFlow equation machinery — expansion, validation, token rewriting, `exec`, optionally Numba. A separate ModelFlow instance evaluates these derivative equations and produces the non-zero coefficients required by the Jacobian.

### Numerical differentiation as fallback

Some expressions contain functions for which symbolic differentiation is unavailable or inconvenient — user-defined functions, interpolations, or constructs that SymPy cannot sensibly handle.

ModelFlow can then use **numerical differentiation as a fallback**, either for individual equations or, on request, for the model as a whole.

This combines the efficiency and precision of symbolic differentiation where possible with the generality of numerical differentiation where necessary.

### Normalized and residual rows

The Jacobian must be built consistently with the form each equation actually takes. A normalized equation $y = F(y, x)$ has residual $F(y) - y$, so its row carries an additional $-1$ on the diagonal. An implicit equation, stored as $y_{\text{RES}} = G(y, x)$, has residual $G(y)$ and carries no such term.

ModelFlow keeps a per-equation mask recording which form each row has, and builds the Jacobian accordingly. This is not a detail: treating $F(y)$ itself as the residual of a normalized equation gives the Jacobian $\partial F/\partial y$ instead of $\partial F/\partial y - I$, and the iteration diverges.

### Sparse Jacobian construction

Large macroeconomic models can contain thousands of endogenous variables, but an individual equation normally depends on only a small fraction of them.

The Jacobian is therefore highly sparse.

| Jacobian element | Meaning | Sparse representation |
| --- | --- | --- |
| $\partial F_i/\partial x_j \neq 0$ | Equation $i$ depends on endogenous variable $j$ | Store row, column and coefficient |
| $\partial F_i/\partial x_j = 0$ | No direct dependence | Structural zero; normally not stored |

The derivative model calculates the coefficients, which are then **stuffed into the appropriate positions of a sparse matrix**.

ModelFlow can thereby retain knowledge of the economic equation structure while Python's efficient sparse libraries handle storage and numerical linear algebra.

### Sparse LU decomposition

At a Newton iteration the linearized system has the form:

$$
J(x) \, \Delta x = -F(x)
$$

The sparse Jacobian is factorized using an efficient sparse **LU decomposition**, and the factorization is used to obtain the Newton update:

$$
x_{k+1} = x_k + \Delta x
$$

### Reusing the factorization

Rebuilding and refactorizing the Jacobian at every iteration is usually wasteful: in a mildly nonlinear model an old factorization remains a perfectly good approximation, and each reuse saves the dominant cost of the iteration.

ModelFlow makes this a single explicit policy rather than a scattering of heuristics. A `nonlin` option decides all refreshing: the factorization is carried forward across iterations and periods, refreshed on a fixed schedule (every *N* iterations), and refreshed additionally whenever the iteration appears to be diverging. A negative setting requests a fresh Jacobian before each new period as well. For a model solved over many periods with a repeated shock, this is the difference between factorizing thousands of times and factorizing a handful of times.

### Newton on the feedback set

The feedback vertex set of the graph analysis is just as useful here, and for a sharper reason: it reduces the *dimension of the linear system*. This is the reduction {cite:t}`don_some_1990` describes — a system that is large but sparse can be solved by a Newton-type algorithm once it has been reduced to the low-dimensional problem in the feedback variables.

If the core is split into a small feedback set and an acyclic remainder, then the remainder is not a system to be solved at all — it can be evaluated exactly by a topological sweep, given the feedback values. Newton therefore only has to iterate on the feedback unknowns, and the linear algebra shrinks from the size of the core to the size of the feedback set.

ModelFlow offers several ways of obtaining that reduced Jacobian:

| Reduced Jacobian | How it is obtained | When it fits |
| --- | --- | --- |
| **Schur complement** | Exact reduction of the full Jacobian to the feedback unknowns | The exact Newton step, at reduced size |
| **Finite differences** | Perturb each feedback unknown and re-sweep the DAG | Captures coupling through the DAG chain without symbolic work |
| **Direct** | Differentiate the feedback equations only, iterating the inner solve | Nonlinear block Gauss-Seidel on the feedback block |
| **Gauss (none)** | Damped fixed-point step, no Jacobian at all | Robustness fallback for large or ill-conditioned feedback sets |

The finite-difference variant is worth noting: it perturbs a feedback unknown, runs the acyclic sweep, and observes the effect on the feedback residuals. It therefore captures the *total* derivative through the whole DAG chain, not merely the direct dependence between feedback equations — and it does so without differentiating anything symbolically.

### Convergence

Gauss-Seidel and Newton share a relative convergence test: a variable is examined only if its absolute value is at least `absconv`, and it must then change by less than `relconv` between iterations.

The floor is necessary — otherwise a variable near zero would demand impossible relative precision — but it has a consequence worth stating plainly. A test on the *step* is blind to unknowns whose values sit below the floor. A saturated 0/1 policy switch, for example, can move between two small values without the test ever noticing, and the solver reports convergence on a system whose equations do not actually hold.

The Newton solvers therefore add an **absolute residual** test: convergence requires not only that the step be small, but that the equations be satisfied —

$$
|G(y)| \le \text{newton\_absconv} \qquad\text{(residual rows)}
$$

$$
|F(y) - y| \le \text{relconv} \cdot \max(|y|, \text{absconv}) \qquad\text{(normalized rows)}
$$

Requiring both is what distinguishes "the iteration stopped moving" from "the model is solved".

---

## Stacked Newton solution for leaded endogenous variables

A dynamic model containing only contemporaneous and lagged endogenous variables can normally be solved one period at a time.

The situation changes when the model contains **leaded endogenous variables**.

An equation in period `t` may then depend on an endogenous variable in `t+1`. Future periods and current periods become mutually dependent, so sequential period-by-period solution is no longer sufficient.

ModelFlow can solve this by stacking all solution periods into one simultaneous system.

If the endogenous vector in one period is $x_t$, the stacked unknown vector is conceptually:

$$
X = \begin{bmatrix} x_{t_0} \\ x_{t_1} \\ x_{t_2} \\ \vdots \\ x_{t_N} \end{bmatrix}
$$

The Jacobian is correspondingly stacked across variables and periods.

A simplified block structure is:

| Equation block | Variables `t-1` | Variables `t` | Variables `t+1` |
| --- | ---: | ---: | ---: |
| **Equations `t-1`** | `J` | `L` | `.` |
| **Equations `t`** | `B` | `J` | `L` |
| **Equations `t+1`** | `.` | `B` | `J` |

Here:

- `J` represents contemporaneous dependencies;
- `B` represents lagged dependencies;
- `L` represents leaded dependencies;
- `.` represents a structural zero block.

The resulting matrix can be extremely large, but it is also **very sparse**.

The solution chain becomes:

:::{figure} diagrams/stacked.png
:alt: All periods are stacked into one sparse system and solved together.
:width: 40%
:name: fig-stacked

The stacked chain.
:::

### The stacked graph

The feedback reduction described for Newton extends to the stacked problem, but it needs a graph that does not exist on the model: the dependency graph over (period, variable) pairs.

ModelFlow constructs it from the structure of the stacked Jacobian itself. Each unknown becomes a node, and each non-zero derivative becomes an edge from `(t + lag, explanatory variable)` to `(t, endogenous variable)`. The result is decomposed exactly as in the graph analysis — strongly connected components in topological order, and an approximate minimum feedback set within each simultaneous block.

The payoff is that the acyclic sweeps may now run *across* periods. An equation whose inputs happen to be known, whether from an earlier period or a later one, is simply evaluated; only the stacked feedback unknowns are given to Newton. Models with leads are covered by exactly the same machinery as models without them, and the reduced system is a small fraction of the full stacked one.

This allows forward-looking models to be solved as one simultaneous intertemporal system while exploiting Python's highly optimized sparse-matrix libraries.

---

## Solver choice

The main solution approaches serve different model structures.

| Feature | Gauss-Seidel | Newton | Newton on feedback set | Stacked Newton |
| --- | --- | --- | --- | --- |
| **Jacobian required** | No | Yes | Reduced only | Yes, stacked |
| **Basic operation** | Repeated equation evaluation | Linearization and sparse linear solve | DAG sweep plus small linear solve | Linearization across all periods |
| **Size of linear system** | — | Endogenous variables in the core | Feedback variables only | Variables x periods |
| **Sequential periods** | Natural | Also period by period | Also period by period | No: all periods at once |
| **Leaded endogenous variables** | Not naturally suited | Not covered period by period | Not covered period by period | Handled by construction |
| **Sparse matrix factorization** | Not required | Sparse LU | Dense or Schur-complement reduced | Sparse LU |
| **Derivative model** | Not required | Symbolic with numerical fallback | Symbolic, finite-difference or none | Symbolic with numerical fallback |
| **Typical strength** | Simple and robust for many traditional models | Strong simultaneous solution for difficult nonlinear systems | Large cores with small feedback sets | Forward-looking models |

Note that Newton is *not* inherently a whole-sample method. Where the model has no leads, the Newton solvers work period by period exactly as Gauss-Seidel does; stacking is required only when leaded endogenous variables make the periods mutually dependent.

ModelFlow can therefore choose a solution strategy appropriate to the structure of the model rather than imposing one numerical method on all models.

A graded hierarchy of this kind is long-standing practice rather than a novelty: {cite:t}`petersen_computer_1987` describe Project LINK solved through a Jacobi, Gauss-Seidel and Newton hierarchy applied according to the difficulty of the system, on hardware two generations removed from anything discussed here. The reasoning survives the change of machine — Newton is more capable and more expensive, so it earns its place only where cheaper iteration fails.

The numerical methods themselves are not ModelFlow's invention and are not described here in any depth. For the underlying theory — iterative and Newton-type solution of large nonlinear systems, ordering and decomposition, and the sparse techniques that make them practical — {cite:t}`pauletto_computational_1997` is the standard treatment for macroeconometric models specifically, and covers most of what this chapter applies.

---


## Worked example: from executable equation to graph and Jacobian

The worked example in [From model specification to executable code](modelflow_specification_to_code.md) ended with the normalized equation for `C__YOUNG` translated to array-indexed Python. The same equation also contributes to the dependency graph and, for Newton solution, to the Jacobian.

**Differentiation.** For Newton, SymPy differentiates the normalized equation with respect to the endogenous variables on its right-hand side. Here the only contemporaneous endogenous variable is `YD__YOUNG`:

$$
\frac{\partial\, C_{\text{YOUNG}}}{\partial\, YD_{\text{YOUNG}}} = 0.5
$$

The lagged terms do not appear: within a period they are known constants, and they enter only the `B` blocks of the stacked Jacobian.

**The Jacobian row.** Because this is a normalized equation, its row carries the `-1` diagonal term described earlier. In the row for `C__YOUNG`:

```text
column  C__YOUNG   :  -1.0
column  YD__YOUNG  :   0.5
all other columns  :  structural zero, not stored
```

Two non-zeros in a row that is as wide as the model is large — which is why the Jacobian is stored sparsely, and why `YD__YOUNG -> C__YOUNG` is also exactly the edge this equation contributes to the dependency graph.



## Solution architecture at a glance

| Layer | Main function |
| --- | --- |
| **Dependency graph** | Directed RHS-to-LHS model dependencies |
| **Graph decomposition** | Topological ordering, strongly connected components, prolog/core/epilog |
| **Feedback reduction** | Approximate feedback vertex set and acyclic remainder |
| **Gauss-Seidel** | Repeated equation evaluation in computational order |
| **Derivative model** | Symbolic differentiation with numerical fallback |
| **Newton** | Sparse Jacobian, LU factorization and simultaneous update |
| **Feedback-set Newton** | DAG sweeps plus a smaller nonlinear system in feedback variables |
| **Stacked Newton** | Sparse simultaneous solution across periods when endogenous leads are present |

The Jacobian produced for Newton also provides a local linearization of the model. That second use is the subject of [Local stability and model dynamics](modelflow_stability.md).
