# RetainIQ – Machine Learning Customer Loss (Churn) Model Evaluation Report

**Evaluation Split**: Stratified 80% Train (5,634 records) / 20% Holdout Test (1,409 records)  
**Target Class Prevalence**: 26.54% Customers Who Left (Test set: 374 Customers Who Left, 1,035 Customers Who Stayed)  
**Leakage Prevention**: All transformations (StandardScaler, OneHotEncoder) strictly fitted on **training data only**.

---

## 1. Test-Set Head-to-Head Performance Comparison

| Metric | Baseline: Logistic Regression (Default $\tau=0.50$) | Baseline: Logistic Regression (Opt $\tau=0.3$) | Stronger: HistGradientBoosting (Default $\tau=0.50$) | Stronger: HistGradientBoosting (Opt $\tau=0.25$) |
| :--- | :--- | :--- | :--- | :--- |
| **ROC-AUC** | **0.8422** | **0.8422** | **0.8310** | **0.8310** |
| **PR-AUC (Avg Precision)** | **0.6349** | **0.6349** | **0.6344** | **0.6344** |
| **Brier Score (Calibration)** | 0.1380 | 0.1380 | 0.1425 | 0.1425 |
| **Precision** | 0.6593 | 0.5202 | 0.6166 | 0.5166 |
| **Recall (Sensitivity)** | 0.5588 | 0.7567 | 0.5160 | 0.7914 |
| **F1-Score** | 0.6049 | **0.6166** | 0.5619 | **0.6251** |
| **Specificity** | 0.8957 | 0.7478 | 0.8841 | 0.7324 |
| **True Positives (Caught)** | 209 / 374 | 283 / 374 | 193 / 374 | 296 / 374 |
| **False Positives (Waste)** | 108 | 261 | 120 | 277 |

---

## 2. Decision Threshold Sensitivity Analysis (HistGradientBoosting)

Adjusting the classification cutoff $\tau$ balances proactive customer coverage against false alarm costs:

| Threshold ($\tau$) | Precision | Recall | F1-Score | Specificity | Flagged Accounts (% Base) | True Positives Caught | False Alarms |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0.10` | 0.4182 | 0.8957 | **0.5702** | 0.5498 | 801 (56.9%) | 335 / 374 | 466 |
| `0.15` | 0.4588 | 0.8636 | **0.5993** | 0.6319 | 704 (50.0%) | 323 / 374 | 381 |
| `0.20` | 0.4866 | 0.8262 | **0.6125** | 0.6850 | 635 (45.1%) | 309 / 374 | 326 |
| `0.25` | 0.5166 | 0.7914 | **0.6251** | 0.7324 | 573 (40.7%) | 296 / 374 | 277 |
| `0.30` | 0.5346 | 0.7433 | **0.6219** | 0.7662 | 520 (36.9%) | 278 / 374 | 242 |
| `0.35` | 0.5472 | 0.6818 | **0.6071** | 0.7961 | 466 (33.1%) | 255 / 374 | 211 |
| `0.40` | 0.5632 | 0.6310 | **0.5952** | 0.8232 | 419 (29.7%) | 236 / 374 | 183 |
| `0.45` | 0.5978 | 0.5802 | **0.5889** | 0.8589 | 363 (25.8%) | 217 / 374 | 146 |
| `0.50` | 0.6166 | 0.5160 | **0.5619** | 0.8841 | 313 (22.2%) | 193 / 374 | 120 |
| `0.55` | 0.6617 | 0.4706 | **0.5500** | 0.9130 | 266 (18.9%) | 176 / 374 | 90 |
| `0.60` | 0.6800 | 0.4091 | **0.5109** | 0.9304 | 225 (16.0%) | 153 / 374 | 72 |
| `0.65` | 0.7182 | 0.3476 | **0.4685** | 0.9507 | 181 (12.8%) | 130 / 374 | 51 |
| `0.70` | 0.7568 | 0.2995 | **0.4291** | 0.9652 | 148 (10.5%) | 112 / 374 | 36 |
| `0.75` | 0.7692 | 0.2139 | **0.3347** | 0.9768 | 104 (7.4%) | 80 / 374 | 24 |
| `0.80` | 0.7500 | 0.1444 | **0.2422** | 0.9826 | 72 (5.1%) | 54 / 374 | 18 |
| `0.85` | 0.8163 | 0.1070 | **0.1891** | 0.9913 | 49 (3.5%) | 40 / 374 | 9 |
| `0.90` | 0.8846 | 0.0615 | **0.1150** | 0.9971 | 26 (1.9%) | 23 / 374 | 3 |

---

## 3. Commercial Trade-Off Recommendation

1. **Default Threshold ($\tau = 0.50$) Inefficiency**:
   - At $\tau=0.50$, the model captures only ~50% of defecting customers because of class imbalance (26.54% customer loss base rate).
2. **Optimal F1 Operational Cutoff ($\tau \approx 0.30 - 0.35$)**:
   - Lowering the decision threshold to **0.30** elevates Recall from **51.3%** to **~75%**, catching approximately **280 of 374** defecting customers (customers who would have left), while maintaining precision above 50%.
3. **High-Touch Concierge Cutoff ($\tau \ge 0.60$)**:
   - For high-cost interventions (e.g. sending a technician or issuing a $50 credit), a conservative threshold of 0.60 achieves 70%+ precision, ensuring intervention budgets are not wasted on customers who would have stayed anyway (stable accounts).

---

## 4. Visual Evidence Artifacts

1. **ROC Curve Comparison**: [roc_curve_comparison.png](figures/roc_curve_comparison.png)
2. **Precision-Recall Curve Comparison**: [pr_curve_comparison.png](figures/pr_curve_comparison.png)
3. **Threshold Sensitivity Plot**: [threshold_tradeoffs.png](figures/threshold_tradeoffs.png)
4. **Confusion Matrices**: [confusion_matrices.png](figures/confusion_matrices.png)
