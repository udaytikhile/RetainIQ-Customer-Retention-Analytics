# RetainIQ – Comprehensive Data Dictionary

This document details the schema, data types, allowable value ranges, business semantics, and empirical distributions across all 21 raw features and 6 derived analytical attributes in RetainIQ.

---

## 1. Primary Identifier & Target

| Column Name | Data Type | Nullable | Domain / Allowed Values | Description & Empirical Context |
| :--- | :--- | :--- | :--- | :--- |
| `customerID` | `VARCHAR(20)` / `str` | No | Unique alphanumeric string (e.g. `'7590-VHVEG'`) | Primary customer identifier. **7,043 unique accounts**, 0 duplicates. |
| `Churn` | `VARCHAR(5)` / `str` | No | `{'Yes', 'No'}` | Target variable indicating whether customer defected. `'No'`: 5,174 (73.46%), `'Yes'`: 1,869 (26.54%). |
| `ChurnBinary` *(derived)* | `INTEGER` / `int` | No | `{0, 1}` | Binary indicator for machine learning and quantitative calculations (1 for 'Yes', 0 for 'No'). |

---

## 2. Demographic Attributes

| Column Name | Data Type | Nullable | Domain / Allowed Values | Description & Empirical Context |
| :--- | :--- | :--- | :--- | :--- |
| `gender` | `VARCHAR(10)` / `str` | No | `{'Female', 'Male'}` | Customer gender. Female: 3,488 (49.5%), Male: 3,555 (50.5%). Negligible churn variance (26.9% vs 26.2%, $p = 0.487$). |
| `SeniorCitizen` | `INTEGER` / `int` | No | `{0, 1}` | Binary flag indicating if customer is $\ge 65$ years old. 1,142 seniors (16.2%), 5,901 non-seniors (83.8%). Seniors churn at **41.7%** vs 23.6%. |
| `Partner` | `VARCHAR(5)` / `str` | No | `{'Yes', 'No'}` | Whether customer has a domestic partner. Yes: 3,402 (48.3%), No: 3,641 (51.7%). Single accounts churn at **33.0%** vs 19.7%. |
| `Dependents` | `VARCHAR(5)` / `str` | No | `{'Yes', 'No'}` | Whether customer has dependents (children/family). Yes: 2,110 (30.0%), No: 4,933 (70.0%). Accounts without dependents churn at **31.3%** vs 15.5%. |

---

## 3. Account, Billing & Contract Attributes

| Column Name | Data Type | Nullable | Domain / Allowed Values | Description & Empirical Context |
| :--- | :--- | :--- | :--- | :--- |
| `tenure` | `INTEGER` / `int` | No | `0 – 72` (Months) | Continuous months of active subscription. Mean: 32.37 mo, Median: 29.0 mo. Churned median is **10.0 mo** vs retained **38.0 mo**. |
| `Contract` | `VARCHAR(20)` / `str` | No | `{'Month-to-month', 'One year', 'Two year'}` | Billing commitment term. Month-to-month: 3,875 (55.0%), One year: 1,473 (20.9%), Two year: 1,695 (24.1%). Month-to-month churn is **42.7%** (Cramér's V = 0.4098). |
| `PaperlessBilling` | `VARCHAR(5)` / `str` | No | `{'Yes', 'No'}` | Electronic invoicing enrollment. Yes: 4,171 (59.2%), No: 2,872 (40.8%). Paperless users churn at **33.6%** vs 16.3%. |
| `PaymentMethod` | `VARCHAR(40)` / `str` | No | `{'Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'}` | Payment channel. Electronic check: 2,365 (33.6%), Mailed check: 1,612 (22.9%), Bank transfer: 1,544 (21.9%), Credit card: 1,522 (21.6%). Electronic check churn is **45.3%**. |
| `MonthlyCharges` | `REAL` / `float64` | No | `$18.25 – $118.75` | Monthly contracted billing rate ($). Mean: $64.76, Median: $70.35. Churned mean is **$74.44** vs retained **$61.27**. |
| `TotalCharges` | `REAL` / `float64` | No | `$0.00 – $8,684.80` | Cumulative historical charges billed ($). 11 initial whitespace values imputed to $0.00 (tenure = 0). Mean: $2,279.73. |

---

## 4. Subscribed Service Dimensions

| Column Name | Data Type | Nullable | Domain / Allowed Values | Description & Empirical Context |
| :--- | :--- | :--- | :--- | :--- |
| `PhoneService` | `VARCHAR(5)` / `str` | No | `{'Yes', 'No'}` | Fixed landline telephony enrollment. Yes: 6,361 (90.3%), No: 682 (9.7%). |
| `MultipleLines` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No phone service'}` | Multiple voice lines. No: 3,390 (48.1%), Yes: 2,971 (42.2%), No phone: 682 (9.7%). |
| `InternetService` | `VARCHAR(20)` / `str` | No | `{'Fiber optic', 'DSL', 'No'}` | Broadband infrastructure. Fiber optic: 3,096 (44.0%), DSL: 2,421 (34.4%), No: 1,526 (21.7%). Fiber churn is **41.9%**. |
| `OnlineSecurity` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No internet service'}` | Antivirus/DNS cyber protection. Yes: 2,019 (28.7%), No: 3,498 (49.7%). Non-subscribers churn at **41.8%** vs 14.6% for subscribers. |
| `OnlineBackup` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No internet service'}` | Cloud storage backup. Yes: 2,429 (34.5%), No: 3,088 (43.8%). Non-subscribers churn at **39.9%** vs 21.5% for subscribers. |
| `DeviceProtection` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No internet service'}` | Hardware warranty/insurance. Yes: 2,422 (34.4%), No: 3,095 (43.9%). Non-subscribers churn at **39.1%** vs 22.5% for subscribers. |
| `TechSupport` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No internet service'}` | Dedicated technical assistance. Yes: 2,044 (29.0%), No: 3,473 (49.3%). Non-subscribers churn at **41.6%** vs 15.2% for subscribers. |
| `StreamingTV` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No internet service'}` | IP television streaming. Yes: 2,707 (38.4%), No: 2,810 (39.9%). Subscribers churn at **30.1%** vs 33.5% non-subscribers. |
| `StreamingMovies` | `VARCHAR(25)` / `str` | No | `{'No', 'Yes', 'No internet service'}` | Video-on-demand movie streaming. Yes: 2,732 (38.8%), No: 2,785 (39.5%). Subscribers churn at **29.9%** vs 33.7% non-subscribers. |

---

## 5. Derived Analytical Features

| Feature Name | Origin / Formula | Data Type | Domain / Values | Strategic Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `TenureCohort` | Discretization of `tenure` | `VARCHAR(30)` | `{'01. Onboarding (0-6m)', '02. Nurture (7-12m)', '03. Established (13-24m)', '04. Mature (25-48m)', '05. Loyalist (49-72m)'}` | Evaluates lifecycle retention hazard decay over customer lifetime. |
| `ServiceBreadth` | Sum of active add-on services | `INTEGER` | `0 – 6` | Measures customer product stickiness and ecosystem integration depth. |
| `ValueRiskQuadrant` | `MonthlyCharges >= $70` $\times$ `Contract = 'Month-to-month'` | `VARCHAR(80)` | `{'Quadrant 1: VIP Flight Risk', 'Quadrant 2: Core Champions', 'Quadrant 3: Transactional Vulnerable', 'Quadrant 4: Stable Base'}` | High-level commercial prioritization balancing financial risk and churn probability. |
| `PredictedChurnProbability` | ML Classifier Holdout Inference | `REAL` | `0.0000 – 1.0000` | Statistical propensity score computed via leakage-free HistGradientBoosting model. |
| `PredictedRiskTier` | Discretization of predicted probability | `VARCHAR(30)` | `{'Low Risk (0-25%)', 'Moderate Risk (25-50%)', 'High Risk (50-70%)', 'Critical Risk (70-100%)'}` | Operational categorization for CRM campaign segmentation and filtering. |
| `RecommendedRetentionPlay` | Decision rule matrix | `VARCHAR(100)` | Prescriptive playbooks (e.g. Concierge, Term incentive, TechSupport trial) | Provides prescriptive, non-causal retention plays for frontline customer success teams. |
