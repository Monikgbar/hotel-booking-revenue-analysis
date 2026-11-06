# ==============================================
# 1. IMPORTS AND CONFIGURATION
# ==============================================

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from data_preparation import load_and_prepare_data


# Define visualization path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISUALS_PATH = PROJECT_ROOT / 'visuals'

# Create visualization directory
VISUALS_PATH.mkdir(parents=True, exist_ok=True)

# Load and prepare data
df, df_analysis = load_and_prepare_data()


# ============================================
# 2. REVENUE ANALYSIS BY COUNTRY
# ============================================

# Identify the top 10 countries by number of bookings
bookings_by_country = df_analysis['country'].value_counts()

top_10_countries = bookings_by_country.head(10).index

# Revenue analysis by country
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

# Calculate the percentage of bookings from the top 10 countries
percentage_top_10_countries = (
    bookings_by_country.head(10).sum() 
    / bookings_by_country.sum()
) * 100

print(
    f'\nPercentage of bookings from the top 10 countries: '
    f'{percentage_top_10_countries:.2f}%'
)


# ============================================
# 3. CORRELATIONS BETWEEN TOTAL NIGHTS AND ADR
# ============================================

# Calculate correlations between total nights and ADR
correlation_nights_adr = (
    df_analysis['total_nights'].corr(df_analysis['adr'])
)

print(
    f'\nCorrelation between total nights and ADR: '
    f'{correlation_nights_adr:.2f}'
)


# ============================================
# 4. MONTHLY BOOKINGS AND ESTIMATED REVENUE
# ============================================

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


# ============================================
# 5. REVENUE ANALYSIS BY BOOKING STATUS
# ============================================

# Estimated revenue analysis by booking status
revenue_by_status = (
    df_analysis
    .groupby('is_canceled')
    .agg(
        total_bookings=('is_canceled', 'size'),
        total_estimated_revenue=('estimated_revenue', 'sum'),
        average_adr=('adr', 'mean')
    )
)

print('\nEstimated revenue by booking status:')
print(revenue_by_status.round(2))


# ============================================
# 6. REVENUE ANALYSIS BY HOTEL AND BOOKING STATUS
# ============================================

# Booking metrics by hotel and cancellation status
booking_metrics_by_segment = (
    df_analysis
    .groupby(['hotel', 'is_canceled'])
    .agg(
        total_bookings=('is_canceled', 'size'),
        total_estimated_revenue=('estimated_revenue', 'sum'),
        average_adr=('adr', 'mean')
    )
)

print('\nBooking metrics by hotel and cancellation status:')
print(booking_metrics_by_segment.round(2))


print('\nRevenue analysis completed successfully.')


# ============================================
# 7. DISTRIBUTION CHANNEL ANALYSIS
# ============================================

# Calculate booking share by distribution channel
channel_booking_share = (
    df_analysis['distribution_channel']
    .value_counts(normalize=True, dropna=False)
    .mul(100)
)

print('\nBookings share by distribution channel (%):')
print(channel_booking_share.round(2))

# Filter completed stays
df_completed = df_analysis[
    df_analysis['reservation_status'] == 'Check-Out'
].copy()

# Analyze estimated revenue by distribution channel
revenue_by_channel = (
    df_completed
    .groupby('distribution_channel')['estimated_revenue']
    .agg(
        total_bookings='count',
        total_estimated_revenue='sum',
        average_revenue_per_booking='mean'
    )
    .sort_values('total_estimated_revenue', ascending=False)    
)

print('\nEstimated revenue by distribution channel:')
print(revenue_by_channel.round(2))

# Calculate booking share among completed stays
completed_booking_share = (
    df_completed['distribution_channel']
    .value_counts(normalize=True)
    .mul(100)
)

# Calculate estimated revenue share by channel
revenue_share = (
    revenue_by_channel['total_estimated_revenue']
    / revenue_by_channel['total_estimated_revenue'].sum()
    * 100
)

# Combine both metrics
channel_comparison = pd.DataFrame({
    'booking_share': completed_booking_share,
    'revenue_share': revenue_share
})

print('\nBooking share vs estimated revenue share(%)')
print(channel_comparison.round(2))

# Analyze estimated revenue by hotel and distribution channel
revenue_by_hotel_channel = (
    df_completed
    .groupby(['hotel', 'distribution_channel'])['estimated_revenue']
    .agg(
        total_bookings='count',
        total_estimated_revenue='sum',
        average_revenue_per_booking='mean'
    )
    .round(2)
)

print('\nEstimated revenue by hotel and distribution channel:')
print(revenue_by_hotel_channel)

# Calculate estimated revenue share by hotel and distribution channel
revenue_share_by_hotel = (
    revenue_by_hotel_channel['total_estimated_revenue']
    .groupby(level='hotel')
    .transform(lambda x:x / x.sum() * 100)
)

revenue_share_by_hotel = revenue_share_by_hotel.rename('revenue_share')

print('\nEstimated revenue share by hotel and distribution channel (%):')
print(revenue_share_by_hotel.round(2))

# Analyze ADR and length of stay by hotel and distribution channel
channel_performance = (
    df_completed
    .groupby(['hotel', 'distribution_channel'])
    .agg(
        total_bookings=('estimated_revenue', 'count'),
        average_adr=('adr', 'mean'),
        average_nights=('total_nights', 'mean'),
        average_revenue=('estimated_revenue', 'mean')
    )
    .round(2)
)

print('\nChannel performance by hotel:')
print(channel_performance)


# ==============================================
# 8. VISUALIZATIONS
# ==============================================

# Plot monthly estimated revenue
fig, ax = plt.subplots(figsize=(12, 6))

monthly_analysis['estimated_revenue'].plot(
    kind='line',
    marker='o',
    ax=ax
)

ax.set_title('Monthly Estimated Revenue')
ax.set_xlabel('Arrival Year-Month')
ax.set_ylabel('Estimated Revenue (€)')

ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'monthly_estimated_revenue.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()

# Plot estimated revenue share by hotel and distribution channel
revenue_share_plot = revenue_share_by_hotel.unstack(
    level='hotel'
)

fig, ax = plt.subplots(figsize=(10, 6))

revenue_share_plot.plot(
    kind='bar',
    ax=ax,
    width=0.85,
    edgecolor='white',
    linewidth=0.7
)

# Add value labels
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.2f%%',
        padding=3,
        fontsize=9
    )

# Customize chart
ax.set_title(
    'Estimated revenue share by distribution channel and hotel',
    fontsize=14,
    pad=15
)
ax.set_xlabel('Distribution Channel')
ax.set_ylabel('Estimated Revenue Share (%)')
ax.legend(title='Hotel')

ax.tick_params(axis='x', rotation=0)
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Remove unnecessary borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'estimated_revenue_share_by_channel_hotel.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()

# Plot total estimated revenue by distribution channel
fig, ax = plt.subplots(figsize=(10, 6))

revenue_by_channel['total_estimated_revenue'].sort_values(
    ascending=False
).plot(
    kind='bar',
    ax=ax,
    width=0.85,
    edgecolor='white',
    linewidth=0.7
)

# Add value labels in millions of euros
for container in ax.containers:
    labels = [
        f'{bar.get_height() / 1_000_000:.2f} M€'
        for bar in container
    ]

    ax.bar_label(
        container,
        labels=labels,
        padding=3,
        fontsize=9
    )

# Customize chart
ax.set_title(
    'Total Estimated Revenue by Distribution Channel',
    fontsize=14,
    pad=15
)
ax.set_xlabel('Distribution Channel')
ax.set_ylabel('Estimated Revenue (Millions €)')

# Format y-axis in millions of euros
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, pos: f'{x / 1_000_000:.0f}')
)

ax.tick_params(axis='x', rotation=0)
ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'estimated_revenue_by_channel.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()
