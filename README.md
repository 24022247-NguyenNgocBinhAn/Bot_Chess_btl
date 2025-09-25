# BOT_CHESS_BTL
BTL môn **AIT2004 - Cơ sở trí tuệ nhân tạo**

---

## 📌 Giới thiệu
**BOT_CHESS_BTL** là một chương trình mô phỏng bàn cờ vua và triển khai các chức năng cơ bản của một "chess bot".  
Bàn cờ được biểu diễn bằng một **mảng 2D kích thước 8×8**.  

---

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


