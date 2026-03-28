import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def list_and_test_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY tidak ditemukan di file .env")
        return

    print(f"🔍 Mencoba koneksi dengan API Key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        genai.configure(api_key=api_key)
        
        print("\n--- Model Terintegrasi ---")
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                available_models.append(m.name)
        
        if not available_models:
            print("❌ Tidak ada model yang mendukung generateContent ditemukan untuk key ini.")
            return

        # Ambil model pertama yang ada di list (biasanya gemini-1.5-flash atau pro)
        target_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
        
        print(f"\n🚀 Mencoba testing dengan model: {target_model}")
        model = genai.GenerativeModel(target_model.replace("models/", ""))
        response = model.generate_content("Say hello from AI!")
        
        print(f"✅ BERHASIL! Respons: {response.text.strip()}")
            
    except Exception as e:
        print(f"❌ KONEKSI GAGAL: {e}")
        print("\n💡 Tip: Pastikan API Key Anda sudah diaktifkan di AI Studio (https://aistudio.google.com/) dan project sudah benar.")

if __name__ == "__main__":
    list_and_test_models()
