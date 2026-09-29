# Introduction

This supplement is about **how a model is specified in ModelFlow** — the step that turns
a piece of readable text into a model object that can be simulated on a Pandas DataFrame.

A ModelFlow model is written in a small domain specific language (DSL). Each equation
states a piece of business logic, one endogenous variable per equation:

```text
> profit__{banks} = revenue__{banks} - expenses__{banks}
```

Before such text can be solved, it has to be **expanded** (loops over lists, sums, tags),
**normalized** (so the endogenous variable stands alone on the left-hand side) and
optionally extended with **add factors**. `Makemodel` performs the expansion,
`normal` performs the normalization, and the `%%Makemymodel` cell magic lets you do the
whole thing in a notebook cell.

## What is in this book

**[Model specification](model%20specification.ipynb)** introduces the DSL and the
`Makemodel` preprocessor: list definitions and `do`-loops, `doable`, `sum()`, the
`<exo>`, `<add>` and `<fit>` tags, `replacements=` and `list_defs=`, and how several
model blocks are combined with `+` into a `Listmodels` container.

**[The `%%Makemymodel` magic](jupyter_magic_makemymodel.ipynb)** shows the notebook
front end: writing Markdown documentation and `>` equations in the same cell, the
available options (`show`, `draw`, `render`, `latex`), and how `segment=` lets you build
a large model from independently developed pieces.

**[Estimation](estimation.ipynb)** covers the behavioural equations, whose coefficients
come from data rather than from accounting: the equation syntax for coefficients and
constraints, the `ols` and `nls_lmfit` backends, and how an equation tagged
`<estimator=...>` is estimated while the model is being built. It stays with the syntax,
demonstrated on small synthetic data where the right answer is known in advance; a
complete estimation on real data is a supplement of its own, *ModelFlow - Estimation, a
worked example*.

**[Normalization](normal.ipynb)** goes one level down, to the `normal` function that
rewrites an equation into `y = F(y, x)` form, and to the `Normalized_frml` class that
carries the original, preprocessed, normalized and fitted versions of an equation.

**[Add factors](add%20factors.ipynb)** looks in detail at what the `<add>` tag actually
generates, and how the resulting add factor can be used to control an equation.

## Prerequisites

The notebooks import from the ModelFlow source, mainly:

```python
from modelconstruct_estimation import Makemodel
import modeljupytermagic          # registers the %%Makemymodel magic
from modelnormalize import normal
```

Estimation needs no import of its own: the method is named in the equation's tag,
as `<est=ols>` or `<est=nls_lmfit>`.

Each notebook can be read on its own, but the chapters are ordered so that later ones
build on the vocabulary of the earlier ones.
