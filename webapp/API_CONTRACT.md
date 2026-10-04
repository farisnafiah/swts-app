# Frontend API contract

This contract describes the version 1 JSON responses available to a future
visualisation frontend. FastAPI also publishes the same typed schemas at
`/docs` and `/openapi.json` while the backend is running.

Base URL during local development: `http://127.0.0.1:8000`

## General rules

- All endpoints are read-only `GET` requests.
- Successful responses use JSON and HTTP `200`.
- The current datasets are unweighted sample summaries.
- Array ordering is part of the contract. The frontend should still use the
  supplied order fields rather than alphabetical ordering.
- Missing salary responses are excluded from `observations` and summary
  calculations; they are not returned as zero.
- Both visual endpoints accept an optional `state_code` query parameter from 1
  to 16. The code is applied independently to the two survey samples.
- If the generated database is unavailable, data endpoints return HTTP `503`
  with a build instruction in `detail`.

## `GET /api/v1/school-pathways`

Purpose: supplies the complete dataset for the stacked school-pathway chart.

Optional query: `state_code`, an integer from 1 to 16. Omit it for all states.

Top-level fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `state_code` | integer or null | Applied state code; null means all states. |
| `state_label` | string | Display label for the selected state. |
| `weighting` | string | Always `unweighted`. |
| `total_respondents` | integer | Number of in-school records represented. |
| `items` | array | One item for every ethnicity and pathway combination. |

Each item contains:

| Field | Type | Frontend use |
| --- | --- | --- |
| `ethnicity_group` | string | Group label. |
| `ethnicity_order` | integer | Y-axis group order. |
| `school_pathway` | string | Stack and legend label. |
| `pathway_order` | integer | Stack and legend order. |
| `respondents` | integer | Count for the combination. |
| `ethnicity_respondents` | integer | Denominator for the ethnicity group. |
| `sample_share_percent` | number | Bar-segment width on a 0-100 scale. |

The endpoint always returns the complete 4 by 4 matrix. A combination with no
responses is represented by an item whose count and percentage are zero.

Example shape:

```json
{
  "state_code": null,
  "state_label": "All states",
  "weighting": "unweighted",
  "total_respondents": 7026,
  "items": [
    {
      "ethnicity_group": "Bumiputera",
      "ethnicity_order": 1,
      "school_pathway": "National / residential / Form 6",
      "pathway_order": 1,
      "respondents": 4044,
      "ethnicity_respondents": 5934,
      "sample_share_percent": 68.149646
    }
  ]
}
```

## `GET /api/v1/salary-offers`

Purpose: supplies the individual dots and summary markers for the maximum
salary-offer chart.

Optional query: `state_code`, an integer from 1 to 16. Omit it for all states.

Top-level fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `state_code` | integer or null | Applied state code; null means all states. |
| `state_label` | string | Display label for the selected state. |
| `employer_type_code` | integer | Always `3` in version 1. |
| `employer_type_label` | string | Label from the published questionnaire. |
| `label_status` | string | Warns that the label is not confirmed for the CSV export. |
| `weighting` | string | Always `unweighted`. |
| `currency` | string | Always `MYR`. |
| `period` | string | Always `month`. |
| `employers` | integer | Employer records selected by `A1 = 3`, including those with missing offers. |
| `observations` | array | Valid individual maximum offers for chart dots. |
| `summaries` | array | One statistical summary per qualification. |

Each observation contains:

| Field | Type | Frontend use |
| --- | --- | --- |
| `employer_id` | integer | Stable identifier for the source employer row. |
| `qualification_order` | integer | Category order from 1 to 4. |
| `qualification` | string | Category label. |
| `maximum_offer_rm` | number | X-axis value in monthly MYR. |

Each summary contains:

| Field | Type | Frontend use |
| --- | --- | --- |
| `qualification_order` | integer | Category order from 1 to 4. |
| `qualification` | string | Category label. |
| `responses` | integer | Valid response count; denominator for that category. |
| `mean_rm` | number | Mean marker. |
| `median_rm` | number | Median marker. |
| `minimum_rm` | number | Observed lower bound. |
| `maximum_rm` | number | Observed upper bound. |

The frontend should join observations and summaries using
`qualification_order`. If a unique chart key is required for an observation,
combine `qualification_order` and `employer_id`. `employers` will be larger
than some `responses` values because missing salary fields are excluded
separately for each qualification.

Some state codes have no employer records in the released employer file. In
that case, `employers` is zero and both salary arrays are empty; the frontend
must present unavailable evidence rather than a zero salary.

## `GET /api/v1/states`

Returns the 16 state-code labels from the SWTS coding manual in code order.
Each item contains integer `code` and string `label` fields. The frontend uses
this endpoint to populate its shared state selector.

## Service endpoints

- `GET /` serves the visualisation page.
- `GET /api` returns links to the documentation and OpenAPI schema.
- `GET /health` confirms that the backend can read the SQLite database.
