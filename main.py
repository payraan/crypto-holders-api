from fastapi import FastAPI, HTTPException
import requests
import os
import uvicorn
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

@app.get("/")
def home():
    return {"message": "✅ API HolderScan روی سرور اجرا شده است!"}

# تابع کمکی برای ارسال درخواست به HolderScan
async def fetch_from_holderscan(endpoint: str, params: dict = None):
    url = f"{BASE_URL}{endpoint}"
    
    print(f"🔍 Sending request to: {url}")
    print(f"🔍 Headers: {HEADERS}")
    print(f"🔍 Params: {params}")

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        
        print(f"✅ Response status: {response.status_code}")
        print(f"✅ Response content: {response.text[:500]}...")  # نمایش فقط 500 کاراکتر اول

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="❌ Bad Request: Invalid Parameters")
        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="❌ Unauthorized: Invalid API Key")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="❌ Not Found: Invalid Token or Parameters")
        elif response.status_code == 500:
            raise HTTPException(status_code=500, detail="❌ Server Error from HolderScan")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"⚠ Unexpected Error: {response.text}")

    except requests.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Connection Error: {str(e)}")

# 1️⃣ دریافت اطلاعات توکن (با پارامتر network)
@app.get("/token/{network}/{address}")
async def get_token_info(network: str, address: str):
    """
    دریافت اطلاعات کلی توکن برای شبکه مشخص شده
    """
    if network.lower() != "solana":
        raise HTTPException(status_code=400, detail="❌ در حال حاضر فقط شبکه solana پشتیبانی می‌شود")
    
    try:
        return await fetch_from_holderscan(f"/v0/solana/tokens/{address}")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error in get_token_info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 2️⃣ دریافت اطلاعات کامل هولدرها
@app.get("/holders/breakdowns/{network}/{address}")
async def get_holders_breakdown(network: str, address: str):
    """
    دریافت تحلیل کامل توزیع هولدرهای توکن
    """
    if network.lower() != "solana":
        raise HTTPException(status_code=400, detail="❌ در حال حاضر فقط شبکه solana پشتیبانی می‌شود")
    
    try:
        return await fetch_from_holderscan(f"/v0/solana/tokens/{address}/holders/breakdowns")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error in get_holders_breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 3️⃣ دریافت روند تغییرات هولدرها
@app.get("/holders/trends/{network}/{address}")
async def get_holders_trends(network: str, address: str, period: str = "day"):
    """
    دریافت روند تغییرات تعداد هولدرها در بازه‌های زمانی مختلف
    """
    if network.lower() != "solana":
        raise HTTPException(status_code=400, detail="❌ در حال حاضر فقط شبکه solana پشتیبانی می‌شود")
    
    try:
        return await fetch_from_holderscan(f"/v0/solana/tokens/{address}/holders/deltas")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error in get_holders_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 4️⃣ دریافت لیست هولدرهای برتر
@app.get("/holders/top/{network}/{address}")
async def get_top_holders(network: str, address: str, limit: int = 10):
    """
    دریافت لیست هولدرهای برتر توکن
    """
    if network.lower() != "solana":
        raise HTTPException(status_code=400, detail="❌ در حال حاضر فقط شبکه solana پشتیبانی می‌شود")
    
    try:
        return await fetch_from_holderscan(f"/v0/solana/tokens/{address}/holders", {"limit": limit})
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error in get_top_holders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 5️⃣ اضافه کردن CEX holdings (برای تطابق با اسکمای GPT)
@app.get("/holders/cex/{network}/{address}")
async def get_cex_holdings(network: str, address: str):
    """
    دریافت اطلاعات نگهداری توکن در صرافی‌های متمرکز
    """
    if network.lower() != "solana":
        raise HTTPException(status_code=400, detail="❌ در حال حاضر فقط شبکه solana پشتیبانی می‌شود")
    
    # توجه: اگر HolderScan اطلاعات CEX ندارد، می‌توانید یک پاسخ ثابت برگردانید
    try:
        # این یک پاسخ موقت است - در صورت وجود API مناسب، آن را جایگزین کنید
        return {
            "message": "اطلاعات CEX در حال حاضر در دسترس نیست",
            "cex_holdings": {
                "total_percentage": 0,
                "exchanges": []
            }
        }
    except Exception as e:
        print(f"❌ Error in get_cex_holdings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# 6️⃣ تحلیل کامل توکن (ترکیب همه API‌ها)
@app.get("/token/analysis/{network}/{address}")
async def get_token_analysis(network: str, address: str):
    """
    تحلیل کامل توکن شامل اطلاعات پایه، هولدرها، روندها
    """
    if network.lower() != "solana":
        raise HTTPException(status_code=400, detail="❌ در حال حاضر فقط شبکه solana پشتیبانی می‌شود")
    
    try:
        # دریافت اطلاعات از همه APIها
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
        print(f"❌ Error in get_token_analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"❌ Server Error: {str(e)}")

# تست ساده API key و اتصال به HolderScan
@app.get("/test-api-key")
async def test_api_key():
    """
    تست اعتبار API key و اتصال به HolderScan
    """
    try:
        url = f"{BASE_URL}/v0/solana/tokens/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/holders"
        params = {"limit": 1}
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            return {"status": "success", "message": "API key معتبر است و اتصال به HolderScan برقرار است", "data": response.json()}
        else:
            return {"status": "error", "message": f"خطا: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"status": "error", "message": f"❌ خطای اتصال: {str(e)}"}

# اجرای سرور
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8082))
    uvicorn.run(app, host="0.0.0.0", port=port)
