-- ============================================================================
-- RetainIQ Production Analytical Query Suite
-- Dialect: SQLite / ANSI SQL Compatible
-- ============================================================================

-- Query 1: Executive KPI Scorecard Reconciliation
-- Calculates aggregate base size, churn rate, average tenures, and monthly contracted charges.
-- NAME: query_01_executive_kpis
SELECT
    COUNT(*) AS total_customers,
    SUM(churn_binary) AS churned_customers,
    COUNT(*) - SUM(churn_binary) AS retained_customers,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 2) AS avg_tenure_overall,
    ROUND(AVG(CASE WHEN churn_binary = 0 THEN tenure END), 2) AS avg_tenure_retained,
    ROUND(AVG(CASE WHEN churn_binary = 1 THEN tenure END), 2) AS avg_tenure_churned,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_contracted_charges,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS historical_mrc_churned_base,
    ROUND(SUM(CASE WHEN churn_binary = 0 THEN monthly_charges ELSE 0 END), 2) AS retained_monthly_recurring_charges
FROM customers;


-- Query 2: Churn & Financial Exposure by Contract Commitment Type
-- Demonstrates how churn rate and contracted revenue vary across commitment lengths.
-- NAME: query_02_churn_by_contract
SELECT
    contract,
    COUNT(*) AS total_customers,
    SUM(churn_binary) AS churned_customers,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_charges,
    ROUND(AVG(tenure), 1) AS avg_tenure_months
FROM customers
GROUP BY contract
ORDER BY churn_rate_pct DESC;


-- Query 3: Churn Hazard Across Lifecycle Tenure Bins
-- Groups customers into 5 standardized lifecycle buckets to reveal the early churn window.
-- NAME: query_03_churn_by_tenure_cohort
SELECT
    CASE 
        WHEN tenure <= 6 THEN '01. 0-6 Months'
        WHEN tenure <= 12 THEN '02. 7-12 Months'
        WHEN tenure <= 24 THEN '03. 13-24 Months'
        WHEN tenure <= 48 THEN '04. 25-48 Months'
        ELSE '05. 49-72 Months'
    END AS tenure_cohort,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_charges
FROM customers
GROUP BY tenure_cohort
ORDER BY tenure_cohort;


-- Query 4: Churn by Internet Service Architecture
-- Compares Fiber Optic, DSL, and Phone-only cohorts on churn propensity and average spend.
-- NAME: query_04_churn_by_internet_service
SELECT
    internet_service,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_charges
FROM customers
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;


-- Query 5: Tech Support & Online Security Attachment Stickiness
-- Evaluates the protective retention effect of cybersecurity and technical support add-ons.
-- NAME: query_05_support_security_attachment
SELECT
    tech_support,
    online_security,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customers
GROUP BY tech_support, online_security
ORDER BY churn_rate_pct DESC;


-- Query 6: Payment Method & Invoicing Risk Analysis
-- Tests whether electronic check vs. automated billing mechanisms correlate with retention.
-- NAME: query_06_payment_method_risk
SELECT
    payment_method,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_charges,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_charges
FROM customers
GROUP BY payment_method
ORDER BY churn_rate_pct DESC;


-- Query 7: Churn by Monthly Charge Quartiles / Price Bands
-- Groups customers into 4 pricing tiers to examine price elasticity and spend-associated churn.
-- NAME: query_07_charge_tier_analysis
SELECT
    CASE
        WHEN monthly_charges < 35.0 THEN 'Tier 1: < $35'
        WHEN monthly_charges < 70.0 THEN 'Tier 2: $35 - $69.99'
        WHEN monthly_charges < 90.0 THEN 'Tier 3: $70 - $89.99'
        ELSE 'Tier 4: $90+'
    END AS charge_tier,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(tenure), 1) AS avg_tenure_months,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_charges
FROM customers
GROUP BY charge_tier
ORDER BY charge_tier;


-- Query 8: High-Spend Flight Risk Identification
-- Identifies premium spenders (>= $80/mo) on uncommitted month-to-month contracts.
-- NAME: query_08_high_spend_flight_risk
SELECT
    customer_id,
    internet_service,
    payment_method,
    tenure,
    monthly_charges,
    total_charges,
    churn
FROM customers
WHERE monthly_charges >= 80.0
  AND contract = 'Month-to-month'
ORDER BY monthly_charges DESC, tenure ASC
LIMIT 20;


-- Query 9: Senior Citizen Demographics & Family Anchoring
-- Examines churn across senior citizenship, partner status, and dependents.
-- NAME: query_09_demographic_anchoring
SELECT
    senior_citizen,
    partner,
    dependents,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM customers
GROUP BY senior_citizen, partner, dependents
ORDER BY churn_rate_pct DESC;


-- Query 10: Entertainment / Streaming Bundle Depth
-- Assesses churn rate among users with both, one, or neither streaming services.
-- NAME: query_10_streaming_bundle_depth
SELECT
    streaming_tv,
    streaming_movies,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customers
GROUP BY streaming_tv, streaming_movies
ORDER BY churn_rate_pct DESC;


-- Query 11: Phone Service & Multiple Lines Telephony Analysis
-- Compares single line, multi-line, and non-phone subscribers.
-- NAME: query_11_telephony_churn
SELECT
    phone_service,
    multiple_lines,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge
FROM customers
GROUP BY phone_service, multiple_lines
ORDER BY churn_rate_pct DESC;


-- Query 12: Paperless Billing Discrepancy
-- Investigates churn divergence between paperless and traditional invoice recipients.
-- NAME: query_12_paperless_billing_discrepancy
SELECT
    paperless_billing,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_charges
FROM customers
GROUP BY paperless_billing;


-- Query 13: Veteran Churn Root-Cause Profiling (Tenure > 36 Months)
-- Analyzes characteristics of long-tenured customers who churned after 3+ years.
-- NAME: query_13_veteran_churn_profiling
SELECT
    contract,
    internet_service,
    payment_method,
    COUNT(*) AS veteran_churn_count,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(total_charges), 2) AS avg_historical_billed
FROM customers
WHERE tenure > 36
  AND churn_binary = 1
GROUP BY contract, internet_service, payment_method
ORDER BY veteran_churn_count DESC
LIMIT 10;


-- Query 14: Ancillary Service Breadth Index
-- Calculates how many ancillary services (Security, Backup, Device, Support, TV, Movies) a customer has.
-- NAME: query_14_service_breadth_index
SELECT
    (
        (CASE WHEN online_security = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN online_backup = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN device_protection = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN tech_support = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN streaming_tv = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN streaming_movies = 'Yes' THEN 1 ELSE 0 END)
    ) AS active_ancillary_service_count,
    COUNT(*) AS customer_count,
    SUM(churn_binary) AS churned_count,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM customers
WHERE internet_service != 'No'
GROUP BY active_ancillary_service_count
ORDER BY active_ancillary_service_count ASC;


-- Query 15: Cumulative Historical Value across Contract & Tenure Segments
-- Provides an empirical proxy for historical realized revenue per customer segment.
-- NAME: query_15_cohort_historical_value
SELECT
    contract,
    CASE
        WHEN tenure <= 12 THEN 'Year 1 (0-12m)'
        WHEN tenure <= 24 THEN 'Year 2 (13-24m)'
        WHEN tenure <= 48 THEN 'Years 3-4 (25-48m)'
        ELSE 'Year 5+ (49-72m)'
    END AS lifecycle_stage,
    COUNT(*) AS customer_count,
    ROUND(AVG(total_charges), 2) AS avg_historical_total_charges,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct
FROM customers
GROUP BY contract, lifecycle_stage
ORDER BY contract, lifecycle_stage;


-- Query 16: Cumulative Recurring Revenue Exposure by Payment and Contract Combinations
-- Highlights where high volume of churned monthly recurring charges is concentrated.
-- NAME: query_16_revenue_exposure_hotspots
SELECT
    contract,
    payment_method,
    COUNT(*) AS total_customers,
    SUM(churn_binary) AS churned_customers,
    ROUND(AVG(churn_binary) * 100.0, 2) AS churn_rate_pct,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END), 2) AS churned_monthly_charges,
    ROUND(SUM(CASE WHEN churn_binary = 1 THEN monthly_charges ELSE 0 END) * 100.0 / 
          (SELECT SUM(monthly_charges) FROM customers WHERE churn_binary = 1), 2) AS share_of_total_churned_mrc_pct
FROM customers
GROUP BY contract, payment_method
ORDER BY churned_monthly_charges DESC;
