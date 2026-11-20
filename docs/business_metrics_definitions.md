# RetainIQ – Business Metrics & Financial Terminology Definitions

This document formalizes the mathematical formulas, business contexts, and accounting guardrails for RetainIQ retention reporting.

---

## 1. Metric Catalog

### Metric 1: Total Customer Base ($N$)
- **Formula**: $\sum_{i=1}^{M} 1 = M$
- **Definition**: The total distinct count of customer accounts captured in the analytical snapshot.
- **Empirical Value**: **7,043** customer accounts.

### Metric 2: Customers Lost ($N_{\text{lost}}$) and Customer Loss Rate ($CR$) (Churn Rate)
- **Formula**:
  $$\text{Customers Lost} = \sum_{i=1}^{M} \mathbb{I}(\text{Churn}_i = \text{'Yes'})$$
  $$\text{Customer Loss Rate (\%)} = \frac{\text{Customers Lost}}{N} \times 100$$
- **Definition**: The volume and percentage of customers who severed their contractual or month-to-month service during the observed period (Customers Who Left).
- **Empirical Value**: **1,869 accounts (26.54% Customer Loss Rate)**.

### Metric 3: Average Customer Tenure ($\overline{T}$)
- **Formula**: $\overline{T} = \frac{1}{|S|} \sum_{i \in S} \text{tenure}_i$
- **Definition**: The arithmetic mean of months active across specified customer subsets.
- **Empirical Values**:
  - **Overall Base**: 32.37 months
  - **Customers Who Stayed (Active Accounts)**: 37.57 months (Median: 38.0)
  - **Customers Who Left (Defected Accounts)**: 17.98 months (Median: 10.0)

### Metric 4: Monthly Contracted Recurring Charges ($\text{MRR}_{\text{total}}$)
- **Formula**: $\text{MRR}_{\text{total}} = \sum_{i=1}^{M} \text{MonthlyCharges}_i$
- **Definition**: Aggregate contractual monthly recurring rate across all accounts prior to loss events.
- **Empirical Value**: **$456,116.60 / month**.
  - **Revenue from Customers Who Stayed**: $316,985.75 / month (69.50%)
  - **Lost Monthly Revenue (Historical)**: $139,130.85 / month (30.50%)

### Metric 5: Lost Monthly Revenue (Historical) ($\text{MRC}_{\text{lost}}$)
- **Formula**: $\sum_{i \in \text{Customers Who Left}} \text{MonthlyCharges}_i$
- **Definition**: Historical contracted monthly recurring charges associated with customers who left (historical churned MRC).
- **Empirical Value**: **$139,130.85 / month**.

---

## 2. Mandatory Reporting Guardrail: Why $\text{MRC}_{\text{lost}}$ is NOT "Future Revenue Loss"

> [!WARNING]
> In executive presentations, business intelligence analysts frequently label $\sum \text{MonthlyCharges}$ of defected accounts as **"Future Revenue Lost"** or **"Annualized Revenue Loss ($1.67M)"**. In RetainIQ, this terminology is **strictly prohibited without qualification** due to the following business and statistical realities:

1. **Absence of Forward Commitments**:
   - **88.55%** ($1,655 / 1,869$) of customers who left were on **Month-to-month** contracts. These customers had zero legal obligation to renew in subsequent months; assuming their revenue would have continued indefinitely is a false counterfactual.
2. **Gross vs. Net Dynamics**:
   - The metric ignores gross adds, organic customer replacement, upgrades, and contractions across the active customer base.
3. **Discount Expirations and Promotions**:
   - Monthly charges in telecommunications frequently include promotional rates, device installment plans, or temporary bill credits that expire, distorting run-rate extrapolation.
4. **Required Standard Phrasing**:
   - *Compliant Title*: **"Lost Monthly Revenue (Historical)"** (or secondary: *Lost Monthly Revenue (Historical) (Churned MRC)*) or **"Historical Monthly Billed Volume of Customers Who Left"**.
