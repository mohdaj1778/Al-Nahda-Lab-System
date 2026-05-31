import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# إعدادات الصفحة الأساسية للتطبيق
st.set_page_config(
    page_title="دليل مختبر مدرسة النهضة الثانوية الشاملة للبنين",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تصميم واجهة النظام الشاملة بالألوان المعتمدة (الأخضر والظلال الاحترافية)
st.markdown("""
    <style>
    /* تنسيق اتجاه الصفحة من اليمين إلى اليسار */
    .main .block-container {
        direction: RTL;
        text-align: right;
    }
    
    /* الهيدر العلوي الرئيسي للنظام */
    .main-header {
        background: linear-gradient(135deg, #1e5631 0%, #4c9a2a 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* تنسيق أزرار الاختيار (Radio Buttons) لتظهر كبطاقات احترافية */
    div.row-widget.stRadio > div {
        flex-direction: row !important;
        justify-content: center;
        gap: 20px;
    }
    div.row-widget.stRadio label {
        background-color: #f1f8f5;
        padding: 12px 25px;
        border-radius: 10px;
        border: 2px solid #e1eedd;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    div.row-widget.stRadio label:hover {
        border-color: #4c9a2a;
        background-color: #eef7f2;
    }
    
    /* شريط البحث */
    .stTextInput input {
        text-align: right;
        border-radius: 10px;
        border: 2px solid #cbd5e1;
        padding: 12px;
    }
    .stTextInput input:focus {
        border-color: #4c9a2a;
        box-shadow: 0 0 0 1px #4c9a2a;
    }
    
    /* تنسيق صندوق عرض تفاصيل العنصر المختار */
    .custom-top-bar {
        background-color: #4c9a2a;
        color: white;
        padding: 12px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px 8px 0 0;
        text-align: center;
        margin-top: 20px;
    }
    .details-box {
        border: 2px solid #4c9a2a;
        border-radius: 0 0 8px 8px;
        padding: 20px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    
    /* تنسيق جدول البيانات */
    .dataframe {
        width: 100% !important;
        direction: rtl !important;
        text-align: right !important;
        border-collapse: collapse;
    }
    .dataframe th {
        background-color: #1e5631 !important;
        color: white !important;
        padding: 12px !important;
        text-align: right !important;
    }
    .dataframe td {
        padding: 10px !important;
        border: 1px solid #e2e8f0 !important;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# عرض الهيدر الرئيسي للموقع بنجاح
st.markdown("""
    <div class="main-header">
        <h1>🏛️ دليل مختبر مدرسة النهضة الثانوية الشاملة للبنين المصور</h1>
    </div>
""", unsafe_allow_html=True)

# دالة لقراءة ملفات البيانات وتجنب مشاكل الترميز للغة العربية
@st.cache_data
def load_data(file_name):
    if os.path.exists(file_name):
        try:
            return pd.read_csv(file_name, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file_name, encoding='windows-1256')
    return pd.DataFrame()

# تحميل البيانات الأساسية
df_chem = load_data("chem.csv")
df_items = load_data("items.csv")

# القائمة العلوية لاختيار السجل المطلوب تصفحه
selected_registry = st.radio(
    "📁 السجل:",
    ["الأصناف العامة", "المواد الكيميائية"],
    index=0
)

# تحديد جدول البيانات النشط بناءً على خيار المستخدم
if selected_registry == "المواد الكيميائية":
    df_active = df_chem
    search_placeholder = "ابحث عن مادة كيميائية باسمها أو صيغتها..."
else:
    df_active = df_items
    search_placeholder = "ابحث عن صنف عام باسمه أو رقمه..."

if not df_active.empty:
    # خانة البحث الذكي والمنظم
    search_query = st.text_input("🔍 ابحث:", placeholder=search_placeholder)
    
    # فلترة البيانات بناءً على نص البحث في كل الأعمدة
    if search_query:
        mask = df_active.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        df_filtered = df_active[mask]
    else:
        df_filtered = df_active

    # إنشاء تقسيم الواجهة: الجدول على اليمين والتفاصيل مع الصورة على اليسار
    col_table, col_details = st.columns([3, 2])
    
    with col_table:
        st.write(f"📊 النتائج المتاحة ({len(df_filtered)}):")
        
        # تحويل اسم العنصر أو المادة إلى قائمة منسدلة للاختيار والعرض المباشر
        item_names = df_filtered.iloc[:, 1].tolist() if len(df_filtered) > 0 else []
        
        if item_names:
            selected_item_name = st.selectbox("🎯 اختر صنفاً لعرض تفاصيله وصورته المعتمدة:", item_names)
            selected_row = df_filtered[df_active.iloc[:, 1] == selected_item_name].iloc[0]
            
            # عرض جدول البيانات بالكامل تحت القائمة بشكل أنيق وجذاب
            st.markdown(df_filtered.to_html(index=False, classes='dataframe'), unsafe_allow_html=True)
        else:
            st.warning("⚠️ لا توجد نتائج مطابقة لبحثك الحالي.")
            selected_row = None
            
    with col_details:
        if selected_row is not None:
            # هنا تم تصحيح الخاصية البرمجية لتصبح متوافقة تماماً ومنع الشاشة الحمراء
            st.markdown('<div class="custom-top-bar">معلومات الصورة والوصف الفني 📝</div>', unsafe_allow_html=True)
            
            with st.container():
                st.markdown('<div class="details-box">', unsafe_allow_html=True)
                
                # جلب مسار الصورة المباشر من المجلد الخارجي للمستودع بناءً على العمود الأخير
                image_file_name = str(selected_row.iloc[-1]).strip()
                
                # قراءة وعرض الصورة مباشرة من الخارج بجانب ملف app.py
                if image_file_name and os.path.exists(image_file_name):
                    st.image(image_file_name, use_container_width=True, caption=f"الصورة الرقمية المعتمدة لـ: {selected_item_name}")
                else:
                    st.info(f"📁 لم يتم العثور على ملف الصورة الخارجي ({image_file_name}) في المستودع حالياً.")
                
                # عرض التفاصيل الفنية والبيانات الكاملة للعنصر المختار داخل الصندوق التنسيقي
                st.write("---")
                for col_name, value in selected_row.items():
                    # عرض كل البيانات عدا اسم ملف الصورة للحفاظ على المظهر العام
                    if col_name != df_active.columns[-1]:
                        st.markdown(f"**• {col_name}:** {value}")
                        
                st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("❌ عذراً، لم يتم العثور على ملفات البيانات المطلوبة في المستودع، يرجى التأكد من رفع ملفات csv.")
