import csv
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 📌 検索キーワード（必要に応じて追加・変更可能）
keywords = [
    "Python 自動化",
    "Selenium",
    "スクレイピング",
    "フォーム入力",
    "Web操作"
]

# Chromeブラウザを起動
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 検索結果の新着案件を格納するリスト
all_new_jobs = []

for keyword in keywords:
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://crowdworks.jp/public/jobs?search%5Bkeywords%5D={encoded_keyword}"
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3 a"))
        )
    except Exception:
        print(f"[{keyword}] ページの読み込みに失敗しました")
        continue

    print(f"🔍 キーワード検索: {keyword}")

    # 案件一覧を取得
    jobs = driver.find_elements(By.CSS_SELECTOR, "div[class*='search_result__item']")

    for job in jobs:
        try:
            title_elem = job.find_element(By.CSS_SELECTOR, "h3 a")
            title = title_elem.text
            link = title_elem.get_attribute("href")

            time_elem = job.find_element(By.CSS_SELECTOR, "div[class*='job_data__posted']")
            time_text = time_elem.text.strip()

            if any(t in time_text for t in ["分以内", "時間以内", "24時間以内"]):
                all_new_jobs.append({
                    "キーワード": keyword,
                    "タイトル": title,
                    "リンク": link,
                    "掲載時間": time_text
                })
        except Exception as e:
            print(f"案件情報の取得エラー: {e}")

    # サーバーへの負荷軽減のため少し待機
    time.sleep(2)

driver.quit()

# CSVファイルへ保存（outputフォルダに出力）
output_path = "output/crowdworks_multi_keywords_new_jobs.csv"
import os
os.makedirs("output", exist_ok=True)

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["キーワード", "タイトル", "リンク", "掲載時間"])
    writer.writeheader()
    writer.writerows(all_new_jobs)

print(f"\n✅ 合計 {len(all_new_jobs)} 件の新着案件を保存しました：{output_path}")
