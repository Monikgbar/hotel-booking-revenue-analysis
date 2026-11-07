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
# 2. CANCELLATION RATE BY LEAD TIME
# ==============================================

# Calculate the cancellation rate for each lead time group
cancellation_by_lead_time = (
    df_analysis
    .groupby('lead_time_group', observed=True)['is_canceled']
    .mean()
    .mul(100)
    .round(2)
)

print('\nCancellation rate by lead time group:')
print(cancellation_by_lead_time)


# ==============================================
# 3. CANCELLATION ANALYSIS BY CUSTOMER TYPE
# ==============================================

# Calculate cancellation statistics for each customer type
bookings_by_customer_type = (
    df_analysis
    .groupby('customer_type')['is_canceled']
    .agg(['count', 'sum', 'mean'])
)

bookings_by_customer_type['cancellation_rate'] = (
    bookings_by_customer_type['mean'] * 100
).round(2)

print('\nCancellation statistics by customer type:')
print(bookings_by_customer_type.round(2))


# =====================================================
# 4. CANCELLATION ANALYSIS BY HOTEL AND CUSTOMER TYPE
# =====================================================

# Calculate cancellation metrics by hotel and customer type
cancellation_by_segment = (
    df_analysis
    .groupby(['hotel', 'customer_type'])
    .agg(
        total_bookings=('is_canceled', 'size'),
        canceled_bookings=('is_canceled', 'sum')
    )
)

# Calculate cancellation rate
cancellation_by_segment['cancellation_rate'] = (
    cancellation_by_segment['canceled_bookings']
    / cancellation_by_segment['total_bookings']
    * 100
)

print('\nCancellation rates by hotel and customer type:')
print(cancellation_by_segment.round(2))


# ==============================================
# 5. CANCELLATION RATE BY HOTEL
# ==============================================

# Calculate cancellation rate for each hotel
cancellation_by_hotel = (
    df_analysis
    .groupby('hotel')
    .agg(
        total_bookings=('is_canceled', 'size'),
        canceled_bookings=('is_canceled', 'sum')
    )
)

cancellation_by_hotel['cancellation_rate'] = (
    cancellation_by_hotel['canceled_bookings']
    / cancellation_by_hotel['total_bookings']
    * 100
)

print('\nCancellation rate by hotel:')
print(cancellation_by_hotel.round(2))


# ==============================================
# 6. CANCELLATION RANKING BY SEGMENT
# ==============================================

# Rank customer segments by cancellation rate within each hotel
cancellation_ranking = (
    cancellation_by_segment
    .sort_values(
        ['hotel', 'cancellation_rate'],
        ascending=[True, False]
    )
)

print('\nCancellation rate ranking by hotel and customer type:')
print(cancellation_ranking.round(2))


# ==============================================
# 7. CONTRIBUTION TO TOTAL CANCELLATIONS
# ==============================================

# Calculate the total number of cancelled bookings
total_cancellations = cancellation_by_segment['canceled_bookings'].sum()

# Calculate each segment's contribution to total cancellations
cancellation_by_segment['cancellation_contribution'] = (
    cancellation_by_segment['canceled_bookings']
    / total_cancellations
    * 100
)

# Sort segments by cancellation contribution
cancellation_by_segment_sorted = (
    cancellation_by_segment
    .sort_values(
        by='cancellation_contribution',
        ascending=False
    )
)

print('\nCancellation contribution by segment:')
print(cancellation_by_segment_sorted.round(2))


# ==============================================
# 8. PARETO ANALYSIS
# ==============================================

# Calculate cumulative cancellation contribution
cancellation_by_segment_sorted['cumulative_contribution'] = (
    cancellation_by_segment_sorted['cancellation_contribution'].cumsum()
)

print('\nCumulative cancellation contribution:')
print(
    cancellation_by_segment_sorted[
        ['cancellation_contribution', 'cumulative_contribution']
    ].round(2)
)


# ==============================================
# 9. VISUALIZATIONS
# ==============================================

# Plot cancellation rate by booking lead time
lead_time = cancellation_by_lead_time.index
cancellation_rate = cancellation_by_lead_time.values

fig, ax = plt.subplots(figsize=(10, 6))

ax.bar(
    lead_time,
    cancellation_rate,
    width=0.85,
    color='#2878A0',
    edgecolor='white',
    linewidth=0.7
)

# Add percentage labels
for index, value in enumerate(cancellation_rate):
    ax.text(
        index,
        value + 1,
        f'{value:.1f}%',
        ha='center',
        fontsize=10,
        color='#333333'
    )

# Customize chart
ax.set_title(
    'Cancellation Rate by Booking Lead Time',
    fontsize=14,
    fontweight='bold',
    pad=15
)

ax.set_xlabel('Lead Time Group', fontsize=11, labelpad=10)
ax.set_ylabel('Cancellation Rate (%)', fontsize=11, labelpad=10)

# Configure grid and axes
ax.set_axisbelow(True)
ax.grid(
    axis='y',
    linestyle='--',
    linewidth=0.7,
    alpha=0.3
)

ax.tick_params(axis='x', length=0)
ax.tick_params(axis='y', length=0)

# Remove unnecessary borders
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.set_axisbelow(True)

# Add space above bars for percentage labels
ax.set_ylim(0, max(cancellation_rate) + 10)

plt.tight_layout()

plt.savefig(
    VISUALS_PATH / 'cancellation_rate_by_lead_time.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# Plot cancellation rates by hotel and customer type
cancellation_rate_plot = (
    cancellation_by_segment['cancellation_rate']
    .unstack(level='hotel')
)

fig, ax = plt.subplots(figsize=(10, 6))

# Define consistent hotel colors
hotel_colors = {
    'City Hotel': '#219EBC',
    'Resort Hotel': '#FB8500'
}

cancellation_rate_plot.plot(
    kind='bar',
    ax=ax,
    width=0.85,
    color=[
        hotel_colors[hotel]
        for hotel in cancellation_rate_plot.columns
    ],
    edgecolor='white',
    linewidth=0.7
)

# Add percentage labels
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3,
        fontsize=9
    )

# Customize chart
ax.set_title(
    'Cancellation Rate by Hotel and Customer Type',
    fontsize=14,
    fontweight='bold',
    pad=15
)

ax.set_xlabel('Customer Type', fontsize=11, labelpad=10)
ax.set_ylabel('Cancellation Rate (%)', fontsize=11, labelpad=10)

ax.set_ylim(0, 100)
ax.tick_params(axis='x', rotation=0)

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
    VISUALS_PATH / 'cancellation_rate_by_hotel_customer_type.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# Plot cancellation rate by hotel
fig, ax = plt.subplots(figsize=(8, 5))

# Define consistent hotel colors
hotel_colors = {
    'City Hotel': '#219EBC',
    'Resort Hotel': '#FB8500'
}

cancellation_by_hotel['cancellation_rate'].plot(
    kind='bar',
    ax=ax,
    width=0.65,
    color=[
        hotel_colors[hotel]
        for hotel in cancellation_by_hotel.index
    ],
    edgecolor='white',
    linewidth=0.7
)

# Add percentage labels
for container in ax.containers:
    ax.bar_label(
        container,
        fmt='%.1f%%',
        padding=3,
        fontsize=10
    )

# Customize chart
ax.set_title(
    'Cancellation Rate by Hotel',
    fontsize=14,
    fontweight='bold',
    pad=15
    )

ax.set_xlabel('Hotel', fontsize=11, labelpad=10)
ax.set_ylabel('Cancellation Rate (%)', fontsize=11, labelpad=10)

ax.set_ylim(0, max(cancellation_by_hotel['cancellation_rate']) + 10)
ax.tick_params(axis='x', rotation=0)

# Configure grid
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
    VISUALS_PATH / 'cancellation_rate_by_hotel.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# Plot Pareto analysis of cancellations by segment
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot cancelled bookings
cancellation_by_segment_sorted['canceled_bookings'].plot(
    kind='bar',
    ax=ax1,
    color='#2878A0',
    edgecolor='white',
    linewidth=0.7,
    width=0.75
)

# Customize primary axis
ax1.set_title(
    'Pareto Analysis of Cancellations by Segment',
    fontsize=14,
    fontweight='bold',
    pad=15
)
ax1.set_xlabel('Hotel and Customer Type', fontsize=11, labelpad=10)
ax1.set_ylabel('Canceled Bookings', fontsize=11, labelpad=10)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(
    axis='y',
    linestyle='--',
    linewidth=0.7,
    alpha=0.3
)
ax1.spines['top'].set_visible(False)
ax1.set_axisbelow(True)

# Add cumulative contribution line
ax2 = ax1.twinx()

ax2.plot(
    range(len(cancellation_by_segment_sorted)),
    cancellation_by_segment_sorted['cumulative_contribution'],
    color="#C611A8",
    marker='o',
    markersize=6,
    linewidth=2,
    label='Cumulative Contribution'
)

# Add 80% reference line
ax2.axhline(
    y=80,
    color='#6C757D',
    linestyle='--',
    linewidth=1.5,
    label='80% Reference'
)

ax2.set_ylabel('Cumulative Contribution (%)', fontsize=11, labelpad=10)
ax2.set_ylim(0, 110)
ax2.spines['top'].set_visible(False)

# Combine legends from both axes
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

ax2.legend(
    handles1 + handles2,
    ['Canceled Bookings', 'Cumulative Contriburion', '80% Reference'],
    loc='upper center',
    bbox_to_anchor=(0.5, 0.99),
    ncol=3,
    frameon=False,
    fontsize=9
)

plt.xticks(rotation=45, ha='right')

# Adjust figure layout
fig.subplots_adjust(
    left=0.10,
    right=0.90,
    bottom=0.10,
    top=0.82
)

plt.savefig(
    VISUALS_PATH / 'cancellation_pareto_analysis.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


print('\nCancellation analysis completed successfully.')