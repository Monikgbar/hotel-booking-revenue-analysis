from pathlib import Path
import pandas as pd


def load_and_prepare_data():

    # Define project paths
    project_root = Path(__file__).resolve().parent.parent
    data_path = project_root / 'data' / 'raw' / 'hotel_bookings.csv'

    # Load the original dataset
    df = pd.read_csv(data_path)

    # Create a working copy
    df_analysis = df.copy()

    # Calculate total nights
    df_analysis['total_nights'] = (
        df_analysis['stays_in_weekend_nights']
        + df_analysis['stays_in_week_nights']
    )

    # Calculate estimated revenue
    df_analysis['estimated_revenue'] = (
        df_analysis['adr'] * df_analysis['total_nights']
    )

    # Create arrival date
    df_analysis['arrival_date'] = pd.to_datetime(
        df_analysis['arrival_date_year'].astype(str)
        + '-'
        + df_analysis['arrival_date_month']
        + '-'
        + df_analysis['arrival_date_day_of_month'].astype(str),
        format='%Y-%B-%d',
        errors='coerce'
    )

    # Extract year and month
    df_analysis['arrival_year'] = df_analysis['arrival_date'].dt.year
    df_analysis['arrival_month'] = df_analysis['arrival_date'].dt.month

    # Create a year-month column 
    df_analysis['arrival_year_month'] = (
        df_analysis['arrival_date'].dt.to_period('M')
    )

    # Identify exact duplicatee rows
    df_analysis['is_duplicate'] = df_analysis.duplicated(keep=False)

    return df, df_analysis