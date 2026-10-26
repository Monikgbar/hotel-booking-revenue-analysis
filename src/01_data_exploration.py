# ==============================================
# 1. IMPORTS AND CONFIGURATION
# ==============================================

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ==============================================
# 2. LOAD DATA
# ==============================================

# Define project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / 'data' / 'raw' / 'hotel_bookings.csv'
VISUALS_PATH = PROJECT_ROOT / 'visuals'

# Load data
df = pd.read_csv(DATA_PATH)


# ==============================================
# 3. DATA PREPARATION
# ==============================================

# Create a working copy for analysis
df_analysis = df.copy()

# Create derived columns
df_analysis['total_nights'] = (
    df_analysis['stays_in_weekend_nights']
    + df_analysis['stays_in_week_nights']
)

df_analysis['estimated_revenue'] = (
    df_analysis['adr'] * df_analysis['total_nights']
)

df_analysis['arrival_date'] = pd.to_datetime(
    df_analysis['arrival_date_year'].astype(str)
    + '-'
    + df_analysis['arrival_date_month']
    + '-'
    + df_analysis['arrival_date_day_of_month'].astype(str),
    format='%Y-%B-%d',
    errors='coerce'
)

df_analysis['arrival_year'] = df_analysis['arrival_date'].dt.year
df_analysis['arrival_month'] = df_analysis['arrival_date'].dt.month

# Create a year-month column for time-based analysis
df_analysis['arrival_year_month'] = (
    df_analysis['arrival_date'].dt.to_period('M')
)

# Create a flag for exact duplicate rows
df_analysis['is_duplicate'] = df_analysis.duplicated(keep=False)


# ==============================================
# 4. DATA QUALITY AUDIT
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

print('|\nDuplicate Analysis: Cancellation Rate by Hotel:')
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
# 5. CHECK POTENTIALLY INVALID VALUES
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

# Count bookings by cancellation statusç
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
print('\nTotal nights with no guests by resertion status:')
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
# 6. EXPLORATORY DATA ANALYSIS
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

# Identify the top 10 countries by number of bookings
bookings_by_country = df_analysis['country'].value_counts()
top_10_countries = bookings_by_country.head(10).index

print('\nTop 10 countries by bookings:')
print(bookings_by_country.head(10))

# Calculate the percentage of bookings from the top 10 countries
percentage_top_10_countries = (
    bookings_by_country.head(10).sum() 
    / bookings_by_country.sum()
) * 100

print(
    f'\nPercentage of bookings from the top 10 countries: '
    f'{percentage_top_10_countries:.2f}%'
)

# Analyze ADR for the top 10 countries
country_analysis = (
    df_analysis[df_analysis['country'].isin(top_10_countries)]
    .groupby('country')
    .agg(
        bookings=('country', 'size'),
        average_adr=('adr', 'mean'),
        estimated_revenue=('estimated_revenue', 'sum'),
        estimated_revenue_per_booking=('estimated_revenue', 'mean'),
        average_nights=('total_nights', 'mean')
    )
    .sort_values('bookings', ascending=False)
)

print('\nKey metrics for the top 10 countries:')
print(country_analysis.round(2))

# Calculate correlations between total nights and ADR
correlation_nights_adr = (
    df_analysis['total_nights'].corr(df_analysis['adr'])
)

print(
    f'\nCorrelation between total nights and ADR:'
    f'{correlation_nights_adr:.2f}'
)

# Check arrival-month coverage by year
months_by_year = (df_analysis.groupby('arrival_year')['arrival_month'].agg(['min', 'max','nunique']))

print('\nArrival month coverage by year:')
print(months_by_year)

# Overall lead time statistics
print('\nOverall lead time statistics:')
print(df_analysis['lead_time'].describe())

# Calculate lead time statistic by customer type
lead_time_by_customer_type = (
        df_analysis.groupby('customer_type')['lead_time']
        .agg(['mean', 'median','count'])
        .sort_values('mean', ascending=False)
    )

print('\nLead time statistics by customer type:')
print(lead_time_by_customer_type)

# Calculate lead time statistics by cancellation status
lead_time_by_cancellation = (
    df_analysis.groupby('is_canceled')['lead_time']
    .agg(['mean', 'median', 'count'])
)

print('\nLead time statistics by cancellation status:')
print(lead_time_by_cancellation)

# Define lead time intervals
lead_time_bins = [0, 30, 90, 180, float('inf')]

# Define labels for each lead time interval
lead_time_labels = [
    '0-30 days', 
    '31-90 days', 
    '91-180 days', 
    '181+ days'
]

# Categorize bookings according to their lead time
df_analysis['lead_time_group'] = pd.cut(
    df_analysis['lead_time'],
    bins=lead_time_bins, 
    labels=lead_time_labels, 
    include_lowest=True
)

# Calculate the cancellation rate for each lead time group
cancellation_by_lead_time = (
    df_analysis.groupby('lead_time_group', observed=True)['is_canceled']
    .mean()
    .mul(100)
    .round(2)
)

print('\nCancellation rate by lead time group:')
print(cancellation_by_lead_time)

# Calculate the proportion of cancelled reservations for each customer type
bookings_by_customer_type = (
    df_analysis.groupby('customer_type')['is_canceled']
    .agg(['count', 'sum', 'mean'])
)

bookings_by_customer_type['cancellation_rate'] = (
    bookings_by_customer_type['mean'] * 100
    ).round(2)

print('\nCancellation statistics by customer type:')
print(bookings_by_customer_type)

# Count bookings by year and month
booking_by_month = (
    df_analysis
    .groupby('arrival_year_month')
    .size()
)

print('\nBookings by month:')
print(booking_by_month)

# Calculate monthly bookings and estimated revenue
monthly_analysis = (
    df_analysis
    .groupby('arrival_year_month')
    .agg(
        bookings=('arrival_year_month', 'size'),
        estimated_revenue=('estimated_revenue', 'sum')
    )
)

print('\nMonthly Bookings and Estimated Revenue:')
print(monthly_analysis)

# Calculate estimated revenue per booking
monthly_analysis['estimated_revenue_per_booking'] = (
    monthly_analysis['estimated_revenue']
    / monthly_analysis['bookings']
)

print('\nMonthly revenue analysis:')
print(monthly_analysis.round(2))

# Calculate monthly bookings by hotel type
monthly_bookings_by_hotel = (
    df_analysis
    .groupby(['arrival_year_month', 'hotel'])
    .size()
    .unstack(fill_value=0)
)

print('\nMonthly bookings by hotel type:')
print(monthly_bookings_by_hotel)

# Calculate month-to-month percentage change in bookings
monthly_booking_growth = monthly_bookings_by_hotel.pct_change() * 100

print('\nMonth-to-month boolking growth (%):')
print(monthly_booking_growth.round(2))

# Calculate year-over-year booking growth
monthly_booking_growth_yoy = (
    monthly_bookings_by_hotel.pct_change(periods=12) * 100
)

print('\nYear-over-year booking growth (%):')
print(monthly_booking_growth_yoy.round(2))

# Analyze bookings by customer type
bookings_by_hotel_customer = (
    df_analysis
    .groupby(['hotel', 'customer_type'])
    .size()
    .unstack(fill_value=0)
)

print('\nBookings by hotel and customer type:')
print(bookings_by_hotel_customer)

# Calculate the percentage of each customer type within each hotel
customer_type_share = (
    bookings_by_hotel_customer
    .div(bookings_by_hotel_customer.sum(axis=1), axis=0)
    * 100
)

print('\nCustomer type distribution by hotel (%):')
print(customer_type_share.round(2))


# Analize cancellation rates by hotel and customer type
cancellation_by_segment = (
    df_analysis
    .groupby(['hotel', 'customer_type'])
    .agg(
        total_bookings=('is_canceled', 'size'),
        canceled_bookings=('is_canceled', 'sum')
    )
)

cancellation_by_segment['cancellation_rate'] = (
    cancellation_by_segment['canceled_bookings']
    / cancellation_by_segment['total_bookings']
    * 100
)

print('\nCancellation rates by hotel and customer type:')
print(cancellation_by_segment.round(2))



# ==============================================
# 7. VISUALIZATIONS
# ==============================================

# Create a bar chart
plt.figure(figsize=(10, 6))

lead_time = cancellation_by_lead_time.index
cancellation_rate = cancellation_by_lead_time.values

plt.bar(
    lead_time, 
    cancellation_rate, 
    width=0.5, 
    color='lightblue', 
    align='center'
)

# Display the cancellation rate above each bar
for index, value in enumerate(cancellation_rate):
    plt.text(index, value + 1, f'{value:.2f}%', ha='center')

# Configure the chart
plt.title('Cancellation Rate by Booking Lead Time')
plt.xlabel('Lead Time Group')
plt.ylabel('Cancellation Rate (%)')
plt.xticks(rotation=0)

plt.tight_layout()

# Create the output directory if it does not exist
VISUALS_PATH.mkdir(parents=True, exist_ok=True)

plt.savefig(
    VISUALS_PATH / 'cancellation_rate_by_lead_time.png',
    dpi=300, 
    bbox_inches='tight'
)

plt.show()

# Plot monthly booking volume
plt.figure(figsize=(12, 6))

booking_by_month.plot(kind='line', marker='o')

plt.title('Monthly Booking Volume')
plt.xlabel('Arrival Year-Month')
plt.ylabel('Number of Bookings')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'monthly_booking_volume.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()


# Plot monthly estimated revenue
plt.figure(figsize=(12, 6))

monthly_analysis['estimated_revenue'].plot(
    kind='line',
    marker='o'
)

plt.title('Monthly Estimated Revenue')
plt.xlabel('Arrival Year-Month')
plt.ylabel('Estimated Revenue (€)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'monthly_estimated_revenue.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()

# Plot monthly bookings by hotel type
monthly_bookings_by_hotel.plot(
    kind='line',
    marker='o',
    figsize=(12, 6)
)

plt.title('Monthly Bookings by Hotel')
plt.xlabel('Arrival Year-Month')
plt.ylabel('Number of Bookings')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.legend(title='Hotel Type')
plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'monthly_bookings_by_hotel.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()

# Prepare year-over-year growth data for visualization
yoy_plot = monthly_booking_growth_yoy.dropna()

# Create the chart
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    yoy_plot.index.astype(str),
    yoy_plot['City Hotel'],
    marker='o',
    label='City Hotel'
)

ax.plot(
    yoy_plot.index.astype(str),
    yoy_plot['Resort Hotel'],
    marker='o',
    label='Resort Hotel'
)


# Add a reference line at zero growth
ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)

# Add labels and formatting
ax.set_title('Year-over-Year Booking Growth by Hotel')
ax.set_xlabel('Arrival Year-Month')
ax.set_ylabel('Booking Growth (%)')
ax.tick_params(axis='x', rotation=45)
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'year_over_year_booking_growth.png',
    dpi=300,
    bbox_inches='tight'
)

plt.show()

# Plot cancellation rates by hotel and customer type
cancellation_rate_plot = (
    cancellation_by_segment['cancellation_rate']
    .unstack(level='hotel')
)

ax = cancellation_rate_plot.plot(
    kind='bar',
    figsize=(10, 6)
)

# Configure the chart
ax.set_title('Cancellation Rate by Hotel and Customer Type')
ax.set_xlabel('Customer Type')
ax.set_ylabel('Cancellation Rate (%)')
ax.set_ylim(0, 100)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.legend(title='Hotel')

# Add percentage labels above each bar
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3
    )

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'cancellation_rate_by_hotel.png',
    dpi=300, 
    bbox_inches='tight'
)

plt.show()
