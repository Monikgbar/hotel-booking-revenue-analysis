
from data_preparation import load_and_prepare_data

df, df_analysis = load_and_prepare_data()

print('Original dataset:', df.shape)
print('Prepared dataset:', df_analysis.shape)

print('\nNew columns:')
print(
    df_analysis[
        [
            'total_nights',
            'estimated_revenue',
            'arrival_date',
            'arrival_year_month',
            'is_duplicate'
        ]
    ].head()
)
