import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# 1. تحميل المفتاح السري
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if not api_key:
    st.error("❌ لم يتم العثور على API Key! يرجى التأكد من ضبط Secrets في Streamlit Cloud")
    st.stop()

# 2. إنشاء اتصال السيرفر مع المكتبة الجديدة
@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)

client = get_client(api_key)

# 3. إعداد صفحة الموقع
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 مساعد الذكاء الاصطناعي")

# 4. إدارة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(model="gemini-2.5-flash")

# 5. عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. استقبال المدخلات وإرسالها
user_prompt = st.chat_input("اكتب رسالتك هنا...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ جاري التفكير...")
        try:
            response = st.session_state.chat.send_message(user_prompt)
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            message_placeholder.markdown(f"❌ حدث خطأ: {str(e)}")
