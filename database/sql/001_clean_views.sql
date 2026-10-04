-- These views are the only place where raw survey codes are interpreted.
-- Raw values remain unchanged in raw_in_school and raw_employer.

CREATE VIEW clean_in_school AS
SELECT
    _source_row_number AS respondent_id,
    CAST(NULLIF(TRIM(state), '') AS INTEGER) AS state_code,
    CAST(NULLIF(TRIM(ethnic), '') AS INTEGER) AS ethnicity_code,
    CAST(NULLIF(TRIM(SchoolType1), '') AS INTEGER) AS school_type_code,
    CASE CAST(NULLIF(TRIM(ethnic), '') AS INTEGER)
        WHEN 1 THEN 'Bumiputera'
        WHEN 2 THEN 'Bumiputera'
        WHEN 3 THEN 'Chinese'
        WHEN 4 THEN 'Indian'
        WHEN 5 THEN 'Other'
    END AS ethnicity_group,
    CASE
        WHEN CAST(NULLIF(TRIM(SchoolType1), '') AS INTEGER) BETWEEN 1 AND 6
            THEN 'National / residential / Form 6'
        WHEN CAST(NULLIF(TRIM(SchoolType1), '') AS INTEGER) = 7
            THEN 'Technical / vocational'
        WHEN CAST(NULLIF(TRIM(SchoolType1), '') AS INTEGER) IN (8, 9)
            THEN 'National religious'
        WHEN CAST(NULLIF(TRIM(SchoolType1), '') AS INTEGER) IN (10, 11)
            THEN 'International / private'
    END AS school_pathway
FROM raw_in_school;

CREATE VIEW clean_salary_offers AS
SELECT
    _source_row_number AS employer_id,
    CAST(NULLIF(TRIM(state), '') AS INTEGER) AS state_code,
    CAST(NULLIF(TRIM(A1), '') AS INTEGER) AS employer_type_code,
    1 AS qualification_order,
    'School leaver / low-skilled' AS qualification,
    CAST(NULLIF(NULLIF(TRIM(C5d_schoollever_maximum), ''), '#NULL!') AS REAL) AS maximum_offer_rm
FROM raw_employer
UNION ALL
SELECT
    _source_row_number,
    CAST(NULLIF(TRIM(state), '') AS INTEGER),
    CAST(NULLIF(TRIM(A1), '') AS INTEGER),
    2,
    'Vocational / technical college',
    CAST(NULLIF(NULLIF(TRIM(C5c_college_maximum), ''), '#NULL!') AS REAL)
FROM raw_employer
UNION ALL
SELECT
    _source_row_number,
    CAST(NULLIF(TRIM(state), '') AS INTEGER),
    CAST(NULLIF(TRIM(A1), '') AS INTEGER),
    3,
    'University undergraduate',
    CAST(NULLIF(NULLIF(TRIM(C5a_undergraduate_maximum), ''), '#NULL!') AS REAL)
FROM raw_employer
UNION ALL
SELECT
    _source_row_number,
    CAST(NULLIF(TRIM(state), '') AS INTEGER),
    CAST(NULLIF(TRIM(A1), '') AS INTEGER),
    4,
    'University postgraduate',
    CAST(NULLIF(NULLIF(TRIM(C5b_postgraduate_maximum), ''), '#NULL!') AS REAL)
FROM raw_employer;
