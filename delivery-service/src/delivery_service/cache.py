import redis
import httpx
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(host='redis', port=6379, db=0)

async def get_exchange_rate():
    cache_key = "exchange_rate"
    cached_rate = redis_client.get(cache_key)
    if cached_rate:
        return float(cached_rate)

    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.cbr-xml-daily.ru/daily_json.js")
        data = response.json()
        rate = data["Valute"]["USD"]["Value"] / data["Valute"]["USD"]["Nominal"]
        redis_client.setex(cache_key, timedelta(hours=1), rate)  # Кэш на 1 час
        return rate