# BOT_CHESS_BTL
Bài tập lớn môn **AIT2004 - Cơ sở trí tuệ nhân tạo**

---

## 📌 Giới thiệu
**BOT_CHESS_BTL** là một chương trình mô phỏng bàn cờ vua và triển khai các chức năng cơ bản của một "chess bot".  
Bàn cờ được biểu diễn bằng một **mảng 2D kích thước 8×8** theo quy tắc chuẩn quốc tế.  

---

# ♟️ Luật Cờ Vua

## ♟️ Quy ước quân cờ
Mỗi quân cờ được biểu diễn dưới dạng **`xy`**:  

- `x`: loại quân cờ  
  - `K` → King (Vua)  
  - `Q` → Queen (Hậu)  
  - `R` → Rook (Xe)  
  - `B` → Bishop (Tượng)  
  - `N` → Knight (Mã)  
  - `P` → Pawn (Tốt)  

- `y`: màu quân cờ  
  - `w` → trắng (white)  
  - `b` → đen (black)  

### Ví dụ
- `Kw` → White King (Vua trắng)  
- `Qb` → Black Queen (Hậu đen)  
- `Pw` → White Pawn (Tốt trắng)  
- `Rb` → Black Rook (Xe đen)  

---

## 1. Mục tiêu trò chơi
Mục tiêu của cờ vua là chiếu hết (**checkmate**) quân `K` của đối thủ.  
Điều này xảy ra khi `K` của đối phương bị chiếu (**check**) và không còn nước đi hợp lệ nào để thoát.

---

## 2. Bàn cờ
- Bàn cờ có 64 ô (8x8), gồm các ô sáng và tối xen kẽ.  
- Bố trí ban đầu:  
  - Hàng 1 (trắng) / hàng 8 (đen): `R`, `N`, `B`, `Q`, `K`, `B`, `N`, `R`  
  - Hàng 2 (trắng) / hàng 7 (đen): toàn bộ `P`  

---

## 3. Cách di chuyển quân cờ

### Vua `K`
- Đi 1 ô theo mọi hướng (ngang, dọc, chéo).  
- Không được đi vào thế chiếu.  

### Hậu `Q`
- Đi bất kỳ số ô theo hàng, cột hoặc đường chéo.  

### Xe `R`
- Đi bất kỳ số ô theo hàng hoặc cột.  

### Tượng `B`
- Đi bất kỳ số ô theo đường chéo.  

### Mã `N`
- Đi theo hình chữ **L** (2 ô theo 1 hướng + 1 ô vuông góc).  
- Có thể nhảy qua quân khác.  

### Tốt `P`
- Đi 1 ô thẳng về phía trước.  
- Ở nước đi đầu tiên, có thể đi 2 ô.  
- Ăn chéo 1 ô về phía trước.  
- Có thể phong cấp (promotion) khi tới hàng cuối của đối phương.  

---

## 4. Nước đi đặc biệt

### Nhập thành (Castling)
- Kết hợp di chuyển `K` và một `R` cùng lúc.  
- Điều kiện:  
  - `K` và `R` chưa di chuyển trước đó.  
  - Không có quân nào nằm giữa `K` và `R`.  
  - `K` không đang bị chiếu và không đi qua ô bị chiếu.  

### Bắt tốt qua đường (En passant)
- Nếu một `P` đi 2 ô từ vị trí ban đầu và dừng ngay bên cạnh `P` đối phương,  
  thì `P` đối phương có quyền bắt quân này như thể nó chỉ đi 1 ô.  

### Phong cấp (Promotion)
- Khi `P` đi đến hàng cuối cùng của đối phương, nó phải được đổi thành `Q`, `R`, `B`, hoặc `N` cùng màu.  

---

## 5. Kết thúc ván cờ
- **Chiếu hết (Checkmate):** `K` bị chiếu và không còn nước đi hợp lệ.  
- **Hòa (Draw):** xảy ra khi:  
  - Thế cờ lặp lại 3 lần (Threefold repetition).  
  - Không còn đủ quân để chiếu hết (ví dụ: chỉ còn `Kw` và `Kb`).  
  - Bế tắc (Stalemate): người đi tới lượt không có nước đi hợp lệ nhưng `K` không bị chiếu.  
  - Quy tắc 50 nước: 50 nước liên tiếp không có di chuyển `P` hoặc ăn quân.  

---


## 🏁 Bàn cờ ban đầu
Bàn cờ được khởi tạo theo quy tắc chuẩn quốc tế:

|   | a | b | c | d | e | f | g | h |
|---|---|---|---|---|---|---|---|---|
| 8 | Rb| Nb| Bb| Qb| Kb| Bb| Nb| Rb|
| 7 | Pb| Pb| Pb| Pb| Pb| Pb| Pb| Pb|
| 6 |   |   |   |   |   |   |   |   |
| 5 |   |   |   |   |   |   |   |   |
| 4 |   |   |   |   |   |   |   |   |
| 3 |   |   |   |   |   |   |   |   |
| 2 | Pw| Pw| Pw| Pw| Pw| Pw| Pw| Pw|
| 1 | Rw| Nw| Bw| Qw| Kw| Bw| Nw| Rw|

---

## ⚙️ Môi trường & Thư viện
- **Ngôn ngữ**: Python 3.12  
- **Môi trường ảo**: `venv`

### Các thư viện sử dụng
- [math](https://docs.python.org/3/library/math.html) → toán học cơ bản  
- [random](https://docs.python.org/3/library/random.html) → sinh số/ngẫu nhiên  
- [numpy](https://numpy.org/) → đại số tuyến tính, mảng 2D  
- [sympy](https://www.sympy.org/) → đại số tượng trưng  
- [scipy](https://scipy.org/) → tính toán khoa học, tối ưu hóa  
- [statistics](https://docs.python.org/3/library/statistics.html) → thống kê cơ bản  
- [itertools](https://docs.python.org/3/library/itertools.html) → tổ hợp, hoán vị  

Cài đặt các thư viện bằng `pip`:
```bash
pip install numpy sympy scipy
🚀 Chạy chương trình
Tạo môi trường ảo:

bash
Sao chép mã
python -m venv venv
Kích hoạt môi trường:

Windows:

bash
Sao chép mã
venv\Scripts\activate
Linux/macOS:

bash
Sao chép mã
source venv/bin/activate
Cài đặt thư viện cần thiết:

bash
Sao chép mã
pip install -r requirements.txt
Chạy chương trình chính:

bash
Sao chép mã
python main.py
🧩 Cấu trúc dự án (gợi ý)
bash
Sao chép mã
BOT_CHESS_BTL/
│── README.md              # Tài liệu mô tả dự án
│── requirements.txt       # Danh sách thư viện cần thiết
│── main.py                # File chính chạy chương trình
│── board.py               # Xử lý bàn cờ
│── pieces.py              # Quy định và xử lý quân cờ
│── bot.py                 # Logic "chess bot"
│── utils.py               # Hàm tiện ích (random move, evaluation, ...)
└── tests/                 # Unit tests
🎯 Mục tiêu
Biểu diễn bàn cờ vua 8×8 bằng Python.

Cài đặt quy tắc di chuyển cơ bản của từng quân cờ.

Xây dựng bot cgó khả năng:

Sinh nước đi hợp lệ.

Lựa chọn nước đi ngẫu nhiên hoặc theo heuristic đơn giản.

Ứng dụng các thư viện toán học để hỗ trợ tính toán & tối ưu hóa.