# Module Tiền Xử Lý (Preprocessing)

Pipeline tiền xử lý hoàn chỉnh để chuyển đổi bộ dữ liệu Online Retail II thành định dạng giao dịch cho khai phá quy tắc kết hợp.

## Cấu Trúc Module

```
src/preprocessing/
├── __init__.py           # Khởi tạo package và xuất các class
├── loader.py            # Tải dữ liệu với auto-download từ UCI
├── cleaner.py           # Làm sạch dữ liệu 5 bước
├── filter.py            # Lọc các item hiếm
├── transformer.py       # Chuyển đổi sang định dạng giao dịch
├── encoder.py           # Mã hóa one-hot nhị phân
├── saver.py             # Lưu dữ liệu nhiều định dạng
└── pipeline.py          # Điều phối chính
```

## Bắt Đầu Nhanh

### Sử Dụng Pipeline Class

```python
from src.preprocessing import PreprocessingPipeline

# Tạo và chạy pipeline với các thông số mặc định
pipeline = PreprocessingPipeline()
results = pipeline.run()
```

### Sử Dụng Hàm Tiện Lợi

```python
from src.preprocessing import PreprocessingPipeline

results = pipeline.run_pipeline(
    min_support_count=50,
    min_support_percentage=0.1,
    min_items_per_transaction=2
)
```

### Chạy Như Script Chính

```bash
python run_preprocessing.py
```

## Các Thành Phần Module

### 1. **DataLoader** (`loader.py`)
- Tải bộ dữ liệu Online Retail II từ tệp Excel
- Tự động tải về từ kho UCI nếu không tìm thấy cục bộ
- Cung cấp khám phá dữ liệu và thống kê

### 2. **DataCleaner** (`cleaner.py`)
Quy trình làm sạch 5 bước:
1. Xóa các hàng có Invoice/Description/Customer ID bị thiếu
2. Xóa giao dịch bị hủy (Invoice bắt đầu bằng 'C') và số lượng âm
3. Xóa giá tiền không dương
4. Xóa các bản sao (Invoice, StockCode, Customer ID)
5. Làm sạch và kiểm chứng mô tả sản phẩm

### 3. **RareItemFilter** (`filter.py`)
- Lọc các item dựa trên ngưỡng tần suất
- Ngưỡng tuyệt đối (số lần) và tương đối (%) có thể cấu hình
- Sử dụng giá trị cao nhất của cả hai ngưỡng
- Cung cấp thống kê lọc chi tiết

### 4. **TransactionTransformer** (`transformer.py`)
- Nhóm các item theo hóa đơn để tạo giao dịch
- Lọc giao dịch có số lượng item tối thiểu
- Trả về dataframe giao dịch và danh sách itemset

### 5. **OneHotEncoder** (`encoder.py`)
- Tạo ma trận mã hóa one-hot nhị phân
- Tạo ánh xạ item-to-index
- Tính toán thưa thớt và thống kê tần suất
- Hỗ trợ cả định dạng ma trận NumPy và DataFrame

### 6. **DataSaver** (`saver.py`)
Lưu 9 tệp đầu ra:
1. `cleaned_data.csv` - Bộ dữ liệu đã làm sạch hoàn chỉnh
2. `transactions.csv` - Bảng giao dịch với itemset
3. `transaction_list.pkl` - Pickle Python (danh sách các tập hợp)
4. `transactions.txt` - Định dạng văn bản (1 giao dịch mỗi dòng)
5. `onehot_matrix.csv` - Ma trận nhị phân one-hot (CSV)
6. `onehot_matrix.npy` - Ma trận nhị phân one-hot (NumPy)
7. `item_mapping.pkl` - Từ điển item-to-index (pickle)
8. `item_mapping.csv` - Ánh xạ item-to-index (dễ đọc)
9. `processing_summary.csv` - Thống kê xử lý

### 7. **PreprocessingPipeline** (`pipeline.py`)
- Điều phối tất cả các thành phần
- Quản lý các thông số cấu hình
- Thực hiện workflow tiền xử lý hoàn chỉnh
- Trả về từ điển kết quả toàn diện

## Thông Số Cấu Hình

- **min_support_count** (mặc định: 50)
  - Ngưỡng tuyệt đối: item phải xuất hiện ≥ 50 lần

- **min_support_percentage** (mặc định: 0.1)
  - Ngưỡng tương đối: item phải xuất hiện ≥ 0.1% bản ghi

- **min_items_per_transaction** (mặc định: 2)
  - Số lượng item tối thiểu mỗi giao dịch (bộ lọc giao dịch đơn item)

## Tệp Đầu Ra

Tất cả tệp được lưu vào thư mục `data/processed/`:

| Tệp | Định Dạng | Trường Hợp Sử Dụng |
|------|--------|----------|
| `cleaned_data.csv` | CSV | Xem xét bộ dữ liệu hoàn chỉnh, nhập Excel |
| `transactions.csv` | CSV | Xem xét giao dịch, phân tích bảng tính |
| `transaction_list.pkl` | Pickle | Nhập trực tiếp Python, đầu vào thuật toán |
| `transactions.txt` | Text | Nhập phổ quát, thuật toán Apriori |
| `onehot_matrix.csv` | CSV | Xem xét ma trận, phân tích bảng tính |
| `onehot_matrix.npy` | NumPy | Xử lý ML/thuật toán hiệu quả |
| `item_mapping.pkl` | Pickle | Tra cứu từ điển Python |
| `item_mapping.csv` | CSV | Tham chiếu item dễ đọc |
| `processing_summary.csv` | CSV | Đảm bảo chất lượng, theo dõi số liệu |

## Thống Kê Xử Lý

Kết quả điển hình từ xử lý notebook:

```
Bản ghi gốc:                     525,461
Sau làm sạch:                    394,960 (75.16% được giữ lại)
Sau lọc item hiếm:              ~150,000 (thay đổi theo ngưỡng)
Giao dịch được tạo:             ~10,000-15,000
Item duy nhất:                  ~800-1,200 (sau lọc)
Độ thưa thớt ma trận:            ~95-98%
```

## Ví Dụ Sử Dụng

### Pipeline Hoàn Chỉnh

```python
from src.preprocessing import PreprocessingPipeline

pipeline = PreprocessingPipeline(
    min_support_count=50,
    min_support_percentage=0.1
)
results = pipeline.run()

print(f"Đã xử lý {results['transactions']} giao dịch")
print(f"Đã tạo {results['unique_items']} item")
```

### Xử Lý Từng Bước

```python
from src.preprocessing import (
    DataLoader, DataCleaner, RareItemFilter,
    TransactionTransformer, OneHotEncoder, DataSaver
)
from pathlib import Path

# Tải
loader = DataLoader()
df = loader.load_data()

# Làm sạch
cleaner = DataCleaner()
df_clean = cleaner.clean(df)

# Lọc
filter_obj = RareItemFilter(min_support_count=50)
df_filtered, rare, common = filter_obj.filter(df_clean)

# Chuyển đổi
transformer = TransactionTransformer(min_items=2)
transactions, trans_list = transformer.transform_by_invoice(df_filtered)

# Mã hóa
encoder = OneHotEncoder()
all_items = transformer.get_unique_items(trans_list)
onehot_matrix, item_mapping = encoder.create_matrix(trans_list, all_items)

# Lưu
saver = DataSaver(Path('data/processed'))
saver.save_all(df_clean, transactions, trans_list, onehot_matrix, 
               encoder.to_dataframe(onehot_matrix, all_items),
               item_mapping, all_items)
```

## Yêu Cầu

- pandas >= 1.0
- numpy >= 1.19
- openpyxl (để đọc Excel)
- urllib (thư viện tiêu chuẩn)
- pickle (thư viện tiêu chuẩn)
- pathlib (thư viện tiêu chuẩn)

## Xử Lý Lỗi

Pipeline bao gồm xử lý lỗi mạnh mẽ:
- Tự động tải về dữ liệu nếu không tìm thấy
- Kiểm chứng kiểu dữ liệu và phạm vi
- Kiểm tra giá trị thiếu và bản sao
- Cung cấp nhật ký xử lý chi tiết
- Lưu thống kê tóm tắt để xác minh

## Ghi Chú Về Hiệu Năng

- Thời gian xử lý: ~30-60 giây cho pipeline hoàn chỉnh
- Sử dụng bộ nhớ: ~2-3 GB cho dữ liệu được tải (bao gồm bộ đệm làm sạch)
- Kích thước đầu ra: ~100-500 MB (tùy thuộc vào số lượng giao dịch và lọc item)
- Nút cổ chai: Đọc Excel (openpyxl) cho tệp lớn

## Khắc Phục Sự Cố

### Danh sách giao dịch trống
- Tăng `min_items_per_transaction` hoặc giảm ngưỡng lọc
- Kiểm tra xem ngưỡng item hiếm có quá mạnh không

### Độ thưa thớt cao (>99%)
- Giảm `min_support_count` hoặc tăng `min_support_percentage`
- Đây là hành vi dự kiến cho dữ liệu giao dịch

### Vấn đề bộ nhớ
- Xử lý trên máy tính có 4+ GB RAM
- Giảm kích thước lô bằng cách triển khai chunking dữ liệu

### Dữ liệu không tải về
- Kiểm tra kết nối Internet
- Kho UCI có thể tạm thời không khả dụng
- Tải về thủ công: https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx
