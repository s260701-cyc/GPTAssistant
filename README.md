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
python -m compileall .
python - <<'PY'
from services.roc_date_service import RocDateService
svc = RocDateService()
assert svc.convert('92/4/21') == '2003/4/21'
assert svc.convert('92/04/21') == '2003/04/21'
assert svc.convert('112/12/31') == '2023/12/31'
assert svc.convert('92年4月21日') == '2003/4/21'
assert svc.convert('92.4.21') == '2003/4/21'
assert svc.convert('92-4-21') == '2003/4/21'
assert svc.convert('92*4*21') == '2003/4/21'
print('ROC date tests passed')
PY
```

Playwright 功能需要 Windows 桌面環境、Google Chrome、有效 ChatGPT 登入狀態與網路連線。

若看到 `Chromium distribution 'chrome' is not found`，代表目前環境沒有 Google Chrome。請在 Windows 本機安裝 Google Chrome，或執行 `playwright install chrome`。本專案目標是 Windows 本機自動化；Streamlit Cloud/Linux 通常不適合互動式登入 ChatGPT。

進階環境變數：

- `CHATGPT_BROWSER_CHANNEL=chrome`：指定使用 Google Chrome。
- `CHATGPT_BROWSER_CHANNEL=`：不指定 channel，改用 Playwright bundled Chromium。
- `PLAYWRIGHT_HEADLESS=true`：使用 headless 模式；首次登入 ChatGPT 不建議使用。

## 維護注意事項

ChatGPT 網頁可能改版。所有 selector 集中於 `config/selectors.py`，優先使用 ARIA role、label、文字內容與 fallback selector，並搭配 timeout、retry、reload 與重新取得 locator。
