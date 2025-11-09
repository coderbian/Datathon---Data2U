# Các Bước Làm Tham Khảo Tiếp Theo - EDA và Tiền xử lý Dữ liệu

## Giai đoạn 1: Chuẩn bị Dữ liệu (Nâng cấp "Tuần-theo-Tuần")

Mục tiêu của giai đoạn này là tạo ra các "nguyên liệu thô" đã được chuẩn hóa. Thay vì merge các file daily (ngày) lộn xộn, chúng ta sẽ tạo ra một bộ feature theo tuần (`df_feature_calendar_weekly`) để join (ghép) vào `df_main`.

---

### 1.1. Mục tiêu 1: Tạo DataFrame gốc (df_main_weekly)

**Tính chất:** File "sự thật" (ground truth), đã được làm sạch và chuẩn hóa trục thời gian.

**Các bước thực hiện:**

1. **Hợp nhất & Chuẩn hóa Tuần:**
   - Merge 3 file: `train.csv`, `stores.csv`, `features.csv`
   - Kiểm tra (Validate): Cột `Date` trong `train.csv` và `features.csv` thực chất đã là ngày Thứ Sáu (Friday) kết thúc tuần
   - Đổi tên cột `Date` → `WeekEndDate` để làm "chìa khóa" (join key) chính

2. **Xử lý MarkDowns (Nâng cấp):**
   - `fillna(0)` cho 5 cột `MarkDown1-5`
   - Tạo 2 feature cờ (flag) mới:
     - `md_missing_any`: = 1 nếu cả 5 cột MarkDown đều là 0 (hoặc NA)
     - `md_sum`: Tính tổng giá trị của `MarkDown1` → `MarkDown5`

3. **Xử lý Sales âm (Nâng cấp):**
   - Tạo 2 feature mới trước khi clip:
     - `returns_flag`: = 1 nếu `Weekly_Sales` < 0, ngược lại = 0
     - `returns_abs`: Lấy `abs(Weekly_Sales)` nếu < 0, ngược lại = 0
   - Sau đó mới clip: `df_main['Weekly_Sales'] = df_main['Weekly_Sales'].clip(lower=0)`

4. **Kiểm tra Chất lượng (Nâng cấp):**
   - Kiểm tra (assert) các điều kiện:
     - `WeekEndDate` không bị NA
     - `Store` và `Dept` không bị NA
     - `Weekly_Sales` (sau clip) không âm

**Thành phẩm:** File `df_main_weekly.csv` (hoặc `.parquet`) sẵn sàng để merge.

---

### 1.2. Mục tiêu 2: Tạo Lịch Sự kiện (df_events_daily)

**Tính chất:** Lịch vạn niên (daily) chứa tất cả sự kiện Payday và Lễ của Mỹ.

**Các bước thực hiện:**

1. **Tạo Lịch gốc:**
   - Tạo DataFrame 1 cột `Date` chạy hàng ngày (daily) từ `min_date` đến `max_date` của `df_main_weekly`

2. **Thêm Giả định Payday (Nâng cấp SNAP):**
   - `is_snap_window_1`: = 1 nếu `Date.day` ∈ [1, 10]
   - `is_snap_window_2`: = 1 nếu `Date.day` ∈ [11, 20] (thử nghiệm xem cửa sổ nào hiệu quả hơn)
   - `is_semimonthly_payday`: = 1 nếu `Date.day == 15` HOẶC `Date.is_month_end == True`
   - `is_tax_refund_season`: = 1 nếu `Date` ∈ [15/02 - 15/04] hàng năm

3. **Thêm Giả định Lễ (Nâng cấp Holiday Score):**
   - Tự tạo 1 file csv (hoặc dict trong code) map `Date` → `HolidayName` (Ví dụ: 2010-02-14, Super Bowl)
   - Thêm cột `holiday_impact` (điểm 1-5):
     - **5 điểm** (Lễ mua sắm lớn): Thanksgiving, Christmas
     - **3 điểm** (Lễ có ảnh hưởng): Super Bowl, Labor Day
     - **1 điểm** (Lễ nhỏ)

**Thành phẩm:** File `df_events_daily.csv` rất chi tiết (khoảng ~1000 dòng).

---

### 1.3. Mục tiêu 3: Gộp Lịch theo Tuần (df_feature_calendar_weekly)

**Tính chất:** File "vũ khí" chứa tất cả "extra data" đã được chuẩn hóa theo `WeekEndDate` (Thứ Sáu).

**Các bước thực hiện:**

1. **Tạo WeekEndDate:**
   - Thêm một cột `WeekEndDate` vào file `df_events_daily`
   - Ví dụ: `Date` '2010-02-06' (Thứ Bảy) sẽ thuộc `WeekEndDate` '2010-02-12' (Thứ Sáu tới)

2. **Gộp nhóm (Groupby):**
   - Dùng `df_events_daily.groupby('WeekEndDate')` và gộp (aggregate) các cột lại:
     - `is_snap_window_1_week`: `.sum() > 0` (tức là = 1 nếu tuần đó có chứa bất kỳ ngày SNAP nào)
     - `is_snap_window_2_week`: `.sum() > 0`
     - `is_semimonthly_payweek`: `.sum() > 0`
     - `is_tax_refund_season_week`: `.sum() > 0`
     - `holiday_impact_week`: `.max()` (Lấy impact lớn nhất trong tuần đó)
     - `holiday_name_week`: `.first()` (Lấy tên Lễ đầu tiên (nếu có))

**Thành phẩm:** File `df_feature_calendar_weekly.csv`. File này có cùng "nhịp" (cadence) với `df_main_weekly`, sẵn sàng để merge.

---

## Giai đoạn 2: Kỹ thuật Đặc trưng (Nâng cấp "Tuần-theo-Tuần")

### 2.1. Mục tiêu 1: Hợp nhất (Merge) & Kiểm tra

**Tính chất:** Tạo file "thành phẩm" cuối cùng.

**Các bước thực hiện:**

1. `df_final = pd.merge(df_main_weekly, df_feature_calendar_weekly, on='WeekEndDate', how='left')`
2. `fillna(0)` cho các cột mới (ví dụ: `holiday_impact_week` sẽ NA vào tuần không lễ)
3. **Kiểm tra (Sanity Check):** Assert rằng mỗi `(Store, Dept, WeekEndDate)` là duy nhất

---

### 2.2. Mục tiêu 2: Tạo Features "Payday Pulse" (Nâng cao)

**Tính chất:** Tạo "vũ khí" chính cho ý tưởng "Payday Pulse" từ các cột `_week` đã merge.

**Các bước thực hiện:**

1. **Feature "Khoảng cách" (Weekly Proximity):**
   - `weeks_since_payday_15_eom`: Đếm số tuần kể từ `is_semimonthly_payweek` gần nhất (feature "trễ" (lag) của cờ payday)

2. **Feature "Suy giảm" (Weekly Decay) (Nâng cấp):**
   - **Tại sao:** Sức mua giảm phi tuyến sau khi nhận lương
   - **Cách 1 (exp):** `payday_decay_exp = exp(-0.25 * weeks_since_payday_15_eom)` (Dùng α=0.25 để giảm nhanh hơn)
   - **Cách 2 (Piecewise):** `payday_decay_piecewise`: 1.0 (nếu `weeks_since...` = 0), 0.7 (nếu = 1), 0.4 (nếu ≥ 2)
   - Nên thử cả 2 cách

3. **Feature "Mùa" (Season):**
   - Giữ nguyên `is_tax_refund_season_week` (0/1)

---

### 2.3. Mục tiêu 3: Tạo Features "Holiday" (Nâng cao)

**Tính chất:** Biến file Lễ (đã có `holiday_impact`) thành feature "tiên tri" (biết trước).

**Các bước thực hiện:**

1. **Feature "Đếm ngược" (Weekly Countdown) (Nâng cấp):**
   - `weeks_until_christmas`: Đếm số tuần cho đến lễ Giáng sinh tiếp theo (Dùng lịch cố định → an toàn, không rò rỉ (leakage))
   - `weeks_until_thanksgiving`: Tương tự

2. **Feature "Cửa sổ" (Weekly Window):**
   - `is_pre_christmas_window_week`: = 1 nếu `weeks_until_christmas` ≤ 3 (3 tuần trước lễ)
   - `is_pre_thanksgiving_window_week`: = 1 nếu `weeks_until_thanksgiving` ≤ 2

---

### 2.4. Mục tiêu 4: Tạo Features "Nền tảng" (Lag/Rolling)

**Tính chất:** Bắt buộc phải có để mô hình bắt được "quán tính" (inertia) và "xu hướng" (trend).

**Các bước thực hiện:**

1. **Feature "Trễ" (Lag) (Nâng cấp):**
   - `lag_sales_t_52`: Feature "năm ngoái" (quan trọng nhất)
   - `lag_sales_t_1`, `lag_sales_t_2`, `lag_sales_t_4`: Bổ sung các lag ngắn hạn (1, 2, 4 tuần trước) để bắt "động lực gần"

2. **Feature "Trượt" (Rolling) (Nâng cấp):**
   - `rolling_mean_sales_4_weeks`: Trung bình 4 tuần gần nhất (Nhớ `.shift(1).rolling(4).mean()` để tránh "leakage" tuần hiện tại)
   - `rolling_std_sales_4_weeks`: Độ lệch chuẩn 4 tuần (Có thể dùng Winsorize (cắt bớt outlier) cho cột này để ổn định mô hình)

---

### 2.5. Mục tiêu 5: Tạo Features "Tương tác" (Interaction)

**Tính chất:** Feature "pro" nhất, giúp mô hình hiểu các bối cảnh phức tạp.

**Các bước thực hiện (Tập trung vào 3 tương tác "sâu" được gợi ý):**

1. `interact_snap_x_type_c`: = `is_snap_window_1_week * (Store_Type == 'C')` (Để xem SNAP tác động mạnh hơn ở cửa hàng loại C không)

2. `interact_holiday_x_impact`: = `is_pre_christmas_window_week * holiday_impact_week` (Khuếch đại tín hiệu Lễ "lớn")

3. `interact_tax_x_temp`: = `is_tax_refund_season_week * Temperature` (Để xem "Mùa hoàn thuế" + "Thời tiết ấm" có bùng nổ không)

---

## Thành phẩm cuối cùng

Sau khi hoàn thành tất cả các mục tiêu trên, xuất ra file `df_final_for_model.csv`.

**Tính chất:** Đây là file sẵn sàng 100% để đưa vào LightGBM (hoặc Prophet) cho Bước 3: Xây dựng PoC (so sánh Model A và Model B)
