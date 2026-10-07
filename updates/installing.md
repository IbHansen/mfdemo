# Installing ModelFlow

This chapter sets up ModelFlow on a Windows PC: Miniforge (a small conda
distribution), a conda environment with ModelFlow, and the programs to work
in: Jupyter Notebook 7, JupyterLab, Spyder and VS Code.

If you only want to try ModelFlow, you don't have to install anything. The
JupyterLite site runs ModelFlow in the browser, and the Codespace runs it in
the cloud.

## 1. Install Miniforge with winget

[Miniforge](https://github.com/conda-forge/miniforge) is a minimal conda
installer that uses the free `conda-forge` channel. Unlike Anaconda, it has no
licence restrictions for organisations.

`winget` comes with Windows 10 and 11. Open a **Command Prompt** or
**PowerShell** window (no administrator rights needed) and run:

```
winget install -e --id CondaForge.Miniforge3
```

Close the window when it finishes. Windows only reads the new settings in a
new terminal window.

:::{note}
Without `winget`, download the installer `Miniforge3-Windows-x86_64.exe`
from the [Miniforge releases](https://github.com/conda-forge/miniforge/releases/latest)
and run it. Choose *Just Me*. Leave *Add Miniforge3 to my PATH* unticked.
:::

Miniforge is installed in your user folder, normally
`C:\Users\<you>\miniforge3`. The Start menu now has a **Miniforge Prompt**:
a command window where conda is ready to use.

## 2. Make conda work in every terminal: `conda init`

So far conda only works in the Miniforge Prompt. `conda init` sets up both
**Command Prompt (cmd)** and **PowerShell**, so that `conda` and
`conda activate` work in any terminal window. VS Code's terminal and the
terminal in JupyterLab also need it.

Open the **Miniforge Prompt** and run:

```
conda init cmd.exe powershell
```

- For **cmd**, `conda init` adds an *AutoRun* entry for your user in the
  registry (`HKEY_CURRENT_USER\Software\Microsoft\Command Processor`). It
  runs conda's start script every time a Command Prompt opens.
- For **PowerShell**, it adds the start script to your PowerShell profile
  (`Documents\WindowsPowerShell\profile.ps1`).

To check that it worked, open a new **Command Prompt** and a new
**PowerShell** window. In both, the prompt should start with `(base)`, and
this should print the conda version:

```
conda --version
```

If cmd says *'conda' is not recognized*, run `conda init cmd.exe` again from
the Miniforge Prompt. Then open a new Command Prompt; the old one doesn't
pick up the change.

If PowerShell says *running scripts is disabled on this system*, allow
locally created scripts once with the following command, then open a new window:

```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

By default, every new terminal starts in the `base` environment. This setting
controls it:

```
conda config --set auto_activate_base true    # start every terminal in base (default)
conda config --set auto_activate_base false   # start with no environment active
```

## 3. Create an environment with ModelFlow

Keep ModelFlow in its own environment, not in `base`. Then an update of one
project can't break another.

```
conda create -n modelflow -c conda-forge python=3.12 ibh::modelflow jupyterlab spyder -y
conda activate modelflow
pip install dash-interactive-graphviz
```

- `ibh::modelflow` takes ModelFlow from the `ibh` channel and its
  dependencies (pandas, numba, graphviz, pandoc, ...) from `conda-forge`.
- `dash-interactive-graphviz` is only on PyPI. It is used by the `.dash()`
  causality dashboard.
- `spyder` is optional. Leave it out if you don't use Spyder.

Remember `conda activate modelflow` each time you open a new terminal.

### Updating ModelFlow later

```
conda activate modelflow
conda update -c ibh -c conda-forge modelflow
```

Check which version you have:

```
conda list modelflow
```

### Installing with pip

ModelFlow is also on PyPI as `modelflowib`:

```
pip install modelflowib
```

Prefer conda on Windows: pip can't install the graphviz and pandoc programs,
which ModelFlow uses to draw graphs and make reports.

## 4. Start Jupyter Notebook or JupyterLab

Open a terminal and change to the folder with your notebooks. Jupyter only
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

The browser opens by itself. Stop the server with **Ctrl+C** in the terminal.

### Jupyter Notebook 7 and JupyterLab 4

Jupyter Notebook 7 is built on JupyterLab, so the two now share extensions,
widgets and settings. The old *classic* notebook (version 6) is no longer
developed. Some things that worked there don't work in version 7:

| In classic Notebook 6 | In Notebook 7 / JupyterLab |
|---|---|
| `nbextensions` (Table of contents, Hide input, ...) | built in: the table of contents is in the left sidebar; collapse a cell's input by clicking the blue bar to its left |
| A notebook could run itself when opened (`modelflow_auto`) | Not possible. `model.modelflow_auto()` now only makes the notebook wider |
| Widen the page with custom CSS | `model.widescreen()` |
| Long output in a scroll box, fixed with custom CSS | `model.scroll_off()` (works in Notebook 7, JupyterLab and JupyterLite) |
| Markdown only | With `jupyterlab-myst` (installed with ModelFlow), markdown cells render MyST directives, such as `{note}` boxes and `{mermaid}` diagrams, like in a Jupyter Book |

Use **Notebook 7** for one notebook at a time, with a simple screen.
Use **JupyterLab** to work with several notebooks, terminals and files side
by side. Both open the same `.ipynb` files.

A typical first cell:

```python
from modelclass import model
model.widescreen()
model.scroll_off()
```

## 5. Spyder

[Spyder](https://www.spyder-ide.org/) is a scientific IDE in the style of
MATLAB and RStudio, with an editor, a variable explorer and an IPython
console. It suits scripts better than notebooks. Write the script in cells
separated by `#%%`, and run one cell with **Ctrl+Enter**.

If you installed `spyder` in the environment above, start it with:

```
conda activate modelflow
spyder
```

Spyder can't show ipywidgets, so use the notebooks for the interactive
widgets. Tables, plots and `model.draw` work.

## 6. Visual Studio Code

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

## 7. Summary

| Task | Command |
|---|---|
| Install Miniforge | `winget install -e --id CondaForge.Miniforge3` |
| Make conda work in cmd and PowerShell | `conda init cmd.exe powershell` (in the Miniforge Prompt) |
| Create the ModelFlow environment | `conda create -n modelflow -c conda-forge python=3.12 ibh::modelflow jupyterlab -y` |
| Activate it | `conda activate modelflow` |
| Notebook 7 | `jupyter notebook` |
| JupyterLab | `jupyter lab` |
| Spyder | `spyder` |
| Update ModelFlow | `conda update -c ibh -c conda-forge modelflow` |
