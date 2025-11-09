"""
Data Preparation Complete - Walmart Sales Forecast

Script này thực hiện toàn bộ các bước chuẩn bị dữ liệu theo file "[Các bước làm tham khảo tiếp theo]".

Cấu trúc:
    GIAI ĐOẠN 1: CHUẨN BỊ DỮ LIỆU
        1.1. Tạo df_main_weekly
        1.2. Tạo df_events_daily  
        1.3. Tạo df_feature_calendar_weekly
    
    GIAI ĐOẠN 2: FEATURE ENGINEERING
        2.1. Merge & Kiểm tra
        2.2. Tạo Features "Payday Pulse"
        2.3. Tạo Features "Holiday"
        2.4. Tạo Features "Lag/Rolling"
        2.5. Tạo Features "Interaction"
    
    GIAI ĐOẠN 3: LƯU CÁC FILE OUTPUT

Author: Data Science Team
Date: 2025
"""

import pandas as pd
import numpy as np
import warnings
import os
from datetime import datetime, timedelta

# Import helper functions
from data_prep_utils import (
    get_us_holidays, get_week_end_date, is_tax_refund_season,
    calculate_weeks_since_payday, piecewise_decay,
    get_christmas_date, get_thanksgiving_date, calculate_weeks_until_holiday
)

warnings.filterwarnings('ignore')

# Cấu hình pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# ============================================================================
# CẤU HÌNH
# ============================================================================

# Đường dẫn đến data (có thể thay đổi)
DATA_PATH = '../data/'
PROCESSED_PATH = '../data/processed/'

print("✅ Libraries imported successfully!")
print(f"📁 Data path: {DATA_PATH}")
print(f"📁 Processed path: {PROCESSED_PATH}\n")

# ============================================================================
# GIAI ĐOẠN 1: CHUẨN BỊ DỮ LIỆU
# ============================================================================

print("="*80)
print("GIAI ĐOẠN 1: CHUẨN BỊ DỮ LIỆU")
print("="*80)

# ----------------------------------------------------------------------------
# 1.1. TẠO DF_MAIN_WEEKLY
# ----------------------------------------------------------------------------

print("\n[1.1] TẠO DF_MAIN_WEEKLY")
print("-" * 80)

# Load các datasets
print("🔄 Loading datasets...")
train_df = pd.read_csv(DATA_PATH + 'train.csv')
stores_df = pd.read_csv(DATA_PATH + 'stores.csv')
features_df = pd.read_csv(DATA_PATH + 'features.csv')

print(f"📈 Train data shape: {train_df.shape}")
print(f"🏪 Stores data shape: {stores_df.shape}")
print(f"🌡️ Features data shape: {features_df.shape}")

# Merge 3 files
print("\n🔄 Merging datasets...")
df_main = pd.merge(train_df, stores_df, on='Store', how='left')
df_main = pd.merge(df_main, features_df, on=['Store', 'Date'], how='left', suffixes=('', '_features'))

# Xử lý duplicate IsHoliday columns
if 'IsHoliday_features' in df_main.columns:
    df_main = df_main.drop(columns=['IsHoliday_features'])

print(f"✅ Merged data shape: {df_main.shape}")

# Chuyển đổi Date sang datetime và đổi tên thành WeekEndDate
df_main['Date'] = pd.to_datetime(df_main['Date'])
df_main = df_main.rename(columns={'Date': 'WeekEndDate'})

print(f"📅 Time range: {df_main['WeekEndDate'].min()} to {df_main['WeekEndDate'].max()}")

# Xử lý MarkDowns
markdown_cols = ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5']
for col in markdown_cols:
    df_main[col] = df_main[col].fillna(0)

df_main['md_missing_any'] = ((df_main[markdown_cols] == 0).all(axis=1)).astype(int)
df_main['md_sum'] = df_main[markdown_cols].sum(axis=1)

print(f"📊 MarkDowns missing (all zeros): {df_main['md_missing_any'].sum()} records")

# Xử lý Weekly_Sales âm
df_main['returns_flag'] = (df_main['Weekly_Sales'] < 0).astype(int)
df_main['returns_abs'] = df_main['Weekly_Sales'].apply(lambda x: abs(x) if x < 0 else 0)
df_main['Weekly_Sales'] = df_main['Weekly_Sales'].clip(lower=0)

print(f"📊 Negative sales processed: {df_main['returns_flag'].sum()} records")

# Validation
assert df_main['WeekEndDate'].notna().all(), "WeekEndDate has NA!"
assert df_main['Store'].notna().all(), "Store has NA!"
assert df_main['Dept'].notna().all(), "Dept has NA!"
assert (df_main['Weekly_Sales'] >= 0).all(), "Weekly_Sales still negative!"

df_main_weekly = df_main.copy()
print(f"✅ df_main_weekly created! Shape: {df_main_weekly.shape}")

# ----------------------------------------------------------------------------
# 1.2. TẠO DF_EVENTS_DAILY
# ----------------------------------------------------------------------------

print("\n[1.2] TẠO DF_EVENTS_DAILY")
print("-" * 80)

# Tạo lịch daily
min_date = df_main_weekly['WeekEndDate'].min()
max_date = df_main_weekly['WeekEndDate'].max()

date_range = pd.date_range(start=min_date, end=max_date, freq='D')
df_events_daily = pd.DataFrame({'Date': date_range})

print(f"📅 Total days: {len(df_events_daily)}")

# Thêm features Payday
df_events_daily['is_snap_window_1'] = (df_events_daily['Date'].dt.day <= 10).astype(int)
df_events_daily['is_snap_window_2'] = ((df_events_daily['Date'].dt.day >= 11) & 
                                       (df_events_daily['Date'].dt.day <= 20)).astype(int)
df_events_daily['is_semimonthly_payday'] = ((df_events_daily['Date'].dt.day == 15) | 
                                           (df_events_daily['Date'].dt.is_month_end)).astype(int)
df_events_daily['is_tax_refund_season'] = df_events_daily['Date'].apply(is_tax_refund_season)

print(f"✅ Payday features added")

# Tạo lịch Holiday events
all_holidays = {}
for year in [2010, 2011, 2012]:
    all_holidays.update(get_us_holidays(year))

df_events_daily['HolidayName'] = df_events_daily['Date'].dt.strftime('%Y-%m-%d').map(
    lambda x: all_holidays.get(x, ('', 0))[0] if x in all_holidays else ''
)
df_events_daily['holiday_impact'] = df_events_daily['Date'].dt.strftime('%Y-%m-%d').map(
    lambda x: all_holidays.get(x, ('', 0))[1] if x in all_holidays else 0
)

print(f"✅ Holiday events added: {(df_events_daily['HolidayName'] != '').sum()} holidays")

# ----------------------------------------------------------------------------
# 1.3. TẠO DF_FEATURE_CALENDAR_WEEKLY
# ----------------------------------------------------------------------------

print("\n[1.3] TẠO DF_FEATURE_CALENDAR_WEEKLY")
print("-" * 80)

# Thêm WeekEndDate vào df_events_daily
df_events_daily['WeekEndDate'] = df_events_daily['Date'].apply(get_week_end_date)

# Groupby WeekEndDate và aggregate
df_feature_calendar_weekly = df_events_daily.groupby('WeekEndDate').agg({
    'is_snap_window_1': lambda x: 1 if x.sum() > 0 else 0,
    'is_snap_window_2': lambda x: 1 if x.sum() > 0 else 0,
    'is_semimonthly_payday': lambda x: 1 if x.sum() > 0 else 0,
    'is_tax_refund_season': lambda x: 1 if x.sum() > 0 else 0,
    'holiday_impact': 'max',
    'HolidayName': lambda x: x[x != ''].iloc[0] if (x != '').any() else ''
}).reset_index()

# Đổi tên cột
df_feature_calendar_weekly = df_feature_calendar_weekly.rename(columns={
    'is_snap_window_1': 'is_snap_window_1_week',
    'is_snap_window_2': 'is_snap_window_2_week',
    'is_semimonthly_payday': 'is_semimonthly_payweek',
    'is_tax_refund_season': 'is_tax_refund_season_week',
    'holiday_impact': 'holiday_impact_week',
    'HolidayName': 'holiday_name_week'
})

print(f"✅ df_feature_calendar_weekly created! Shape: {df_feature_calendar_weekly.shape}")

# ============================================================================
# GIAI ĐOẠN 2: FEATURE ENGINEERING
# ============================================================================

print("\n" + "="*80)
print("GIAI ĐOẠN 2: FEATURE ENGINEERING")
print("="*80)

# ----------------------------------------------------------------------------
# 2.1. MERGE & KIỂM TRA
# ----------------------------------------------------------------------------

print("\n[2.1] MERGE & KIỂM TRA")
print("-" * 80)

df_final = pd.merge(df_main_weekly, df_feature_calendar_weekly, on='WeekEndDate', how='left')

# Fillna
fill_cols = ['is_snap_window_1_week', 'is_snap_window_2_week', 'is_semimonthly_payweek', 
             'is_tax_refund_season_week', 'holiday_impact_week']
for col in fill_cols:
    df_final[col] = df_final[col].fillna(0)

df_final['holiday_name_week'] = df_final['holiday_name_week'].fillna('')

# Sanity check
duplicates = df_final.groupby(['Store', 'Dept', 'WeekEndDate']).size()
if (duplicates > 1).any():
    print(f"⚠️ Warning: Found {((duplicates > 1).sum())} duplicates!")
else:
    print("✅ No duplicates found!")

print(f"✅ Merged! Shape: {df_final.shape}")

# ----------------------------------------------------------------------------
# 2.2. TẠO FEATURES "PAYDAY PULSE"
# ----------------------------------------------------------------------------

print("\n[2.2] TẠO FEATURES PAYDAY PULSE")
print("-" * 80)

df_final = df_final.sort_values(['Store', 'Dept', 'WeekEndDate']).reset_index(drop=True)

df_final['weeks_since_payday_15_eom'] = df_final.groupby(['Store', 'Dept']).apply(
    calculate_weeks_since_payday, include_groups=False
).reset_index(level=[0, 1], drop=True)

df_final['weeks_since_payday_15_eom'] = df_final['weeks_since_payday_15_eom'].fillna(999)

df_final['payday_decay_exp'] = np.exp(-0.25 * df_final['weeks_since_payday_15_eom'])
df_final['payday_decay_piecewise'] = df_final['weeks_since_payday_15_eom'].apply(piecewise_decay)

print("✅ Payday Pulse features created!")

# ----------------------------------------------------------------------------
# 2.3. TẠO FEATURES "HOLIDAY"
# ----------------------------------------------------------------------------

print("\n[2.3] TẠO FEATURES HOLIDAY")
print("-" * 80)

df_final['weeks_until_christmas'] = df_final['WeekEndDate'].apply(
    lambda x: calculate_weeks_until_holiday(x, get_christmas_date)
)
df_final['weeks_until_thanksgiving'] = df_final['WeekEndDate'].apply(
    lambda x: calculate_weeks_until_holiday(x, get_thanksgiving_date)
)

df_final['is_pre_christmas_window_week'] = (df_final['weeks_until_christmas'] <= 3).astype(int)
df_final['is_pre_thanksgiving_window_week'] = (df_final['weeks_until_thanksgiving'] <= 2).astype(int)

print(f"✅ Holiday features created!")
print(f"   Pre-Christmas weeks: {df_final['is_pre_christmas_window_week'].sum()}")
print(f"   Pre-Thanksgiving weeks: {df_final['is_pre_thanksgiving_window_week'].sum()}")

# ----------------------------------------------------------------------------
# 2.4. TẠO FEATURES "LAG/ROLLING"
# ----------------------------------------------------------------------------

print("\n[2.4] TẠO FEATURES LAG/ROLLING")
print("-" * 80)

df_final = df_final.sort_values(['Store', 'Dept', 'WeekEndDate']).reset_index(drop=True)

# Lag features
df_final['lag_sales_t_52'] = df_final.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(52)
df_final['lag_sales_t_1'] = df_final.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(1)
df_final['lag_sales_t_2'] = df_final.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(2)
df_final['lag_sales_t_4'] = df_final.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(4)

# Rolling features
df_final['rolling_mean_sales_4_weeks'] = df_final.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(1).rolling(window=4, min_periods=1).mean().reset_index(level=[0,1], drop=True)
df_final['rolling_std_sales_4_weeks'] = df_final.groupby(['Store', 'Dept'])['Weekly_Sales'].shift(1).rolling(window=4, min_periods=1).std().reset_index(level=[0,1], drop=True)

print("✅ Lag/Rolling features created!")

# ----------------------------------------------------------------------------
# 2.5. TẠO FEATURES "INTERACTION"
# ----------------------------------------------------------------------------

print("\n[2.5] TẠO FEATURES INTERACTION")
print("-" * 80)

df_final['interact_snap_x_type_c'] = df_final['is_snap_window_1_week'] * (df_final['Type'] == 'C').astype(int)
df_final['interact_holiday_x_impact'] = df_final['is_pre_christmas_window_week'] * df_final['holiday_impact_week']
df_final['interact_tax_x_temp'] = df_final['is_tax_refund_season_week'] * df_final['Temperature']

print("✅ Interaction features created!")

# ============================================================================
# GIAI ĐOẠN 3: LƯU CÁC FILE OUTPUT
# ============================================================================

print("\n" + "="*80)
print("GIAI ĐOẠN 3: LƯU CÁC FILE OUTPUT")
print("="*80)

os.makedirs(PROCESSED_PATH, exist_ok=True)

# Lưu các file
df_main_weekly.to_csv(PROCESSED_PATH + 'df_main_weekly.csv', index=False)
print(f"✅ Saved: df_main_weekly.csv ({df_main_weekly.shape})")

df_events_daily.to_csv(PROCESSED_PATH + 'df_events_daily.csv', index=False)
print(f"✅ Saved: df_events_daily.csv ({df_events_daily.shape})")

df_feature_calendar_weekly.to_csv(PROCESSED_PATH + 'df_feature_calendar_weekly.csv', index=False)
print(f"✅ Saved: df_feature_calendar_weekly.csv ({df_feature_calendar_weekly.shape})")

df_final.to_csv(PROCESSED_PATH + 'df_final_for_model.csv', index=False)
print(f"✅ Saved: df_final_for_model.csv ({df_final.shape})")

# ============================================================================
# TÓM TẮT KẾT QUẢ
# ============================================================================

print("\n" + "="*80)
print("📊 TÓM TẮT KẾT QUẢ")
print("="*80)

print(f"\n📊 Final dataset shape: {df_final.shape}")
print(f"📊 Total columns: {len(df_final.columns)}")
print(f"📅 Time range: {df_final['WeekEndDate'].min()} to {df_final['WeekEndDate'].max()}")
print(f"🏪 Stores: {df_final['Store'].nunique()}, Departments: {df_final['Dept'].nunique()}")

print(f"\n💰 Weekly Sales statistics:")
print(df_final['Weekly_Sales'].describe())

print(f"\n📋 All columns ({len(df_final.columns)}):")
for i, col in enumerate(df_final.columns, 1):
    print(f"  {i:2d}. {col}")

print("\n" + "="*80)
print("✅ DATA PREPARATION COMPLETED SUCCESSFULLY!")
print("="*80)
