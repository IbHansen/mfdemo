# Historical Background: From MACRO and PCIM to ModelFlow

## Overview

ModelFlow's translation architecture has predecessors in earlier economic-model systems. A recurring design idea has been to transform only the notation specific to economic modelling and delegate the general-purpose language processing and numerical execution to an established programming language and compiler.

This history is kept separate from [From model specification to executable code](modelflow_specification_to_code.md), which describes the same idea in its present form.

The point of recording it is not nostalgia. The architecture now used by ModelFlow was not arrived at by designing for Python. It was first used around 1983, thirty years before ModelFlow was begun, and it has since been implemented three times in four different languages.

It is not, however, a story of continuous evolution, and the line is not even unbroken. PCIM, the second generation, was replaced in 2009 by Gekko, a C# system that took over the handling of ADAM. ModelFlow is not PCIM's successor in that sense; that role belongs to Gekko. ModelFlow arose separately, four years later, from an unrelated practical problem — the maintainability of bank stress-test models built in Excel — and the older architecture was adopted because it turned out to answer that problem too. The same author wrote PCIM and ModelFlow, which is why the resemblance is not a coincidence; but the later system was a fresh start rather than a port, and it reached its design by re-deriving it rather than by inheriting it.

Nor was the architecture designed in the abstract at any point. Each generation was a response to an immediate practical difficulty:

| Generation | The problem that forced it |
| --- | --- |
| **MACRO / NASS**, ~1983 | A new version of ADAM that TSP could not handle, and TSP could not be modified |
| **PCIM**, 1985 | ADAM was expensive to run and reachable only by the few institutions that could afford it |
| **ModelFlow**, ~2013 | Bank stress-test models in Excel that had become unmaintainable |

That an architecture first reached for under deadline on a mainframe should still be the right answer to spreadsheet maintainability in a bank thirty years later is reasonable evidence that it is a property of the *problem* — translating economic notation into something a machine can evaluate — rather than an artefact of any one language, machine or application.

## ADAM, TSP, MACRO and NASS

Around 1983, at **RECKU**, the computer centre of the University of Copenhagen, the present author used UNIVAC MACRO to **connect the ADAM model from TSP to NASS**, the simulation system at **Danmarks Nationalbank developed by Jørgen Petersen**.

### The forcing problem

This was not an architectural exercise. ADAM had until then been handled in TSP. A new version of the model was then produced which **TSP could not handle**, and TSP was not a system that could be modified to accommodate it.

That left an immediate and practical difficulty: an existing model, a new version of it that the existing tool would not run, and no possibility of changing the tool. Moving the model to NASS was the way out, and it had to work.

The architecture described here was a response to that, arrived at under time pressure. It is worth keeping in mind when reading what follows, because the same is true of each later generation.

### The mainframe setting

The work was done on a **UNIVAC 1100**, a mainframe on which simulation ran in **batch mode**. A run was submitted, waited for, and paid for: both the **cost and the elapsed time** of a simulation were significant.

This shapes everything about the period. Iteration was expensive, so a model run was something to be got right rather than repeated casually, and any error that surfaced only at run time was costly in a way that is difficult to appreciate now. It also makes the attraction of the following generation obvious: a PC, however limited, gave the modeller a machine that could be run again immediately and at no marginal cost.

### What MACRO was

UNIVAC MACRO was a **pattern-matching and text-substitution language** available on the 1100 series, intended for **source-to-source transformation** — producing program source from other program source. RECKU published its own manual for it {cite:p}`frentz_macro_1981`, under a title that says plainly what it was taken to be: *Tekstbehandlingssystemet MACRO* — the text-processing system MACRO.

It is worth being clear about how little it knew. MACRO was not a modelling tool, had no notion of an equation, a variable or a lag, and no arithmetic interest in what it processed. It read text, recognized patterns in it, and emitted other text. Everything specific to economics had to be expressed as patterns to match and text to substitute in their place.

That turns out to be exactly the right amount of knowledge for the job, and the reason it was the right tool is the reason the same shape of tool is still used today: the task is not to understand the equations, only to re-express the parts of them that the target language does not already understand.

### Translation into FORTRAN

NASS was written in FORTRAN. Economic equations therefore had to be transformed into a representation suitable for the NASS/FORTRAN environment: the model specification originated as ADAM in and from TSP, MACRO performed the pattern matching and substitution, FORTRAN was the target language, and NASS provided the simulation machinery.

The economic equations already contained most of the required expression structure — arithmetic, parentheses, precedence, function calls. None of that had to be re-implemented, because the FORTRAN compiler already knew how to handle it. What did *not* exist in FORTRAN was the model-specific notation: the meaning of a lag, the distinction between an endogenous and an exogenous variable, the mapping from a variable name to a location in the data. MACRO could concentrate on exactly that, and hand everything else to the compiler.

This is the division of labour that the current system still uses, with `ast` and the Python compiler in place of the FORTRAN compiler.

## PCIM: the PC generation

**PCIM** — *PC Integrated Modelling* — moved this type of modelling architecture onto the PC. Written by the present author, it was started in **1985** and handled ADAM until **2009**, when **Gekko**, a system written in C#, took over.

Twenty-four years is a long life for a program written for an 8086, and the length of service is easier to show than to assert: the model group at Statistics Denmark was still publishing guides to running ADAM in it in the 1990s {cite:p}`kristensen_introduktion_1996,dst_pcim_brugerhaandbog_1999`, a decade after it was written.

### Who could afford to run a model

The purpose was not primarily technical. It was to make using ADAM **cheap**, and thereby to make it **available to a far wider group of economists**.

On the mainframe, the cost and turnaround described above were not merely an inconvenience; they were a barrier to entry. Running the national model was in practice reserved for the few government bodies with the resources to do it. Everyone else could read about ADAM, and argue about its results, but could not put a question to it themselves.

A model that only a handful of institutions can run is a different kind of object from one that any competent economist can run — as an instrument of analysis, and as a subject of debate. Moving ADAM to the PC changed which of the two it was. Against the mainframe the PC gave up memory, speed and storage; what it offered in return was a model on the desk of anyone who wanted one, at no cost per run.

That trade is what the memory problem described next was the price of.

### The machine, and what it could not do

PCIM was developed in 1985 on an **Olivetti M21**, fitted with an Intel **8086** and an **8087** floating-point coprocessor.

Both chips mattered. Early PCs did floating-point arithmetic in software, which for a model of ADAM's size would have been hopeless. The 8087 did it in hardware. The 8086, for its part, had a full 16-bit path to memory where the IBM PC's 8088 had only eight bits externally, so data access was correspondingly faster.

It is worth pausing on what that hardware could actually do. Depending strongly on the operation, an 8087 delivered floating-point performance on the order of **tens of thousands of operations per second**, enormously below a present-day processor. A national macroeconomic model was nevertheless solved, repeatedly and usefully, on that hardware.

Memory was the harder limit. The machines of the day offered **640 KB of RAM**, and neither ADAM's data nor the generated code came close to fitting in it. Underneath that sat the **64 KB segment** that 8086 addressing imposed, constraining how data could be addressed even within the memory that did exist.

That the whole thing was possible at all was not obvious at the time. The project began as a wager — **a box of beer that it could be done**. How it was won is the subject of *The solver* below, and the two decisions that won it outlived the constraint that forced them.

### Two languages

PCIM itself was written in **FORTRAN**, while the **text-processing and substitution component was written in Pascal**. The numerical model and simulation machinery belonged naturally in FORTRAN; Pascal provided the textual front end that read the economic specification and produced FORTRAN from it.

The choice of two languages is the architecture showing through. The transformation stage and the execution stage have genuinely different requirements — string handling and pattern matching on one side, numerical throughput on the other — and each could be written in whatever language suited it. The boundary between them is generated source text, which any language can write and any compiler can read.

What that freedom was actually spent on here was the compiler. The FORTRAN was compiled with **Ryan-McFarland FORTRAN**, chosen for one specific reason: RM/FORTRAN supported **arrays larger than the 64 KB segment**. A model databank does not fit in 64 KB, so a compiler that could not exceed it was of no use whatever else it did well. Because the boundary was generated text, the front end neither knew nor cared which FORTRAN compiler consumed its output, and the compiler could be picked purely on what the machine demanded.

### What the user saw

The two parts are visible in the contemporary user documentation, which describes PCIM as consisting of one — "which few users ever become acquainted with" — that turns a model into an executable file, and the executable itself, which understands the commands a user issues for model runs {cite:p}`dst_pcim_brugerhaandbog_1999`. A model was a `.frm` formula file compiled into a matching `.exe`; the May 1998 version of ADAM was `maj98.frm` and `maj98.exe`. That the translation stage was invisible to most users is exactly the intention: the generated code is an implementation detail.

The same handbook shows how much of the current feature set the system had acquired. Alongside simulation, PCIM offered **exogenization and endogenization**, **calculation of add factors**, and target-instrument analysis. These are the operational transformations described in [From model specification to executable code](modelflow_specification_to_code.md), under recognizably the same names, documented in 1999 — a decade and a half before ModelFlow re-derived them.

What the user saw changed more than what ran underneath it. The early system relied on conventional **FORTRAN `READ` and `WRITE`** interaction; later the front end moved to **Windows**, giving users a more modern way to prepare runs, inspect results and operate the model. The equation generator and the solver were left largely unchanged — the interface could be replaced without redesigning them, which is the same separation at work one level up.

### The solver, and how 640 KB was won

The basic numerical method was conventional **Gauss-Seidel**, already old long before PCIM. The distinctive engineering problem was not inventing an iteration scheme but arranging a large econometric model so that repeated equation evaluation was fast and feasible on the available hardware.

The equations were generated as FORTRAN assignments and evaluated sequentially. As soon as an endogenous variable had been recalculated, its new value was available to equations later in the same sweep. That algorithm stayed in use for PCIM's whole lifetime, from 1985 to 2009, while the hardware, the data precision and the user interface all changed around it.

Getting it into 640 KB took two decisions.

The first was to recognize that solving a period does not require the whole databank. It requires the current value of each variable and those lagged values that actually occur in the equations — and nothing else. PCIM therefore assembled a **solution vector** holding exactly that working set, and kept only it in memory while solving. The rest of the data stayed on disk.

The second was **segmentation of both code and data**, so that only the part of the generated code being executed, and only the data it needed, had to be resident at any moment.

Together they were enough. The wager was won — and won more comprehensively than the terms required, since PCIM went on to handle ADAM for the next twenty-four years.

Neither decision is a modelling idea; both are consequences of the machine. What became of them afterwards is more interesting than either.

### What became of the two memory decisions

Segmentation went when the constraint went, and left nothing behind. The operating system does that work now, and the machinery for it is simply gone.

The solution vector did not go. As memory stopped being scarce the pressure that produced it went away, and something else was bought with the same money: under the original constraint the arithmetic was done in **single precision**, and once memory was no longer the binding limit it moved to **double**. That did more than add significant digits. The greater precision made the iterative solution converge more cleanly and could cut the number of iterations enough to improve overall solving speed, despite each value taking twice the memory, and it allowed convergence tolerances to be set with less concern for rounding noise.

The vector survived anyway, for a reason that had nothing to do with the one that created it. Packing the values the equations need into one compact, contiguous block means consecutive equations read memory that is close together. On machines with a cache hierarchy that **improved the cache hit ratio** — the working set now fits in cache for much the same reason it once had to fit in RAM. A design forced by a 640 KB limit turned out to be a good design on machines with a thousand times more memory, because the relevant scarcity had moved up a level rather than disappeared.

It is still in the code. ModelFlow contains one Gauss-Seidel solver built on a stuffed one-period vector, computing a fixed offset for each variable and lag, gathering the working set into one contiguous array before iterating and writing only the endogenous results back afterwards. Its stated advantages are the 1985 ones: compile-time offsets and data locality.

It is an experiment rather than the working default, though. The ordinary solvers index the full two-dimensional array directly, and on modern machines that is fast enough that the extra gather-and-scatter has not earned its place in the mainline.

So of the two decisions that won the beer, one is gone and the other is kept as a curiosity. What actually survived into everyday use is neither of them, but the habit of thought behind them — the subject of *Continuity of the design idea* below.

## A different problem

The lineage described so far ends in 2009 with Gekko — a normal succession, and not the origin of what follows.

ModelFlow began some four years later, around **2013**, and somewhere else entirely: from the **maintainability of bank stress-test models built in Excel**.

A spreadsheet is an excellent calculator and a poor model specification. The economic logic is distributed across cells rather than written down anywhere; the specification, the data and the presentation occupy the same object; and repeated structure — the same relationship across many portfolios, exposures or scenarios — has to be produced by copying formulas, after which the copies are independent and can silently diverge. None of this matters much for a small calculation. For a stress-test model that has to be reviewed, audited, re-run under many scenarios and handed to someone else, it matters a great deal.

Stated that way, the problem is recognizably the one the older architecture had always addressed: separate the economic specification from its implementation, write each relationship once, and generate whatever the machine needs from that single authoritative statement.

### Why not restart PCIM

The obvious move would have been to revive the existing system, which already embodied the answer — by then no longer in service, and so in principle available.

It was rejected for the same reason that had motivated the exercise in the first place. Bringing a Pascal and FORTRAN system from the 1980s back into service would have created a maintainability problem of its own — and solving a maintainability problem by taking on another is not progress.

The alternative had also become considerably more attractive in the intervening years. Much of what PCIM had been obliged to build for itself was by then available off the shelf in Python — the extent of it is set out under *What changed* below — while the part that genuinely had to be written, the model-specific translation, was the part the architecture had always isolated anyway.

So the architecture was carried forward and the implementation was not. ModelFlow is a new system rather than a translation of the old one — what it inherits is a design, not a code base.

## Continuity of the design idea

The implementation technologies changed completely, and the third entry is not a continuation of the second — ModelFlow was written from scratch, for a different purpose. The architecture nonetheless remained recognizable.

| Generation | Economic specification | Transformation | Target language | Runtime |
| --- | --- | --- | --- | --- |
| **UNIVAC / NASS**, from ~1983 | ADAM equations from TSP | MACRO | FORTRAN | NASS |
| **PC / PCIM**, 1985 – 2009 | Economic equations | Pascal text processing | FORTRAN | PCIM |
| **Python / ModelFlow**, from ~2013 | ModelFlow DSL or imported model | Expansion, normalization, AST validation, token rewriting | Python (optionally Numba) | ModelFlow |

The first two generations targeted macroeconomic models — ADAM in both cases. The third began from bank stress testing and has since been applied to macroeconomic models as well, which is the reverse of the path one might expect and a further sign that the architecture is not tied to a particular class of model.

The recurring principle is:

> **Transform the economic notation that is specific to modelling, and delegate the general-purpose programming-language work to an existing compiler or language implementation.**

Four things stayed constant across all three generations:

- the **boundary is generated source text**, not a shared in-memory data structure, which is what allows the two sides to be written in different languages and replaced independently;
- the transformation stage handles **only** the model-specific notation, never the general expression grammar;
- the modeller writes economic equations, and the generated code is treated as an implementation detail they are not expected to read;
- **variable names are resolved to fixed positions once**, while the code is being generated, so that solving is arithmetic on numbered slots rather than repeated lookup by name.

The last of these is worth drawing out, because it is easy to mistake for an implementation detail of whichever language is in use. It is not. The FORTRAN arrays of the earlier systems and the NumPy array the current system indexes as `values[row, 42]` embody the same decision: a name is something the *modeller* uses, a position is something the *machine* uses, and the translation between them belongs at code-generation time — once — rather than in the inner loop.

Note that this is the durable inheritance, and it is a more modest claim than it might first appear. What carried forward is resolving names to positions, which every ModelFlow solver does. The particular way PCIM arranged those positions — one contiguous working-set vector — did not carry forward into normal use, and did not need to.

## The same approach elsewhere

Nothing described here is a private invention, and it would be misleading to present it as one. Translating an economic model into a general-purpose programming language, and letting that language's compiler do the rest, is a recognized way of building modelling systems, arrived at independently by others.

**Dynare** is the clearest contemporary example. A model is written in Dynare's own `.mod` notation; a preprocessor reads it and **generates MATLAB/Octave code**, which is then executed {cite:p}`adjemian_dynare_2011`. The economic notation is Dynare's; the expression language, the numerical libraries and the runtime are MATLAB's. That is precisely the division of labour described in this document, with a different source notation and a different target language.

The resemblance goes further than the split itself. The generated files include a `driver` that runs the computing tasks, and separate static and dynamic model files that return the residuals of the equations **and their Jacobian** — the same derivative-generation step described in [Model structure and solution](modelflow_structure_and_solution.md), arrived at for the same reason. And the preprocessor takes an option `language=matlab|julia`, which is the clearest possible demonstration of what the architecture buys: when the boundary is generated source text, the target language becomes a setting rather than a rewrite.

**Project LINK**, the international linked-model project, belongs to the same tradition. {cite:t}`petersen_computer_1987` describe its solution machinery, and the resemblance to what is described in this document extends well past the translation step.

Two points from that account are worth singling out.

The first is the **solver hierarchy**: Jacobi, Gauss-Seidel and Newton, applied according to how difficult the system proves to be. That is, in outline, the arrangement ModelFlow arrived at independently — Gauss-Seidel as the ordinary method for models that suit it, Newton reserved for the harder nonlinear and simultaneous cases. The reasoning behind the hierarchy is the same in both: Newton is more powerful and more expensive, so it is worth using only where cheaper iteration fails.

The second is that LINK was solved on an **IBM 3090** with a **parallel and vector implementation**. The specific techniques have dated, but the underlying position has not: a model system that generates its own computational code is in a good position to exploit whatever the hardware of the day rewards, because the generator can emit whatever form the machine prefers. What was vector code on a 3090 is machine code from a just-in-time compiler now, and the reason both are available is the same — the equations are text at the point where the decision is made.

None of this is folklore, either. The numerical side of it — the iterative methods, the ordering and decomposition of large systems, the sparse techniques — is documented as a subject in its own right, most fully by {cite:t}`pauletto_computational_1997`, whose account of solving large macroeconometric models covers much the same ground as [Model structure and solution](modelflow_structure_and_solution.md).

The convergence is the interesting part. These systems were built by different people, in different countries, for different models, in different decades, with no particular reason to imitate one another. That they arrived at the same arrangement — the same separation of specification from execution, and in LINK's case the same hierarchy of solvers on top of it — is better evidence for the argument made in this document than the persistence of a single lineage could ever be. The architecture is a response to the shape of the problem, and people who take the problem seriously tend to end up somewhere near it.

There is a neat consequence. ModelFlow can **import and solve Dynare models**, so far as they fall within what it can handle.

That it works at all follows from the shared architecture. Both systems keep the specification separate from the machinery that runs it. Each leaves a specification the other can read.

## What changed: the scope of what can be delegated

The principle survived unchanged, but its leverage grew, because the amount of work that can be handed to someone else grew. This was the deciding argument against restarting PCIM, and it is worth setting out in full.

In the FORTRAN generations, essentially one thing was delegated: parsing and compiling the expression language. Everything else had to be written, and — as the 640 KB problem shows — that included work at a considerable distance from economics. Deciding which values constitute the working set, segmenting code and data, and orchestrating what was resident at any moment were all part of building a model system, because nothing else was going to do them.

The current system delegates considerably more, and to specialized libraries rather than to a single compiler:

| Task | Delegated to |
| --- | --- |
| Expression grammar, compilation, execution | Python |
| Machine-code compilation of the generated equations | Numba |
| Symbolic differentiation and equation rearrangement | SymPy |
| Graph decomposition, ordering, feedback sets | NetworkX |
| Sparse matrix storage and LU factorization | SciPy |
| Data management, periods, series alignment | pandas |
| Visualization and reporting | the wider Python ecosystem |
| Memory residency and paging | the operating system |

This is why the current system can offer things that had no counterpart in the earlier generations — automatic Jacobians from symbolic differentiation, prolog/core/epilog decomposition and feedback-set reduction, sparse and stacked Newton solution for forward-looking models — without a corresponding growth in the amount of model-specific code that has to be maintained.

The architecture did not change to make this possible. It simply became possible to apply the same architecture to more of the problem.

The last row of that table is the one with a moral. Both of PCIM's memory decisions were answers to a constraint the operating system now handles, and both have accordingly lapsed from everyday use, as described above. Neither was kept out of loyalty to a design that once mattered.

That is the harder half of maintaining a long-lived architecture. The principle at its centre was worth carrying across four decades and three implementations; a good deal of what was built around it was worth letting go — including, in the end, the implementation itself.

## A note on sources

MACRO is documented in {cite:t}`frentz_macro_1981`, Project LINK in
{cite:t}`petersen_computer_1987`, and the numerical methods generally in
{cite:t}`pauletto_computational_1997`. PCIM has surviving user documentation from the
model group at Statistics Denmark: the handbook {cite:p}`dst_pcim_brugerhaandbog_1999`,
written by the present author but published without attribution, and Tony M. Kristensen's
introduction to running ADAM in it {cite:p}`kristensen_introduktion_1996`. Statistics
Denmark has confirmed that these may be cited here.

NASS is not documented, and none of these systems was written up as a description of its
design. What is said about their architecture rests on the recollection of the person who
built them; dates and details should be read in that light.

---

*The current architecture continues in [From model specification to executable code](modelflow_specification_to_code.md), [Model structure and solution](modelflow_structure_and_solution.md), and [Local stability and model dynamics](modelflow_stability.md).*
