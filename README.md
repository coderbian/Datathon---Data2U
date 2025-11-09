# Walmart Sales Forecast - Datathon

Dự án phân tích và dự đoán doanh số bán hàng của Walmart sử dụng dữ liệu lịch sử từ 45 cửa hàng và 81 phòng ban trong giai đoạn 2010-2012.

## 📊 Dataset

**Source**: [Kaggle - Walmart Sales Forecast](https://www.kaggle.com/datasets/aslanahmedov/walmart-sales-forecast/data)

**Data Files**:
- `train.csv` (421K rows): Dữ liệu doanh số hàng tuần theo Store và Department
- `stores.csv` (45 rows): Thông tin cửa hàng (Type A/B/C, Size)
- `features.csv` (8K rows): Các yếu tố ngoại vi (Temperature, Fuel_Price, MarkDowns, CPI, Unemployment)
- `test.csv`: Dữ liệu test để dự đoán

## 🎯 Mục tiêu

- Phân tích dữ liệu và tìm patterns, seasonality
- Xây dựng features từ dữ liệu (Payday Pulse, Holiday effects, Lag/Rolling)
- Dự đoán Weekly Sales sử dụng Time Series Forecasting
- Đánh giá model bằng WMAE (Weighted Mean Absolute Error)

## 📁 Cấu trúc Project

```
.
├── data/                           # Raw datasets
│   ├── train.csv
│   ├── stores.csv
│   ├── features.csv
│   └── test.csv
├── data/processed/                 # Processed datasets
│   ├── df_main_weekly.csv
│   ├── df_events_daily.csv
│   ├── df_feature_calendar_weekly.csv
│   └── df_final_for_model.csv
├── notebooks/                      # Jupyter notebooks
│   ├── 00_Reprocessing_Main_Data.ipynb
│   └── 01_Data_Preparation_Complete.ipynb
└── README.md
```

## 🛠️ Tech Stack

- **Python 3.10+**
- **Libraries**: pandas, numpy, matplotlib, seaborn, plotly, scikit-learn, statsmodels

## 🚀 Quick Start

1. **Clone repository**
```bash
git clone <repo-url>
cd Datathon
```

2. **Install dependencies**
```bash
pip install pandas numpy matplotlib seaborn plotly scikit-learn statsmodels
```

3. **Download dataset**
- Tải dataset từ [Kaggle](https://www.kaggle.com/datasets/aslanahmedov/walmart-sales-forecast/data)
- Giải nén vào thư mục `data/`

4. **Run notebooks**
```bash
jupyter notebook
```

## 📈 Key Features

**Data Preparation**:
- Merge và làm sạch dữ liệu
- Xử lý missing values (MarkDowns)
- Xử lý negative sales (returns)

**Feature Engineering**:
- **Payday Pulse**: SNAP windows, semimonthly payday, tax refund season
- **Holiday Effects**: Christmas, Thanksgiving với countdown và impact
- **Lag Features**: t-1, t-2, t-4, t-52 (year-over-year)
- **Rolling Statistics**: 4-week mean và std
- **Interactions**: SNAP×Type, Holiday×Impact, Tax×Temperature

## 📝 Notebooks

1. **00_Reprocessing_Main_Data.ipynb**: EDA ban đầu và phân tích dữ liệu
2. **01_Data_Preparation_Complete.ipynb**: Data preparation và feature engineering hoàn chỉnh

## 📊 Insights

- **Seasonality**: Doanh số tăng mạnh vào Nov/Dec (Thanksgiving, Christmas) và Feb/Mar (Tax Refund)
- **Payday Effect**: Doanh số cao hơn vào đầu tháng và giữa tháng (payday periods)
- **Holiday Impact**: Các ngày lễ lớn có impact score từ 1-5

---

**Author**: Datathon Team  
**Last Updated**: November 2025

