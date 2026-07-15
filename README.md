# Windows Streamlit + Playwright + ChatGPT 自動化網站

本專案提供 Windows 11 本機執行的 Streamlit 網站，包含民國日期轉西元、地址補全、客服文字修飾，以及透過 Playwright 控制已登入 ChatGPT 的功能。專案不使用 OpenAI API。

## 專案目錄

```text
.
├── app.py                    # Streamlit 入口與頁面排版
├── api/                      # Streamlit 與服務層之間的薄 API/handler
├── browser/user_data/        # Chrome Persistent Context 登入資料
├── config/                   # 設定與 ChatGPT selectors 集中管理
├── logs/                     # app.log 與輪替日誌
├── pages/                    # 保留給未來 Streamlit 多頁面
├── services/                 # 商業邏輯與 ChatGPT Controller
├── utils/                    # logging 等共用工具
├── requirements.txt          # Python 相依套件
└── README.md                 # 安裝、執行與測試說明
```

## 功能

- 民國日期轉西元：支援 `/`、`-`、`.`、`*`、`年月日`。
- 地址補全：透過 ChatGPT 網頁回覆完整地址，包含村里；無法確認時要求回覆「查無法確認之里別」。
- 客服文字修飾：將文字改寫為自然、禮貌、親切且不新增資訊的客服回覆。
- ChatGPT 控制：重新整理、開啟新對話、停止目前自動化。

## GitHub / Streamlit Cloud 檢查

- `runtime.txt` 固定 Streamlit Cloud 使用 Python 3.12，避免雲端使用未預期的 Python 版本。
- `.github/workflows/ci.yml` 會在 push / pull request 時執行 `python scripts/verify_python.py` 與 `pytest -q`，若 GitHub 上的檔案真的有 SyntaxError，CI 會直接失敗並指出檔案與行號。
- Playwright 控制 ChatGPT 仍建議在 Windows 本機執行；Streamlit Cloud 不適合互動式登入既有 Chrome session。

## 安裝

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chrome
```

## 執行

```powershell
streamlit run app.py
```

第一次使用時，Chrome 會以 `browser/user_data/` 作為 Persistent Context 開啟。請在 Chrome 中登入 ChatGPT；之後重新啟動會沿用此 Session。

## 測試方式

```powershell
python scripts/verify_python.py
pytest -q
```

Playwright 功能需要 Windows 桌面環境、Google Chrome、有效 ChatGPT 登入狀態與網路連線。

若看到 `Chromium distribution 'chrome' is not found`，代表目前環境沒有 Google Chrome。請在 Windows 本機安裝 Google Chrome，或執行 `playwright install chrome`。本專案目標是 Windows 本機自動化；Streamlit Cloud/Linux 通常不適合互動式登入 ChatGPT。

進階環境變數：

- `CHATGPT_BROWSER_CHANNEL=chrome`：指定使用 Google Chrome。
- `CHATGPT_BROWSER_CHANNEL=`：不指定 channel，改用 Playwright bundled Chromium。
- `PLAYWRIGHT_HEADLESS=true`：使用 headless 模式；首次登入 ChatGPT 不建議使用。

## 維護注意事項

ChatGPT 網頁可能改版。所有 selector 集中於 `config/selectors.py`，優先使用 ARIA role、label、文字內容與 fallback selector，並搭配 timeout、retry、reload 與重新取得 locator。
