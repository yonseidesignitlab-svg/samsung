import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time
import random
import base64
import re

# --- 1. 페이지 기본 설정 및 스타일 ---
st.set_page_config(
    page_title="RAEMIAN Sovereign AI",
    page_icon="🤖",
    layout="centered"
)

# --- 로고 파일을 Base64로 인코딩하는 함수 ---
def get_image_as_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"로고 파일({path})을 찾을 수 없습니다. app.py와 같은 폴더에 넣어주세요.")
        return None

# --- CSS 스타일 주입 ---
st.markdown("""
<style>
    /* 페이지 전체 배경: 새로운 색상 적용 */
    .stApp {
        background-color: #1D3940;
        background-attachment: fixed;
    }

    /* 헤더 (로고 + 타이틀) */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 2rem;
        position: relative;
    }
    .logo-image {
        width: 150px;
        position: absolute;
        left: 0;
    }
    .app-title {
        color: #D9D8D2;
        font-size: 2.2rem;
        font-weight: bold;
    }

    /* 기본 텍스트 색상 (새로운 색상 적용) */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stException,
    div[data-testid="stSubheader"],
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricValue"] > div,
    [data-testid="caption"] {
        color: #D9D8D2 !important;
    }
    
    /* 버튼 스타일 (새로운 색상 적용) */
    .stButton > button {
        border-radius: 20px;
        border: 1px solid #589EA6;
        background-color: transparent;
        color: #D9D8D2;
        transition: all 0.3s;
        padding: 10px 24px;
        margin-top: 10px;
    }
    .stButton > button:hover {
        background-color: #589EA6;
        color: #D9D8D2;
        border-color: #589EA6;
    }
    .stButton > button[kind="primary"] {
        background-color: #589EA6;
        color: #D9D8D2;
        font-weight: bold;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4a8a92;
    }
    
    /* 텍스트 입력창 스타일 */
    .stTextInput > div > div > input {
        border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.9);
        color: black;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* 시간/분 선택 UI 스타일 */
    .time-selector-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* 스피너 스타일 (새로운 색상 적용) */
    .stSpinner > div > div {
        border-top-color: #589EA6;
    }

    /* Glassmorphism 알림창 스타일 */
    .glass-notification {
        background: rgba(88, 158, 166, 0.15);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(88, 158, 166, 0.2);
        padding: 20px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .notification-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .notification-icon {
        font-size: 24px;
        margin-right: 15px;
    }
    .notification-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #D9D8D2;
    }
    .notification-body {
        font-size: 1rem;
        color: #D9D8D2;
    }
    
    /* 반응형 UI (모바일) */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .logo-image {
            position: static;
            width: 120px;
        }
        .app-title {
            font-size: 1.8rem;
        }
        div[data-testid="stSubheader"] {
            font-size: 1.2rem;
            text-align: center;
        }
        .stApp > div:first-of-type > .main > .block-container {
            padding-top: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- 2. API 키 설정 및 모델 초기화 ---
try:
    genai.configure(api_key="AIzaSyAYiV9x-7fZHba-HlM7ENGV9ZlnGSbugg0")
except Exception as e:
    st.error(f"API 키 설정 중 오류가 발생했습니다: {e}")
    st.stop()

image_generation_model = genai.GenerativeModel('gemini-2.5-flash-image-preview')


# --- 3. 핵심 기능 함수 ---
def generate_visitor_car_image(plate_number):
    """Gemini를 사용해 아파트 주차장에 들어오는 차량 이미지를 생성하는 함수."""
    rand_hour = random.randint(0, 23)
    rand_min = random.randint(0, 59)
    rand_sec = random.randint(0, 59)
    timestamp = f"2025-10-01 {rand_hour:02d}:{rand_min:02d}:{rand_sec:02d}"
    
    prompt = (
        f"A realistic photo taken from the perspective of a high-angle CCTV security camera positioned **just inside an underground parking garage**. "
        f"The camera is **looking up the entrance ramp towards the daylight outside**. "
        f"A modern car (sedan, SUV, or coupe) is **driving down the ramp, entering the garage and moving towards the camera's viewpoint**. "
        f"The car's license plate must legibly and clearly display the text '{plate_number}'. "
        f"The lighting should be clean and modern, with bright daylight visible at the top of the ramp. "
        f"In a corner of the image, include a CCTV timestamp overlay showing the text '{timestamp}'."
    )
    try:
        response = image_generation_model.generate_content(prompt)
        image_data = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if image_data:
            image = Image.open(io.BytesIO(image_data))
            return image
        else:
            st.error("API 응답에서 이미지 데이터를 찾을 수 없습니다.")
            return Image.new('RGB', (512, 512), color='gray')

    except Exception as e:
        st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")
        return Image.new('RGB', (512, 512), color='gray')

def generate_parking_spot_image(spot_details):
    """지정된 주차 공간의 이미지를 생성하는 함수."""
    try:
        floor, spot_code = spot_details.split('층 ')
        spot_prefix = ''.join(re.findall(r'[A-Za-z]', spot_code))
        spot_num = int(''.join(re.findall(r'\d', spot_code)))
        neighbor_spot1 = f"{spot_prefix}{spot_num - 1}"
        neighbor_spot2 = f"{spot_prefix}{spot_num + 1}"
    except:
        floor, spot_code, neighbor_spot1, neighbor_spot2 = "B2", "A12", "A11", "A13"

    prompt = (
        f"A photorealistic image of a single empty parking space in a clean, modern, well-lit underground parking garage. "
        f"The main focus is this empty spot. Right next to it, a large concrete pillar is prominently and clearly marked with the parking spot number '{spot_code}' and the floor level '{floor}층'. "
        f"To create a realistic environment, other cars are visible parked in the background, further down the aisle. "
        f"**Crucially, other pillars visible in the distance MUST be marked with different but similar numbers**, for example '{neighbor_spot1}' or '{neighbor_spot2}'. Do not repeat '{spot_code}' on background pillars. "
        f"The perspective is from a person standing looking directly at the empty '{spot_code}' spot."
    )
    try:
        response = image_generation_model.generate_content(prompt)
        image_data = None
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if image_data:
            image = Image.open(io.BytesIO(image_data))
            return image
        else:
            st.error("주차 공간 이미지 생성 API 응답에서 이미지 데이터를 찾을 수 없습니다.")
            return Image.new('RGB', (512, 512), color='gray')

    except Exception as e:
        st.error(f"주차 공간 이미지 생성 중 오류가 발생했습니다: {e}")
        return Image.new('RGB', (512, 512), color='gray')


def assign_parking_spot():
    """방문객에게 주차 공간을 랜덤으로 배정하는 함수."""
    floor = random.choice(['B1', 'B2'])
    section = random.choice(['A', 'B', 'C', 'L', 'M'])
    number = random.randint(10, 20) 
    return f"{floor}층 {section}{number}"

def generate_resident_unit():
    """규칙에 따라 랜덤한 호수를 생성하는 함수."""
    digits = random.choice([3, 4])
    tens = 0 # 십의 자리는 0으로 고정
    if digits == 3:
        hundreds = random.randint(1, 9)
        units = random.randint(0, 9)
        unit_number = f"{hundreds}{tens}{units}"
    else: # digits == 4
        hundreds = random.randint(0, 9)
        units = random.randint(0, 9)
        unit_number = f"1{hundreds}{tens}{units}"
    return f"{unit_number}호님"


# --- 4. 세션 상태(Session State) 초기화 ---
if 'step' not in st.session_state: st.session_state.step = "initial"
if 'car_number' not in st.session_state: st.session_state.car_number = ""
if 'parking_hours' not in st.session_state: st.session_state.parking_hours = ""
if 'generated_image' not in st.session_state: st.session_state.generated_image = None
if 'parking_spot_image' not in st.session_state: st.session_state.parking_spot_image = None
if 'resident_unit' not in st.session_state: st.session_state.resident_unit = generate_resident_unit()

# --- 5. UI 렌더링 (화면 전환 방식) ---
logo_base64 = get_image_as_base64("logo.png")
if logo_base64:
    st.markdown(
        f"""
        <div class="header-container">
            <img src="data:image/png;base64,{logo_base64}" class="logo-image">
            <h1 class="app-title">RAEMIAN Sovereign</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

current_step = st.session_state.step

if current_step == "initial":
    st.subheader(f"안녕하세요, {st.session_state.resident_unit}.")
    st.write("무엇을 도와드릴까요?")
    st.write("---")
    if st.button("✅ 방문객 차량 등록", type="primary"): st.session_state.step = "input_car_number"; st.rerun()
    st.button("🗓️ 커뮤니티 시설 예약", disabled=True)
    st.button("🧾 관리비 조회", disabled=True)

elif current_step == "input_car_number":
    st.subheader("방문객 차량 등록")
    st.write("손님의 차량 번호를 입력해주세요.")
    
    with st.form("car_input_form"):
        car_number_input = st.text_input("차량 번호", placeholder="예시) 123가 4567", label_visibility="collapsed")
        submitted = st.form_submit_button("다음", type="primary")

        if submitted:
            if car_number_input:
                st.session_state.car_number = car_number_input
                st.session_state.step = "select_parking_hours"
                st.rerun()
            else:
                st.warning("차량 번호를 입력해주세요.")

elif current_step == "select_parking_hours":
    st.subheader("방문객 주차 시간 설정")
    st.info(f"차량 번호 '{st.session_state.car_number}'를 접수했습니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        sub_col_hour1, sub_col_hour2 = st.columns([2, 1])
        with sub_col_hour1: hour = st.selectbox("시간", options=list(range(24)), index=3, label_visibility="collapsed")
        with sub_col_hour2: st.markdown('<p style="padding-top: 0.7rem;">시간</p>', unsafe_allow_html=True)
    with col2:
        sub_col_min1, sub_col_min2 = st.columns([2, 1])
        with sub_col_min1: minute = st.selectbox("분", options=list(range(0, 51, 10)), index=0, label_visibility="collapsed")
        with sub_col_min2: st.markdown('<p style="padding-top: 0.7rem;">분</p>', unsafe_allow_html=True)
    if st.button("설정 완료", type="primary"):
        if hour == 0 and minute == 0: st.warning("주차 시간은 10분 이상이어야 합니다.")
        else:
            parking_time_str = f"{hour}시간 {minute}분" if hour > 0 and minute > 0 else f"{hour}시간" if hour > 0 else f"{minute}분"
            st.session_state.parking_hours = parking_time_str; st.session_state.step = "standby"; st.rerun()

elif current_step == "standby":
    st.success(f"**차량 번호 {st.session_state.car_number}**, 방문 주차 **{st.session_state.parking_hours}**으로 예약을 설정했습니다.")
    st.info("해당 차량이 단지 입구에 도착하면 알려드리겠습니다.")
    with st.spinner("차량 도착 대기 중..."): time.sleep(3)
    st.session_state.step = "final_confirmation"; st.rerun()

elif current_step == "final_confirmation":
    st.markdown(f"""
        <div class="glass-notification">
            <div class="notification-header"><span class="notification-icon">🚗</span><span class="notification-title">방문 차량 도착 알림</span></div>
            <p class="notification-body">예약하신 <strong>{st.session_state.car_number}</strong> 차량이 단지 입구에서 감지되었습니다.</p>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.generated_image is None:
        with st.spinner("실시간 차량 이미지를 불러오는 중입니다..."):
            st.session_state.generated_image = generate_visitor_car_image(st.session_state.car_number)
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, caption="단지 입구에서 촬영된 이미지")
        st.warning("등록을 최종 완료하려면 입주민의 확인이 필요합니다. **해당 차량이 맞습니까?**")
        col1, col2 = st.columns(2)
        if col1.button("✅ 예, 맞습니다", type="primary"): st.session_state.step = "complete"; st.rerun()
        if col2.button("❌ 아니오"):
            st.session_state.generated_image = None # Reset only the image to regenerate
            st.rerun()

elif current_step == "complete":
    if 'parking_spot' not in st.session_state: st.session_state.parking_spot = assign_parking_spot()
    parking_spot = st.session_state.parking_spot
    st.subheader("✅ 등록 완료")
    st.success(f"방문객 차량({st.session_state.car_number}) 등록이 모두 완료되었습니다.")
    st.write("---")
    st.subheader("🅿️ 주차 공간 안내")
    st.metric(label="배정된 주차 공간", value=parking_spot)
    if st.session_state.parking_spot_image is None:
        with st.spinner("주차 공간 실시간 이미지를 불러오는 중입니다..."):
            st.session_state.parking_spot_image = generate_parking_spot_image(parking_spot)
    if st.session_state.parking_spot_image:
        st.image(st.session_state.parking_spot_image, caption="배정된 주차 공간 실시간 이미지")
    st.info("배정된 주차 공간으로 방문객 안내를 시작하겠습니다.")
    if st.button("🏠 처음으로 돌아가기"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

