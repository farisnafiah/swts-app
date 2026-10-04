-- Current chart datasets. The clean views retain state_code so a later app can
-- apply a state filter before performing the same aggregations.

CREATE VIEW analysis_school_pathways_by_ethnicity AS
WITH
ethnicity_groups(ethnicity_group, ethnicity_order) AS (
    VALUES
        ('Bumiputera', 1),
        ('Indian', 2),
        ('Chinese', 3),
        ('Other', 4)
),
pathways(school_pathway, pathway_order) AS (
    VALUES
        ('National / residential / Form 6', 1),
        ('Technical / vocational', 2),
        ('National religious', 3),
        ('International / private', 4)
),
pathway_counts AS (
    SELECT
        ethnicity_group,
        school_pathway,
        COUNT(*) AS respondents
    FROM clean_in_school
    GROUP BY ethnicity_group, school_pathway
),
complete_counts AS (
    SELECT
        ethnicity_groups.ethnicity_group,
        ethnicity_groups.ethnicity_order,
        pathways.school_pathway,
        pathways.pathway_order,
        COALESCE(pathway_counts.respondents, 0) AS respondents
    FROM ethnicity_groups
    CROSS JOIN pathways
    LEFT JOIN pathway_counts
        USING (ethnicity_group, school_pathway)
)
SELECT
    ethnicity_group,
    ethnicity_order,
    school_pathway,
    pathway_order,
    respondents,
    SUM(respondents) OVER (PARTITION BY ethnicity_group) AS ethnicity_respondents,
    ROUND(
        100.0 * respondents
        / SUM(respondents) OVER (PARTITION BY ethnicity_group),
        6
    ) AS sample_share_percent
FROM complete_counts;

CREATE VIEW analysis_salary_offers_a1_3 AS
WITH ranked AS (
    SELECT
        qualification_order,
        qualification,
        maximum_offer_rm,
        ROW_NUMBER() OVER (
            PARTITION BY qualification
            ORDER BY maximum_offer_rm
        ) AS value_rank,
        COUNT(*) OVER (PARTITION BY qualification) AS response_count
    FROM clean_salary_offers
    WHERE employer_type_code = 3
      AND maximum_offer_rm IS NOT NULL
)
SELECT
    qualification_order,
    qualification,
    COUNT(*) AS responses,
    AVG(maximum_offer_rm) AS mean_rm,
    AVG(
        CASE
            WHEN value_rank IN ((response_count + 1) / 2, (response_count + 2) / 2)
                THEN maximum_offer_rm
        END
    ) AS median_rm,
    MIN(maximum_offer_rm) AS minimum_rm,
    MAX(maximum_offer_rm) AS maximum_rm
FROM ranked
GROUP BY qualification_order, qualification;
