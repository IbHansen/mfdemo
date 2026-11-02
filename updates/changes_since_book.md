# All changes since the book (2.59–2.92)

This chapter lists every change from 2.59 to **2.92** (October 2026), based on `changelog.md`, grouped by topic. The version column shows the release where a change first shipped; *next* marks changes that are in the source but not yet released. For worked examples of the main features, see [New features by example](whats_new.ipynb).

(changes-ng)=
## Next-generation (`_ng`) solvers

From 2.73 there is a new solver framework (`modelsolver_ng`). Each old solver repeated the same setup, code generation, convergence test, statistics and teardown around a small iteration loop. In the `_ng` solvers all of this is written once in a shared base class (`SolverBase`). Every `_ng` solver inherits it and only adds its own iteration step. So a fix or a new option in the shared part works for all solvers at once, and a new solver is a small subclass.

The `_ng` solvers run alongside the old ones, which are unchanged. They give the same results as the old solvers and will in time become the default solvers. `model()` already uses them for hybrid models and for models with fixed-period references such as `X(2002)`. Choose one with `solver='<name>_ng'`, or use `model.solve_ng(solver=...)`.

From 2.89 a model can use the `_ng` solvers as its default: create or load it with `ng=True`, or set `mmodel.ng = True`. A call without `solver=` then uses `xgenr_ng`, `sim_ng`, `newton_ng` or `newtonstack_ng` in place of the old solvers. A normalized simultaneous model gets `sim_ng` (Gauss-Seidel); Newton must be asked for with `solver=`. The add-factor model and `dekomp` follow the option. On PAK, FRB/US (with and without model-consistent expectations), five other World Bank models, the Chilean pension model and DK_5eq, `ng=True` gives the same solutions as the old solvers, with and without jit, at the same speed. The plan is to make `ng=True` the default in a later release.

| Solver | What it does |
|---|---|
| `xgenr_ng` | One pass in logical order, for models without simultaneity |
| `res_ng` | Evaluates every equation once per period against the input data |
| `sim_ng` | Gauss-Seidel (with damping) |
| `sim1d_ng` | Gauss-Seidel on a compact one-period array |
| `newton_ng` | Newton per period on the whole model; handles normalized, implicit and hybrid models |
| `newtonstack_ng` | Stacked Newton over all periods, for models with leads (alias `newtonstack_implicit_ng`) |
| `newton_fbmin_ng` | Newton per period on only the minimal feedback set; the rest is solved by exact sweeps |
| `newtonstack_fbmin_ng` | Stacked Newton on only the feedback set of the stacked model, for models with leads |

`newton_fbmin_ng` is the fastest solver, because Newton runs only on the few feedback variables and everything else is solved by exact sweeps in logical order. For models with leads, try both `newtonstack_ng` and `newtonstack_fbmin_ng`: which one is faster depends on the model.

| Version | Change |
|---|---|
| 2.73 | `_ng` framework with `xgenr_ng`, `sim_ng`, `newton_ng`, `newtonstack_ng` and the fbmin solvers |
| 2.73 | `jacobian='gauss'` for the fbmin solvers: no Jacobian, for large feedback sets |
| 2.73 | `newtonstack_fbmin_ng(jacobian='stack')` (default) uses the exact stacked Newton step on the reduced system |
| 2.87 | `model()` picks a unified Newton solver for hybrid models (normalized and `___RES` equations mixed) |
| 2.87 | Stacked Newton solvers skip a Jacobian rebuild once converged; `stats=True` reports the total build time |
| 2.89 | `ng=True` model option: a call without `solver=` uses the `_ng` solvers; the add-factor model and `dekomp` follow it |
| 2.89 | `newtonstack_ng` splits the model into prolog, core and epilog by default (`split=1`); the three parts run as compiled period loops, so the split also gains from jit (FRB/US with model-consistent expectations: 0.2–0.3 s per shock with jit) |
| 2.90 | `newtonstack_ng` and `newtonstack_fbmin_ng` solve models with an endogenous variable at a fixed period inside the solve span, such as `Z = Y/Y(2006)*100` solved 2003–2010; the per-period solvers still refuse it and point to the stacked solvers |
| 2.91 | `model.stack_info()` prints the size of the last stacked Newton system: periods, prolog/core/epilog split, Jacobian nonzeros and the memory of the LU factorization |

## Building and estimating models

This is a new way to write a model: describe it in a Markdown notebook cell, with equations, lists and text together. Then let ModelFlow expand it, estimate the tagged equations and turn it into a solvable model. Most of this lives in three modules: `modelconstruct_estimation` (the `Makemodel` class), `modelestimator_new` (the estimators) and the `%%Makemymodel` magic in `modeljupytermagic`. These modules were developed over several releases, so only part of the work appears as dated lines in the changelog.

### Makemodel class

| Feature | What it does |
|---|---|
| `Makemodel(text)` | Turns a model template (Markdown or plain ModelFlow) into normalized FRMLs that are ready to solve |
| `type_input=` | `'markdown'` (default), `'modelflow'` or `'single'`; from 2.90 also `'gekko'` and `'eviews'` |
| Non-markdown input | `eq_start=`, `eq_end=`, `comment_start=` and `transform=` pick the equations out of other text, such as Gekko or EViews programs (2.90) |
| Expansion pipeline | `LIST`/`TLIST`, `DOABLE`, `DO` loops and `SUM` are expanded in turn; each step can be inspected |
| `TLIST` | Transposed list: sublist names in the second row, values down the columns |
| `DOABLE` | Writes one equation over a list as LaTeX-like shorthand and unrolls it |
| `replacements=` | String replacements applied before expansion |
| `funks=` | User functions available in the model |
| `list_defs=` | Lists supplied separately from the equations |
| `show<attribute>` | Prints any stage, e.g. `mm.showpost_sum`; an unknown name lists all options |
| `.mmodel` | The finished ModelFlow model |
| `.clean_model` | Model with only the core equations (no fitted, add-factor or exogenizing equations) |
| `.add_model` | Model with only the add-factor calculations |
| `.init_addfactors(df)` | Calculates add factors so the model reproduces the historical data |
| `.draw`, `.clean_model_draw` | Dependency graphs |
| `.render`, `.render_est` | Show the model as Markdown/LaTeX, optionally with estimation tables |
| `mm1 + mm2` | Combines models into a `Listmodels` with the same interface |
| Warning on duplicates | Says when several equations define the same variable (the last one wins) |
| Syntax check | The whole generated model is syntax-checked |
| `model.equpdate(mm)` | `equpdate` takes a `Makemodel` as well as plain equation text, so new equations can be written, estimated and tagged in Makemodel and then put into an existing model (2.77) |

### FRML options in Makemodel

| Option | What it does |
|---|---|
| `<ADD>` / `<STOC>` | Adds an add factor (suffix set with `ADD_SUFFIX=`) |
| `<EXO>` | Makes the equation exogenizable (fixable) |
| `<FIT>` | Also generates a fitted-value equation |
| `<ENDO=var>`, `<ENDO_LHS=FALSE>` | Picks the endogenous variable for normalization |
| `<IMPLICIT>` | Keeps the equation in implicit (residual) form |
| `<DAMP>` (or `Z`) | The equation is damped in Gauss-Seidel solving (`alfa=`) |
| `<IDENT>` (or `I`) | Marks an identity; `model.get_histmodel()` uses these to make a model that calculates historic values (`tags=` picks other tags, 2.89) |
| `<QUASIIDENT>` | Set by the EViews onboarding for quasi-identities from MFMSA |
| `<DROP>` | Leaves the equation out |
| `<estimator=...>` / `<est=...>` | Estimates the equation while the model is built and inserts the coefficients |
| `<smpl=2001 2020>` | Estimation sample for this equation |
| `<caption=...>` | Title of the estimation report |
| `<constraints=...>` | Parameter constraints (same as an inline `ST.` clause) |

### Markdown models and the `%%Makemymodel` magic

| Feature | What it does |
|---|---|
| Equations in Markdown | Model lines are picked out of the Markdown; the text and `$$` LaTeX stay as documentation |
| Lists rendered as tables | `LIST` definitions are shown as tables in the rendered model |
| `%%Makemymodel name` | Builds a `Makemodel` from the cell and puts it in the namespace |
| `segment=` | Builds a model from several cells (list, text and equation segments) |
| `input_df=`, `est=`, `smpl=` | Estimation settings on the magic line |
| `param_names=` | Named coefficients (`lambda`, `beta`) instead of `c(1)`, `c(2)` |
| `render`, `render_est`, `render_list` | Control what is displayed |
| `show`, `draw`, `latex`, `display` | Print the FRMLs, draw the graph, produce LaTeX |
| `%%mdmodel` | Revised Markdown model magic with LaTeX output (2.63) |

### Estimators (`modelestimator_new`)

| Feature | What it does |
|---|---|
| `Estimate_ols` | OLS with statsmodels; write `C(1)` in the equation for an intercept |
| `Estimate_nls_lmfit` | Nonlinear least squares with lmfit (start values, bounds) |
| `Estimate_nls_eviews` | Nonlinear least squares done by EViews through py2eviews |
| `Estimate_nls(solver=...)` | Old single-class API, dispatches to lmfit or EViews |
| Built-in names | `ols`, `nls_lmfit` and `nls_eviews` can be used directly in `<est=...>` |
| `.with_defaults(input_df=, smpl=)` | Makes a factory such as `ls = ...`, then `<est=ls>` in a model |
| `ST.` clause | Inline constraints for `nls_lmfit`: bounds, fixed or start values, e.g. `... ST. C(2) < 0; C(3) = [0, 1]` |
| `param_names=` | Coefficients with their own names |
| Imposed coefficients | Terms without a coefficient are moved to the left before the fit (2.83) |
| Checks before fitting | Syntax, missing variables, sample with missing lags/leads (2.78–2.79) |
| t-values | `.tvalues` per equation, `mm.tvalues` for the whole model (2.78) |
| `.af_df`, `.residuals_df` | Actual vs. fitted and residuals |
| `EstimatorBackend` | Base class: a new estimator only needs `_fit` and `_render_summary_html` |
| `EqContainer` | Combines estimated equations into one model with add factors |

### Estimation reports

| Feature | What it does |
|---|---|
| Inline report | Each estimator shows a summary with an actual-vs-fitted plot |
| `mm.markdown_with_estimation` | The Markdown model with a small estimation table under each estimated equation |
| `mm.estimation_report()` | One HTML file with all estimations (`report_all=True` adds identities) |
| `mm.report()` | `MakeModelReport`: the whole model documentation as HTML, with a table of contents and collapsible estimation panels |
| `mm.pdf()` | The model documentation as PDF |
| PNG plots by default | So notebooks with estimations also export to PDF in Jupyter Book |

(changes-deployment)=
## Deployment in the cloud and the browser

ModelFlow no longer needs a local installation. The same models and notebooks now run in several cloud and browser systems:

| Where | How ModelFlow runs |
|---|---|
| JupyterLite | Entirely in the browser (Pyodide); nothing to install |
| Shinylive | Shiny apps made with `modelinput_shiny` run in the browser |
| Jupyter Book live code | Code cells in a book page can be run in the browser |
| GitHub Codespaces | A ready-made cloud environment with ModelFlow installed from conda |
| Google Colab | Notebooks open in Colab from a link or badge |

This needed a number of changes and fixes, listed below.

### Browser (JupyterLite, Shinylive, live code in books)

| Version | Change |
|---|---|
| 2.79 | numba is only imported with `ljit=True`, so models solve without it |
| 2.80 | Graphs are drawn without graphviz (networkx); SVG is the default engine in the browser |
| 2.81 | Browser-incompatible dependencies are marked as optional, so `micropip install modelflowib` just works |
| 2.81 | The tqdm monitor thread is switched off in the browser |
| 2.81 | `scroll_off` shows the whole output cell in JupyterLite |
| 2.83 | `model.causality(var)` works in JupyterLite (no graphviz or Dash needed) |
| 2.84 | Shiny apps from the notebook widget definitions, which run with Shinylive |
| 2.85 | pyarrow is optional in the browser (older Pyodide in Jupyter Book live code) |
| 2.86 | `modelload` finds files regardless of upper/lower case (Linux, JupyterLite) |
| 2.87 | `model.table` works under pandas 3 without pyarrow, as in JupyterLite |

### Colab and Codespaces

| Version | Change |
|---|---|
| 2.61 | `download_github_repo` accepts a subfolder; `Worldbank_Models` uses it |
| 2.67 | Colab version of the input widgets' tab container |
| 2.70 | Better detection of whether code runs in a notebook |
| 2.71 | `colab_link`: link/badge to open a notebook in Colab |
| 2.79 | The Dash sidebar redraws after 1.5 and 3 seconds for slow page loads (Codespaces) |

(changes-packaging)=
### Packaging and notebooks

| Version | Change |
|---|---|
| 2.70 | `packageify_modelflow_main` script for building a package (not used in production yet) |
| 2.81 | ipython, jinja2, statsmodels and plotly are declared dependencies |
| 2.83 | Requires Python 3.12 or newer |
| 2.86 | `jupyterlab-myst` dependency: MyST markdown and mermaid render in notebook cells |
| 2.86 | Notebook links use `/`, so they open in JupyterLab on Windows |

## Other new features

### Solvers (other changes)

| Version | Change |
|---|---|
| 2.63 | Newton: derivatives of `log` and `exp` are computed symbolically |
| 2.63 | Models with both implicit and normalized equations can be solved |
| 2.63 | `model_cvx.mv_opt` can maximize as well as minimize |

(changes-drawing)=
### Drawing and causality

| Version | Change |
|---|---|
| 2.80 | `draw` can use networkx instead of graphviz: `engine='dot'`, `'mpl'` or `'svg'` |
| 2.80 | Automatic fallback to networkx when graphviz is missing; `model.no_graphviz = True` forces it |
| 2.80 | SVG engine: stays sharp when zoomed, shows tooltips on hover, `browser=True` opens it in a new window |
| 2.80 | `get_alllinks` / `alllinks_to_nx` expose the graph so other renderers can use it |
| 2.80 | Whole-model graphs are layered by the logical order |
| 2.82 | Networkx drawings show links back over periods (`gdp -> gdp(-1)`) |
| 2.83 | `model.causality(var)`: interactive causality graph that works in JupyterLab, VS Code and JupyterLite; click a variable to move to it |
| next | Where the causality viewer is not run, as in a static book, it shows "Interactive causality viewer for VAR, run the notebook to use it" instead of the object's address |

(changes-reporting)=
### Reporting and display

| Version | Change |
|---|---|
| 2.60 | A warning is shown when a report PDF is not produced |
| 2.70 | Report figures can be summed: `sum([fig1, fig2])` |
| 2.71 | Variable search: prefix a pattern with `@` to use a regex instead of wildcards |
| 2.71 | Structural information can be shown for a model without data |
| 2.72 | Wide-screen and scroll on/off work in Notebook 7 |
| 2.79 | Tab completion works in Jupyter, including mixin methods |
| 2.79 | Better markdown display |
| 2.79 | `dekomp_fast` / `compare_dekomp`: experimental faster attribution |
| 2.86 | `model.plain_html = True` shows the result viewer and `rplot` as plain HTML, so they also work in RISE slides |
| 2.87 | `model.table(scenarios=...)`: tables for saved scenarios with one headline per scenario (or `scenario_layout='suffix'`) |
| 2.88 | `model.explain` respects `start=` and `end=` |
| 2.88 | `dekomp` growth tables show 3 decimals, so small shocks no longer show as 0.0% |

(changes-widgets)=
### Input widgets and apps

| Version | Change |
|---|---|
| 2.63 | `sheetwidget` remade: scrollable, with the operators `=`, `+`, `*` and `%` |
| 2.63 | `modelwidget_input` rebuilt on abstract base classes |
| 2.71 | Input widgets start fast; `keep_plot_widget` stays fast for models with more than 100,000 variables |
| 2.83 | `slidewidget` gets the operators `%of` and `+%of` (and `_impulse` variants): the slider value is a percent of, for example, GDP |
| 2.84 | `modelwidget_core`: UI-independent widget logic shared by the notebook and Shiny |
| 2.84 | `modelinput_shiny.make_app(widgetdef)`: a standalone Shiny app built from the same widget definitions, which also runs in the browser with Shinylive |
| 2.84 | `show_app` shows a Shiny app inside a notebook |

(changes-files)=
### Model files and helpers

| Version | Change |
|---|---|
| 2.65 | `modelhelp`: `build_sorted_rate_desc_dict` and `build_sorted_bond_desc_dict` for debt simulations |
| 2.69 | `mfquery` handles float column names |
| 2.71 | `.pcimx` (parquet) files make `modeldump` / `modelload` fast |
| 2.79 | Structure-only `.pcims` files: dump without data, load with `run=False` |
| 2.79 | `large=True` falls back to json when there is no dataframe |
| 2.90 | `model.run_on_load = True` is saved by `modeldump`; `modelload` then simulates the model with the saved period and options (`run=None` is the new default; `run=True`/`False` still decides) |

## Onboarding

### Other model sources

| Version | Change |
|---|---|
| 2.63 | `modelgrabwf2` handles `py2eviews` |
| 2.63 | `wf2_to_clean` works when the wf2 file has no model |
| 2.71 | `modelgrabgdx`: reads GAMS `.gdx` files into dataframes, plus a dummy model for reporting |
| 2.88 | `modelgrabgekkobank.read_gbk`: reads Gekko `.gbk` databanks |
| 2.88 | `modelgrabexcel` (renamed from `model_Excel`): Excel onboarding without xlwings; array formulas and data tables give a clear error |

### Checking an onboarded model

| Version | Change |
|---|---|
| 2.88 | `model.test_model(df, ref_df=)`: one-pass check of a model against known results |
| 2.92 | `model.test_model` reports equations whose calculated value is NaN, with the number of NaN periods and the first one (before, NaN slipped through the tolerance test) |

### Clearer error messages

| Version | Change |
|---|---|
| 2.70 | Syntax errors report their location |
| 2.70 | `errfunk` shows more information and reports calls to unknown functions |
| 2.70 | `errfunk` shows all arguments to `log`, as a bad `log` argument is the most common error |
| 2.71 | Clear message when a variable name and an operator are not separated in `upd` |
| 2.77 | Normalize stops on reserved variable names with a clear error |
| 2.79 | Clear error when the model text has no `FRML` statements |
| 2.79 | Clearer fbmin message when feedback variables are not directly connected |
| 2.88 | A function name with a lag, such as `EXP(-1)`, raises an error; `INSPECT`, `JIT` and `CLASSFUNK` can be used as variable names |

## Fixes

### Solving

| Version | Change |
|---|---|
| 2.59 | Deterministic prolog/epilog order |
| 2.89 | The minimal feedback set is the same in every Python session, so solutions with `use_fbmin=True` (the default) are replicable to the last digit |
| 2.89 | `newtonstack_fbmin_ng` reports the residual at the solution when it finishes (it showed the one from before the last Newton step) |
| 2.89 | `model.fix` works under pandas 3 when the `_X`/`_D` columns were read as integers |
| 2.87 | `newton_implicit` gives correct results on normalized and hybrid models |
| 2.87 | `newtonstack_ng(split=1)` gives correct results on hybrid models |
| 2.87 | Implicit models no longer regenerate solver code on every solve |
| 2.88 | Newton solvers always report non-convergence, including with `silent=1` |
| 2.88 | `sim1d`, `sim1d_ng`, `base_sim` and `base_res` raise an error on models with leads |
| 2.88 | `keep`, `keep_variables`, `setbase` and `setlast` apply to one call only |
| 2.88 | `targets_instruments` restores options and sample, also when it fails |
| 2.88 | The `fair_max_iterations` option is no longer ignored |
| 2.88 | Legacy jit solvers rebuild the transpiled code when it changes |
| 2.90 | `newtonstack_ng(split=1)` works when the core reads no core variable (only leads or a fixed period of the prolog); it raised `AttributeError` |
| next | A solution with NaN or inf is no longer reported as converged, in the `_ng` solvers and in `sim`, `sim1d` and `base_sim`; the Gauss-Seidel solvers stop iterating and name the NaN variables |

### Equations and parsing

| Version | Change |
|---|---|
| 2.76 | `smpl` in Makemodel and markdown with estimation fixed |
| 2.77 | Fixed `PCT` in normalize and the missing add factor in `flipendo` |
| 2.88 | `LOGIT(1-S)` is expanded with parentheses |
| 2.88 | `CONSUM(-1)` is no longer read as `SUM`, and `RDIFF(-1)` is no longer read as `DIFF` |
| 2.89 | A function name followed by a signed number, such as `LOG(+25)`, loads again (2.88 refused it, which stopped FRB/US models from loading) |
| 2.92 | Makemodel `type_input='eviews'` no longer fails with an `ImportError` |

### Attribution, reports and display

| Version | Change |
|---|---|
| 2.59 | Removed a future warning in `dekomp` |
| 2.63 | `ibsstyle` tooltips fixed |
| 2.63 | No text substitution when writing LaTeX reports |
| 2.73 | Fixed a pandas 3 error in groupby `dekomp` |
| 2.78 | Continuation lines in HTML reports fixed |
| 2.88 | `dekomp` works with `basedf=` / `altdf=` and follows a changed `smpl` |
| 2.88 | `explain` uses the current attribution for "% Explained by" |

### Other

| Version | Change |
|---|---|
| 2.60 | Dash: `app.run_serve` changed to `app.run` |
| 2.63 | `modelload` works for files with data but no model |
| 2.63 | `var_description` and `cty` fixed in `modelgrabwf2` |
| 2.71 | `mfcalc` rewritten for pandas 3 |

## Changed behaviour to watch for

Code written for the book may behave differently in these cases:

| Version | Change |
|---|---|
| 2.83 | `modelflow_auto` no longer autoruns the notebook; it only makes it wider |
| 2.83 | `display_toc` no longer shows the root folder name (`showroot=True` brings it back) |
| 2.83 | Python 3.12 or newer is required |
| 2.88 | `keep=` and the related options no longer carry over to later `model()` calls |
| 2.88 | `model.test_model` is the new version; the old one is `model.test_model_old` |
| 2.88 | `model_Excel` is now `modelgrabexcel` (the old name warns) |
| 2.89 | `newtonstack_ng` uses `split=1` by default; `split=0` gives the old behaviour (the solutions agree within the convergence tolerance) |
| next | A run that ends with NaN or inf in the solution now reports non-convergence; before, it could be reported as converged |
