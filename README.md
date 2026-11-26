# Aspect-Level Financial News Analysis for Goal-Based Investment Decision Support

This repository contains the code, data pipelines, and experimental results for our Final Year Project (FYP). The project integrates fine-grained aspect-level sentiment extracted from unstructured financial news with quantitative portfolio optimization.

## Project Overview
Traditional robo-advisors rely on historical price actions, ignoring the rich context of financial news. This project bridges that gap by utilizing Large Language Models (LLMs) to extract `(Entity, Aspect, Sentiment)` triplets from US financial headlines. These signals will ultimately be used to estimate volatility and improve the probability of achieving goal-based investment targets.

## 📂 Repository Structure
```text
├── docs/               # Taxonomy, annotation guidelines, prompts, and domain gap analyses
├── notebooks/          # Colab/Jupyter notebooks for baselines, LLM evaluation, and variance checks
├── results/
│   ├── figures/        # Confusion matrices, variance screenshots
│   └── tables/         # Evaluation metrics (CSVs), Gold Set annotations, and LLM predictions
└── README.md
