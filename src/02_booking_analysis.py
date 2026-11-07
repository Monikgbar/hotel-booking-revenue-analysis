# ==============================================
# 1. IMPORTS AND CONFIGURATION
# ==============================================

from pathlib import Path
import matplotlib.pyplot as plt

from data_preparation import load_and_prepare_data


# Load and prepare data
df, df_analysis = load_and_prepare_data()

# Define visualization path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISUALS_PATH = PROJECT_ROOT / 'visuals'

# Create visualization directory
VISUALS_PATH.mkdir(parents=True, exist_ok=True)


# ==============================================
# 2. LENGTH OF STAY ANALYSIS
# ==============================================

# Calculate descriptive statistics for total nights
stay_duration = df_analysis['total_nights'].describe()

print('\nLength of stay - Descriptive statistics:')
print(stay_duration)

# Compare length of stay by hotel
stay_duration_by_hotel = (
    df_analysis
    .groupby('hotel')['total_nights']
    .agg(
        total_bookings='count',
        average_nights='mean',
        median_nights='median',
        min_nights='min',
        max_nights='max'
    ) 
)

print('\nLength of stay by hotel:')
print(stay_duration_by_hotel.round(2))

# Compare length of stay by hotel and customer type
stay_duration_by_customer_hotel = (
    df_analysis
    .groupby(['customer_type', 'hotel'])['total_nights']
    .agg(
        total_bookings='count',
        average_nights='mean',
        median_nights='median'
    )
    .sort_values('average_nights', ascending=False)
)

print('\nLength of stay by customer type and hotel:')
print(stay_duration_by_customer_hotel.round(2))


# ==============================================
# 3. BOOKING VOLUME ANALYSIS
# ==============================================

# Count bookings by year and month
booking_by_month = (
    df_analysis
    .groupby('arrival_year_month')
    .size()
)


# ==============================================
# 4. BOOKING ANALYSIS BY HOTEL
# ==============================================

# Calculate monthly bookings by hotel type
monthly_bookings_by_hotel = (
    df_analysis
    .groupby(['arrival_year_month', 'hotel'])
    .size()
    .unstack(fill_value=0)
)

print('\nMonthly bookings by hotel type:')
print(monthly_bookings_by_hotel)


# ==============================================
# 5. BOOKING GROWTH ANALYSIS
# ==============================================

# Calculate month-to-month percentage change in bookings
monthly_booking_growth = monthly_bookings_by_hotel.pct_change() * 100

print('\nMonth-to-month booking growth (%):')
print(monthly_booking_growth.round(2))


# Calculate year-over-year booking growth
monthly_booking_growth_yoy = (
    monthly_bookings_by_hotel.pct_change(periods=12) * 100
)

print('\nYear-over-year booking growth (%):')
print(monthly_booking_growth_yoy.round(2))


# ==============================================
# 6. BOOKING ANALYSIS BY CUSTOMER TYPE
# ==============================================

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


# ==============================================
# 7. LEAD TIME ANALYSIS BY CUSTOMER TYPE
# ==============================================

# Analyze lead time
print('\nLead time statistics:')
print(df_analysis['lead_time'].describe())

# Calculate lead time statistics by customer type
lead_time_by_customer_type = (
    df_analysis
    .groupby('customer_type')['lead_time']
    .agg(['mean', 'median', 'count'])
    .sort_values('mean', ascending=False)
)

print('\nLead time statistics by customer type:')
print(lead_time_by_customer_type.round(2))


# ==============================================
# 8. COMPLETED STAY ANALYSIS
# ==============================================

# Filter bookings with completed stays
df_checked_out = df_analysis[
    df_analysis['reservation_status'] == 'Check-Out'
].copy()

# Calculate length of stay by hotel and customer type
actual_stay_by_segment = (
    df_checked_out
    .groupby(['hotel', 'customer_type'])['total_nights']
    .agg(
        total_bookings='count',
        average_nights='mean',
        median_nights='median'
    )
    .round(2)
)

print('\nActual length of stay by hotel and customer type:')
print(actual_stay_by_segment.round(2))


# ==============================================
# 9. VISUALIZATIONS
# ==============================================

# Plot monthly booking volume
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    booking_by_month.index.astype(str),
    booking_by_month.values,
    color='#2878A0',
    marker='o',
    markersize=6,
    linewidth=2,
    label='Bookings'
)

# Customize chart
ax.set_title(
    'Monthly Booking Volume',
    fontsize=14,
    fontweight='bold',
    pad=15
)

ax.set_xlabel('Arrival Year-Month', fontsize=11, labelpad=10)
ax.set_ylabel('Number of Bookings', fontsize=11, labelpad=10)

# Display one date label every two months
tick_positions = range(0, len(booking_by_month))

ax.set_xticks(tick_positions)
ax.set_xticklabels(
    [
        str(month) if i % 2 == 0 else ''
        for i, month in enumerate(booking_by_month.index)
    ],
    rotation=45,
    ha='right'
)

ax.tick_params(
    axis='x',
    which='major',
    length=5,
    width=0.8
)

# Configure grid and legend
ax.grid(
    axis='y',
    linestyle='--',
    linewidth=0.7,
    alpha=0.3
)

# Remove unnecessary borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'monthly_booking_volume.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# Plot monthly bookings by hotel type
fig, ax = plt.subplots(figsize=(12, 6))

# Define consistent hotel colors
hotel_colors = {
    'City Hotel': '#219EBC',
    'Resort Hotel': '#FB8500'
}

# Plot each hotel
for hotel in monthly_bookings_by_hotel.columns:
    ax.plot(
        monthly_bookings_by_hotel.index.astype(str),
        monthly_bookings_by_hotel[hotel],
        color=hotel_colors[hotel],
        marker='o',
        markersize=5,
        linewidth=2,
        label=hotel
    )

# Customize chart
ax.set_title(
    'Monthly Bookings by Hotel',
    fontsize=14,
    fontweight='bold',
    pad=15
)

ax.set_xlabel('Arrival Year-Month', fontsize=11, labelpad=10)
ax.set_ylabel('Number of Bookings', fontsize=11, labelpad=10)

# Display one date label every two months
tick_positions = range(len(monthly_bookings_by_hotel))

ax.set_xticks(tick_positions)
ax.set_xticklabels(
    [
        str(month) if i % 2 == 0 else ''
        for i, month in enumerate(monthly_bookings_by_hotel.index)
    ],
    rotation=45,
    ha='right'
)

# Configure grid and legend
ax.grid(
    axis='y',
    linestyle='--',
    linewidth=0.7,
    alpha=0.3
)
ax.legend(title='Hotel', frameon=False)

# Remove unnecessary borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'monthly_bookings_by_hotel.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# Plot year-over-year booking growth
yoy_plot = monthly_booking_growth_yoy.dropna()

fig, ax = plt.subplots(figsize=(12, 6))

# Plot each hotel
ax.plot(
    yoy_plot.index.astype(str),
    yoy_plot['City Hotel'],
    color='#219EBC',
    marker='o',
    markersize=5,
    linewidth=2,
    label='City Hotel'
)

ax.plot(
    yoy_plot.index.astype(str),
    yoy_plot['Resort Hotel'],
    color='#FB8500',
    marker='o',
    markersize=5,
    linewidth=2,
    label='Resort Hotel'
)

# Add a zero-growth reference line
ax.axhline(
    y=0,
    color='#6C757D',
    linestyle='--',
    linewidth=1.5,
    alpha=0.8,
    label='Zero growth'
)

# Customize chart
ax.set_title(
    'Year-over-Year Booking Growth by Hotel',
    fontsize=14,
    fontweight='bold',
    pad=15
)

ax.set_xlabel('Arrival Year-Month', fontsize=11, labelpad=10)
ax.set_ylabel('Booking Growth (%)', fontsize=11, labelpad=10)

# Display one date label every two months
tick_positions = range(len(yoy_plot))

ax.set_xticks(tick_positions)
ax.set_xticklabels(
    [
        str(month) if i % 2 == 0 else ''
        for i, month in enumerate(yoy_plot.index)
    ],
    rotation=45,
    ha='right'
)

# Configure grid and legend
ax.grid(
    axis='y',
    linestyle='--',
    linewidth=0.7,
    alpha=0.3
)
ax.legend(title='Hotel', frameon=False)

# Remove unnecessary borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'year_over_year_booking_growth.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# Plot average length of stay by hotel and customer type
stay_duration_plot = actual_stay_by_segment['average_nights'].unstack(
    level='hotel'
)

fig, ax = plt.subplots(figsize=(10, 6))

# Define consistent hotel colors
hotel_colors = {
    'City Hotel': '#219EBC',
    'Resort Hotel': '#FB8500'
}

stay_duration_plot.plot(
    kind='bar',
    ax=ax,
    width=0.85,
    color=[
        hotel_colors[hotel]
        for hotel in stay_duration_plot.columns
    ],
    edgecolor='white',
    linewidth=0.7
)

# Add value labels
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.2f',
        padding=3,
        fontsize=9
    )

# Customize chart
ax.set_title(
    'Average Stay by Customer Type',
    fontsize=14,
    pad=15
)
ax.set_xlabel('Customer Type', fontsize=11, labelpad=10)
ax.set_ylabel('Average Nights', fontsize=11, labelpad=10)

ax.tick_params(axis='x', rotation=0)
ax.grid(
    axis='y', 
    linestyle='--', 
    linewidth=0.7,
    alpha=0.3
)

ax.legend(title='Hotel', frameon=False)

# Remove unnecessary borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_axisbelow(True)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'average_stay_by_customer_type.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()

print('\nBooking analysis completed successfully.')