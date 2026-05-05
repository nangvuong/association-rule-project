# Association Rule Mining Project

Hệ thống **khai phá luật kết hợp (Association Rule Mining)** hoàn chỉnh sử dụng các thuật toán Apriori, FP-Growth và so sánh với thư viện mlxtend. Bao gồm pipeline tiền xử lý dữ liệu, các thuật toán custom, web interface, và các notebook demo.

## 📋 Mục Lục

- [Tổng Quan](#tổng-quan)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Cách Sử Dụng](#cách-sử-dụng)
- [Các Thành Phần Chính](#các-thành-phần-chính)
- [Ví Dụ](#ví-dụ)
- [Kết Quả Đầu Ra](#kết-quả-đầu-ra)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Tổng Quan

Dự án này cung cấp:

✅ **Pipeline Tiền Xử Lý**: Tự động tải, làm sạch, lọc dữ liệu Online Retail II  
✅ **Thuật Toán Custom**: Cài đặt từ đầu Apriori và FP-Growth với Hash Tree  
✅ **Web Interface**: Giao diện Flask để chạy thuật toán và xem kết quả  
✅ **So Sánh Thuật Toán**: So sánh hiệu suất với thư viện mlxtend  
✅ **Jupyter Notebooks**: Demo chi tiết EDA, Apriori, FP-Growth, runtime comparison  

---

## 📁 Cấu Trúc Dự Án

```
association-rule-project/
│
├── data/                          # Dữ liệu
│   ├── raw/                       # Dữ liệu gốc
│   └── processed/                 # Dữ liệu sau tiền xử lý
│       ├── cleaned_data.csv
│       ├── transactions.csv
│       ├── transactions.txt
│       ├── item_mapping.csv
│       ├── onehot_matrix.csv
│       └── processing_summary.csv
│
├── src/                           # Source code chính
│   ├── preprocessing/             # Pipeline tiền xử lý
│   │   ├── loader.py             # Tải dữ liệu
│   │   ├── cleaner.py            # Làm sạch
│   │   ├── filter.py             # Lọc item
│   │   ├── transformer.py        # Chuyển đổi sang transaction
│   │   ├── encoder.py            # One-hot encoding
│   │   ├── saver.py              # Lưu dữ liệu
│   │   └── pipeline.py           # Điều phối main
│   │
│   ├── algorithms/                # Các thuật toán khai phá
│   │   ├── apriori.py            # Apriori algorithm
│   │   ├── fp_growth.py          # FP-Growth algorithm
│   │   └── hash_tree.py          # Cấu trúc Hash Tree
│   │
│   ├── mining/                    # Quản lý itemset và rule
│   │   ├── frequent_itemset.py   # Lớp FrequentItemset
│   │   └── rule_generation.py    # Sinh luật kết hợp
│   │
│   └── evaluation/                # Đánh giá & so sánh
│       ├── metrics.py            # Support, confidence, lift
│       └── compare.py            # So sánh thuật toán
│
├── notebooks/                     # Jupyter Notebooks
│   ├── eda.ipynb                 # Phân tích dữ liệu
│   ├── apriori_demo.ipynb        # Demo Apriori
│   ├── fp_growth_demo.ipynb      # Demo FP-Growth
│   ├── library_comparison_demo.ipynb  # So sánh mlxtend
│   └── runtime_comparison.ipynb  # So sánh thời gian
│
├── outputs/                       # Kết quả đầu ra
│   ├── apriori/                  # Kết quả Apriori
│   ├── fp_growth/                # Kết quả FP-Growth
│   └── library/                  # Kết quả mlxtend
│
├── web/                           # Web Interface
│   ├── app.py                    # Flask app chính
│   ├── models.py                 # SQLAlchemy models
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── mining.html           # Trang chạy thuật toán
│       ├── rules.html            # Hiển thị luật
│       └── transactions.html     # Hiển thị giao dịch
│
├── main.py                        # Pipeline chính
├── requirements.txt               # Dependencies cho analysis
├── requirements_web.txt           # Dependencies cho web
├── docker-compose.yml             # Docker Compose (PostgreSQL)
├── Dockerfile                     # Dockerfile cho web
├── start.sh                       # Script khởi động web
└── README.md                      # Tài liệu này
```

---

## ⚙️ Yêu Cầu Hệ Thống

- **Python**: 3.9+
- **Docker**: Để chạy PostgreSQL (tùy chọn, có thể dùng SQLite)
- **Git**: Để clone repo

---

## 🚀 Cài Đặt

### 1. Clone Repository
```bash
git clone <repository-url>
cd association-rule-project
```

### 2. Tạo Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# hoặc
.venv\Scripts\activate  # Windows
```

### 3. Cài Đặt Dependencies

**Cho phân tích (Analysis)**:
```bash
pip install -r requirements.txt
```

**Cho web interface**:
```bash
pip install -r requirements_web.txt
```

**Hoặc cài tất cả**:
```bash
pip install -r requirements.txt -r requirements_web.txt
```

### 4. Cấu Hình Environment
```bash
# Copy .env template nếu chưa có
cp .env.example .env  # nếu có
```

Chỉnh sửa `.env` với các thông số mong muốn:
```env
# Data paths
RAW_DATA_PATH=data/raw/online_retail_II.xlsx
OUTPUT_DIR=data/processed

# Mining parameters
MINING_MIN_SUPPORT=100
MINING_MIN_CONFIDENCE=0.5
APRIORI_USE_HASH_TREE=True
```

---

## 💡 Cách Sử Dụng

### Cách 1: Chạy Pipeline Chính
```bash
# Chạy toàn bộ pipeline: tiền xử lý → khai phá → đánh giá
python main.py
```

### Cách 2: Dùng Jupyter Notebooks
```bash
# Khởi động Jupyter
jupyter notebook

# Mở các notebook:
# - notebooks/eda.ipynb          # Phân tích dữ liệu
# - notebooks/apriori_demo.ipynb # Demo Apriori
# - notebooks/fp_growth_demo.ipynb # Demo FP-Growth
```

### Cách 3: Chạy Web Interface

**Tùy chọn A: Dùng Script (khuyến nghị)**
```bash
./start.sh
```

Script sẽ:
- ✓ Khởi động PostgreSQL qua Docker
- ✓ Chờ database sẵn sàng
- ✓ Cài dependencies
- ✓ Chạy Flask trên http://localhost:500

**Tùy chọn B: Chạy thủ công**
```bash
# Terminal 1: Khởi động PostgreSQL
docker compose up -d db

# Terminal 2: Khởi động Flask
export DATABASE_URL="postgresql://arm_user:arm_password@localhost:5432/arm_db"
python web/app.py
```

Truy cập: `http://localhost:5001`

### Cách 4: Sử Dụng Hàm Python Trực Tiếp
```python
from src.algorithms import Apriori, FPGrowth
from src.preprocessing import PreprocessingPipeline

# Bước 1: Tiền xử lý
pipeline = PreprocessingPipeline()
transactions = pipeline.run()

# Bước 2: Chạy Apriori
apriori = Apriori(min_support=100, min_confidence=0.5)
apriori.fit(transactions)
rules = apriori.generate_rules()

# Bước 3: Xem kết quả
print(apriori.get_results_summary())
```

---

## 🔧 Các Thành Phần Chính

### 📊 1. Preprocessing Pipeline
Vị trí: `src/preprocessing/`

**Chức năng**:
- Tải Online Retail II dataset (auto-download từ UCI)
- 5 bước làm sạch: kiểm tra giá trị null, xóa transaction negative, v.v.
- Lọc item hiếm (support < min_support_count)
- Chuyển đổi sang định dạng transaction
- One-hot encoding
- Lưu data định dạng (CSV, TXT, NPY)

**Sử dụng**:
```python
from src.preprocessing import PreprocessingPipeline

pipeline = PreprocessingPipeline(
    min_support_count=50,
    min_support_percentage=0.1,
    min_items_per_transaction=2
)
results = pipeline.run()
print(f"Loaded: {results['num_transactions']} transactions")
```

### 🧮 2. Thuật Toán Apriori
Vị trí: `src/algorithms/apriori.py`

**Đặc điểm**:
- Cài đặt từ đầu theo thuật toán chuẩn Agrawal et al.
- Hỗ trợ Hash Tree để tối ưu đếm support
- Sinh luật kết hợp có tính toán confidence, lift, leverage

**Thông số**:
- `min_support`: Mức support tối thiểu (số lượng transaction)
- `min_confidence`: Mức confidence tối thiểu
- `use_hash_tree`: Sử dụng Hash Tree (tối ưu hơn)

**Sử dụng**:
```python
from src.algorithms import Apriori

apriori = Apriori(
    min_support=100,
    min_confidence=0.5,
    use_hash_tree=True
)
apriori.fit(transactions)
rules = apriori.generate_rules()
```

### 🌳 3. Thuật Toán FP-Growth
Vị trí: `src/algorithms/fp_growth.py`

**Đặc điểm**:
- Khai phá itemset phổ biến bằng FP-Tree
- Hiệu suất tốt hơn Apriori cho dataset lớn
- Không cần sinh candidate itemsets

**Sử dụng**:
```python
from src.algorithms import FPGrowth

fpgrowth = FPGrowth(
    min_support=100,
    min_confidence=0.5
)
fpgrowth.fit(transactions)
rules = fpgrowth.generate_rules()
```

### 🔍 4. Hash Tree
Vị trị: `src/algorithms/hash_tree.py`

**Chức năng**: Cấu trúc dữ liệu để đếm support candidate itemsets hiệu quả
- Routing: Route candidate theo item tại mỗi level
- Counting: Đếm support bằng cách traverse tree
- Tối ưu hóa: Giảm thời gian đếm trong Apriori

### 📈 5. Evaluation & Comparison
Vị trị: `src/evaluation/`

**Chức năng**:
- Tính toán metrics (support, confidence, lift)
- So sánh kết quả Apriori custom vs FP-Growth custom vs mlxtend
- Đo thời gian chạy

---

## 📝 Ví Dụ

### Ví Dụ 1: Chạy Pipeline Hoàn Chỉnh
```bash
python main.py
```

**Output**:
```
═══════════════════════════════════════════════════════════════════════════════════
  Association Rule Mining – Pipeline Chính
═══════════════════════════════════════════════════════════════════════════════════

── Bước 1: Load cấu hình ────────────────────────────────────────────────────────
  Min Support: 100, Min Confidence: 0.5
  Output: data/processed

── Bước 2: Tiền xử lý dữ liệu ────────────────────────────────────────────────────
  ✓ Loaded 541,909 transactions
  ✓ Cleaned 512,345 transactions
  ✓ Filtered 15,240 items → 1,250 items
  ✓ Generated itemsets

── Bước 3: Chạy Apriori ─────────────────────────────────────────────────────────
  ✓ Found 2,453 frequent itemsets
  ✓ Generated 461 rules
  Time: 2.34s

── Bước 4: Chạy FP-Growth ────────────────────────────────────────────────────────
  ✓ Found 2,453 frequent itemsets
  ✓ Generated 952 rules
  Time: 0.87s

── Bước 5: So sánh với mlxtend ──────────────────────────────────────────────────
  ✓ Found 2,453 frequent itemsets
  ✓ Generated 457 rules
  Time: 1.12s

── Bước 6: Lưu kết quả ────────────────────────────────────────────────────────
  ✓ Saved to outputs/
```

### Ví Dụ 2: Sử Dụng Apriori Trực Tiếp
```python
from src.preprocessing import PreprocessingPipeline
from src.algorithms import Apriori

# Tiền xử lý
pipeline = PreprocessingPipeline(min_support_count=50)
transactions = pipeline.run()['transactions']

# Khai phá
apriori = Apriori(min_support=100, min_confidence=0.5)
apriori.fit(transactions)
rules = apriori.generate_rules()

# Xem kết quả
for rule in rules[:5]:
    print(f"{rule['antecedent']} → {rule['consequent']}: "
          f"confidence={rule['confidence']:.2f}, lift={rule['lift']:.2f}")
```

### Ví Dụ 3: Chạy Web Interface
```bash
# Terminal 1
docker compose up -d db

# Terminal 2
export DATABASE_URL="postgresql://arm_user:arm_password@localhost:5432/arm_db"
python web/app.py
```

Truy cập: http://localhost:5000
- Trang chủ: Dashboard
- Mining: Chạy thuật toán
- Rules: Xem luật kết hợp
- Transactions: Xem giao dịch

---

## 📊 Kết Quả Đầu Ra

### 1. Dữ liệu Tiền Xử Lý
```
data/processed/
├── cleaned_data.csv              # Dữ liệu sau làm sạch
├── transactions.csv              # Format giao dịch
├── transactions.txt              # Format giao dịch (text)
├── item_mapping.csv              # Mapping item ID ↔ Name
├── onehot_matrix.csv             # Ma trận one-hot
├── onehot_matrix.npy             # Ma trận numpy
└── processing_summary.csv        # Thống kê xử lý
```

### 2. Kết Quả Khai Phá
```
outputs/
├── apriori/
│   ├── frequent_itemsets.csv     # Itemset phổ biến
│   ├── association_rules.csv     # Luật kết hợp
│   └── statistics.csv            # Thống kê
│
├── fp_growth/
│   ├── frequent_itemsets.csv
│   ├── association_rules.csv
│   ├── statistics.csv
│   └── statistics.json
│
└── library/                      # Kết quả mlxtend
    ├── apriori_itemsets.csv
    ├── association_rules.csv
    ├── fpgrowth_itemsets.csv
    └── statistics.json
```

### 3. Cấu Trúc CSV Luật Kết Hợp
```csv
antecedent,consequent,support,confidence,lift,leverage,conviction
"(item1, item2)","(item3)",150,0.85,1.45,0.12,3.25
```

---

## 🐛 Troubleshooting

### ❌ Lỗi: `ModuleNotFoundError: No module named 'flask_cors'`
**Giải pháp**:
```bash
pip install flask-cors
```

### ❌ Lỗi: `psycopg2.OperationalError: connection to server failed`
**Nguyên nhân**: PostgreSQL chưa khởi động  
**Giải pháp**:
```bash
docker compose up -d db
sleep 2  # Chờ database sẵn sàng
python web/app.py
```

### ❌ Lỗi: `FATAL: password authentication failed for user "arm_user"`
**Nguyên nhân**: Database credentials sai  
**Giải pháp**: Kiểm tra `.env`:
```bash
DATABASE_URL="postgresql://arm_user:arm_password@localhost:5432/arm_db"
```

### ❌ Lỗi: `FileNotFoundError: data/raw/online_retail_II.xlsx`
**Giải pháp**: Script sẽ tự động tải từ UCI nếu file không tồn tại:
```python
from src.preprocessing import DataLoader
loader = DataLoader()
df = loader.load()  # Tự động tải nếu cần
```

### ❌ Lỗi: Kết quả Apriori vs FP-Growth không giống nhau
**Kiểm tra**:
1. `min_support` có giống nhau không?
2. `min_confidence` có giống nhau không?
3. Kiểm tra `use_hash_tree` có ảnh hưởng không?

---

## 📚 Thêm Thông Tin

### Jupyter Notebooks
- **eda.ipynb**: Phân tích dữ liệu, visualize distributions
- **apriori_demo.ipynb**: Step-by-step Apriori algorithm
- **fp_growth_demo.ipynb**: FP-Growth implementation
- **library_comparison_demo.ipynb**: So sánh với mlxtend
- **runtime_comparison.ipynb**: Đo hiệu suất 3 cách

### Tài Liệu Tham Khảo
- Agrawal, R., & Srikant, R. (1994). Fast algorithms for mining association rules.
- Han, J., Pei, J., & Yin, Y. (2000). Mining frequent patterns without candidate generation.
- mlxtend Documentation: https://rasbt.github.io/mlxtend/

---

## 👨‍💻 Phát Triển

### Chạy Tests
```bash
python -m pytest tests/
```

### Format Code
```bash
black src/
isort src/
```

### Linting
```bash
pylint src/
```

---

## 📄 License

MIT License

---

## ✉️ Support

Có câu hỏi? Tạo issue hoặc liên hệ tác giả.

---

**Cập nhật lần cuối**: May 5, 2026
