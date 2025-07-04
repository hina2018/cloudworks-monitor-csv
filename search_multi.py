import csv
import time
import os
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 🔍 検索キーワード一覧
keywords = [
    "Python 自動化",
    "Selenium",
    "スクレイピング",
    "フォーム入力",
    "Web操作"
]

# ブラウザ起動
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 新着案件を格納するリスト
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
        print(f"[{keyword}] ページ読み込み失敗")
        continue

    print(f"🔎 検索中: {keyword}")

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
            print(f"取得エラー: {e}")

    time.sleep(2)  # サーバー負荷軽減のため待機

driver.quit()

# 出力フォルダ作成
os.makedirs("output", exist_ok=True)
output_file = "output/crowdworks_multi_keywords_new_jobs.csv"

# CSVに保存
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["キーワード", "タイトル", "リンク", "掲載時間"])
    writer.writeheader()
    writer.writerows(all_new_jobs)

print(f"\n✅ {len(all_new_jobs)} 件の新着案件を保存しました（{output_file}）")
