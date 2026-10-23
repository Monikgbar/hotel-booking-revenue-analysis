# Hotel Booking & Revenue Analysis

## Project Overview

This project analyzes hotel booking data to identify patterns in demand, seasonality, cancellations, revenue, and customer behavior.

The goal is to transform raw booking data into actionable business insights that could support hotel management and revenue-related decision-making.

## Business Questions

1. How does the number of bookings evolve over time?
2. Is there a seasonal pattern in demand?
3. How does monthly revenue evolve?
4. What is the average length of stay, and how does it vary?
5. How far in advance do customers make their bookings?
6. What is the booking volume and cancellation rate?
7. Which countries and booking channels generate the highest revenue?
8. Which customer characteristics are associated with higher value?

## Data Source

The main dataset used in this project is the **Hotel Booking Demand Dataset**, originally published in:

> Antonio, N., de Almeida, A., & Nunes, L. (2019).  
> _Hotel booking demand datasets._  
> _Data in Brief, 22_, 41–49.

The dataset contains booking information from two real hotels in Portugal:

- Resort Hotel
- City Hotel

The observations cover bookings with arrival dates between July 2015 and August 2017.

The dataset contains 119,390 booking records and includes both completed and canceled bookings.

Source:  
https://www.sciencedirect.com/science/article/pii/S2352340918315191

## Dataset Limitations

The dataset has several limitations that must be considered when interpreting the results:

- Customer identification data was removed for privacy reasons.
- The dataset represents two hotels rather than a single hotel.
- Customer-level longitudinal analysis is therefore limited.
- The dataset does not provide detailed operational costs.
- It does not include detailed spending on additional hotel services such as restaurants, spa treatments, excursions, or transportation.
- Customer satisfaction scores are not included.

Therefore, this project focuses primarily on booking behavior, demand, cancellations, revenue-related metrics, and customer segments rather than individual customer lifetime value.

## Analysis

### Data quality and duplicate records

The dataset contains 31,994 rows identified as duplicates by `pandas.DataFrame.duplicated()` using its default behavior.

These rows are identical to previously encountered rows across the available columns. However, the dataset does not provide a unique booking identifier to confirm whether they represent duplicate records or distinct bookings with identical attributes.

**Decision:** Duplicate rows will be retained in the processed dataset. They will not be removed automatically, as doing so could alter booking counts and other analytical results. This limitation will be considered when interpreting the findings.

### Missing values in children

Four records contain missing values in the `children` column. All four belong to canceled City Hotel bookings.

The available data does not establish the actual number of children in these bookings.

**Decision:** Missing values will be preserved as `NaN` rather than replaced with zero, because the absence of a recorded value does not prove that no children were included.

### Negative ADR value

One record contains a negative Average Daily Rate (ADR) of -6.38. The booking belongs to a Resort Hotel and is marked as not canceled. The available data does not establish why the ADR is negative.

Excluding this record has a negligible effect on the overall average ADR, changing it from approximately 101.8311 to 101.8320.

**Decision:** The original record will be retained in the dataset. However, the negative ADR will be excluded from analyses that assume non-negative room rates, where appropriate. The record will not be treated as a confirmed data error because its cause cannot be established from the available information.

### Bookings with no adults or guests recorded

The dataset contains 403 bookings with zero adults. Of these, 223 include children and/or babies, while 180 have no adults, children, or babies recorded.

Among the 180 bookings with no guests recorded, 70 have a total stay of zero nights and 110 have a positive total stay. The available data does not establish whether these records represent data-entry issues, unusual booking circumstances, or other situations.

**Decision:** These records will be retained in the dataset. They will not be automatically classified as invalid or removed, as the available information is insufficient to establish that they are erroneous. Their potential impact will be considered when analyzing guest counts, occupancy, and average stay duration.

### Bookings with zero nights

The dataset contains 715 bookings with a total stay duration of zero nights, calculated as the sum of weekend nights and weekday nights.

These records may represent different booking circumstances, but the available data does not establish why the total stay duration is zero.

**Decision:** These records will be retained in the dataset. They will not be automatically classified as invalid or removed. However, they will be considered when interpreting analyses involving length of stay and estimated revenue, as bookings with zero nights contribute zero to the estimated revenue calculation based on ADR multiplied by total nights.

### Cancellation rate by booking lead time

The cancellation rate varies across booking lead-time groups. Bookings made 30 days or less before arrival have a cancellation rate of 18.56%, compared with 57.01% for bookings made 181 days or more in advance.

This indicates an association between longer booking lead times and higher cancellation rates in the dataset.

**Business insight:** Bookings made far in advance may warrant closer monitoring, as they are associated with a higher likelihood of cancellation. Hotels could investigate whether reminder campaigns, flexible booking policies, or targeted follow-up strategies would be appropriate for these bookings.

**Limitation:** These results show an association, not causation. The analysis does not establish that booking lead time alone explains the differences in cancellation rates.

### Cancellation rate by customer type

Cancellation rates vary across customer types. Transient customers have the highest cancellation rate at 40.75%, followed by Contract customers at 30.96%, Transient-Party customers at 25.43%, and Group customers at 10.23%.

Transient customers account for 89,613 bookings, of which 36,514 were canceled. In comparison, the Group segment contains 577 bookings, with 59 cancellations.

**Business insight:** The Transient segment represents a key area for further investigation because it combines the largest booking volume with the highest cancellation rate. Understanding the characteristics and booking conditions of this segment could help hotels identify opportunities to manage cancellations.

**Limitation:** These differences show an association between customer type and cancellation rates. They do not establish that customer type itself causes cancellations. The Group segment also has a much smaller booking volume than the Transient segment.

### Booking patterns by country

The ten countries with the highest booking counts account for 84.78% of all bookings with a recorded country.

Portugal has the highest number of bookings among the countries analyzed, followed by the United Kingdom and France. Spain has the highest average Daily Rate (ADR) among the top ten countries, while Ireland has the highest estimated revenue per booking, at approximately €489.51.

Portugal has the lowest average ADR and the shortest average length of stay among these ten countries, at approximately 2.92 nights.

**Business insight:** The results highlight differences in booking volume, average room rates, and length of stay across markets. These metrics could help hotels identify which source markets to investigate further when developing pricing, marketing, and guest-retention strategies.

**Limitations:** The country analysis includes only the ten countries with the highest booking counts. Country-level averages do not explain the reasons behind the observed differences. Estimated revenue is calculated as ADR multiplied by total nights and should not be interpreted as actual revenue or profit. In addition, 488 bookings have no recorded country, so the country analysis does not cover every booking in the dataset.

### Overall findings and next steps

The exploratory analysis identified several patterns in hotel booking behavior. Cancellation rates are higher among bookings made further in advance and vary across customer types. The analysis also revealed differences in booking volume, average ADR, and estimated revenue across countries.

The data quality assessment identified exact duplicate rows, missing values, a negative ADR value, bookings with no guests recorded, and bookings with zero nights. These limitations have been documented, and potentially problematic records have been retained unless there is sufficient evidence to justify a different treatment.

**Next steps:**

- Investigate cancellation patterns in greater detail, considering additional booking characteristics.
- Analyze trends in bookings and estimated revenue over time, taking into account the partial coverage of 2015 and 2017.
- Evaluate the impact of data quality decisions on key metrics.
- Develop visualizations and business recommendations based on the findings.

**Important limitation:** Estimated revenue is calculated as ADR multiplied by total nights. It is a proxy derived from the available data and should not be interpreted as actual revenue or profit.

## Technologies

- Python
- Pandas
- NumPy
- Matplotlib
- VS Code
- Git
- GitHub

## Project Status

🚧 Work in progress
