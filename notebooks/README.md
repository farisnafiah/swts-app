# TVET report visualisations

With the source data and metadata organised in `raw_data/`, the next step is to calculate the summaries and create the visuals in a Jupyter notebook.

Open [tvet_pathway.ipynb](tvet_pathway.ipynb), select **KRI-app (.venv)** and choose **Run All**.

The notebook creates two charts from the raw data. Visual 1 shows the school-pathway distribution within each ethnic group using all 7,026 records in `SWTS_InSchool.csv`. Visual 2 selects the 405 employer records with `A1 = 3` and shows individual maximum salary offers, unweighted means, medians and valid response counts. The questionnaire labels this code public sector, but its mapping in the CSV remains unconfirmed.

Each chart includes a source reference and an interpretation note. The report uses survey weights, but no weight field is available in the public CSVs. Both charts therefore describe the unweighted sample rather than reproduce the published estimates. Source metadata was extracted from KRI on **2 October 2026**. PNG and SVG exports are saved in `outputs/`.

Once the dependencies are installed, the notebook runs offline from the repository root or the `notebooks/` directory using the shared environment. The complete report and evidence manifest are documented in the [report guide](../raw_data/report/README.md).
