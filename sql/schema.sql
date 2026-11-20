-- RetainIQ SQLite / ANSI SQL Schema Definition
-- Table: customers

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10) NOT NULL,
    senior_citizen INTEGER NOT NULL CHECK (senior_citizen IN (0, 1)),
    partner VARCHAR(5) NOT NULL CHECK (partner IN ('Yes', 'No')),
    dependents VARCHAR(5) NOT NULL CHECK (dependents IN ('Yes', 'No')),
    tenure INTEGER NOT NULL CHECK (tenure >= 0),
    phone_service VARCHAR(5) NOT NULL CHECK (phone_service IN ('Yes', 'No')),
    multiple_lines VARCHAR(25) NOT NULL,
    internet_service VARCHAR(20) NOT NULL CHECK (internet_service IN ('DSL', 'Fiber optic', 'No')),
    online_security VARCHAR(25) NOT NULL,
    online_backup VARCHAR(25) NOT NULL,
    device_protection VARCHAR(25) NOT NULL,
    tech_support VARCHAR(25) NOT NULL,
    streaming_tv VARCHAR(25) NOT NULL,
    streaming_movies VARCHAR(25) NOT NULL,
    contract VARCHAR(20) NOT NULL CHECK (contract IN ('Month-to-month', 'One year', 'Two year')),
    paperless_billing VARCHAR(5) NOT NULL CHECK (paperless_billing IN ('Yes', 'No')),
    payment_method VARCHAR(40) NOT NULL,
    monthly_charges REAL NOT NULL CHECK (monthly_charges >= 0),
    total_charges REAL NOT NULL CHECK (total_charges >= 0),
    churn VARCHAR(5) NOT NULL CHECK (churn IN ('Yes', 'No')),
    churn_binary INTEGER NOT NULL CHECK (churn_binary IN (0, 1))
);

-- Performance Indexes for BI queries
CREATE INDEX idx_customers_churn ON customers(churn_binary);
CREATE INDEX idx_customers_contract ON customers(contract);
CREATE INDEX idx_customers_tenure ON customers(tenure);
CREATE INDEX idx_customers_internet ON customers(internet_service);
CREATE INDEX idx_customers_payment ON customers(payment_method);
