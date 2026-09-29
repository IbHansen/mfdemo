# Introduction

This supplement works one estimation example through from beginning to end: national
accounts data for **Nepal**, a handful of behavioural equations estimated from it, and a
model assembled from those equations that reproduces history and can be simulated.

The point is the sequence rather than any one step. A model is not a set of estimated
equations sitting beside a dataset — it is the equations, the identities that close them,
the add factors that make them fit the past, the machinery that solves the lot, and the
experiments that are the reason for building it at all. This book follows that path once,
end to end, on a model small enough to read in full.

## What is here

**[A model for Nepal](estimation_example.ipynb)** is the whole example:

- entering the data and deriving what the model needs from it,
- a default estimator carrying the sample, the coefficient names and the variable
  descriptions, so each equation can be written without repeating them,
- estimating a single equation and reading the result,
- constraining coefficients where the sample is too short to identify them,
- estimating equations *as part of building the model*, with `Makemodel` and with the
  `%%Makemymodel` magic,
- add factors, which make the assembled model reproduce both the history it was estimated
  from and the forecast that comes with the data,
- solving the model and checking that it returns what it was given,
- and an experiment — exports raised by 10 per cent for three years — solved against that
  baseline and compared with it, with a note on the three other ways a shock can be
  administered.

## What is not here

The **syntax** of estimation — the equation form, coefficient placeholders, the `ST.`
constraint clause, the estimation tags, the available backends and the full option list —
belongs to the language rather than to this example, and is set out in the *Estimation*
chapter of the *ModelFlow - Model Specification* supplement, alongside small synthetic
examples where the right answer is known in advance.

The architecture underneath — how a specification becomes executable code, how the
resulting system is ordered and solved — is described in *ModelFlow - Architecture and
History*.

## Data

The data is annual national accounts for Nepal, taken from a World Bank model. It is
entered directly in the notebook with the `%%dataframe` magic rather than read from a
file, so the example is self-contained and can be run anywhere ModelFlow is installed.
