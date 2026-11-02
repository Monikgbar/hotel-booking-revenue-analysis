# ==============================================
# 1. IMPORTS AND CONFIGURATION
# ==============================================

import pandas as pd

from data_preparation import load_and_prepare_data


# Load and prepare data
df, df_analysis = load_and_prepare_data()


# ==============================================
# 2. DATA QUALITY AUDIT
# ==============================================

# Check the dataset dimensions
print('Dataset shape:', df_analysis.shape)

# Count missing values in each column
missing_values = df_analysis.isnull().sum()

print('\nMissing values by column:')
print(missing_values[missing_values > 0].sort_values(ascending=False))

# Count duplicate rows
duplicate_count = df_analysis.duplicated().sum()

print('\nNumber of duplicated rows:', duplicate_count)

# Count all rows involved in exact duplicates
duplicate_rows = df_analysis.duplicated(keep=False).sum()

print('Total rows involved in duplicates:', duplicate_rows)

# Inspect a sample of duplicated rows
duplicates = df_analysis[df_analysis['is_duplicate']]

print('\nSample of duplicated rows:')
print(
    duplicates[
        ['hotel', 'is_canceled', 'country', 'adr', 'reservation_status']
    ].head(10).to_string(index=False)
)

duplicate_summary = (df_analysis.groupby('is_duplicate')['is_canceled'].agg(['count', 'sum', 'mean']))
duplicate_summary['cancellation_rate'] = (duplicate_summary['mean'] * 100).round(2)

print('\nDuplicate Analysis: Cancellation Statistics:')
print(duplicate_summary)

# Compare duplicate rows by hotel
duplicate_rate_by_hotel = (df_analysis.groupby(['hotel', 'is_duplicate'])['is_canceled'].agg(['count', 'mean']))
duplicate_rate_by_hotel['cancellation_rate'] = (duplicate_rate_by_hotel['mean'] * 100).round(2)

print('\nDuplicate Analysis: Cancellation Rate by Hotel:')
print(duplicate_rate_by_hotel)

# Count exact-row combinations by group size
data_columns = df_analysis.columns.drop('is_duplicate')

group_summary = (
    df_analysis.groupby(list(data_columns), dropna=False)
    .size()
    .rename('group_size')
    .reset_index()
)

# Summarize exact-row duplicates
total_rows = len(df_analysis)

unique_groups = (group_summary['group_size'] == 1).sum()

row_in_duplicate_groups = group_summary.loc[
    group_summary['group_size'] > 1,
    'group_size'
].sum()

number_of_duplicate_groups = (group_summary['group_size'] > 1).sum()

print('\nDuplicate audit summary:')
print('Total rows:', total_rows)
print('Groups appearing once:', unique_groups)
print('Rows in duplicate groups:', row_in_duplicate_groups)
print('Number of duplicate groups:', number_of_duplicate_groups)


# ============================================
# 3. CHECK POTENTIALLY INVALID VALUES
# ============================================

# Check negative ADR values
print('Negative ADR values:', (df_analysis['adr'] < 0).sum())

# Check bookings with zero nights
print('Bookings with zero nights:', (df_analysis['total_nights'] == 0).sum())

# Inspect bookings with zero adults
zero_adults = df_analysis[df_analysis['adults'] == 0]
print('Number of bookings with zero adults:', len(zero_adults))

print('\nGuest composition:')
print(zero_adults[['adults', 'children', 'babies']].value_counts(dropna=False))

print('\nCancellation status:')
print(zero_adults['is_canceled'].value_counts())

print('\nTotal nights with zero adults:')
print((zero_adults['total_nights']).value_counts().sort_index())

# Select bookings with no guests recorded
no_guests = df_analysis[(df_analysis['adults'] == 0) & (df_analysis['children'] == 0) & (df_analysis['babies'] == 0)]

# Count the selected bookings
print('\nBookings with no guests:', len(no_guests))

# Count bookings by cancellation status
print('\nBookings with no guests: Cancellation status')
print(no_guests['is_canceled'].value_counts())

# Calculate total nights for bookings with no guests
no_guests_nights = no_guests['total_nights']

print('\nTotal nights with no guests:')
print(no_guests_nights.value_counts().sort_index())

# Compare cancellation status and total nights
print('\nBookings with no guests: Nights by cancellation status')
print(pd.crosstab(no_guests_nights, no_guests['is_canceled']))

# Compare reservation status and total nights
print('\nTotal nights with no guests by reservation status:')
print(pd.crosstab(no_guests_nights, no_guests['reservation_status']))

# Identify zero-night bookings marked as checked out
zero_nights_checkouts = no_guests[
    (no_guests_nights == 0)
    & (no_guests['reservation_status'] == 'Check-Out')
]

# Inspect relevant booking details
print('\nZero-nights bookings marked as Check Out: Details')
print(zero_nights_checkouts[
    [
        'hotel',
         'lead_time',
         'arrival_date_year',
         'arrival_date_month',
        'adults',
        'children',
        'babies',
        'adr',
        'is_repeated_guest',
        'deposit_type',
        'reservation_status_date'
    ]
].head(10).to_string(index=False)
)

# Inspect bookings with negative ADR
negative_adr = df_analysis[df_analysis['adr'] < 0]

print('\nNegative ADR: Booking details')
print(
    negative_adr[
        [
            'hotel',
            'is_canceled',
            'lead_time',
            'adults',
            'children',
            'babies',
            'stays_in_weekend_nights',
            'stays_in_week_nights',
            'adr',
            'booking_changes',
            'deposit_type',
            'reservation_status'
        ]
    ].to_string(index=False)
)

# Compare average ADR with and without negative values
adr_mean_original = df_analysis['adr'].mean()
adr_mean_non_negative = df_analysis.loc[df_analysis['adr'] >= 0, 'adr'].mean()

print('\nAverage ADR, original data:', adr_mean_original)
print('Average ADR, excluding negative values:', adr_mean_non_negative)
print('Difference:', adr_mean_non_negative - adr_mean_original)

# Select bookings with non-negative ADR
df_adr_analysis = df_analysis.loc[df_analysis['adr'] >= 0].copy()

# Compare dataset sizes
print('\nOriginal rows:', len(df_analysis))
print('Rows available for ADR analysis:', len(df_adr_analysis))
print('Rows excluded due to negative ADR:', len(df_analysis) - len(df_adr_analysis))

# Keep bookings with children or babies
bookings_no_adults = zero_adults[(zero_adults['children'] > 0) | (zero_adults['babies'] > 0)]

print('\nBookings with no adults but children or babies:', len(bookings_no_adults))

# Inspect the composition of bookings with no adults
print('\nBookings with no adults: Guest composition')
print(bookings_no_adults[['children', 'babies']].value_counts(dropna=False))

# Compare reservation status for bookings with no adults
print('\nBookings with no adults: Reservation status')
print(bookings_no_adults['reservation_status'].value_counts(dropna=False))

# Identify bookings with missing children values
missing_children = df_analysis[df_analysis['children'].isna()]

# Inspect relevant booking details
print('\nBookings with missing children values: Details')
print(
    missing_children[
        [
            'hotel',
            'is_canceled',
            'adults',
            'children',
            'babies',
            'stays_in_weekend_nights',
            'stays_in_week_nights',
            'adr',
            'reservation_status'
        ]
    ].to_string(index=False)
    )


# ==============================================
# 4. EXPLORATORY DATA ANALYSIS
# ==============================================

# Inspect dataset structure and data types
print('\nDataset structure and data types:')
df_analysis.info()

# Generate descriptive statistics for numerical columns
print('\nDescriptive statistics:')
print(df_analysis.describe())

# Inspect the most frequent agents and companies
print('\nTop 10 agents:')
print(df_analysis['agent'].value_counts().head(10))

print('\nTop 10 companies:')
print(df_analysis['company'].value_counts().head(10))

# Check arrival-month coverage by year
months_by_year = (df_analysis.groupby('arrival_year')['arrival_month'].agg(['min', 'max','nunique']))

print('\nArrival month coverage by year:')
print(months_by_year)

# Overall lead time statistics
print('\nOverall lead time statistics:')
print(df_analysis['lead_time'].describe())

# Calculate lead time statistics by cancellation status
lead_time_by_cancellation = (
    df_analysis.groupby('is_canceled')['lead_time']
    .agg(['mean', 'median', 'count'])
)

print('\nLead time statistics by cancellation status:')
print(lead_time_by_cancellation)

print('\nData exploration completed successfully.')