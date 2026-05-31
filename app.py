import streamlit as st
import pandas as pd
import os
import urllib.parse
import google.generativeai as genai

# تم ضبط تهيئة المفتاح وتفعيل البحث الذكي عن النموذج المدعوم تلقائياً
MY_API_KEY = "AIzaSyBKvBYlXKCsfkshd7TyHf6FJV84xHH2BUQ"
genai.configure(api_key=MY_API_KEY)

# 1. إعداد الصفحة
st.set_page_config(page_title="نظام مختبر مدرسة النهضة الثانوية للبنين", layout="wide")

# 2. التنسيق الجمالي المطور (CSS) - الهوية الجديدة باللون الأخضر الفاتح والمريح
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        direction: RTL; text-align: right; background-color: #f7faf8;
    }
    [data-testid="stSidebar"] { display: none; }

    /* تقليل مساحة الحاوية العلوية */
    [data-testid="stHeader"] { height: 0px; }
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }

    /* شريط التحكم العلوي - أخضر مريح ومتدرج خفيف */
    .stHorizontalBlock {
        background: linear-gradient(90deg, #3b7a57, #4caf50);
        padding: 12px 20px; border-radius: 15px; margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); color: white !important;
    }

    label, .stMarkdown p {
        color: white !important; font-size: 1.1rem !important;
        font-weight: bold !important; margin-bottom: 2px !important;
    }

    .stRadio div[role="radiogroup"] label {
        font-size: 1rem !important; background: rgba(255, 255, 255, 0.2);
        padding: 4px 12px; border-radius: 8px;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 1.1rem !important; height: 40px !important; border-radius: 8px !important;
    }

    /* تصميم الأشرطة العلوية - أخضر فاتح متناسق */
    .custom-top-bar {
        background-color: #4caf50; 
        color: white !important; 
        text-align: center; 
        padding: 8px 15px; 
        border-radius: 12px 12px 0 0; 
        font-size: 1.2rem; 
        font-weight: bold;
        border: 2px solid #3b7a57;
        border-bottom: none;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.03);
    }

    /* صندوق معلومات المادة */
    .green-info-box {
        background: white; padding: 25px; border-radius: 0 0 20px 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.03); border: 2px solid #e2ece6;
        border-top: none;
        border-right: 8px solid #4caf50;
    }

    .main-title-green {
        color: #2e6930; font-size: 2.2rem; font-weight: bold; margin-top: 0; margin-bottom: 5px;
    }

    .details-header-green {
        color: #3b7a57; font-size: 1.4rem; margin-bottom: 15px;
        border-bottom: 3px solid #a1dfa4; display: inline-block; 
        padding-bottom: 3px; font-weight: bold;
    }

    /* 🟢 صفوف البيانات البيضاء - تم تكبير الخط لـ 1.5rem وإضافة مسافة أمان عن الحافة اليمنى */
    .data-row-green {
        background: white !important;
        padding: 15px 25px !important; 
        padding-right: 1cm !important; /* مسافة أمان صغيرة لإبعاد النص عن الحافة اليمنى */
        margin-bottom: 12px;
        border-radius: 10px; 
        display: flex; 
        align-items: center; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* تكبير خط العناوين الفرعية (مثل: اسم الصنف:) */
    .data-label-green { 
        color: #2e6930 !important; 
        font-weight: bold !important; 
        min-width: 280px !important; /* زيادة العرض ليتناسق مع الخط الكبير الجديد ويمسك مكانه */
        font-size: 2rem !important;  
    }
    
    /* تكبير خط القيم (مثل: ترمومتر مئوي...) */
    .data-value-green { 
        color: #334135 !important; 
        font-size: 2rem !important;  
        font-weight: bold !important; 
    }

    /* صندوق الصورة الأيسر */
    .green-image-box {
        background: white; padding: 20px; border-radius: 0 0 20px 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.03); border: 2px solid #e2ece6;
        border-top: none;
        text-align: center;
        margin-bottom: 15px;
    }
    .image-border { border-radius: 12px; overflow: hidden; border: 1px solid #e2ece6; }
    
    /* 🎯 تنسيق صندوق إجابة جيميناي ممتد العرض (تم ضبط الخط والمحاذاة والمسافة البادئة للنتائج فقط) */
    .gemini-response-box {
        background-color: #ffffff;
        padding: 25px;
        padding-right: 1.5cm !important; /* مسافة بادئة آمنة 1.5 سم من حافة الصفحة اليمنى */
        text-align: right !important;    /* إجبار النص على محاذاة اليمين بالكامل */
        border-radius: 15px;
        border-right: 8px solid #0066cc;
        box-shadow: 0 6px 20px rgba(0,0,0,0.05);
        margin-top: 15px;
        width: 100%;
        color: black !important;
        font-size: 2.15rem !important;   /* حجم خط نتائج جيميناي الكبير والمطلوب */
        line-height: 2.6 !important;
    }

    /* 🧠 التنسيق الاحترافي الكامل للزر الأزرق الممتد والملتصق بالكامل من الأسفل */
    div.stButton > button:first-child {
        background-color: #0066cc !important;
        color: #ffffff !important;
        font-size: 2rem !important;       /* ضبط خط حافة الزر بـ 2rem */
        font-weight: bold !important;
        border-radius: 0px 0px 8px 8px !important;
        border: none !important;
        padding: 12px 0px !important;
        margin-top: 0px !important;
        height: auto !important;          /* إعطاء مساحة للزر ليتسع للخط الكبير */
    }
    
    /* إجبار النص الداخلي للزر بكل مستوياته وعناصره الفرعية على أخذ حجم 2rem */
    div.stButton > button:first-child * {
        font-size: 2rem !important;       /* إجبار النص المكتوب داخل الزر على مقاس 2rem */
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    div.stButton {
        margin-top: -16px !important;
    }
    
    div.stButton > button:first-child:hover {
        background-color: #0052a3 !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. دالة جلب البيانات المعدلة للبحث في مسار السكريبت المباشر
def load_data(prefix):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(base_dir) if f.lower().startswith(prefix.lower())]
    if files:
        target = os.path.join(base_dir, files[0])
        try:
            if target.endswith('.xlsx'): 
                return pd.read_excel(target)
            
            for sep in [',', ';']:
                for enc in ['utf-8-sig', 'cp1256', 'utf-8']:
                    try:
                        df = pd.read_csv(target, encoding=enc, sep=sep, on_bad_lines='skip')
                        if len(df.columns) >= 2: 
                            return df
                    except: 
                        continue
            return None
        except: 
            return None
    return None

translate_cols = {
    'item_id': 'رقم العهدة', 'item_name': 'اسم الصنف', 'en_name': 'الاسم العلمي (EN)',
    'sup': 'القسم الرئيسي', 'sub_scince': 'التصنيف', 'ch_form': 'الصيغة الكيميائية',
    'chem_cls': 'تصنيف المادة الكيميائية', 'الوصف': 'الاسم العلمي بالعربي', 'alsiga': 'الصيغة الجزيئية'
}

# 4. واجهة التحكم العلوي
st.markdown('<h2 style="text-align:center; padding:5px; color:#2e6930; margin-top:-20px;">🏛️ دليل مختبر مدرسة النهضة الثانوية الشاملة للبنين المصور</h2>', unsafe_allow_html=True)

with st.container():
    col1, col2, col3 = st.columns([1, 1, 1.2])
    
    with col1:
        category = st.radio("📂 السجل:", ["الأصناف العامة", "المواد الكيميائية"], horizontal=True)
    
    with col2:
        search_input = st.text_input("🔍 ابحث:")
        
    prefix = 'items' if category == "الأصناف العامة" else 'chem'
    df = load_data(prefix)
    
    with col3:
        options_list = ["--- اختر ---"]
        
        if df is not None:
            df.columns = [c.strip() for c in df.columns]
            if category == "المواد الكيميائية":
                if 'الوصف' in df.columns and 'ch_form' in df.columns:
                    df['display_name'] = df['الوصف'].astype(str) + " - " + df['ch_form'].astype(str)
                else:
                    df['display_name'] = df[df.columns[1]].astype(str)
                name_col = 'display_name'
            else:
                name_col = df.columns[1]
            
            mask = df[name_col].astype(str).str.contains(search_input, na=False, case=False)
            df_display = df[mask]
            options_list += df_display[name_col].tolist()
        
        chosen_display_name = st.selectbox("🎯 النتائج:", options_list)

st.markdown("<br>", unsafe_allow_html=True)

# 5. العرض الرئيسي للمادة المختارة
if df is not None and chosen_display_name != "--- اختر ---":
    if category == "المواد الكيميائية":
        item_data = df[df['display_name'] == chosen_display_name].iloc[0]
        item_title = str(item_data['الوصف']) if 'الوصف' in df.columns else chosen_display_name
    else:
        item_data = df[df[df.columns[1]] == chosen_display_name].iloc[0]
        item_title = chosen_display_name

    col_info, col_img = st.columns([1.4, 1])
    
    with col_info:
        st.markdown('<div class="custom-top-bar">📝 معلومات الصورة والوصف الفني</div>', unsafe_allow_html=True)
        st.markdown('<div class="green-info-box">', unsafe_allow_html=True)
        st.markdown(f'<div class="main-title-green">{item_title}</div>', unsafe_allow_html=True)
        st.markdown('<div class="details-header-green">المواصفات الفنية المطلوبة</div>', unsafe_allow_html=True)
        
        for i in range(1, len(df.columns)):
            label = df.columns[i]
            if label == 'display_name': continue
            arabic_label = translate_cols.get(label, label)
            val = item_data.iloc[i]
            if pd.notna(val) and str(val).strip() not in ["", "-", "nan"]:
                st.markdown(f"""
                    <div class="data-row-green">
                        <span class="data-label-green">{arabic_label}:</span>
                        <span class="data-value-green">{val}</span>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_img:
        st.markdown('<div class="custom-top-bar">🖼️ انظر الصورة التوضيحية </div>', unsafe_allow_html=True)
        st.markdown('<div class="green-image-box">', unsafe_allow_html=True)
        
        raw_id = str(item_data.iloc[0]).strip().replace("/", "-")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_p = os.path.join(base_dir, "images", f"{raw_id}.jpg")
        
        if os.path.exists(img_p):
            st.image(img_p, use_container_width=True)
        else:
            st.warning(f"⚠️ الصورة غير متوفرة في المسار المحدد للمادة.")
        st.markdown('</div>', unsafe_allow_html=True)

    # 🛠️ زر جيميناي ممتد ومكتوب بالصيغة المطلوبة وملتصق بأسفل الصناديق مباشرة
    if st.button(f"✨ هل ترغب في معلومات أكثر عن استخدامات ({item_title})؟", use_container_width=True):
        with st.spinner("جاري الاتصال بـ Gemini وجلب المعلومات الدقيقة ممتدة العرض..."):
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                if available_models:
                    selected_model_name = available_models[0]
                    model = genai.GenerativeModel(selected_model_name)
                    prompt = f"أنت خبير مختبرات علمية متميز، اشرح لي بالتفصيل وبنقاط واضحة ومنسقة باللغة العربية استخدامات '{item_title}' في مختبر المدرسة، والفوائد التعليمية، والتحذيرات الأساسية للسلامة العامة عند التعامل معه."
                    response = model.generate_content(prompt)
                    
                    st.success("🤖 إجابة Google Gemini الكاملة ممتدة العرض:")
                    st.markdown(f'<div class="gemini-response-box">{response.text}</div>', unsafe_allow_html=True)
                else:
                    st.error("لم يتم العثور على أي نماذج توليد نصوص مدعومة في هذا الإصدار.")
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بـ Gemini: {str(e)}")

else:
    welcome_msg = "يرجى اختيار <b>نوع السجل</b> ثم استخدام صندوق <b>البحث</b> أو اختر مباشرة من <b>قائمة النتائج</b> بالأعلى لعرض مواصفات الأصناف الكيميائية والعامة وصورها المخزنة فوراً."
    if df is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        welcome_msg = f"<b style='color:red;'>⚠️ تنبيه: لم يتمكن الكود من قراءة الملفات من المسار التلقائي للمشروع: ({base_dir}).</b> يرجى التأكد من وجود ملفات chem.csv أو items.csv داخل هذا المجلد بالذات."
        
    st.markdown(f"""
        <div class="welcome-card_green" style="background: white; padding: 40px; border-radius: 25px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid #e2ece6; border-top: 6px solid #4caf50; margin-top: 20px;">
            <div class="welcome-title" style="color: #2e6930; font-size: 2rem; font-weight: bold; margin-bottom: 15px;">👋 مرحباً بك في الدليل الرقمي المصور لشؤون المختبرات</div>
            <div class="welcome-text" style="color: #556b57; font-size: 1.2rem; font-weight: normal; direction: rtl;">
                {welcome_msg}
            </div>
            <br>
            <span style="font-size: 2.2rem; color: #2e6930; font-weight: bold; display: block;">🔬🧪 إعداد قيم المختبر: محمد الأجرب 📚</span>
        </div>
    """, unsafe_allow_html=True)