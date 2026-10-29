import streamlit as st
import random
import time

# Thiết lập giao diện màn hình dọc kiểu Mobile giống WePlay
st.set_page_config(page_title="Người Vận Chuyển - WePlay Style", page_icon="🛵", layout="centered")

# --- KHỞI TẠO TRẠNG THÁI GAME ---
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.distance = 0       # Quãng đường đã đi (mét)
    st.session_state.target = 500       # Đích đến (mét)
    st.session_state.speed = 0          # Tốc độ hiện tại (km/h)
    st.session_state.balance = 100      # Độ thăng bằng của xe (%)
    st.session_state.score = 0          # Điểm (dựa trên thời gian và độ khéo)
    st.session_state.log = "Hệ thống: Sẵn sàng nhận đơn hàng! 📦"
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.hazard = "Đường phẳng"  # Chướng ngại vật phía trước

# Các loại địa hình / chướng ngại vật xuất hiện ngẫu nhiên
HAZARDS = {
    "Đường phẳng": {"risk": 0.05, "desc": "🟢 Đường thẳng, bằng phẳng. Có thể vít ga!"},
    "Khúc cua gắt": {"risk": 0.4, "desc": "⚠️ Khúc cua hiểm trở! Giảm tốc độ tránh lật xe."},
    "Gờ giảm tốc / Ổ gà": {"risk": 0.3, "desc": "💥 Ổ gà liên tiếp! Chạy nhanh sẽ mất thăng bằng."},
    "Cảnh sát bắn tốc độ": {"risk": 0.2, "desc": "🚓 Có chốt cảnh sát! Vượt quá 60km/h sẽ bị phạt."}
}

def reset_game():
    st.session_state.game_started = True
    st.session_state.distance = 0
    st.session_state.speed = 0
    st.session_state.balance = 100
    st.session_state.log = "🏍️ Bắt đầu lên ga giao hàng! Né vật cản nhé!"
    st.session_state.game_over = False
    st.session_state.victory = False
    st.session_state.hazard = "Đường phẳng"

# --- GIAO DIỆN CHÍNH ---
st.title("🛵 NGƯỜI VẬN CHUYỂN (WEPLAY)")
st.write("Đơn tới là chạy, khách réo là phi! Điều khiển tay lái khéo léo để về đích an toàn.")

# 1. XỬ LÝ TRẠNG THÁI KẾT THÚC GAME
if st.session_state.game_over:
    st.error(f"💥 **GAME OVER:** {st.session_state.log}")
    st.button("Thử lại đơn khác 🔄", on_click=reset_game)

elif st.session_state.victory:
    st.balloons()
    st.success(f"🎉 **XUẤT SẮC!** Bạn đã giao hàng thần tốc thành công! Điểm số: {st.session_state.distance * 2 + st.session_state.balance}")
    st.button("Nhận đơn hàng mới 📦", on_click=reset_game)

# 2. MÀN HÌNH CHỜ SẴN SÀNG KHỞI HÀNH
elif not st.session_state.game_started:
    st.info("💡 **Cách chơi:** Nhấn nút 'Lên Ga' để tăng tốc chạy về đích. Tuy nhiên, khi gặp 'Khúc cua' hoặc 'Ổ gà', bạn phải chủ động 'Hãm Phanh' hạ tốc độ xuống, nếu không xe sẽ mất thăng bằng và lật!")
    st.button("Bắt đầu giao hàng ngay 🚀", on_click=reset_game)

# 3. VÒNG LẶP CHƠI GAME CHÍNH
else:
    # Hiển thị HUD thông số
    col1, col2, col3 = st.columns(3)
    col1.metric("🏁 Quãng đường", f"{st.session_state.distance} / {st.session_state.target} m")
    col2.metric("⚡ Tốc độ", f"{st.session_state.speed} km/h")
    
    # Thanh hiển thị độ thăng bằng (Nếu về 0% là lật xe)
    balance_color = "🟢" if st.session_state.balance > 60 else ("🟡" if st.session_state.balance > 30 else "🔴")
    col3.write(f"⚖️ **Thăng bằng:** {balance_color} **{st.session_state.balance}%**")
    st.progress(st.session_state.balance / 100)

    # Hiển thị thanh tiến trình hành trình đến nhà khách hàng
    progress_percent = int((st.session_state.distance / st.session_state.target) * 100)
    st.write("🗺️ **Tiến trình di chuyển:**")
    st.progress(min(100, max(0, progress_percent)))

    # Quét cảm biến vật cản phía trước
    st.markdown(f"### 🔮 Phía trước: {HAZARDS[st.session_state.hazard]['desc']}")
    
    st.warning(f"📰 {st.session_state.log}")

    st.write("---")
    st.write("🕹️ **BẢNG ĐIỀU KHIỂN TAY LÁI:**")
    
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    
    # HÀNH ĐỘNG 1: LÊN GA (TĂNG TỐC)
    if btn_col1.button("🔥 LÊN GA ++", use_container_width=True):
        st.session_state.speed += 30  # Mỗi lần vặn ga tăng 30km/h
        hz = st.session_state.hazard
        
        # Tính toán rủi ro dựa trên tốc độ và địa hình
        if hz == "Khúc cua gắt" and st.session_state.speed > 40:
            st.session_state.balance -= 35
            st.session_state.log = "💥 Xe vào cua quá nhanh! Suýt chút nữa thì lật xe rồi!"
        elif hz == "Gờ giảm tốc / Ổ gà" and st.session_state.speed > 50:
            st.session_state.balance -= 25
            st.session_state.log = "🛹 Xe vấp ổ gà nảy tưng tưng! Thùng hàng rung lắc dữ dội."
        elif hz == "Cảnh sát bắn tốc độ" and st.session_state.speed > 60:
            st.session_state.balance -= 10
            st.session_state.log = "🚓 Bạn phóng nhanh qua chốt! Cảnh sát đang đuổi theo gầm rú."
        else:
            st.session_state.log = "🚀 Bạn kéo ga mạnh mẽ, phóng vút đi trên đường phẳng!"
            st.session_state.balance = min(100, st.session_state.balance + 5) # Hồi nhẹ thăng bằng khi đường thẳng
            
        # Cập nhật quãng đường chạy được dựa trên tốc độ
        st.session_state.distance += int(st.session_state.speed * 0.5)
        # Thay đổi ngẫu nhiên chướng ngại vật tiếp theo
        st.session_state.hazard = random.choice(list(HAZARDS.keys()))
        st.rerun()

    # HÀNH ĐỘNG 2: RÀ PHANH (GIẢM TỐC)
    if btn_col2.button("🛑 RÀ PHANH --", use_container_width=True):
        st.session_state.speed = max(0, st.session_state.speed - 40) # Giảm tốc mạnh
        st.session_state.balance = min(100, st.session_state.balance + 25) # Lấy lại thăng bằng
        st.session_state.log = "📉 Bạn chủ động rà phanh, làm chủ tốc độ một cách an toàn."
        st.session_state.distance += int(st.session_state.speed * 0.5)
        st.session_state.hazard = random.choice(list(HAZARDS.keys()))
        st.rerun()

    # HÀNH ĐỘNG 3: GIỮ NGUYÊN TỐC ĐỘ (CHẠY ĐỀU)
    if btn_col3.button("🛵 CHẠY ĐỀU", use_container_width=True):
        hz = st.session_state.hazard
        if hz != "Đường phẳng" and st.session_state.speed > 50:
            st.session_state.balance -= 15
            st.session_state.log = f"⚠️ Giữ tốc độ cao đi qua {hz} khiến xe hơi loạng choạng."
        else:
            st.session_state.log = "🛵 Giữ đều tay ga, xe đi rất ổn định."
            
        st.session_state.distance += int(st.session_state.speed * 0.5)
        st.session_state.hazard = random.choice(list(HAZARDS.keys()))
        st.rerun()

    # --- KIỂM TRA ĐIỀU KIỆN THẮNG / THUA CUỐI LƯỢT ---
    if st.session_state.balance <= 0:
        st.session_state.game_over = True
        st.session_state.log = "Bạn ôm cua/vấp ổ gà ở tốc độ cao làm xe lật nhào, hàng hóa vỡ tan tành! 🏍️💥"
        st.rerun()
        
    if st.session_state.distance >= st.session_state.target:
        st.session_state.victory = True
        st.rerun()
