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
# 2. BOOKING VOLUME ANALYSIS
# ==============================================

# Count bookings by year and month
booking_by_month = (
    df_analysis
    .groupby('arrival_year_month')
    .size()
)


# ==============================================
# 3. BOOKING ANALYSIS BY HOTEL
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
# 4. BOOKING GROWTH ANALYSIS
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
# 5. BOOKING ANALYSIS BY CUSTOMER TYPE
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
# 6. LEAD TIME ANALYSIS BY CUSTOMER TYPE
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
# 7. VISUALIZATIONS
# ==============================================

# Plot monthly booking volume
plt.figure(figsize=(12, 6))

booking_by_month.plot(
    kind='line',
    marker='o'
)

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

plt.close()


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
plt.legend(title='Hotel Type')
plt.grid(True, alpha=0.3)
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
ax.axhline(
    y=0,
    color='gray',
    linestyle='--',
    linewidth=1
)

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

plt.close()


print('\nBooking analysis completed successfully.')