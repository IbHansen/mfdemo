# ModelFlow: Local Stability and Model Dynamics

## Summary

ModelFlow can reuse the derivative machinery built for Newton solution to study the local dynamics of a solved model. Contemporaneous effects are solved out, lagged endogenous effects are assembled into a companion matrix, and the eigenvalues of that matrix show whether small disturbances decay, persist, oscillate or grow.

The analysis is **local and period-specific**: it describes small perturbations around the point where the Jacobian is evaluated, not the nonlinear model everywhere. ModelFlow can also recompute the dominant root after removing individual equations, providing a diagnostic of which relationships carry an instability.

This chapter follows [Model structure and solution](modelflow_structure_and_solution.md). The translation from economic specification to executable equations is described in [From model specification to executable code](modelflow_specification_to_code.md).

---

## Linearization, the companion matrix and local stability

The derivative machinery used for Newton solution has a second use: it provides a local linearization of the model that can be analysed in its own right.

A Jacobian *is* a linearization. Once ModelFlow has evaluated the derivatives around a solved point, the resulting approximation can be used to ask a different question from the one posed by the solver: **is the model locally stable there, and if not, what is making it unstable?**

The construction starts from the same derivative model described in [Model structure and solution](modelflow_structure_and_solution.md), but the output is analysed rather than used for a Newton step. The implementation is in `modelnewton.py` (the `newton_diff` class) and reached from `modelclass.py`.

### From Jacobian to transition matrix

Take a model with $n$ endogenous variables $y$, $k$ exogenous variables $x$, maximum endogenous lag $r$ and maximum exogenous lag $s$, where $t$ is the time frame — year, quarter, day, second or another unit. Written out equation by equation, the whole model is

$$
\begin{aligned}
y_t^1 &= F^1(y_t^2 \ldots y_t^n,\; y_{t-1}^1 \ldots y_{t-r}^n,\; x_t^1 \ldots x_t^k,\; \ldots x_{t-s}^1 \ldots x_{t-s}^k) \\
y_t^2 &= F^2(y_t^1 \ldots y_t^n,\; y_{t-1}^1 \ldots y_{t-r}^n,\; x_t^1 \ldots x_t^k,\; \ldots x_{t-s}^1 \ldots x_{t-s}^k) \\
&\;\;\vdots \\
y_t^n &= F^n(y_t^1 \ldots y_t^{n-1},\; y_{t-1}^1 \ldots y_{t-r}^n,\; x_t^1 \ldots x_t^k,\; \ldots x_{t-s}^1 \ldots x_{t-s}^k)
\end{aligned}
$$

This is the **normalized** form, which is what the analysis below assumes: each endogenous variable is on the left hand side exactly once, and an unlagged endogenous variable never appears on the right hand side of its own equation. Collecting the variables of a period into the vectors $\mathbf{y}_t$ and $\mathbf{x}_t$, the same system is

$$
\mathbf{y}_t = \mathbf{F}(\mathbf{y}_t \cdots \mathbf{y}_{t-r},\; \mathbf{x}_t \cdots \mathbf{x}_{t-s})
$$

The derivative model produces the Jacobian split by lag, which gives three families of matrices:

$$
A = \frac{\partial \mathbf{F}}{\partial \mathbf{y}_t^{T}}, \qquad
E_i = \frac{\partial \mathbf{F}}{\partial \mathbf{y}_{t-i}^{T}}\;\; (i = 1 \dots r), \qquad
F_j = \frac{\partial \mathbf{F}}{\partial \mathbf{x}_{t-j}^{T}}\;\; (j = 0 \dots s)
$$

$A$ holds the contemporaneous derivatives, $E_i$ the lagged endogenous ones, $F_j$ the exogenous ones. Linearizing around a solution, the response to a small perturbation is

$$
\Delta\mathbf{y}_t = A\,\Delta\mathbf{y}_t + \sum_{i=1}^{r} E_i\,\Delta\mathbf{y}_{t-i} + \sum_{j=0}^{s} F_j\,\Delta\mathbf{x}_{t-j}
$$

The contemporaneous term appears on both sides, so it must be resolved first:

$$
(\mathbb{I} - A)\,\Delta\mathbf{y}_t = \sum_{i=1}^{r} E_i\,\Delta\mathbf{y}_{t-i} + \sum_{j=0}^{s} F_j\,\Delta\mathbf{x}_{t-j}
$$

$$
\Delta\mathbf{y}_t = \sum_{i=1}^{r} C_i\,\Delta\mathbf{y}_{t-i} + \dots, \qquad C_i = (\mathbb{I} - A)^{-1} E_i
$$

Inverting $\mathbb{I} - A$ is the same operation the Newton solvers perform, applied here to a different end: the simultaneous block is solved out, leaving a system in the lags alone.

The exogenous terms carry through, but they play no part in what follows. Stability is a question about how the system responds to its *own* past, so it is settled by the endogenous transition alone; the $F_j$ describe how disturbances enter, not whether they die out.

### The companion matrix

A system with $r$ lags is a difference equation of order $r$, and stability is read off a *first*-order system. There is a standard way to get one: stack the lagged states into a single state vector

$$
\mathbf{z}_t = \begin{bmatrix} \mathbf{y}_t \\ \mathbf{y}_{t-1} \\ \vdots \\ \mathbf{y}_{t-r+1} \end{bmatrix}
$$

and write the whole system as one step, $\Delta\mathbf{z}_t = M\,\Delta\mathbf{z}_{t-1}$:

$$
\Delta\mathbf{z}_t
=
\underbrace{\begin{bmatrix}
C_1 & C_2 & \cdots & C_{r-1} & C_r \\
\mathbb{I} & 0 & \cdots & 0 & 0 \\
0 & \mathbb{I} & \cdots & 0 & 0 \\
\vdots & & \ddots & & \vdots \\
0 & 0 & \cdots & \mathbb{I} & 0
\end{bmatrix}}_{M \;=\; (\mathbb{I}-A)^{-1}\bar{E}}
\Delta\mathbf{z}_{t-1}
$$

$M$ is the **companion matrix**. Its top block row carries the $C_k$; everything below it is an identity block that simply shifts each lag down one place. ModelFlow assembles it exactly this way — the $C_k$ horizontally stacked on top, a rectangular identity underneath.

### Eigenvalues and local stability

One matrix now describes the whole dynamic system, and its eigenvalues characterize the behaviour:

| Eigenvalues $\lambda$ of $M$ | Behaviour |
| --- | --- |
| all $\lvert\lambda\rvert < 1$ | The system converges — a disturbance dies out |
| at least one $\lvert\lambda\rvert > 1$ | The system amplifies — a disturbance grows |
| $\lvert\lambda\rvert = 1$ | On the boundary; perpetual, undamped movement |
| at least one $\lambda$ has an imaginary part | The system oscillates — damped if all $\lvert\lambda\rvert < 1$, amplifying if any $\lvert\lambda\rvert > 1$ |

Magnitude and oscillation are separate questions: the moduli decide whether movement grows or dies away, the imaginary parts decide whether it is monotone or cyclical. The **largest modulus** is therefore the summary number, and a complex dominant root says the model cycles on its way there.

ModelFlow computes the eigenvalues with a dense solver, falling back to a sparse one for large systems, and plots them in polar coordinates — modulus as distance from the origin, argument as angle — so that the unit circle is the stability boundary and oscillatory roots are visible off the real axis. The calculation is carried out by a `newton_diff` object — obtained from a model with `get_newton()` — whose `get_eigenvalues()` builds the companion matrix per period; the eigenvalues and their eigenvectors are then available per period from `get_df_eigen_dict()`.

The next chapter, [Stability in practice](modelflow_stability_examples.ipynb), works through the five cases on a Samuelson multiplier-accelerator model — no amplification, explosion, exploding oscillations, perpetual oscillations and damped oscillations — showing each as a picture of where the roots sit relative to the unit circle.

Two properties of this matter in practice.

**It is local, and therefore period-specific.** The derivatives are evaluated at a particular solution in a particular period, so the answer describes the model *there*. ModelFlow computes the eigenvalues per period, and they can differ from one year to the next. A model can be stable in one part of the sample and not in another — which is itself a finding, and one that a single global statement about the model would hide.

**It is a property of the linearization, not of the model everywhere.** Local stability says what happens to small disturbances near the evaluation point. It is silent about large shocks and about behaviour far away.

### Which equation is responsible

Knowing that a model amplifies is less useful than knowing *what* amplifies. ModelFlow can therefore delete the row and column belonging to one equation, recompute the eigenvalues, and repeat for every equation in turn — ranking them by how much their removal changes the largest modulus. `get_eigen_jackknife_abs_select(year)` returns that ranking, together with the undisturbed value for comparison.

An equation whose removal collapses the dominant root is carrying the instability. That is a pointer to the mechanism, since each equation is one endogenous variable and one behavioural relationship.

Two honest qualifications. It is expensive — the eigenvalues are recomputed once per equation, so the results are cached. And it is uninformative on small models, where deleting almost any equation breaks the single loop that drives everything; its value is on large models, where it can isolate the few equations that matter out of thousands. The name is borrowed loosely from jackknife resampling and is not an exact fit.

### Application: macroprudential models

One possible - but untested - use of this feature is  **macroprudential model.** 

The reasoning is this. Macroprudential models are about feedback: credit conditions affect asset prices, asset prices affect balance sheets, balance sheets affect credit conditions. The policy question is often not the level of a forecast but whether such loops **amplify or damp** a shock, and whether that has changed over time.

That is the question the eigenvalues answer. A dominant root that has moved closer to the unit circle across the sample would say that the same shock now produces a larger and longer-lasting response — a statement about the system rather than about any single variable. A complex dominant root would say the response cycles. The jackknife would then point at the equations carrying it.

The attraction is that none of this requires a second model. The stability calculation is derived from the same equations, by the same derivative machinery, as the simulation — so there is no separate linearized model to build, calibrate and keep in step with the one actually being used.

The caveats from earlier in this section apply with some force here. The result is local and period-specific, and macroprudential concern is precisely with large shocks and non-linear behaviour, which a linearization around a solution does not describe. Whether the local measure says anything useful about the non-linear regime is exactly the question that would have to be settled by trying it.

---
