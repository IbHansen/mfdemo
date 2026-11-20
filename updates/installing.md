# Installing ModelFlow

This chapter sets up ModelFlow on a Windows PC: Miniforge (a small conda
distribution), a conda environment with ModelFlow, and the programs to work
in: Jupyter Notebook 7, JupyterLab, Spyder and VS Code.

(install-miniforge)=
## 1. Install Miniforge with winget

[Miniforge](https://github.com/conda-forge/miniforge) is a minimal conda
installer that uses the free `conda-forge` channel. Unlike Anaconda, it has no
licence restrictions for organisations.

`winget` comes with Windows 10 and 11. Open a **Command Prompt** or
**PowerShell** window (no administrator rights needed) and run:

```
winget install -e --id CondaForge.Miniforge3
```

:::{note}
Without `winget`, download the installer `Miniforge3-Windows-x86_64.exe`
from the [Miniforge releases](https://github.com/conda-forge/miniforge/releases/latest)
and run it. Choose *Just Me*. Leave *Add Miniforge3 to my PATH* unticked.
:::

Miniforge is installed in your user folder, normally
`C:\Users\<you>\miniforge3`. The Start menu now has a **Miniforge Prompt**:
a command window where conda is ready to use. Run all the commands in this
chapter in the Miniforge Prompt.

(install-environment)=
## 2. Create an environment with ModelFlow

Keep ModelFlow in its own environment, not in `base`. Then an update of one
project can't break another. Open the **Miniforge Prompt** and run:

```
conda create -n modelflow -c conda-forge python=3.14 ibh::modelflow jupyterlab spyder-kernels -y
conda activate modelflow
pip install dash-interactive-graphviz
```

- `ibh::modelflow` takes ModelFlow from the `ibh` channel and its
  dependencies (pandas, numba, graphviz, pandoc, ...) from `conda-forge`.
- `dash-interactive-graphviz` is only on PyPI. It is used by the `.dash()`
  causality dashboard.
- `spyder-kernels` lets Spyder (step 4) run code in this environment. Leave
  it out if you don't use Spyder.

Remember `conda activate modelflow` each time you open a new Miniforge Prompt.

(install-smart-app-control)=
### If `import scipy` fails: Smart App Control

Check that the scientific packages load:

```
conda activate modelflow
python -c "import scipy.special; from modelclass import model; print('ok')"
```

On some Windows 11 PCs this fails with an error like:

```
ImportError: DLL load failed while importing _ufuncs: An Application Control policy has blocked this file.
```

Windows may also show a notice that *part of this app has been blocked*. The
cause is **Smart App Control**, which blocks program files Windows doesn't
know. The packages from conda-forge are not signed, so Smart App Control can
block them. scipy is usually the first to fail, but numba and other packages
can be hit too.

Only do this if you get the error. Turn Smart App Control off:

> Settings → Privacy & security → Windows Security → App & browser control →
> Smart App Control settings → **Off**

On a Danish Windows: *Indstillinger → Beskyttelse af personlige oplysninger og
sikkerhed → Windows-sikkerhed → App- og browserkontrol → Indstillinger for
Smart appkontrol → Fra*.

:::{warning}
On most Windows 11 versions, Smart App Control **can't be turned on again**
without resetting or reinstalling Windows. Microsoft Defender antivirus keeps
running. Smart App Control is already off on many PCs, for instance most
company-managed PCs and PCs upgraded from Windows 10.
:::

If you can't or won't turn it off, ModelFlow can still run in the browser;
see *Trying ModelFlow without installing* at the end of this chapter.

(install-update)=
### Updating ModelFlow later

Don't update the environment. Create it again with the same command as above,
so that ModelFlow and all the packages it uses are new and fit together. Conda
asks whether to remove the existing environment; `-y` answers yes. Run it in a
new Miniforge Prompt, where `modelflow` is not active:

```
conda create -n modelflow -c conda-forge python=3.14 ibh::modelflow jupyterlab spyder-kernels -y
conda activate modelflow
pip install dash-interactive-graphviz
```

Your notebooks and data are not touched; they are in your own folders. Only
packages you have installed in the environment yourself are lost. Install them
again.

Check which version you have:

```
conda list modelflow
```

ModelFlow is also on PyPI (`pip install modelflowib`), but use conda on
Windows: pip can't install graphviz and pandoc, which ModelFlow uses for
graphs and reports.

(install-jupyter)=
## 3. Start Jupyter Notebook or JupyterLab

Open the Miniforge Prompt and change to the folder with your notebooks. Jupyter only
shows files in and below the folder it was started from. Then start one of
them:

```
conda activate modelflow
cd C:\models\mynotebooks
jupyter notebook
```

or

```
conda activate modelflow
cd C:\models\mynotebooks
jupyter lab
```

The browser opens by itself. Stop the server with **Ctrl+C** in the Miniforge Prompt.

A typical first cell:

```python
from modelclass import model
model.widescreen()
model.scroll_off()
```

(install-spyder)=
## 4. Spyder

[Spyder](https://www.spyder-ide.org/) is a scientific IDE in the style of
MATLAB and RStudio, with an editor, a variable explorer and an IPython
console. It suits scripts better than notebooks. Write the script in cells
separated by `#%%`, and run one cell with **Ctrl+Enter**.

Install Spyder as a standalone program, not in the conda environment:

1. Download and run the Windows installer from
   [spyder-ide.org](https://www.spyder-ide.org/download/).
2. Start Spyder from the Start menu.
3. Point it at the ModelFlow environment: **Tools > Preferences > Python
   interpreter > Use the following Python interpreter**, and choose
   `C:\Users\<you>\miniforge3\envs\modelflow\python.exe`. Click **OK** and
   open a new console (**Consoles > Restart kernel**).

This needs `spyder-kernels` in the environment, which the `conda create`
command above installs. If Spyder says the `spyder-kernels` version doesn't
fit, install the version it asks for in the Miniforge Prompt, for example:

```
conda activate modelflow
conda install -c conda-forge spyder-kernels=3.1
```

Spyder can't show ipywidgets, so use the notebooks for the interactive
widgets. Tables, plots and `model.draw` work.

(install-vscode)=
## 5. Visual Studio Code

[VS Code](https://code.visualstudio.com/) opens notebooks and Python
scripts in the same editor. Install it with winget:

```
winget install -e --id Microsoft.VisualStudioCode
```

Then:

1. Install the **Python** and **Jupyter** extensions from Microsoft.
   VS Code offers them the first time you open a `.py` or `.ipynb` file.
2. Open the folder with your notebooks (**File > Open Folder**).
3. Open a notebook and click **Select Kernel** in the top right corner. Pick
   *Python Environments* and then **modelflow**
   (`~\miniforge3\envs\modelflow\python.exe`).

The `#%%` cells in a `.py` file get a *Run Cell* button, as in Spyder.
Widgets and the `model.causality()` viewer work in VS Code notebooks.

(install-conda-terminal)=
## 6. Optional: conda in every terminal

Only needed if you want `conda` in an ordinary Command Prompt or PowerShell,
or in the terminals inside VS Code and JupyterLab. In the Miniforge Prompt run:

```
conda init cmd.exe powershell
```

Open a new window; the prompt should start with `(base)`. If PowerShell says
*running scripts is disabled on this system*, run this once and open a new
window:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

(install-summary)=
## 7. Summary

| Task | Command |
|---|---|
| Install Miniforge | `winget install -e --id CondaForge.Miniforge3` |
| Create the ModelFlow environment | `conda create -n modelflow -c conda-forge python=3.14 ibh::modelflow jupyterlab -y` |
| Activate it | `conda activate modelflow` |
| Notebook 7 | `jupyter notebook` |
| JupyterLab | `jupyter lab` |
| Spyder | Standalone installer from spyder-ide.org; set its interpreter to the `modelflow` environment |
| Update ModelFlow | Run the `conda create` command again (in a new Miniforge Prompt) |
| Optional: conda in cmd and PowerShell | `conda init cmd.exe powershell` |
| Additions: PARDISO, MUMPS, R, EViews, GAMS, Shiny | See [section 8](#install-advanced) |

(install-advanced)=
## 8. Advanced: additions to the environment

The `modelflow` environment from step 2 is enough for most work. The additions
below are only needed for some parts of ModelFlow. Each one is added to the
existing environment, so install only those you need. Each section has the
same four parts: what the addition is used for, what it needs, how to install
it and how to check it.

| Addition | Used for | Needs besides the environment |
|---|---|---|
| [PARDISO](#install-large) | solving large forward-looking models (`factorizer='normal'`, `'pardiso'`) | - |
| [MUMPS](#install-mumps) | `factorizer='mumps'` | an environment of its own |
| [R](#install-r) | estimation with R (`<estimator=r_lm>`, `<estimator=r_nls>`) | R and RStudio |
| [EViews](#install-eviews) | estimation with EViews, EViews models and workfiles | EViews with a licence |
| [GAMS](#install-gams) | results of GAMS models (`.gdx` files) | - |
| [Shiny](#install-shiny) | web apps with `modelinput_shiny` | - |

Run the commands in the Miniforge Prompt. When you create the `modelflow`
environment again to update ModelFlow ([updating](#install-update)), the
additions are gone; install them again.

`numba` (compiled models, `ljit=True`) and `cvxopt` (`factorizer='umfpack'`)
come with ModelFlow and need nothing more.

(install-large)=
### 8.1 PARDISO, for large models

**Used for:** a large forward-looking model solved with the stacked Newton
solver (`newtonstack_ng`) ends in one very large linear system. For systems
too large for the default (SuperLU), `factorizer='normal'` and
`factorizer='pardiso'` use Intel's PARDISO. How to choose and set the options
is in [New features: large models](#largemodels).

**Needs:** nothing besides the environment. Memory is the limit: the Danish
model MAKRO, 100 years with 1.5 million unknowns, needs about 25 GB of free
memory.

**Install:**

```
conda activate modelflow
pip install pypardiso
```

pip also installs Intel's MKL library.

**Check:**

```
python -c "import modelfactorize; print(modelfactorize.mkl_version())"
```

It prints the MKL version, for instance `2026`. The option `iparm={1: 13}`,
the faster factorization, needs 2026 or newer. With an older MKL, ModelFlow
leaves the option out with a note, and the solve still works.

**Good to know:** `ljit=True` compiles the equations with numba. For a large
model the first compile takes long (MAKRO: about 20 minutes). The compiled code
is saved in the folder `modelsource` below the working folder, and later
sessions load it from there.

(install-mumps)=
### 8.2 MUMPS

**Used for:** `factorizer='mumps'`, an LU factorization with pivoting, for
large systems that are too badly conditioned for PARDISO.

**Needs:** an environment of its own. MUMPS can't share an environment with
PARDISO: the two use different OpenMP libraries, and the Jupyter kernel dies
with `OMP: Error #15`. ModelFlow runs MUMPS in a helper process with the Python
of that environment.

**Install:**

```
conda create -n mfmumps -c conda-forge python-mumps numpy scipy -y
setx MODELFLOW_MUMPS_PYTHON %USERPROFILE%\miniforge3\envs\mfmumps\python.exe
```

Open a new Miniforge Prompt and start Jupyter again after `setx`.

**Check:**

```
%USERPROFILE%\miniforge3\envs\mfmumps\python.exe -c "import mumps; print('ok')"
```

(install-r)=
### 8.3 R

**Used for:** estimating equations with R: OLS, Newey-West standard errors and
2SLS (`<estimator=r_lm>`), and nonlinear least squares (`<estimator=r_nls>`).
This comes with the release after 2.94.

**Needs:** R and RStudio, installed as ordinary Windows programs. ModelFlow
doesn't load R into Python. It writes an R script and runs it with
`Rscript.exe`, so R and the packages of the environment never meet, and they
can be updated separately. Nothing is added to the environment.

**Install:** R from [cran.r-project.org](https://cran.r-project.org/bin/windows/base/)
and RStudio from [posit.co](https://posit.co/download/rstudio-desktop/), or
with winget:

```
winget install -e --id RProject.R
winget install -e --id Posit.RStudio
```

Then open RStudio and install the R packages ModelFlow uses, once, in the
*Console*:

```r
install.packages(c("sandwich", "lmtest", "ivreg", "minpack.lm"))
```

If R asks whether to use a personal library, answer yes.

**Check:**

```
conda activate modelflow
python -c "import modelestimator_r as mr; print(mr.find_rscript())"
```

It prints something like `C:\Program Files\R\R-4.6.2\bin\x64\Rscript.exe`.

**Good to know:** ModelFlow finds R in the Windows registry, in
`C:\Program Files\R` or, for an installation without administrator rights, in
`%LOCALAPPDATA%\Programs\R`. The newest version wins. For R in another folder:
`setx MODELFLOW_RSCRIPT "D:\R\R-4.6.2"`, then a new Miniforge Prompt. Install R
only with its own installer, not with conda: conda's R can't be installed in
the ModelFlow environment on Windows.

(install-eviews)=
### 8.4 EViews

**Used for:** estimating nonlinear equations with EViews
(`Estimate_nls_eviews`, `<est=nls_eviews>`), and reading EViews models and
workfiles (`.wf1`, `.wf2`) into ModelFlow.

**Needs:** EViews installed and licensed on the same PC. Python talks to it
through the package `py2eviews`.

**Install:**

```
conda activate modelflow
conda install -c conda-forge eviews::py2eviews
```

**Check:**

```
python -c "import py2eviews; print('ok')"
```

(install-gams)=
### 8.5 GAMS

**Used for:** reading the results of a GAMS model (`.gdx` files) into a
ModelFlow dataframe with `modelgrabgdx`.

**Needs:** nothing besides the environment. GAMS itself doesn't have to be
installed: the package `gamspy-base` brings the GAMS libraries that read
`.gdx` files. The package `gams.transfer` needs pandas older than 3.1.

**Install:** first limit pandas with conda, so that pip doesn't replace conda's
pandas, then install the packages:

```
conda activate modelflow
conda install -c conda-forge "pandas<3.1"
pip install "gamsapi[transfer]" gamspy-base
```

**Check:**

```
python -c "import gamspy_base; from gams import transfer; print(gamspy_base.directory)"
```

It prints the folder with the GAMS libraries.

**Good to know:** from the release after 2.94, `modelgrabgdx` uses the GDX
library of `gamspy-base` by itself. With 2.94, give it the folder:

```python
import gamspy_base
from modelgrabgdx import model_grab_gdx
mgams = model_grab_gdx(['baseline.gdx'], gams_dir=gamspy_base.directory)
```

(install-shiny)=
### 8.6 Shiny

**Used for:** web apps with ModelFlow's input widgets (`modelinput_shiny`).

**Needs:** nothing besides the environment.

**Install:**

```
conda activate modelflow
pip install shiny shinywidgets
```

**Check:**

```
python -c "import shiny, shinywidgets; print('ok')"
```

ModelFlow can also be used from Claude, with plugins and skills for Claude Code;
see [New features: ModelFlow with Claude](#claude).

(install-browser)=
## 9. Trying ModelFlow without installing

[**ModelFlow in the browser (JupyterLite)**](https://ibhansen.github.io/jupyter_lite/)
runs ModelFlow inside your web browser, with nothing to install and no account
needed. It opens with the Pakistan model, and has the World Bank country models
and examples. Solving is slower than on a PC (no numba), and the Dash
dashboards don't work.
