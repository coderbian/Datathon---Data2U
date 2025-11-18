# PAYDAY PULSE - MÔ HÌNH DỰ ĐOÁN VÀ TỐI ƯU HÓA CHUỖI CUNG ỨNG THEO CHU KỲ NGÀY LƯƠNG

**Đội thi:** DATA2U  
**Cuộc thi:** Vietnam Datathon 2025  
**Chủ đề:** Tối ưu hóa vận hành bán lẻ dựa trên dữ liệu (Retail Data Optimization)

---

## 1. Tổng quan dự án

### Vấn đề

Các mô hình dự báo truyền thống thường tập trung vào các yếu tố vĩ mô (Lễ, Tết, Mùa vụ năm) nhưng bỏ sót **"nhịp đập kinh tế vi mô"** - đó là **Chu kỳ nhận lương (Payday Cycle)**.

Điều này dẫn đến hai nỗi đau lớn cho nhà bán lẻ:

- **Hết hàng (Stock-out):** Khi nhu cầu tăng vọt vào ngày lương về
- **Tồn kho (Overstock):** Khi sức mua giảm sâu vào những ngày "thắt lưng buộc bụng" cuối tháng

### Giải pháp - Payday Pulse

Chúng tôi đề xuất một phương pháp tiếp cận mới bằng cách **trích xuất đặc trưng chu kỳ lương ẩn (Latent Payday Features)** từ phần dư (residuals) của dữ liệu bán hàng lịch sử, sử dụng kỹ thuật **Gaussian Decomposition**.

Đặc trưng này sau đó được đưa vào mô hình **LightGBM** để tăng độ chính xác dự báo.

---

## 2. Cấu trúc thư mục nộp bài

Thư mục **Sản phẩm nộp** bao gồm các thành phần sau:

```text
Sản phẩm nộp/
│
├── [Data2U] Báo cáo.pdf
├── [Data2U] Bảng kế hoạch dự kiến.xlsx
├── [Data2U] Code_walmart_payday_pulse_unified.ipynb
│
├── [Data2U] Data/
│   ├── Extra Data/
│   │   ├── snap_dist_dates_notes.csv
│   │   ├── snap_dist_dates_notesvarlist.csv
│   │   ├── snap_dist_dates_nyc.csv
│   │   ├── snap_dist_dates_nycvarlist.csv
│   │   ├── snap_dist_dates_readme.csv
│   │   ├── snap_dist_dates_states.csv
│   │   └── snap_dist_dates_statesvarlist.csv
│   │
│   └── Provided Data/
│       ├── features.csv
│       ├── stores.csv
│       ├── test.csv
│       └── train.csv
│
├── [Data2U] README.md
├── [Data2U] Slide giới thiệu.pdf
└── [Data2U] Video giới thiệu.mp4
```

---

## 3. Hướng dẫn chạy Code

Mã nguồn được đóng gói trong một **Jupyter Notebook duy nhất** để đảm bảo tính tiện lợi và khả năng tái lập kết quả.

### 3.1. Yêu cầu môi trường

- **Python:** 3.7+
- **Thư viện chính:**
  - `pandas`
  - `numpy`
  - `scipy`
  - `lightgbm`
  - `scikit-learn`
  - `matplotlib`
  - `seaborn`

### 3.2. Các bước thực hiện

1. Đảm bảo các file dữ liệu (`train.csv`, `features.csv`, `stores.csv`) được đặt trong thư mục `[Data2U] Data/Provided Data/` (hoặc điều chỉnh đường dẫn `TRAIN_PATH`, `FEATURES_PATH`, `STORES_PATH` ở cell đầu tiên của notebook)

2. Mở file **`[Data2U] Code_walmart_payday_pulse_unified.ipynb`**

3. Chạy **Run All**

### 3.3. Pipeline xử lý trong Notebook

#### **A. Data Loading & Cleaning**

- Xử lý giá trị thiếu (MarkDown)
- Xử lý doanh số âm (Returns)

#### **B. Decomposition**

Dùng LightGBM để tách các thành phần:

- Xu hướng
- Mùa vụ tuần
- Lấy ra phần dư (residual)

#### **C. Payday Feature Engineering**

1. Phân tích residual theo `month_phase` (giai đoạn trong tháng)
2. Fit hàm 2-Gaussian để mô hình hóa 2 đỉnh lương (đầu tháng và giữa tháng)
3. Tạo features: `pay_peak_1` và `pay_peak_2`

#### **D. Modeling & Evaluation**

- Huấn luyện 2 model:
  - **Model A** - Baseline (không có payday features)
  - **Model B** - Payday Pulse (có payday features)
- So sánh RMSE

---

## 4. Kết quả nổi bật

Mô hình đã chứng minh được giả thuyết rằng việc tích hợp tín hiệu ngày lương giúp **cải thiện độ chính xác dự báo**:

| Metric | Model A (Baseline) | Model B (Payday Pulse) | Cải thiện |
|--------|-------------------:|----------------------:|----------:|
| **RMSE** | 3,581.92 | 3,324.58 | **~7.2%** |

> *Kết quả trên tập validation (Time-based split, dữ liệu Walmart)*

---

## 5. Tính thực tiễn và Hướng phát triển

### 5.1. Tính khả thi (Feasibility)

#### **Công nghệ**

- Sử dụng **LightGBM** - nhẹ, nhanh, dễ triển khai trên các nền tảng Cloud (AWS/GCP/Azure)

#### **Dữ liệu**

- Chỉ yêu cầu dữ liệu lịch sử bán hàng cơ bản (POS data)
- Không cần dữ liệu nhạy cảm về thu nhập khách hàng

### 5.2. Kế hoạch triển khai (Roadmap)

> *(Chi tiết xem trong file `[Data2U] Bảng kế hoạch dự kiến.xlsx`)*

- **Giai đoạn Pilot (Tháng 1-2):** Chạy thử nghiệm trên ngành hàng Tiêu dùng nhanh (FMCG)
- **Đánh giá (Tháng 3):** A/B Testing giữa kho áp dụng Payday Pulse và kho đối chứng
- **Mở rộng (Tháng 4+):** Tích hợp vào hệ thống ERP/Demand Planning chính thức

---

## 6. Thông tin liên hệ

### Nhóm DATA2U

| STT | Vai trò | Họ và tên |
|-----|---------|-----------|
| 1 | Trưởng nhóm | Trương Minh Tiền |
| 2 | Thành viên | Lưu Vũ Lâm |
| 3 | Thành viên | Nguyễn Thị Thanh Nga |
| 4 | Thành viên | Kiêm Thị Thanh Thảo |
| 5 | Thành viên | Trần Minh Hiếu Học |

---

**Cảm ơn Ban tổ chức và Ban giám khảo đã dành thời gian xem xét sản phẩm của chúng tôi!**
