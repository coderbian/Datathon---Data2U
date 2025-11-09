# EDA và Tiền xử lý Dữ liệu - Phần Đã Hoàn Thành

## Tổng quan
File này mô tả những gì đã được thực hiện trong notebook `00_Reprocessing_Main_Data.ipynb`.

## Phần Đã Hoàn Thành

### 1. Load và Khám phá Dữ liệu Cơ bản
- ✅ Đọc file `train.csv` (chưa merge với stores.csv và features.csv)
- ✅ Kiểm tra kích thước dữ liệu: 4,420 bản ghi, 5 cột
- ✅ Kiểm tra thông tin cột và kiểu dữ liệu
- ✅ Thống kê mô tả cơ bản

### 2. Chuyển đổi Kiểu Dữ liệu
- ✅ Chuyển cột `Date` từ object sang datetime: `pd.to_datetime(df['Date'])`
- ✅ Chuyển cột `IsHoliday` sang boolean
- ✅ Thêm các cột thời gian: `Year`, `Month`, `Week` từ Date

### 3. Phân tích Weekly_Sales Âm
- ✅ Phát hiện: Có **1,285** bản ghi có Weekly_Sales < 0 (giá trị nhỏ nhất: -4988.94)
- ✅ Nhận định: Đây là dữ liệu "Trả hàng" (Product Returns)
- ⚠️ **Chưa xử lý**: Chưa clip về 0 hoặc tạo features returns_flag, returns_abs

### 4. Phân tích Theo Thời Gian
- ✅ Phân tích phạm vi thời gian: Từ 05/02/2010 đến 26/10/2012
- ✅ Phân tích doanh thu theo tháng:
  - Tháng 11 & 12: Đỉnh cao nhất (Thanksgiving & Christmas)
  - Tháng 2 & 3: Đỉnh thứ hai (Tax Refund Season)
  - Tháng 1 & 9: Thấp nhất
- ✅ So sánh doanh thu theo tháng giữa các năm (2010, 2011, 2012)
- ✅ Phân tích chu kỳ doanh thu theo ngày trong tháng
  - Tạo cột `day_of_month`
  - Tạo cột `is_payday_period` (ngày 25-31 hoặc 1-5)

### 5. Phân tích Theo Ngày Lễ
- ✅ So sánh doanh thu trung bình giữa ngày lễ và không lễ
- ✅ Phân tích phân phối doanh thu theo IsHoliday
- ✅ Visualization: Pie chart và boxplot

### 6. Visualizations
- ✅ Histogram phân phối Weekly_Sales
- ✅ Biểu đồ doanh thu trung bình theo tháng
- ✅ Biểu đồ so sánh năm
- ✅ Biểu đồ chu kỳ doanh thu theo ngày trong tháng

## Phần Chưa Hoàn Thành

### 1. Merge Dữ liệu
- ❌ Chưa merge `train.csv` với `stores.csv`
- ❌ Chưa merge với `features.csv`
- ❌ Chưa xử lý các cột MarkDown1-5 (fillna)

### 2. Xử lý Weekly_Sales Âm
- ❌ Chưa tạo `returns_flag` và `returns_abs`
- ❌ Chưa clip Weekly_Sales về >= 0

### 3. Tạo Lịch Payday
- ❌ Chưa tạo `df_payday_calendar` hoặc `df_events_daily`
- ❌ Chưa tạo các features: `is_snap_window`, `is_semimonthly_payday`, `is_tax_refund_season`

### 4. Tạo Lịch Holiday Events
- ❌ Chưa tạo `df_holiday_events` với các ngày lễ cụ thể
- ❌ Chưa map các ngày lễ Mỹ (2010-2012)

### 5. Feature Engineering
- ❌ Chưa tạo features Payday Pulse (proximity, decay)
- ❌ Chưa tạo features Holiday (countdown, window)
- ❌ Chưa tạo features Lag/Rolling
- ❌ Chưa tạo features Interaction

## Ghi chú
- Notebook hiện tại chỉ tập trung vào EDA cơ bản trên `train.csv`
- Cần thực hiện các bước tiếp theo theo file "[Các bước làm tham khảo tiếp theo]"
