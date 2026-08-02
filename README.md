# 📊HR Analytics & Attrition Risk Prediction

🔗 **Repository:** [github.com/gcemozdogan/hr-analytics-data-cleaning](https://github.com/gcemozdogan/hr-analytics-data-cleaning)

> ## ⚠️ **Legal Notice & Disclaimer**
>
> This project, along with all associated datasets, models, and visual reports, is built entirely using synthetic (fictional) data generated solely for portfolio, educational, and demonstration purposes. This project has no affiliation, connection, or commercial relation with Beko, Arçelik, or any of their corporate affiliates. Any resemblance to real corporate data or personnel is purely coincidental.

## 🚀 Project Overview
An end-to-end HR analytics project simulating the workforce of a large, multi-country consumer durables organization modeled on **Beko** — the white-goods brand of **Arçelik A.Ş.**, part of **Koç Holding**, operating in 130+ countries. Starting from a purpose-built job grading framework, the project generates a fully synthetic HR master dataset in Python, audits and cleans it, surfaces it through an executive dashboard, and trains a validated machine learning model to predict employee attrition risk.

## 📑 Table of Contents

- [📖 Overview](#-overview)
- [✨ What This Project Demonstrates](#-what-this-project-demonstrates)
- [🔄 Project Pipeline](#-project-pipeline)
- [🏗️ 1. Job Grading Framework & Architecture](#️-1-job-grading-framework--architecture)
- [🧬 2. Synthetic HR Dataset Generation](#-2-synthetic-hr-dataset-generation)
- [🧹 3. Data Auditing & Cleaning](#-3-data-auditing--cleaning)
- [📈 4. Executive HR Dashboard](#-4-executive-hr-dashboard)
- [🤖 5. Attrition Risk Model](#-5-attrition-risk-model)
- [🔍 Key Findings](#-key-findings)
- [🛠️ Tech Stack](#-tech-stack)
- [📂 Project Structure](#-project-structure)
- [▶️ Getting Started](#-getting-started)
- [⚠️ Limitations](#-limitations)
- [📄 License](#-license)

## 📖 Overview

Most public HR analytics datasets (e.g. the classic "IBM HR Attrition" set) are small, static, and disconnected from any real organizational logic. This project takes a different approach: design a **10-level job grading framework** with defined salary bands, apply it to a simulated job architecture by assigning a grade to every position across a full corporate structure, and use that architecture as the foundation to generate a large, internally-consistent synthetic HR master dataset in Python — complete with realistic messiness (duplicate records, inconsistent formatting, business-logic violations) so the full pipeline, from raw export to a validated ML model, can be demonstrated end to end.

## ✨ What This Project Demonstrates

- A 10-level job grading framework with defined salary bands, applied across a multi-department corporate structure
- A Python-based synthetic HR master data generator that mimics a real HRIS (Workday-style) export, with attrition driven by an interpretable, feature-based risk model rather than pure randomness
- An automated data quality audit and cleaning pipeline (encoding issues, inconsistent categorical values, business-rule violations)
- An executive-level HR analytics dashboard (headcount, turnover, cost, org structure)
- An attrition-risk classifier trained with LightGBM and **rigorously validated** for genuine, generalizable signal (leakage-safe encoding + multi-seed stability testing)
- Production-ready exports (risk-scored employee report + serialized model) for downstream BI tools

## 🔄 Project Pipeline

```
job_architecture.xlsx  ──▶  generate_realistic_hr_data.py  ──▶  raw_worker_details.csv
                                                                        │
                                                                        ▼
                                                      hr_data_cleaning.ipynb
                                              (audit → DuckDB cleaning → diff report
                                               → executive dashboard → ML model → export)
                                                                        │
                                        ┌───────────────────────────────┼───────────────────────────────┐
                                        ▼                                                                ▼
                          cleaned_worker_details.csv                                    Active_Employees_Risk_Report.csv
                          Executive HR Dashboard (in-notebook)                          lgbm_attrition_model.pkl
```

## 🏗️ 1. Job Grading Framework & Architecture

The foundation of the entire project is a **10-level job grading framework** (Grade 1 = Director/top of function, Grade 10 = minimum-wage/entry level) with a defined minimum and maximum gross salary band per grade. That framework is then applied to a full **job architecture**: every position across 12 departments — Marketing, Finance, IT, HR, EHS & Administrative Affairs, Corporate Communications & Affairs, Legal, Trade Marketing, Sales Force Effectiveness & Net Revenue Management, Supply Chain, Procurement, and Sales — is assigned a grade, a reporting line, and a salary band, mirroring how a real multinational manufacturer structures its workforce. This architecture (stored in `job_architecture.xlsx`) is the single source of truth that every synthetic employee record is generated against, so titles, grades, and salaries stay organizationally coherent rather than randomly assigned.

## 🧬 2. Synthetic HR Dataset Generation

`generate_realistic_hr_data.py` builds `raw_worker_details.csv`, a ~90-column Workday-style export of 4,000 employee records, entirely in Python. The generation logic works in three stages:

**Stage 1 — Per-employee profile generation.** For each of the 4,000 employees, [Faker](https://faker.readthedocs.io/) (`tr_TR` locale) generates a name, hire date, and date of birth. A position is drawn from the job architecture using **department-weighted random sampling** — Production, Sales, and Supply Chain are weighted heavily to mirror a real manufacturing workforce's shape, while corporate functions (HR, Finance, Legal, etc.) are kept proportionally small. The employee inherits that position's job title, grade, and reporting line, and a `Base Salary` is drawn from within the position's grade band, from which a **Compa-Ratio** (`Base Salary / grade midpoint`) is derived — a real, meaningful pay-equity metric rather than a placeholder. Tenure-related fields (years in current position, years since last promotion) and demographic fields are also assigned per employee at this stage.

**Stage 2 — Interpretable attrition scoring.** Rather than flipping a random coin for who leaves, every employee is given a **churn score** built from realistic, weighted risk factors:

| Risk factor | Score impact |
|---|---|
| Compa-Ratio < 0.85 (underpaid vs. grade) | +60 |
| Last promotion > 3.5 years ago | +40 |
| 4+ years in current position | +30 |
| Age > 56 (approaching retirement) | +30 |
| Individual contributor at grade 8+ | +15 |

40% of employees are then sampled as `Terminated`, **weighted by this score** (via `numpy.random.choice`), so higher-risk profiles are proportionally more likely to be selected — the attrition label is generated *from* the features, not independently of them.

**Stage 3 — Consistent labeling and enrichment.** Each terminated employee is assigned a `Termination Reason` that matches *their own* strongest risk driver — `Pay Dissatisfaction` for a low Compa-Ratio, `Lack of Promotion` for a stale promotion date, `Retirement` for age > 56, `Career Development` for long tenure in position, with a weighted mix of secondary reasons (relocation, personal reasons, work-life balance, health) for everyone else — so every label is traceable back to a real cause. Leave status and leave type (maternity, military, sick, annual) are layered on top for active employees only, with gender-consistent logic for maternity/military leave. Roughly 60 additional Workday-style columns (position IDs, cost centers, manager references, job codes, org hierarchy fields, etc.) are then synthesized to complete a realistic full HRIS export, and the columns are ordered to match a typical Workday extract.

**Intentional data-quality issues are injected on purpose**, so the auditing and cleaning stage has something real to catch: 10 gender spellings/cases (`M`, `m`, `MALE`, `Erkek`, `Kadın`, ...), mixed `Turkey`/`Türkiye`/`UK`/`USA` country values, an intentional `Business Unit` typo (`Adminastrative`), lower-case/untrimmed text fields, a Turkish-character encoding glitch in one name, and 20 fully duplicated rows appended to the final export.

## 🧹 3. Data Auditing & Cleaning

Everything downstream lives in a single notebook, **`hr_data_cleaning.ipynb`**, which reads `raw_worker_details.csv` and writes a separate `cleaned_worker_details.csv` — **the raw export is never modified in place**, so every transformation can be audited by diffing the two files.

**Automated data quality audit.** Before any cleaning is applied, the notebook runs a dedicated audit pass that programmatically quantifies every issue category — duplicate rows, gender-format variants, country variants, the `Adminastrative` typo, the Turkish-character encoding glitch, uncleaned `Business Title` records, `Is Manager` vs. `Number of Direct Reports` contradictions, lowercase-first-letter names, and Grade 9–10 employees incorrectly flagged as managers — turning "the data is messy" into a precise, numbered checklist.

**Cleaning pipeline (DuckDB SQL + a custom Python UDF):**

- **Deduplication** by `Employee ID` (keeping the most recent `Hire Date` per employee)
- **Text standardization** (`Full Legal Name`, `Business Unit`, `Job Title`) via a custom Title Case function that is **Turkish-character-safe** (correctly handles `ü, ö, ç, ğ, ı, ş, İ`) and **acronym-aware** (preserves `HR`, `IT`, `EHS`, `CSR`, `FP&A`, `S&OP`, `B2B`, `L&D`, `C&B`, `BI` instead of lowercasing them to `Hr`, `It`, `Ehs`, ...)
- **Typo correction** (`Adminastrative` → `Administrative`) and **country normalization** (`Türkiye`/`Turkey` → `Turkey`, etc.)
- **Gender standardization** into `Male` / `Female` / `Unknown`
- **Business-rule enforcement:** Grade 9–10 (individual contributor) roles are forced to `Is Manager = No`; Grade 10 employees are forced to `0` direct reports
- **Salary sanity checks** (non-positive `Base Salary` values are nulled rather than silently kept)

Every cleaning run prints a **before/after diff summary**, computed dynamically by comparing every shared column between the raw (deduplicated-only) and cleaned dataframes — the impact of each transformation is verifiable at a glance, never hardcoded.

<img width="1384" height="764" alt="Data Cleaning Summary" src="https://github.com/user-attachments/assets/4c378ada-fdef-4890-9ec9-c3303dcb1563" />

## 📈 4. Executive HR Dashboard

A four-panel executive summary is generated directly from the cleaned dataset, from real computed values only:

1. **Headcount Summary** — active headcount and % of total workforce by department
2. **Turnover Summary** — total employees, terminations, and turnover rate by department, sorted highest-risk first
3. **Personnel Cost & Compa-Ratio Summary** — monthly base salary cost and average Compa-Ratio by department (healthy departments hover close to 100% Compa-Ratio)
4. **Organizational Structure** — headcount, % of workforce, manager count, total direct reports, and **span of control** by grade (computed from actual direct-report counts, not a headcount proxy)

<img width="2184" height="1332" alt="Executive HR Analytics Dashboard" src="https://github.com/user-attachments/assets/74fbcf20-0914-4ce4-8415-461777773f81" />

This dashboard runs on the cleaned dataset alone, before any model is trained — it's a pure reporting layer. The attrition **risk** view (who is likely to leave) only exists once the model below has been trained, and is presented separately in Section 5.

## 🤖 5. Attrition Risk Model

A binary classifier (`Status == Terminated` vs. `Active`) is trained with **LightGBM**, using its native categorical-feature support rather than one-hot encoding (tree models need neither scaling nor dummy variables).

**Feature engineering:**
- `Tenure_Years` — computed from `Hire Date`
- `Compa-Ratio` — recomputed from `Base Salary` vs. the position's grade midpoint
- Numeric features: `Base Salary`, `Levels from Top of Organisation`, `Number of Direct Reports`, `Tenure_Years`, `Compa-Ratio`, `Last Promotion Years Ago`, `Years in Current Position`, `Age`, `FTE %`
- Low-cardinality categoricals (`Business Unit`, `Country`, `Gender`, `Is Manager`) are passed as native pandas `category` dtype
- `Job Title` (163 distinct values) is deliberately encoded rather than passed as a native categorical — see **Encoding & Validation Methodology** below

**Training:** stratified 80/20 train/test split, `GridSearchCV` (5-fold, `roc_auc` scoring) tuning `n_estimators`, `learning_rate`, `max_depth`, `subsample`, and `colsample_bytree`, with `class_weight='balanced'`. ID/name/date/target-leakage columns (`Employee ID`, `Full Legal Name`, `Hire Date`, `Status`) are excluded from the feature set.

### Encoding & validation methodology

`Job Title` has 163 distinct values with a median of only ~6 employees each — too high-cardinality for safe native categorical splitting or one-hot encoding without risking the model latching onto rare, sample-specific noise. To capture its real predictive value without that risk, the project uses an **out-of-fold, smoothed target encoding**: each employee's `Job_Title_Risk` value is computed only from *other* training folds (5-fold `KFold`), pulled toward the global mean for small categories, with the test set scored using a mapping learned strictly from training data — a standard, leakage-safe technique for high-cardinality categorical features.

To confirm the resulting performance reflects a genuine, generalizable pattern rather than a single favorable train/test split, the full pipeline (split → encode → train → evaluate) was validated across 5 independent random seeds:

| Seed run | 1 | 2 | 3 | 4 | 5 | **Mean** | **Std dev** |
|---|---|---|---|---|---|---|---|
| Test ROC-AUC | 0.6834 | 0.7327 | 0.6936 | 0.6956 | 0.6812 | **0.6973** | **0.0207** |

A ~0.02 standard deviation across 5 seeds confirms the signal is stable and generalizable.

**Reference results** (`random_state=42`): CV ROC-AUC **0.7129**, test ROC-AUC **0.7236**.

| Metric | Active (0) | Terminated (1) |
|---|---|---|
| Precision | 0.75 | 0.57 |
| Recall | 0.66 | 0.68 |
| F1-score | 0.70 | 0.62 |

Overall accuracy: 0.67 · Macro avg F1: 0.66 · Weighted avg F1: 0.67 · Support: 800

**Top predictive features** (by LightGBM feature importance): `Job_Title_Risk` (by far the strongest driver), `Base Salary`, `Age`, `Tenure_Years`, `Compa-Ratio`, `Years in Current Position`, `Last Promotion Years Ago`.

<img width="984" height="384" alt="Feature Importance" src="https://github.com/user-attachments/assets/76131f1a-a4be-452d-85e5-1e7df8a7a88c" />

**Scoring active employees.** Once trained, the model scores every currently-active employee and produces a `Risk Score (%)` per person. An interactive, **ipywidgets-powered** explorer (filterable by department) surfaces the Top-20 highest-risk active employees with their tenure, Compa-Ratio, salary, and risk score, color-coded red/orange/green by risk band — designed so a People team can act on individual names, not just an aggregate metric.

<img width="1396" height="827" alt="Overall Company Report" src="https://github.com/user-attachments/assets/87d32df1-d6fc-4c2e-b150-1be7ec103c33" />

**Production export:** this same scored output — every active employee's risk score — is written to `Active_Employees_Risk_Report.csv` (ready to load into Power BI/Tableau/Excel), alongside the serialized model, `lgbm_attrition_model.pkl` (via `joblib`), so the risk list above can be regenerated or refreshed without retraining.

## 🔍 Key Findings

- **Role/position is the single strongest attrition signal** — more predictive than any individual compensation or tenure metric on its own, because a job title bundles department, grade, and career track (manager vs. individual contributor) into one feature.
- **Compensation and career stagnation are the next-strongest drivers** — Base Salary, Age, Tenure, and Compa-Ratio all rank highly, consistent with the risk factors designed into the data generator (underpayment vs. grade, time since last promotion, time in role).
- **Compensation is well-controlled at the department level** — average Compa-Ratio sits within a few points of 100% across every department, meaning attrition risk is more of an individual/role-level phenomenon than a systemic department-wide pay problem.
- **Turnover rate varies meaningfully by function**, useful context for prioritizing retention conversations by department.
- **The model favors recall over precision on leavers** (68% recall, 57% precision on the Terminated class) — an intentional trade-off from `class_weight='balanced'`, appropriate for a screening/triage tool where missing an at-risk employee is costlier than a wasted retention conversation.

## 🛠️ Tech Stack

- **Python 3.10+**
- `pandas`, `numpy` — data manipulation and feature engineering
- `Faker` — synthetic PII/record generation
- `DuckDB` — SQL-based data cleaning and business-rule enforcement
- `scikit-learn` — `train_test_split`, `KFold`, `GridSearchCV`, evaluation metrics
- `lightgbm` — gradient boosting classifier (native categorical support)
- `matplotlib`, `seaborn` — static visualizations, executive dashboard, feature importance
- `ipywidgets` — interactive, department-filterable risk explorer inside the notebook
- `joblib` — model serialization
- `openpyxl` — job architecture workbook

## 📂 Project Structure

```
.
├── job_architecture.xlsx              # 10-level grading framework + position/salary-band reference
├── generate_realistic_hr_data.py      # Synthetic HR data generator -> raw_worker_details.csv
├── raw_worker_details.csv             # Generated raw HR export (never modified after generation)
├── hr_data_cleaning.ipynb             # Full pipeline: audit -> clean -> dashboard -> model -> export
├── cleaned_worker_details.csv         # Cleaned, analysis-ready dataset
├── Active_Employees_Risk_Report.csv   # Model output: risk score per active employee
├── lgbm_attrition_model.pkl           # Serialized trained model (joblib)
└── README.md
```

## ▶️ Getting Started

```bash
# Clone the repo
git clone https://github.com/gcemozdogan/hr-analytics-data-cleaning.git
cd hr-analytics-data-cleaning

# Install dependencies
pip install pandas numpy faker duckdb scikit-learn lightgbm matplotlib seaborn ipywidgets joblib openpyxl

# 1. Generate the synthetic raw dataset
python generate_realistic_hr_data.py

# 2. Run the full pipeline notebook (audit -> clean -> dashboard -> model -> export)
jupyter notebook hr_data_cleaning.ipynb
```

Run the notebook's cells in order — later cells (model training, dashboard, export) depend on variables (`df_clean`, `df_ml`, `best_model`) created earlier in the notebook.

## ⚠️ Limitations

- **Synthetic data is a proxy, not ground truth.** All conclusions here (top attrition drivers, department turnover patterns) reflect the data generator's design assumptions, not a real workforce — this project is a pipeline and methodology demonstration, not an HR research result.
- **Precision on the minority (Terminated) class (0.57) leaves room for improvement.** Further gains would likely come from richer per-role and per-team features (e.g. manager-level aggregates, team turnover history) rather than additional hyperparameter tuning, since the search space is already fairly exhaustive (72 candidates × 5 folds).
- **High-cardinality categorical features require care.** `Job Title`'s predictive value is real, but only once encoded safely (out-of-fold, smoothed) and validated across multiple random seeds — a reminder that any similarly granular categorical added in the future should go through the same validation discipline before being trusted.

## 📄 License

This project uses entirely synthetic data (no real employee information) and is provided under the MIT License. Feel free to fork and adapt it.

## 🧑‍💻 Author

<table>
<tr>
<td align="center">
<img src="https://github.com/gcemozdogan.png" width="100px"/><br/>
<b>Cem Özdoğan</b><br/>
<a href="https://github.com/gcemozdogan">GitHub</a> •
<a href="https://linkedin.com/in/gcemozdogan">LinkedIn</a>
</td>
</tr>
</table>
