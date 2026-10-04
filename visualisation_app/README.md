# TVET pathway visualisation app

Status: placeholder; there is no runnable app in this project yet. The SQLite
data layer it will consume is now implemented.

This directory is reserved for a dashboard built from the survey data. The [notebook](../notebooks/tvet_pathway.ipynb) now calculates both visuals from raw in-school and employer records. Any app must distinguish these unweighted sample results from KRI's weighted published estimates; the public CSVs do not include survey-weight fields.

The app should treat the documented views in the
[database guide](../database/README.md) as its data boundary. Start with
`analysis_school_pathways_by_ethnicity` and `analysis_salary_offers_a1_3` for
the current visuals. The clean views retain state codes so filtering can be
added later without changing the raw import.

No runnable dashboard is currently included. The executed
[notebook](../notebooks/tvet_pathway.ipynb) remains the current visual output.
