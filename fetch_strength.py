from datetime import datetime, timezone, timedelta
import json
import requests
from bs4 import BeautifulSoup


def get_currency_strength():
  url = "https://currencystrengthmeter.org/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/91.0.4472.124 Safari/537.36"
      )
  }

  try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    currency_data = {}

    containers = soup.find_all("div", class_="str-container")

    for container in containers:
      title_tag = container.find("p", class_="title")
      level_tag = container.find("div", class_="level")

      if title_tag and level_tag:
        currency = title_tag.text.strip()
        style = level_tag.get("style", "")
        strength_str = (
            style.replace("height:", "")
            .replace("%;", "")
            .replace("%", "")
            .strip()
        )

        try:
          currency_data[currency] = int(strength_str)
        except ValueError:
          currency_data[currency] = 0

    sorted_currency_data = dict(
        sorted(currency_data.items(), key=lambda item: item[1], reverse=True)
    )

    # 日本時間 (JST: UTC+9) の現在時刻を取得
    jst = timezone(timedelta(hours=9))
    now_str = datetime.now(jst).strftime("%Y-%m-%d %H:%M")

    # データ構造をラップして更新日時を持たせる
    output_data = {"updated_at": now_str, "strengths": sorted_currency_data}

    return output_data

  except Exception as e:
    print(f"Error fetching data: {e}")
    return None


if __name__ == "__main__":
  data = get_currency_strength()
  if data:
    with open("data.json", "w", encoding="utf-8") as f:
      json.dump(data, f, indent=4, ensure_ascii=False)
    print("data.json updated successfully.")
