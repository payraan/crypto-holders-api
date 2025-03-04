from fastapi import FastAPI, HTTPException
import requests
import os
import uvicorn
from typing import Optional
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

app = FastAPI()

# مقدار API Key از متغیر محیطی
HOLDERSCAN_API_KEY = os.getenv("HOLDERSCAN_API_KEY", "3895e3019d79363e91a10983904c49bae2c4a7ff2db12caf124f5fe68143069c")

BASE_URL = "https://api.holderscan.com"
HEADERS = {
    "Accept": "application/json",
    "X-API-Key": HOLDERSCAN_API_KEY,
    "User-Agent": "Crypto-Analyst-GPT"
}

# نگاشت نام شبکه به chain_id
CHAIN_ID_MAP = {
    "solana": "solana",
    "eth": "ethereum",
    "bsc": "bsc"
}

@app.get("/")
def home():
    return {"message": "✅ API HolderScan روی سرور اجرا شده است!"}

# تابع کمکی برای ارسال درخواست به HolderScan با لاگ بیشتر
async def fetch_from_holderscan(endpoint: str, params: Optional[dict] = None):
    url = f"{BASE_URL}{endpoint}"
    
    # لاگ برای دیباگ
    print(f"Sending request to: {url}")
    print(f"With params: {params}")
    print(f"With headers: {HEADERS}")
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        # لاگ برای دیباگ
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text[:500]}...")  # فقط 500 کاراکتر اول برای جلوگیری از لاگ بزرگ
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="❌ Bad Request: Invalid Parameters")
        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="❌ Unauthorized: Invalid API Key")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="❌ Not Found: Invalid Token or Parameters")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"⚠ Unexpected Error: {response.text}")
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Connection Error: {str(e)}")

# تبدیل نام شبکه به chain_id
def get_chain_id(network: str):
    if network.lower() in CHAIN_ID_MAP:
        return CHAIN_ID_MAP[network.lower()]
    raise HTTPException(status_code=400, detail=f"❌ Unsupported network: {network}. Use one of: {', '.join(CHAIN_ID_MAP.keys())}")

# 1️⃣ دریافت اطلاعات توکن
@app.get("/token/{network}/{address}")
async def get_token_info(network: str, address: str):
    """
    دریافت اطلاعات کلی توکن مانند نام، نماد، Market Cap و تعداد حساب‌های فعال
    """
    try:
        chain_id = get_chain_id(network)
        
        # توجه: مسیر دقیق در داکیومنت برای دریافت اطلاعات توکن مشخص نشده است
        # برای تست، از مسیر tokens استفاده می‌کنیم
        return await fetch_from_holderscan(f"/v0/{chain_id}/tokens/{address}")
    except HTTPException as e:
        # ارسال پاسخ خطا به کاربر
        raise e
    except Exception as e:
        print(f"Error in get_token_info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 2️⃣ دریافت اطلاعات کامل هولدرها
@app.get("/holders/breakdowns/{network}/{address}")
async def get_holders_breakdown(network: str, address: str):
    """
    دریافت تحلیل کامل توزیع هولدرها، دسته‌بندی‌ها و تمرکز هولدرها
    """
    try:
        chain_id = get_chain_id(network)
        return await fetch_from_holderscan(f"/v0/{chain_id}/tokens/{address}/holders/breakdowns")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_holders_breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 3️⃣ دریافت روند تغییرات هولدرها
@app.get("/holders/trends/{network}/{address}")
async def get_holders_trends(network: str, address: str, period: str = "day"):
    """
    دریافت روند تغییرات هولدرها در بازه‌های زمانی مختلف (hour, day, week)
    """
    try:
        chain_id = get_chain_id(network)
        return await fetch_from_holderscan(f"/v0/{chain_id}/tokens/{address}/holders/deltas")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_holders_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 4️⃣ دریافت لیست هولدرهای برتر
@app.get("/holders/top/{network}/{address}")
async def get_top_holders(network: str, address: str, limit: int = 10):
    """
    دریافت لیست هولدرهای برتر توکن
    """
    try:
        chain_id = get_chain_id(network)
        return await fetch_from_holderscan(f"/v0/{chain_id}/tokens/{address}/holders", {"limit": limit})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_top_holders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 5️⃣ تحلیل کامل توکن (ترکیب همه API‌ها)
@app.get("/token/analysis/{network}/{address}")
async def get_token_analysis(network: str, address: str):
    """
    تحلیل کامل توکن شامل اطلاعات پایه، هولدرها، روندها و صرافی‌ها
    """
    try:
        # ساده‌سازی شده برای تست - در نسخه نهایی باید همه APIها ترکیب شوند
        token_info = await get_token_info(network, address)
        holders_breakdown = await get_holders_breakdown(network, address)
        holders_trends = await get_holders_trends(network, address)
        top_holders = await get_top_holders(network, address)
        
        # ترکیب نتایج
        return {
            "token_info": token_info,
            "holders": {
                "breakdown": holders_breakdown,
                "trends": holders_trends,
                "top_holders": top_holders
            },
            "analysis": {
                "message": "تحلیل کامل توکن با موفقیت انجام شد"
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in get_token_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# تست ساده API key و اتصال به HolderScan
@app.get("/test-api-key")
async def test_api_key():
    """
    تست اعتبار API key و اتصال به HolderScan
    """
    try:
        # یک درخواست ساده برای بررسی اعتبار API key
        # چون مسیر مشخصی برای تست در داکیومنت نیست، از یک توکن معروف استفاده می‌کنیم
        url = f"{BASE_URL}/v0/solana/tokens/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/holders"
        params = {"limit": 1}
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            return {"status": "success", "message": "API key معتبر است و اتصال به HolderScan برقرار است", "data": response.json()}
        else:
            return {"status": "error", "message": f"خطا: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"status": "error", "message": f"خطای اتصال: {str(e)}"}

# اجرای سرور با دریافت پورت از متغیر محیطی
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8082))
    uvicorn.run(app, host="0.0.0.0", port=port)
