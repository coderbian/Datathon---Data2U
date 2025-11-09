"""
Utilities for Data Preparation - Walmart Sales Forecast
Chứa các hàm helper để xử lý dữ liệu
"""

import pandas as pd
import numpy as np
from datetime import timedelta


def get_us_holidays(year):
    """
    Tính các ngày lễ Mỹ cho một năm
    
    Returns:
        dict: {date_string: (holiday_name, impact_score)}
    """
    holidays = {}
    
    # New Year's Day
    holidays[f'{year}-01-01'] = ('New Years Day', 1)
    
    # Super Bowl (Chủ nhật đầu tháng 2)
    super_bowl_dates = {2010: '2010-02-07', 2011: '2011-02-06', 2012: '2012-02-05'}
    if year in super_bowl_dates:
        holidays[super_bowl_dates[year]] = ('Super Bowl', 3)
    
    # Presidents Day
    presidents_day_dates = {2010: '2010-02-15', 2011: '2011-02-21', 2012: '2012-02-20'}
    if year in presidents_day_dates:
        holidays[presidents_day_dates[year]] = ('Presidents Day', 1)
    
    # Memorial Day
    memorial_day_dates = {2010: '2010-05-31', 2011: '2011-05-30', 2012: '2012-05-28'}
    if year in memorial_day_dates:
        holidays[memorial_day_dates[year]] = ('Memorial Day', 1)
    
    # Independence Day
    holidays[f'{year}-07-04'] = ('Independence Day', 1)
    
    # Labor Day
    labor_day_dates = {2010: '2010-09-06', 2011: '2011-09-05', 2012: '2012-09-03'}
    if year in labor_day_dates:
        holidays[labor_day_dates[year]] = ('Labor Day', 3)
    
    # Thanksgiving
    thanksgiving_dates = {2010: '2010-11-25', 2011: '2011-11-24', 2012: '2012-11-22'}
    if year in thanksgiving_dates:
        holidays[thanksgiving_dates[year]] = ('Thanksgiving', 5)
    
    # Christmas
    holidays[f'{year}-12-25'] = ('Christmas', 5)
    holidays[f'{year}-12-24'] = ('Christmas Eve', 3)
    
    return holidays


def get_week_end_date(date):
    """
    Tính WeekEndDate (Thứ Sáu cuối tuần) cho một ngày
    
    Args:
        date: pandas Timestamp
        
    Returns:
        pandas Timestamp: Thứ Sáu cuối tuần
    """
    weekday = date.weekday()  # 0=Monday, 4=Friday, 6=Sunday
    if weekday == 4:  # Friday
        return date
    elif weekday == 5:  # Saturday
        return date + timedelta(days=6)
    elif weekday == 6:  # Sunday
        return date + timedelta(days=5)
    else:  # Monday-Thursday
        return date + timedelta(days=4-weekday)


def is_tax_refund_season(date):
    """
    Kiểm tra xem ngày có thuộc mùa hoàn thuế không (15/02 - 15/04)
    
    Args:
        date: pandas Timestamp hoặc datetime
        
    Returns:
        int: 1 nếu thuộc mùa hoàn thuế, 0 nếu không
    """
    month = date.month
    day = date.day
    if month == 2 and day >= 15:
        return 1
    elif month == 3:
        return 1
    elif month == 4 and day <= 15:
        return 1
    return 0


def calculate_weeks_since_payday(group):
    """
    Tính số tuần kể từ payday gần nhất cho mỗi group (Store, Dept)
    
    Args:
        group: DataFrame group từ groupby
        
    Returns:
        pd.Series: Số tuần kể từ payday gần nhất
    """
    weeks_since = []
    last_payday_week = None
    
    for idx, row in group.iterrows():
        if row['is_semimonthly_payweek'] == 1:
            last_payday_week = row['WeekEndDate']
            weeks_since.append(0)
        elif last_payday_week is not None:
            weeks_diff = (row['WeekEndDate'] - last_payday_week).days // 7
            weeks_since.append(weeks_diff)
        else:
            weeks_since.append(np.nan)
    
    return pd.Series(weeks_since, index=group.index)


def piecewise_decay(weeks):
    """
    Tính giá trị decay theo piecewise function
    
    Args:
        weeks: Số tuần
        
    Returns:
        float: Giá trị decay
    """
    if weeks == 0:
        return 1.0
    elif weeks == 1:
        return 0.7
    elif weeks >= 2:
        return 0.4
    else:
        return 0.0


def get_christmas_date(year):
    """Trả về ngày Giáng sinh"""
    return pd.Timestamp(f'{year}-12-25')


def get_thanksgiving_date(year):
    """
    Tính ngày Thanksgiving (Thứ 5 thứ 4 của tháng 11)
    
    Args:
        year: Năm
        
    Returns:
        pandas Timestamp: Ngày Thanksgiving
    """
    nov_1 = pd.Timestamp(f'{year}-11-01')
    first_thursday = nov_1 + timedelta(days=(3 - nov_1.weekday()) % 7)
    if first_thursday.day > 7:
        first_thursday = first_thursday - timedelta(days=7)
    thanksgiving = first_thursday + timedelta(days=21)
    return thanksgiving


def calculate_weeks_until_holiday(date, holiday_func):
    """
    Tính số tuần cho đến lễ tiếp theo
    
    Args:
        date: pandas Timestamp
        holiday_func: Hàm tính ngày lễ (get_christmas_date hoặc get_thanksgiving_date)
        
    Returns:
        int: Số tuần cho đến lễ tiếp theo
    """
    year = date.year
    holiday_date = holiday_func(year)
    
    # Nếu lễ đã qua trong năm này, tính lễ năm sau
    if date > holiday_date:
        holiday_date = holiday_func(year + 1)
    
    weeks_diff = (holiday_date - date).days // 7
    return weeks_diff

