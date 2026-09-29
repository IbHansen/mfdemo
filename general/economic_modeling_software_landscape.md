# Software Used for Economic Model Building and Simulation

## Summary

There is no single dominant software package across all economic modelling. The software used depends strongly on the type of model:

| Model type | Established software | Increasingly important alternatives |
|---|---|---|
| Large macroeconometric / semi-structural models | **EViews**, MATLAB, TROLL and institution-specific systems | **Python**, Julia |
| DSGE / rational-expectations models | **Dynare**, usually with MATLAB or Octave | Dynare on Julia, native Julia and Python tools |
| CGE / trade / climate / energy models | **GAMS**, **GEMPACK**, MPSGE | Python-based CGE frameworks |
| Heterogeneous-agent / computational macro models | MATLAB, Dynare | **Python, Julia, Econ-ARK, QuantEcon** |
| Econometric estimation and forecasting | EViews, MATLAB, Stata, R | **Python**, Julia |

A reasonable description of the current landscape is therefore:

> **EViews, Dynare and GAMS/GEMPACK remain major established specialist platforms for economic models, while Python and Julia are becoming increasingly important as open-source computational environments.**

This is not a market-share estimate. Published surveys usually cover particular model classes or institutions rather than all economists.

---

## 1. BIS survey of open-source central-bank macroeconomic models

A particularly useful source is Douglas Araujo's 2025 paper for the Bank for International Settlements (BIS), **“Open-sourced central bank macroeconomic models.”**

The paper inventories actual official-sector macroeconomic models and reports their implementation languages or packages. In the sample, the main systems include:

- MATLAB, often associated with **Dynare**
- **EViews**
- Portable TROLL
- Julia
- SAS
- EUCAM
- GAP
- **GAMS**

The paper specifically notes that Dynare is an important reason why MATLAB is widely used for central-bank models.

The underlying information in the software table is from September 2023, so it should be interpreted as evidence about the installed base of official models rather than a complete 2026 software census.

Source:

- [BIS: Open-sourced central bank macroeconomic models](https://www.bis.org/ifc/publ/ifcb64_17_rh.pdf)

---

## 2. European Central Bank and the ESCB

The ECB's 2025 review, **“The ESCB forecasting models: what are they and what are they good for?”**, surveys modelling practice across the European System of Central Banks.

It finds that central banks use several complementary model types:

- semi-structural models,
- DSGE models,
- time-series models,
- specialised satellite models.

Semi-structural models are particularly important for baseline forecasting because they combine empirical structure with the possibility of expert judgement and country-specific detail.

This is important when discussing software because it shows that large operational forecasting models have not been displaced by DSGE models. There remains a substantial institutional role for the type of large or semi-structural system historically handled by software such as EViews, TROLL and institution-specific modelling systems.

Source:

- [ECB: The ESCB forecasting models, Occasional Paper No. 381](https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op381.en.pdf)

An earlier ECB review from 2021 also documents the mixture of software environments used in Eurosystem modelling, including MATLAB/Dynare, EViews and other systems.

- [ECB: Review of macroeconomic modelling in the Eurosystem, Occasional Paper No. 267](https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op267~63c1f094d6.en.pdf)

---

## 3. EViews is still actively used

EViews remains relevant for operational macroeconomic modelling.

In April 2026 the IMF published **“Solving the Canonical Quarterly Projection Model Using EViews.”** The Quarterly Projection Model is one of the IMF's standard frameworks for monetary-policy analysis and forecasting-policy analysis systems.

The note explains how the canonical QPM can be implemented, solved and used for scenarios in EViews.

Source:

- [IMF: Solving the Canonical Quarterly Projection Model Using EViews](https://www.imf.org/en/publications/tnm/issues/2026/04/06/solving-the-canonical-quarterly-projection-model-using-eviews-573519)

The US Federal Reserve also continues to distribute the large **FRB/US** macroeconomic model in EViews.

- [Federal Reserve: FRB/US in EViews](https://www.federalreserve.gov/econres/us-models-package.htm)

However, this example also demonstrates the movement toward Python. The Federal Reserve provides a separate Python implementation, PyFRB/US, and updated that package in February 2026.

- [Federal Reserve: FRB/US in Python](https://www.federalreserve.gov/econres/us-models-python.htm)

FRB/US is therefore a useful example of a long-established large macro model being made available in both a traditional specialist package and Python.

---

## 4. Dynare remains central for DSGE modelling

Dynare continues to be one of the main specialist systems for solving and estimating DSGE and related dynamic macroeconomic models.

Dynare currently supports MATLAB and GNU Octave and is also developing a Julia implementation. Dynare 7.1 was released in May 2026.

Its continued institutional importance is also indicated by financial support from organisations including the European Central Bank, Banque de France and the European Commission's Joint Research Centre.

Source:

- [Dynare](https://www.dynare.org/)

---

## 5. GAMS and GEMPACK dominate much of the CGE tradition

For computable general-equilibrium models, the software picture differs from central-bank forecasting models.

The OECD states explicitly that:

> Most existing CGE models are built using packages such as GAMS or GEMPACK.

The OECD contrasts this established infrastructure with its newer Python-based `cge_modeling` framework, which can compile models to JAX and make use of the wider Python scientific ecosystem.

Source:

- [OECD: Software infrastructure for CGE modelling](https://www.oecd.org/en/publications/energy-prices-and-subsidies-in-the-western-balkans_082ea26a-en/full-report/scenarios-for-energy-market-reform-in-the-western-balkans_dc1608be.html)

The World Bank's MANAGE-WB CGE framework is another important example. Its public implementation requires GAMS.

- [World Bank: CGE modelling and MANAGE-WB](https://www.worldbank.org/en/programs/economicpolicy-macro-modeling/cge)

GEMPACK should therefore be mentioned alongside GAMS. The standard GTAP global trade model is implemented in GEMPACK.

- [GTAP: GEMPACK requirements for the standard GTAP model](https://www.gtap.agecon.purdue.edu/products/requirements.asp)

For CGE modelling, the established pair is therefore better described as:

> **GAMS / MPSGE and GEMPACK / RunGTAP**

rather than GAMS alone.

---

# Society for Computational Economics

The **Society for Computational Economics (SCE)** provides a useful view of the research frontier rather than the installed software base inside central banks and ministries.

Its purpose explicitly includes:

- numerical solution of economic models,
- econometric computation,
- simulation,
- artificial intelligence,
- large-scale and distributed computing,
- programming and modelling languages,
- software libraries.

Source:

- [Society for Computational Economics](https://comp-econ.com/)
- [SCE: About the Society](https://comp-econ.org/about/)

## SCE computational resources

The Society's current **Computational Resources** page prominently lists:

- **Dynare**
- **Econ-ARK**
- **IRIS Macroeconomic Modeling Toolbox**
- **Macroeconomic Model Data Base**
- **QuantEcon**
- code and courses from researchers in computational economics.

Source:

- [SCE: Computational Resources](https://comp-econ.com/computational-resources/)

This is noteworthy because EViews, GAMS and GEMPACK are not the main emphasis on this SCE resource page. The emphasis is much more strongly on dynamic modelling, numerical methods and open computational frameworks.

## CEF 2026

The Society's 32nd Conference on Computing in Economics and Finance, held in Venice in June–July 2026, gives an even clearer indication of current research directions.

The conference included a special session:

**“Dynare and the Evolution of Economic Dynamic Methods.”**

The session connected DSGE modelling in Dynare with:

- agent-based models,
- heterogeneous-agent models,
- HANK models,
- newer econometric approaches,
- artificial intelligence,
- machine learning,
- reinforcement learning,
- model-predictive-control methods.

Source:

- [SCE: CEF 2026](https://comp-econ.com/32nd-cef-conference/)

CEF 2026 also opened with a pre-conference workshop on **computational toolkits and standards**, co-hosted with Econ-ARK, with participation from representatives of **Dynare, QuantEcon and other computational-economics groups**.

This suggests that interoperability, open-source software and common computational standards are becoming important issues in the computational-economics community.

The movement toward Python and Julia is not entirely new. As early as the 2014 SCE conference, the Society offered a workshop titled **“Scientific Computing in Python and Julia”**, covering Python, SciPy, pandas, statsmodels, Numba and Julia for economic modelling.

- [SCE 2014 workshop: Scientific Computing in Python and Julia](https://comp-econ.org/CEF_2014/PreConf.htm)

---

# Overall assessment

The evidence suggests two overlapping software worlds.

## Established policy-model infrastructure

For operational models used in central banks, international organisations and policy institutions, the traditional specialist packages remain highly important:

- **EViews** — large macroeconometric and semi-structural models;
- **Dynare + MATLAB/Octave** — DSGE and rational-expectations models;
- **GAMS** — CGE, optimisation, energy and climate models;
- **GEMPACK** — CGE and especially the GTAP modelling tradition;
- legacy or institution-specific systems such as TROLL also remain in use.

## Emerging computational infrastructure

The Society for Computational Economics and newer institutional projects show a clear movement toward:

- **Python**
- **Julia**
- Econ-ARK
- QuantEcon
- JAX and automatic differentiation
- open-source model repositories
- reusable numerical and modelling libraries
- reproducible computational workflows.

Thus the most useful concise description of the current situation is:

> **EViews, Dynare, GAMS and GEMPACK remain the major established specialist economic-modelling environments, but Python and Julia are increasingly important as the common open-source computational layer around — and in some cases replacing — specialist modelling packages.**

For large macroeconomic models in particular, the Federal Reserve's parallel EViews and Python versions of FRB/US are a good illustration of this transition.
