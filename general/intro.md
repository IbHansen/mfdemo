# Introduction

:::{important} This is a draft
This supplement is a **work in progress**. It is circulated to be read and argued with,
not as a finished account.

Comments, corrections and suggestions are very welcome — on the substance, on the
history, or on anything that is unclear, wrong or missing.
:::

This supplement is about **how ModelFlow is put together** — what happens between an
economic equation written by a modeller and a number produced by a solver, and why the
chain is arranged the way it is.

The guiding principle is a division of labour:

> **Use Python syntax wherever possible, transform only the notation specific to economic
> modelling, and delegate the general language and numerical machinery to Python and its
> scientific libraries.**

ModelFlow therefore does not implement an expression language, a compiler, a sparse
linear algebra package or a graph library. It implements the part that is specific to
economic models — lags and leads, endogenous and exogenous variables, add factors,
normalization, dimensional expansion — and generates ordinary Python for everything else.

## What is in this book

The four chapters follow one chain, and are ordered so that each takes over where the
last leaves off.

**[Historical background](Historic_complete.md)** comes first because it explains why the
rest looks as it does. The same architecture was used on a UNIVAC 1100 mainframe around
1983 to move the ADAM model from TSP into Danmarks Nationalbank's NASS, and again in PCIM
from 1985, which put ADAM on a PC with 640 KB of memory and an 8087 coprocessor.
ModelFlow, begun around 2013 for an unrelated problem — unmaintainable bank stress-test
models in Excel — re-derived it a third time. The chapter also notes that the approach is
not unique to ModelFlow: Dynare and Project LINK arrived at much the same arrangement
independently.

**[Specification to executable code](modelflow_specification_to_code.md)** takes the
translation side. The higher-level DSL of lists, `do`, `doable` and `sum`; the
preprocessors that bring in models from other systems; normalization into `y = F(y, x)`
form together with the add-factor, exogenizable and fitted variants; syntax validation
against the equation the modeller actually wrote; the token rewriting that turns variable
names into array positions; and compilation with `exec` or Numba.

**[Structure and solution](modelflow_structure_and_solution.md)** starts from the
executable equations and asks how to order and solve them. The dependency graph, its
decomposition into prolog, simultaneous core and epilog, and the feedback vertex set that
shrinks the problem that remains — then the solvers that use all of it: Gauss-Seidel,
Newton, Newton reduced to the feedback variables, and stacked Newton when leads couple
the periods together.

**[Local stability and dynamics](modelflow_stability.md)** turns the derivative machinery
to a different purpose. The Jacobian built for a Newton step is a linearization, and it
can be analysed instead of iterated on: contemporaneous effects solved out, lags assembled
into a companion matrix, and its eigenvalues used to ask whether small disturbances decay,
oscillate or grow.

## How to read it

The history stands on its own and can be skipped by anyone who only wants to know how the
system works today. The three technical chapters are meant to be read in order — the
second begins from the executable equations the first produces, and the third from the
Jacobian the second builds — but each states its own starting point, so they can also be
consulted separately.

Two conventions are worth flagging. Generated code is treated throughout as an
implementation detail that the modeller is not expected to read; where it appears, it is
to show what the translation produces, not because anyone works at that level. And claims
about what the software does are meant to describe what it actually does — where something
is an intention rather than a tested capability, it is marked as such.

Readers interested in the specification language itself — the DSL, the `%%Makemymodel`
magic, normalization and add factors in practical detail — will find them in the companion
supplement on model specification.
