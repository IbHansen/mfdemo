# Installing ModelFlow

This chapter sets up ModelFlow on a Windows PC: Miniforge (a small conda
distribution), a conda environment with ModelFlow, and the programs to work
in: Jupyter Notebook 7, JupyterLab, Spyder and VS Code.

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

## 8. Trying ModelFlow without installing

[**ModelFlow in the browser (JupyterLite)**](https://ibhansen.github.io/jupyter_lite/)
runs ModelFlow inside your web browser, with nothing to install and no account
needed. It opens with the Pakistan model, and has the World Bank country models
and examples. Solving is slower than on a PC (no numba), and the Dash
dashboards don't work.
