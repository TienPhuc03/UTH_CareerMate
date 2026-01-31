# server/test_ai.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Thiếu API Key")
    exit()

client = genai.Client(api_key=api_key)

print(f"📡 Đang hỏi Google danh sách model cho Key: {api_key[:5]}...")

try:
    # Lấy danh sách các model
    # Lưu ý: Với SDK mới (google-genai), cú pháp list hơi khác
    # Chúng ta sẽ thử gọi model cơ bản nhất để test
    
    print("\n--- THỬ NGHIỆM MODEL CỤ THỂ ---")
    
    # Danh sách các tên model có thể đúng. Hãy thử lần lượt.
    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-3-flash-preview"
    ]
    
    for model_name in candidates:
        print(f"\n👉 Đang thử model: {model_name}")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hello, are you working?"
            )
            print(f"✅ THÀNH CÔNG! Model chuẩn là: {model_name}")
            print(f"   Trả lời: {response.text}")
            break # Tìm thấy rồi thì dừng lại
        except Exception as e:
            if "404" in str(e):
                print(f"❌ Không tìm thấy (404)")
            else:
                print(f"⚠️ Lỗi khác: {e}")

except Exception as e:
    print(f"Lỗi chung: {e}")