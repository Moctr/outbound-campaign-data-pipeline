-- SQL Server reporting mart for the UCI Bank Marketing campaign dataset.
-- Load data\processed\fact_campaign_contact.csv into dbo.FactCampaignRecord.
CREATE TABLE dbo.FactCampaignRecord (
    campaign_record_id INT NOT NULL PRIMARY KEY,
    age TINYINT NOT NULL,
    job NVARCHAR(40) NOT NULL,
    marital_status NVARCHAR(20) NOT NULL,
    education NVARCHAR(40) NOT NULL,
    credit_default NVARCHAR(10) NOT NULL,
    account_balance_eur DECIMAL(12,2) NOT NULL,
    housing_loan NVARCHAR(10) NOT NULL,
    personal_loan NVARCHAR(10) NOT NULL,
    contact_channel NVARCHAR(20) NOT NULL,
    contact_day_of_month TINYINT NOT NULL,
    contact_month CHAR(3) NOT NULL,
    call_duration_seconds INT NOT NULL,
    campaign_contact_number SMALLINT NOT NULL,
    days_since_previous_contact INT NULL,
    previous_campaign_contacts SMALLINT NOT NULL,
    previous_campaign_outcome NVARCHAR(20) NOT NULL,
    subscribed_term_deposit BIT NOT NULL,
    previously_contacted BIT NOT NULL,
    duration_minutes DECIMAL(8,2) NOT NULL
);
GO

CREATE OR ALTER VIEW dbo.vw_CampaignPerformanceByChannel AS
SELECT
    contact_channel,
    COUNT_BIG(*) AS campaign_records,
    SUM(CONVERT(BIGINT, subscribed_term_deposit)) AS subscriptions,
    CAST(100.0 * SUM(CONVERT(DECIMAL(18,4), subscribed_term_deposit)) / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6,2)) AS subscription_rate_pct,
    CAST(AVG(CONVERT(DECIMAL(18,4), call_duration_seconds)) AS DECIMAL(10,2)) AS avg_last_call_duration_seconds
FROM dbo.FactCampaignRecord
GROUP BY contact_channel;
GO

-- Month is a categorical value: the source file has no year/date field.
CREATE OR ALTER VIEW dbo.vw_CampaignPerformanceByMonthCategory AS
SELECT
    contact_month,
    COUNT_BIG(*) AS campaign_records,
    SUM(CONVERT(BIGINT, subscribed_term_deposit)) AS subscriptions,
    CAST(100.0 * SUM(CONVERT(DECIMAL(18,4), subscribed_term_deposit)) / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6,2)) AS subscription_rate_pct
FROM dbo.FactCampaignRecord
GROUP BY contact_month;
GO

CREATE OR ALTER VIEW dbo.vw_CampaignFrequency AS
SELECT
    CASE WHEN campaign_contact_number >= 5 THEN '5+' ELSE CONVERT(VARCHAR(3), campaign_contact_number) END AS campaign_contact_band,
    COUNT_BIG(*) AS campaign_records,
    SUM(CONVERT(BIGINT, subscribed_term_deposit)) AS subscriptions,
    CAST(100.0 * SUM(CONVERT(DECIMAL(18,4), subscribed_term_deposit)) / NULLIF(COUNT_BIG(*), 0) AS DECIMAL(6,2)) AS subscription_rate_pct
FROM dbo.FactCampaignRecord
GROUP BY CASE WHEN campaign_contact_number >= 5 THEN '5+' ELSE CONVERT(VARCHAR(3), campaign_contact_number) END;
GO

