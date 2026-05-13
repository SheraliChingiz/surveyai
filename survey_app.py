import streamlit as st
import streamlit.components.v1 as components
import json
import os
import random
import time
import zipfile
import io
from datetime import datetime

# --- ИНФРАСТРУКТУРА И АВТО-СОЗДАНИЕ ФАЙЛОВ ---
DATA_FOLDER = "captured_data"
V9_DATABASE = "interface_cognition_dataset_v9.jsonl"
NICHE_FILE = "niche_sites.txt"
REQ_FILE = "requirements.txt"

# 1. Создаем папку для данных
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# 2. Создаем файл для нишевых сайтов (если его нет)
if not os.path.exists(NICHE_FILE):
    with open(NICHE_FILE, "w", encoding="utf-8") as f:
        f.write("https://example-local-business.kz\n") # Заглушка, чтобы файл не был пустым

# 3. Создаем requirements.txt для Streamlit Cloud (если его нет)
if not os.path.exists(REQ_FILE):
    with open(REQ_FILE, "w", encoding="utf-8") as f:
        f.write("streamlit\n")

# --- АДМИН-ФУНКЦИЯ: СКАЧИВАНИЕ БАЗЫ ---
def get_all_data_zip():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "x", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(DATA_FOLDER):
            for file in files:
                f.write(os.path.join(root, file), file)
    return buf.getvalue()

# --- АВТОМАТИЧЕСКИЙ СБОР МЕТРИК УСТРОЙСТВА (JS) ---
def get_device_metrics():
    components.html(
        """
        <script>
        const metrics = {
            sw: window.screen.width,
            sh: window.screen.height,
            dpr: window.devicePixelRatio,
            touch: ('ontouchstart' in window || navigator.maxTouchPoints > 0)
        };
        window.parent.postMessage({type: 'streamlit:set_user_metrics', data: metrics}, '*');
        </script>
        """,
        height=0,
    )

# --- ФУНКЦИЯ ЗАГРУЗКИ ПОПУЛЯРНЫХ САЙТОВ ---
def get_popular_sites():
    sites = ["https://kaspi.kz", "https://www.sulpak.kz", "https://shop.kz", "https://krisha.kz", "https://kolesa.kz", "https://aviata.kz"]
    if os.path.exists(V9_DATABASE):
        with open(V9_DATABASE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    url = data.get('meta', {}).get('url')
                    if url and url not in sites:
                        sites.append(url)
                except: pass
    return sites

# --- ФУНКЦИЯ ЗАГРУЗКИ ЛОКАЛЬНЫХ САЙТОВ (ЖИВЫЕ + ИЗ ФАЙЛА) ---
def get_niche_sites():
    # Гарантированно живые сайты реального бизнеса (Алматы/РК)
    sites = [
        "https://manga.kz", "https://bluefin.kz", "https://delpapa.kz", "https://salamabro.kz", 
        "https://yakitoriya.kz", "https://onclinic.kz", "https://hakmedical.kz", "https://darismile.kz",
        "https://almatherm.kz", "https://12mesyatcev.kz", "https://chechil.kz", "https://pinta.kz", 
        "https://abdi.kz", "https://glotus.kz", "https://tumar.kz", "https://mastergrad.kz",
        "https://dodopizza.kz", "https://keruen-medicus.kz", "https://euphoria.kz", "https://chocofood.kz"
    ]
    
    # Подгрузка твоих личных сайтов из авто-созданного файла niche_sites.txt
    if os.path.exists(NICHE_FILE):
        with open(NICHE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                # Проверяем, что строка не пустая и это реально ссылка
                if url and url.startswith("http") and url not in sites:
                    sites.append(url)
    return sites

# --- UI CONFIG ---
st.set_page_config(page_title="UX AI Research", page_icon="🔬", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    div.stButton > button { width: 100%; border-radius: 8px; height: 3em; background-color: #2563eb; color: white; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #1d4ed8; }
    .stSlider { padding-top: 10px; padding-bottom: 10px; }
    .research-box { background-color: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- СЕКРЕТНАЯ АДМИНКА В SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Admin Panel")
    pwd = st.text_input("Введите пароль доступа", type="password")
    if pwd == "admin777": # МОЖЕШЬ ИЗМЕНИТЬ ПАРОЛЬ ТУТ
        st.success("Доступ разрешен")
        count_files = len(os.listdir(DATA_FOLDER))
        st.write(f"Собрано отчетов: **{count_files}**")
        
        if count_files > 0:
            zip_data = get_all_data_zip()
            st.download_button(
                label="📥 СКАЧАТЬ ВСЮ БАЗУ (ZIP)",
                data=zip_data,
                file_name=f"ux_dataset_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                mime="application/zip"
            )
        else:
            st.warning("База пока пуста")

if 'step' not in st.session_state: st.session_state.step = 1
if 'user_data' not in st.session_state: st.session_state.user_data = {}
if 'random_pop' not in st.session_state: st.session_state.random_pop = random.choice(get_popular_sites())
if 'random_niche' not in st.session_state: st.session_state.random_niche = random.choice(get_niche_sites())
if 'start_time' not in st.session_state: st.session_state.start_time = None

# --- ШАГ 1: ПРОФИЛЬ РЕСПОНДЕНТА ---
if st.session_state.step == 1:
    st.title("🔬 UX Research: RL Environment")
    get_device_metrics()
    
    st.markdown("""
    <div class='research-box'>
    <b>Протокол инициализации:</b> Пожалуйста, заполните профиль. Нейросети требуются демографические данные для устранения bias (когнитивных искажений) при оценке интерфейсов.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Возраст", min_value=12, max_value=90, value=25)
        gender = st.selectbox("Пол", ["Мужской", "Женский", "Предпочитаю не указывать"])
        status = st.selectbox("Семейное положение", ["Холост / Не замужем", "В браке", "В отношениях"])
    with col2:
        occupation = st.text_input("Профессия / Сфера деятельности", placeholder="Например: Аналитик, Студент")
        device_type = st.radio("Тип устройства сейчас", ["Смартфон", "Компьютер / Ноутбук", "Планшет"])
        device_brand = st.text_input("Точная марка/модель (напр. Galaxy S24, MacBook M4)", placeholder="Apple iPhone 13")
    
    if st.button("Инициализировать сессию (Шаг 1 из 3)"):
        st.session_state.user_data = {
            "demographics": {"age": age, "gender": gender, "status": status, "occupation": occupation},
            "device": {"type": device_type, "brand": device_brand},
            "session_id": str(random.randint(10000, 99999))
        }
        st.session_state.step = 2
        st.rerun()

# --- ШАГ 2: ВЫБОР ОБЪЕКТА ИССЛЕДОВАНИЯ ---
elif st.session_state.step == 2:
    st.title("Целевые среды (Environments)")
    st.write("Для калибровки RL-модели выберите систему. Мы рекомендуем чередовать лидеров рынка и локальный бизнес.")
    
    col1, col2 = st.columns(2)
    all_pop = get_popular_sites()
    all_niche = get_niche_sites()
    
    with col1:
        st.markdown("#### Эталонные (Market Leaders)")
        pop_choice = st.selectbox("Выберите сайт", all_pop, index=all_pop.index(st.session_state.random_pop))
        if st.button("Аудит лидера"):
            st.session_state.target_url = pop_choice
            st.session_state.is_popular = True
            st.session_state.step = 3
            st.rerun()

    with col2:
        st.markdown("#### Локальные (SMB)")
        niche_choice = st.selectbox("Выберите сайт", all_niche, index=all_niche.index(st.session_state.random_niche))
        if st.button("Аудит локального бизнеса"):
            st.session_state.target_url = niche_choice
            st.session_state.is_popular = False
            st.session_state.step = 3
            st.rerun()

# --- ШАГ 3: РАЗМЕТКА (TASK-BASED GOLD LABELS) ---
elif st.session_state.step == 3:
    st.title("Телеметрия интерфейса")
    st.caption(f"Target URL: {st.session_state.target_url}")
    
    if st.session_state.start_time is None:
        st.info("🎯 **Task-based Evaluation:** Попробуйте найти контактную информацию или попытайтесь добавить товар в корзину.")
        st.write("Нажмите кнопку ниже, чтобы запустить таймер инспекции (`inspection_time`).")
        if st.button("Запустить таймер и открыть сайт"):
            st.session_state.start_time = time.time()
            components.html(f"<script>window.open('{st.session_state.target_url}', '_blank');</script>", height=0)
            st.rerun()
    else:
        st.success("⏱️ Телеметрия активна. Оцените интерфейс по заданным векторам.")
        
        # 1. Trajectory & Task Validation
        st.subheader("1. Поведенческая траектория")
        c_traj1, c_traj2 = st.columns(2)
        with c_traj1:
            first_element = st.text_input("First-click target (Куда кликнули первым делом?)", placeholder="Напр: Иконка профиля, Поиск")
            time_to_understand = st.number_input("Time-to-understand (Секунд до понимания сути сайта)", min_value=1, max_value=300, value=5)
        with c_traj2:
            nav_path = st.text_input("Navigation path (Какие разделы открывали по порядку?)", placeholder="Напр: Главная -> Каталог -> Корзина")
            task_success = st.checkbox("success: Тестовая задача (поиск/корзина) выполнена")
            
        familiarity = st.radio("familiar_with_brand:", ["Вижу впервые", "Слышал бренд", "Активно пользуюсь"], horizontal=True)
        
        # 2. Binary Preference & Rage Signals
        st.subheader("2. Action & Rage Labels")
        c_bin1, c_bin2 = st.columns(2)
        with c_bin1:
            would_buy = st.checkbox("would_buy: Совершил бы транзакцию")
            would_return = st.checkbox("would_return: Вернулся бы сюда")
        with c_bin2:
            confusing = st.checkbox("confusing: Логика интерфейса запутана")
            lost_action = st.checkbox("could_not_find_action: Искал, но не нашел кнопку/раздел")

        # 3. Emotional Labels
        st.subheader("3. Emotional Context")
        emotions = st.multiselect("Выберите эмоциональные паттерны:", 
                                  ["felt_premium", "felt_safe", "felt_fast", "felt_overwhelmed", "felt_cheap", "felt_frustrated", "felt_confused"])

        # 4. Continuous Variables & Confidence
        st.subheader("4. Core Metrics (0-10)")
        mental_effort = st.slider("Mental Effort (1 - всё интуитивно, 10 - высокая когнитивная нагрузка)", 1, 10, 5)
        ui_density = st.slider("UI Density (1 - пусто, 10 - перегруз)", 1, 10, 5)
        cta_clarity = st.slider("CTA Clarity (1 - слепо, 10 - очевидно)", 1, 10, 5)
        visual_noise = st.slider("Visual Noise (1 - чисто, 10 - хаос)", 1, 10, 5)
        trust = st.slider("Perceived Trust (1 - скам, 10 - надежно)", 1, 10, 5)
        
        st.markdown("---")
        confidence = st.slider("confidence_in_rating: Насколько вы уверены в своих оценках?", 1, 10, 8)
        comment = st.text_area("Аналитический комментарий (Qualitative Data)", placeholder="Что стало триггером для ваших оценок?...")

        if st.button("Зафиксировать веса (Save Weights)"):
            if len(comment) < 10:
                st.error("Добавьте качественный фидбек (минимум пару слов)!")
            else:
                inspection_time = round(time.time() - st.session_state.start_time, 2)
                
                report = {
                    "meta": {
                        "url": st.session_state.target_url,
                        "inspection_time_sec": inspection_time,
                        "timestamp": str(datetime.now())
                    },
                    "user": st.session_state.user_data,
                    "target_attributes": {
                        "is_popular": st.session_state.is_popular,
                        "familiar_with_brand": familiarity
                    },
                    "behavioral_trajectory": {
                        "first_clicked_element": first_element,
                        "navigation_path": nav_path,
                        "time_to_understand_sec": time_to_understand,
                        "task_success": task_success
                    },
                    "gold_labels": {
                        "binary_preference": {
                            "would_buy": would_buy,
                            "would_return": would_return
                        },
                        "rage_signals": {
                            "confusing": confusing,
                            "could_not_find_action": lost_action
                        },
                        "emotional_labels": emotions
                    },
                    "continuous_metrics": {
                        "mental_effort": mental_effort / 10.0,
                        "ui_density": ui_density / 10.0,
                        "cta_clarity": cta_clarity / 10.0,
                        "visual_noise": visual_noise / 10.0,
                        "perceived_trust": trust / 10.0
                    },
                    "confidence_in_rating": confidence / 10.0,
                    "qualitative_feedback": comment
                }
                
                fname = f"rlhf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{st.session_state.user_data['session_id']}.json"
                with open(os.path.join(DATA_FOLDER, fname), "w", encoding="utf-8") as f:
                    json.dump(report, f, ensure_ascii=False, indent=4)
                
                st.session_state.last_time = inspection_time
                st.session_state.step = 4
                st.rerun()

# --- ШАГ 4: ЗАВЕРШЕНИЕ ---
elif st.session_state.step == 4:
    st.success(f"Телеметрия сохранена. Время на сайте: {st.session_state.last_time} сек.")
    
    st.markdown("---")
    if st.session_state.is_popular:
        st.info("Система рекомендует провести контрольный замер на локальном сайте для балансировки датасета.")
    else:
        st.info("Исследование локального сайта завершено. Ожидание новой итерации.")
        
    if st.button("Инициировать новый цикл"):
        st.session_state.start_time = None
        st.session_state.random_pop = random.choice(get_popular_sites())
        st.session_state.random_niche = random.choice(get_niche_sites())
        st.session_state.step = 2
        st.rerun()
