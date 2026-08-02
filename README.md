# **📊 End-to-End HR Analytics, Data Cleaning & Attrition Risk Prediction Pipeline**


## **⚠️ Legal Notice & Disclaimer:**	

This project, along with all associated datasets, models, and visual reports, is built entirely using synthetic (fictional) data generated solely for portfolio, educational, and demonstration purposes. This project has no affiliation, connection, or commercial relation with Beko, Arçelik, or any of their corporate affiliates. Any resemblance to real corporate data or personnel is purely coincidental.

## **🚀 Project Overview**

This repository contains a comprehensive Human Resources Analytics, Automated Data Cleaning, and Machine Learning Pipeline. It processes raw, unstructured, and messy corporate workforce data, standardizes it through robust business logic, generates executive-level summaries, and implements an advanced LightGBM machine learning model to predict employee attrition risk.

## **🛠️ Tech Stack & Libraries**

Python (Data Manipulation & Machine Learning)

Pandas & NumPy (Data Engineering & Transformation)

DuckDB / SQL (Analytical Querying & Cleaning Operations)

Scikit-Learn (Pipeline Architecture & Model Evaluation)

LightGBM (High-Performance Gradient Boosting Classifier with Native Categorical Support)

IPywidgets / Matplotlib / Seaborn (Interactive Dashboards & Data Visualization)

## **📈 Key Workflow & Project Stages**
### **1. Automated Data Cleaning & Business Logic**
Raw data often contains structural anomalies, formatting inconsistencies, and duplicates. The data cleaning pipeline automatically resolves these issues:

Duplicate Removal: Identifies and eliminates duplicate rows based on Employee ID.

String Standardization: Applies titlecase and trimming while protecting Turkish characters and acronyms.

Typo Correction: Automatically fixes known departmental entry errors (e.g., mapping misspellings in Human Resources/Administrative units).

Missing Value & Rule Enforcement: Enforces organizational logic, such as mapping managerial flags based on job grades.

<img width="1384" height="764" alt="Data Cleaning Summary" src="https://github.com/user-attachments/assets/d46ac81c-2862-466a-861c-dbad135ce3d7" />

### **2. Executive HR Analytics & Workforce Summary**
Before diving into machine learning, the pipeline aggregates data to build comprehensive structural summaries:

Headcount Summary: Distribution of active workforce across business units.

Turnover Summary: Department-based termination rates and historical trends.

Personnel Cost Summary: Total base salary costs and average Compa-Ratios per department.

Organizational Structure: Span of control and management hierarchy metrics broken down by job grades.

<img width="2184" height="1332" alt="Executive HR Analytics Dashboard" src="https://github.com/user-attachments/assets/13ea52e1-574a-4133-b434-f5f00db62591" />

### **3. Machine Learning: Attrition Risk Prediction**
To forecast which active employees are at risk of leaving, we engineered key HR metrics (Tenure_Years, Compa-Ratio, Last Promotion Years Ago) and trained a LightGBM Classifier leveraging its native categorical handling capabilities.

Feature Importance Analysis: The model prioritizes critical drivers such as time spent in the current position, age, time since last promotion, and market competitiveness (Compa-Ratio).

<img width="1227" height="483" alt="Feature Importance" src="https://github.com/user-attachments/assets/76330978-6b29-49f9-8768-b525d556cfd4" />

### **4. Interactive HR Risk Dashboard**
An interactive Jupyter widget dashboard allows HR business partners to filter personnel by department, instantly view top-risk employees, and assess risk scores dynamically highlighted via visual risk thresholds (High, Medium, Low).
<img width="1266" height="836" alt="Overall Company Report" src="https://github.com/user-attachments/assets/90299886-f4a4-4290-ae62-88bf5945f0a7" />

## ⚙️ How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gcemozdogan/hr-analytics-data-cleaning.git


Install dependencies:

   pip install pandas numpy scikit-learn lightgbm ipywidgets matplotlib seaborn openpyxl
	 
Run the pipeline:

Run the data generation, cleaning, and model pipeline scripts sequentially in your Jupyter / VS Code environment.

Developed by Günay Cem Özdoğan

