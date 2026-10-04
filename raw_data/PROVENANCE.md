# SWTS source data and provenance

The project retains two respondent-level CSVs from Khazanah Research Institute's [SWTS dataset page](https://www.krinstitute.org/publications/the-school-to-work-transition-survey-swts-of-young-malaysian):

| Local file | Records | Columns | Official download |
| --- | ---: | ---: | --- |
| `SWTS_Employer.csv` | 1,620 | 109 | [Employers](https://kri-public-data.s3.ap-southeast-1.amazonaws.com/SWTS/SWTS_Employer.csv) |
| `SWTS_InSchool.csv` | 7,026 | 72 | [In-school students](https://kri-public-data.s3.ap-southeast-1.amazonaws.com/SWTS/SWTS_InSchool.csv) |

The repository does not record the original download date and cannot guarantee that future downloads will be byte-identical. The dimensions above describe the preserved local files.

The survey was collected in late 2017 and early 2018. KRI used probability sampling and weights for its published in-school and employer estimates. No identifiable weight field exists in the released CSV headers, so this project reports unweighted sample results.

[source_column_definitions.json](metadata/source_column_definitions.json) preserves KRI's published column definitions for these two modules and a local file inventory. The metadata was extracted from KRI's website on **2 October 2026**. Instrument versions and exported codes do not always align, so the notebook documents each recode it uses.

The files are not reconstructed from report tables or published percentages. The notebook reads them without modification and creates no derived CSVs.

Attribution: Khazanah Research Institute. 2018. *The School-to-Work Transition of Young Malaysians dataset*. Kuala Lumpur: Khazanah Research Institute. Licence: Creative Commons Attribution CC BY 3.0.

