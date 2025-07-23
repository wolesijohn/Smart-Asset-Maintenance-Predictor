

import pandas as pd
import numpy as np
import os

try:
    print("Loading files...")
    equipment_data = pd.read_csv('Machine-Data/equipment_data.csv', parse_dates=['Purchase_Date'])
    print("Loaded equipment_data:", equipment_data.columns)
    usage_log_df = pd.read_csv('Machine-Data/usage_log.csv', parse_dates=['Date'])
    print("Loaded usage_log_df:", usage_log_df.columns)
    maintenance_log_df = pd.read_csv('Machine-Data/maintenance_log.csv', parse_dates=['Date'])
    print("Loaded maintenance_log_df:", maintenance_log_df.columns)
    failure_log_df = pd.read_csv('Machine-Data/failure_log.csv', parse_dates=['Failure_Date'])
    print("Loaded failure_log_df:", failure_log_df.columns)

    print("Cleaning usage log...")
    usage_log_df['Operating_Hours'] = usage_log_df['Operating_Hours'].clip(lower=0, upper=24)

    print("Aggregating usage statistics...")
    usage_summary = usage_log_df.groupby('Equipment_ID').agg({
        'Operating_Hours': ['mean', 'sum', 'std']
    }).reset_index()
    usage_summary.columns = ['Equipment_ID', 'Avg_Usage_Hours', 'Total_Usage_Hours', 'Usage_Std']

    print("Extracting latest maintenance...")
    latest_maintenance = maintenance_log_df.groupby('Equipment_ID').apply(
        lambda x: x.sort_values('Date').tail(1)
    ).reset_index(drop=True)
    latest_maintenance = latest_maintenance[['Equipment_ID', 'Date']].rename(columns={'Date': 'Last_Maintenance_Date'})

    print("Aggregating failure data...")
    failure_summary = failure_log_df.groupby('Equipment_ID').agg({'Failure_Date': 'count'}).reset_index()
    failure_summary['Failure_Flag'] = (failure_summary['Failure_Date'] > 0).astype(int)
    failure_summary = failure_summary[['Equipment_ID', 'Failure_Flag']]

    print("Merging dataframes...")
    # Modified to include Type, Manufacturer, and Location
    merged_df = equipment_data[['Equipment_ID', 'Type', 'Manufacturer', 'Location', 'Purchase_Date']].merge(
        usage_summary, on='Equipment_ID', how='left')
    merged_df = merged_df.merge(latest_maintenance, on='Equipment_ID', how='left')
    merged_df = merged_df.merge(failure_summary, on='Equipment_ID', how='left').fillna({'Failure_Flag': 0})

    print("Performing feature engineering...")
    reference_date = pd.to_datetime('today').normalize()
    merged_df['Days_Since_Last_Maintenance'] = (reference_date - merged_df['Last_Maintenance_Date']).dt.days.fillna(-1)
    merged_df['Days_Since_Purchase'] = (reference_date - merged_df['Purchase_Date']).dt.days.fillna(-1)

    print("Saving output...")
    output_path = 'Machine-Data/feature_engineered_data.csv'
    os.makedirs('Machine-Data/', exist_ok=True)
    merged_df.to_csv(output_path, index=False)
    print(f"✅ Feature-engineered dataset saved to: {output_path}")

except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise