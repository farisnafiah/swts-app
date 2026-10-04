# Retained SWTS metadata

[source_column_definitions.json](source_column_definitions.json) contains KRI's published definitions and the local file inventory for the two modules used by the notebook:

| File | Records | Columns | Use |
| --- | ---: | ---: | --- |
| `SWTS_InSchool.csv` | 7,026 | 72 | School pathway by ethnicity. |
| `SWTS_Employer.csv` | 1,620 | 109 | Public-sector maximum salary offers. |

Numeric category codes are labels, not quantities. Blank values and `#NULL!` strings are treated field by field and are never automatically replaced with zero. No identifiable survey-weight field exists in either CSV.

## Visual 1 mappings

The KRI coding manual defines ethnicity as 1 Malay, 2 Other Bumiputera, 3 Chinese, 4 Indian and 5 Other. The notebook combines codes 1 and 2 as Bumiputera.

`SchoolType1` is collapsed to the four pathway families used in report Chart 2.3:

| Codes | Pathway family |
| --- | --- |
| 1–6 | National/residential/Form 6 |
| 7 | Technical/vocational |
| 8–9 | National religious |
| 10–11 | International/private |

## Visual 2 mappings

All `A1` codes observed in `SWTS_Employer.csv` are listed below. Visual 2 selects code **3**, labelled public sector in the published questionnaire; the CSV-specific mapping is unconfirmed. The published manual and questionnaire use an earlier category scheme; their labels are shown separately and are **not confirmed labels for the released CSV codes**.

| A1 code | CSV respondents | Released CSV interpretation | Earlier questionnaire label (not transferable) |
| --- | ---: | --- | --- |
| `1` | 813 | Not verified | Sole proprietorship |
| `2` | 246 | Not verified | Family business |
| `3` | 405 | Not verified | Public sector/government agency |
| `4` | 24 | Not verified | Public listed company |
| `5` | 15 | Not verified | Foreign-owned/multinational |
| `6` | 21 | Not verified | Private local company |
| `7` | 16 | Not verified | Other, specify |
| `8` | 18 | Not verified | Not listed |
| `9` | 12 | Not verified | Not listed |
| `10` | 4 | Not verified | Not listed |
| `11` | 45 | Not verified | Not listed |
| Missing | 1 | No employer-type code recorded | Not applicable |

Total: **1,620 employers**, including **1 missing A1 code**. The earlier labels are from the employer questionnaire, PDF page 5, and coding manual, PDF page 32. Codes 8-11 occur in the released CSV but are not enumerated in that earlier scheme. A confirmed export-specific codebook is needed to assign the remaining CSV labels.

The four maximum monthly salary-offer fields are mapped as follows:

| CSV field | Qualification label in Visual 2 |
| --- | --- |
| `C5d_schoollever_maximum` | School leaver / low-skilled |
| `C5c_college_maximum` | Vocational / technical college |
| `C5a_undergraduate_maximum` | University undergraduate |
| `C5b_postgraduate_maximum` | University postgraduate |

Visual 2 selects `A1 = 3`, labelled public sector in the published instruments. Its CSV-specific label remains unconfirmed. The chart describes the selected sample; it does not claim to reproduce the report's wage-gap figures.

`C5c_college_maximum` is the vocational/technical-college maximum offer. The `C5d_schoollever_maximum` header is retained, but the questionnaire describes low-skilled/manual workers while the report labels the category school leaver, so the chart displays both descriptions. Blank and `#NULL!` salary entries are excluded.

Sources: [KRI dataset page](https://www.krinstitute.org/publications/the-school-to-work-transition-survey-swts-of-young-malaysian), [coding manual](https://kri-public-data.s3.ap-southeast-1.amazonaws.com/SWTS/20170727_SWTS+Coding+Manual.pdf), [employer questionnaire](https://kri-public-data.s3.ap-southeast-1.amazonaws.com/SWTS/20170731_SWTS+Employer+Survey+v10.pdf), and [SWTS report](https://www.krinstitute.org/file/20181205-swts-main-book).
