# RetainIQ – Exploratory Data Analysis & Statistical Inference Report

**Target Dataset**: IBM Telco Customer Churn (`WA_Fn-UseC_-Telco-Customer-Churn.csv`)  
**Records Analyzed**: 7,043 customer accounts | **Features**: 22 attributes  
**Baseline Customer Loss Rate**: **26.54%** (1,869 customers lost, 5,174 customers who stayed)  

---

## 1. Executive Summary of Key Statistical Insights

1. **Contract Commitment is the Strongest Categorical Correlate (Cramér's V = 0.4098)**:
   - Month-to-month subscribers experience an empirical customer loss rate of **Month-to-month (42.7%)**, whereas One-year is **11.3%** and Two-year contract holders experience a loss rate of only **2.8%**.
2. **Early Tenure Hazard Window**:
   - Median tenure for customers who left is **10 months**, compared to **38 months** for customers who stayed ($p < 0.001$, Mann-Whitney U). Customer losses heavily concentrate within the first 1–6 billing cycles.
3. **Fiber Optic Spend Paradox**:
   - Fiber optic internet users experience a loss rate of **Fiber optic (41.9%)**, contrasted with **19.0%** for DSL and **7.4%** for No Internet service. Furthermore, customers who left have significantly higher average monthly charges (**$74.44** vs. **$61.27**, $p < 0.001$).
4. **Protective Ancillary Services**:
   - Customers subscribing to `TechSupport` and `OnlineSecurity` exhibit dramatically lower loss rates (~15%) compared to non-subscribers (~41%), indicating product stickiness.

---

## 2. Categorical Association Ranking (Chi-Square & Cramér's V)

Features ranked in descending order of association with customer loss (churn):

| Rank | Feature | Chi-Square ($\chi^2$) | p-value | Degrees of Freedom | Cramér's V | Highest Loss Rate Group | Lowest Loss Rate Group |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `Contract` | 1,184.6 | < 0.001 | 2 | **0.4098** | Month-to-month (42.7%) | Two year (2.8%) |
| 2 | `OnlineSecurity` | 850.0 | < 0.001 | 2 | **0.3470** | No (41.8%) | No internet service (7.4%) |
| 3 | `TechSupport` | 828.2 | < 0.001 | 2 | **0.3425** | No (41.6%) | No internet service (7.4%) |
| 4 | `InternetService` | 732.31 | < 0.001 | 2 | **0.3220** | Fiber optic (41.9%) | No (7.4%) |
| 5 | `PaymentMethod` | 648.14 | < 0.001 | 3 | **0.3027** | Electronic check (45.3%) | Credit card (automatic) (15.2%) |
| 6 | `OnlineBackup` | 601.81 | < 0.001 | 2 | **0.2919** | No (39.9%) | No internet service (7.4%) |
| 7 | `DeviceProtection` | 558.42 | < 0.001 | 2 | **0.2811** | No (39.1%) | No internet service (7.4%) |
| 8 | `StreamingMovies` | 375.66 | < 0.001 | 2 | **0.2304** | No (33.7%) | No internet service (7.4%) |
| 9 | `StreamingTV` | 374.2 | < 0.001 | 2 | **0.2299** | No (33.5%) | No internet service (7.4%) |
| 10 | `PaperlessBilling` | 258.28 | < 0.001 | 1 | **0.1911** | Yes (33.6%) | No (16.3%) |
| 11 | `Dependents` | 189.13 | < 0.001 | 1 | **0.1634** | No (31.3%) | Yes (15.5%) |
| 12 | `SeniorCitizen` | 159.43 | < 0.001 | 1 | **0.1500** | 1 (41.7%) | 0 (23.6%) |
| 13 | `Partner` | 158.73 | < 0.001 | 1 | **0.1497** | No (33.0%) | Yes (19.7%) |
| 14 | `MultipleLines` | 11.33 | 0.0035 | 2 | **0.0364** | Yes (28.6%) | No phone service (24.9%) |
| 15 | `gender` | 0.48 | 0.4866 | 1 | **0.0000** | Female (26.9%) | Male (26.2%) |
| 16 | `PhoneService` | 0.92 | 0.3388 | 1 | **0.0000** | Yes (26.7%) | No (24.9%) |

---

## 3. Numerical Feature Hypothesis Testing

Comparison between Customers Who Stayed (`Churn = 'No'`) and Customers Who Left (`Churn = 'Yes'`) cohorts:

| Metric | Customers Who Stayed Mean (Median) | Customers Who Left Mean (Median) | Welch's t-stat (p-val) | Mann-Whitney U (p-val) | Point-Biserial Corr |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `tenure` | $37.57 (38.0) | $17.98 (10.0) | -34.82 (< 0.001) | 2,515,538 (< 0.001) | **-0.3522** |
| `MonthlyCharges` | $61.27 (64.43) | $74.44 (79.65) | 18.41 (< 0.001) | 6,003,126 (< 0.001) | **0.1934** |
| `TotalCharges` | $2,549.91 (1679.52) | $1,531.80 (703.55) | -18.71 (< 0.001) | 3,381,224 (< 0.001) | **-0.1983** |

---

## 4. Visual Evidence Artifacts

1. **Target Distribution**: [churn_distribution.png](figures/churn_distribution.png)
2. **Tenure Decay Curve**: [tenure_distribution_by_churn.png](figures/tenure_distribution_by_churn.png)
3. **Monthly Charges Distribution**: [monthly_charges_distribution_by_churn.png](figures/monthly_charges_distribution_by_churn.png)
4. **Contract Type Impact**: [churn_by_contract.png](figures/churn_by_contract.png)
5. **Internet Service Impact**: [churn_by_internet_service.png](figures/churn_by_internet_service.png)

---

## 5. Methodological & Non-Causal Interpretation Guardrail

> [!CAUTION]
> **Correlation vs. Causation Guard**: While month-to-month contracts and lack of tech support exhibit strong empirical correlation with churn, this does **not** imply that locking customers into longer contracts or forcing tech support attachments will causally reduce churn. Customers with high inherent propensity to leave may naturally select month-to-month terms (self-selection bias). Any targeted retention intervention must be validated via randomized controlled trials (A/B testing).
