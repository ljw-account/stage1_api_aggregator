import httpx
import asyncio

APIS = {
    "天氣": "https://api.open-meteo.com/v1/forecast?latitude=22.99&longitude=120.21&current_weather=true",
    "比特幣": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
    "新聞": "https://hacker-news.firebaseio.com/v0/topstories.json"
}

async def fetch_one(client, name, url):
    try:
        response = await client.get(url)
        response.raise_for_status()
        print(f"{name} 取得成功")
        return name, response.json()
    except httpx.HTTPStatusError as e:
        print(f"{name} 回傳錯誤狀態碼 : {e.response.status_code}")
        return name, None
    except httpx.ConnectError:
        print(f"{name} 無法連線")
        return name, None
    
def parse_results(results):
    report = {}
    for name, data in results:
        if data is None:
            report[name] = "資料取得失敗"
            continue
        if name == "天氣":
            report[name] = {
                "溫度": data["current_weather"]["temperature"],
                "風速": data["current_weather"]["windspeed"]
            }
        elif name == "比特幣":
            report[name] = {
                "美元價格": data["bitcoin"]["usd"]
            }
        elif name == "新聞":
            report[name] = {
                "熱門文章ID": data[:5]
            }
    return report

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [fetch_one(client, name, url) for name, url in APIS.items()]
        results = await asyncio.gather(*tasks)
        report = parse_results(results)
        for name, content in report.items():
            print(f"\n【{name}】")
            if isinstance(content, dict):
                for key, value in content.items():
                    print(f"  {key}：{value}")
            else:
                print(f"  {content}")

asyncio.run(main())