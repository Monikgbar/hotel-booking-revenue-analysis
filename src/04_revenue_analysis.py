# ==============================================
# 1. IMPORTS AND CONFIGURATION
# ==============================================

from pathlib import Path
import matplotlib.pyplot as plt

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

# Identify the top 10 countries
top_10_countries = (
    df_analysis['country']
    .value_counts()
    .head(10)
    .index
)

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


# ==============================================
# 7. VISUALIZATIONS
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