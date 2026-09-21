import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# 1. تحميل المفتاح السري من ملف .env
load_dotenv()

# الحصول على المفتاح من ملف .env أو من Streamlit Secrets عند النشر
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error("❌ لم يتم العثور على API Key! يرجى التأكد من وضع المفتاح داخل ملف .env")
    st.stop()

# إعداد الاتصال بـ Gemini API
genai.configure(api_key=api_key)

# 2. إعداد صفحة الموقع
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 مساعد الذكاء الاصطناعي")

# 3. تحميل نموذج Gemini المحدث الموصى به
@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-3.6-flash')

model = load_model()

# 4. إنشاء جلسة المحادثة في الذاكرة المؤقتة (بدون قاعدة بيانات)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 5. عرض سجل المحادثة السابق في الشاشة
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else message.role
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 6. مربع إدخال النص واستقبال سؤال المستخدم
user_prompt = st.chat_input("اكتب رسالتك هنا...")

if user_prompt:
    # عرض سؤال المستخدم فوراً
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # إرسال السؤال إلى Gemini واستقبال الرد
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ جاري التفكير...")
        
        try:
            response = st.session_state.chat_session.send_message(user_prompt)
            message_placeholder.markdown(response.text)
        except Exception as e:
            message_placeholder.markdown(f"❌ حدث خطأ: {str(e)}")
