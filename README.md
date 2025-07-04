# 旅行花費記錄系統

版本：v0.3

一個現代化、響應式的旅行花費記錄網頁，支援多國幣別自動換算台幣，並將資料即時寫入 Google Sheets。介面簡潔、分區明確，適合個人或團體旅遊記帳。

## v0.3 主要更新
- **安全強化**：加入 CSRF 防護（Flask-WTF）、HTTP 安全標頭（Flask-Talisman）、請求速率限制（Flask-Limiter），所有敏感資訊（如 secret key、Google Sheets ID、client secret 檔名）皆改用環境變數管理。
- **雙語隱私權政策與服務條款**：/privacy、/privacy_zh.html、/terms、/terms_zh.html 支援中英文切換，並自動依瀏覽器語言導向。
- **Render 雲端部署最佳化**：支援 Render Secret Files 安全存放 Google 憑證，環境變數於 Render 後台集中管理。
- **requirements.txt 補齊依賴**：新增 flask-talisman、flask-limiter、python-dotenv 等，確保部署即安全。
- **config.py 重構**：所有敏感設定集中於環境變數，程式碼更安全、彈性。
- **404 頁面與錯誤處理優化**：自訂 404.html，並建議加上 500.html。
- **README 文件同步更新**：補充 Render 部署、環境變數、Secret Files 實作說明。

## v0.2 主要更新
- 國家清單改為台灣人常去的前20個，並支援台灣、澳門、香港、中國。
- KLOOK/KKDAY 欄位統一改為「票券」。
- Google Sheets 標題自動同步為最新（自動修正舊表單標題）。
- 登入後按鈕顯示「繼續登記」，未登入顯示「登入並同步」。
- 送出後自動提示並重置表單，方便連續登記。
- 登入與登出按鈕體驗與樣式優化，僅登入後顯示登出。
- UI 細節優化，說明區塊更美觀，響應式更佳。
- 表單說明區塊優化，加入icon與更精簡的說明文字。
- 計算公式說明更清楚，票券、匯率換算細節明確。
- 票券、國家、匯率等欄位完全動態化，維護更方便。
- Google Sheets 欄位順序、標題自動同步，舊表單也會自動修正。
- 表單UI與互動體驗多處細節優化。

### v0.2 修復重點
- 修正回國日未選日期時誤跳提示窗的問題
- 修正 Google Sheets 標題自動同步時 row 變數未定義的錯誤
- 修正票券、國家、匯率等欄位同步與顯示細節
- 修正 Google Sheets 建立失敗時的錯誤提示與流程
- 修正表單送出後自動重置與提示的體驗
- 其他細節與穩定性修正

## 主要功能特色
- 支援多國幣別，匯率自動查詢與換算
- 所有資料寫入同一 Google Sheets，方便彙整
- 響應式現代化表單，手機/桌機皆美觀
- 欄位分區明確，填寫體驗佳
- 即時計算總花費，公式透明
- 前端/後端皆有資料驗證
- 新增「保險」欄位，記錄旅遊保險金額

## 新版 Google Sheets 串接說明
- 採用 Google Identity Services (GIS) 新版登入，使用者以自己 Google 帳號登入。
- 登入後自動搜尋 Google Drive 是否已有「我的旅行花費表單」，有則直接使用，無則自動建立新表單並寫入標題。
- access token、email、spreadsheetId 皆儲存於 localStorage，保留登入狀態。
- 送出表單時自動帶出 access token 與 spreadsheetId，後端直接寫入該用戶自己的 Google Sheets。
- 若表單被刪除或 localStorage 遺失，系統會自動重新搜尋或建立新表單。
- 完善的錯誤處理，access token 過期、表單不存在、權限不足等情境皆有對應 UX 引導。
- 所有 debug alert 已移除，介面乾淨，僅於 console.log 保留開發資訊。

## 安裝與執行
1. **安裝 Python 3.8+**
2. 安裝套件：
   ```sh
   pip install -r requirements.txt
   ```
3. （新版已不需 Service Account 憑證，僅需前端 Google OAuth 設定 client_id）
4. 啟動 Flask 伺服器：
   ```sh
   python app.py
   ```
5. 於瀏覽器開啟 http://localhost:5000

## 前端表單特色
- 國家下拉選單+其他自訂，匯率自動帶出
- 日期區間選擇，天數自動計算
- 金額欄位分區排列，欄位說明清楚
- 匯率區塊即時顯示幣別
- 送出前前端驗證，回國日不可早於出發日
- 旅程花費區塊即時計算總花費

## Google Sheets 欄位說明
依照最新順序，寫入 Google Sheets 的欄位如下：

| 欄位         | 說明                         |
|--------------|------------------------------|
| 旅行國家     | 旅遊國家名稱                |
| 時間區間     | 出發日 ~ 回國日              |
| 天數         | 旅程天數                     |
| 機票         | 機票花費（TWD）              |
| 住宿         | 住宿花費（TWD）              |
| SIM          | SIM卡花費（TWD）             |
| 票券         | 行程票券（TWD）              |
| 換匯         | 換匯金額（TWD）              |
| 刷卡         | 刷卡金額（當地貨幣）         |
| 原本有的貨幣 | 出發時持有的當地貨幣         |
| 現餘         | 回國時剩餘的當地貨幣         |
| 匯率         | 1 TWD = ? 當地貨幣           |
| 總花費       | 依公式自動計算（TWD）        |
| 保險         | 旅遊保險金額（TWD）            |

## 版權與聯絡方式
- 作者：xiaoweijie18@gmail.com
- GitHub: https://github.com/xiaoweijie18 

## 常見問題（FAQ）

### Q1. Google 登入時出現「已封鎖存取權：這項要求遭到 Google 政策封鎖」或「錯誤代碼 400：redirect_uri_mismatch」？
A: 這是 Google OAuth 安全機制，通常是「授權的重新導向 URI」未正確設定。請到 Google Cloud Console > API 與服務 > 憑證 > OAuth 2.0 Client IDs，將你的 Render 網址（如 `https://yourapp.onrender.com/`）、自訂網域（如 `https://yourdomain.com/`）、本地測試網址（如 `http://localhost:5000/`）全部加進「授權的重新導向 URI」清單。網址必須完全一致（包含協定、網域、路徑、斜線），否則會出現 400 錯誤。修改後約需數分鐘生效。

### Q2. Google Sheets 建立失敗，顯示 `{{}}` 或空白？
A: 請確認 Google 帳號已授權 Google Drive 權限，並確保網路連線正常。如持續失敗，請重新登入或稍後再試。

### Q3. 匯率、國家清單、票券等資料如何維護？
A: 所有對應資料皆集中於後端，前端自動同步，維護只需修改一處即可。

### Q4. 如何自訂國家或幣別？
A: 下拉選單選「其他」即可手動輸入國家，並自行填寫匯率。

### Q5. 表單送出後如何繼續登記？
A: 送出後會自動重置表單，直接填寫新資料並再次點擊「繼續登記」即可。

## 未來規劃
- 支援多語系（繁中/英文）自動切換
- 更多欄位自訂與統計分析
- 團體旅遊分帳功能
- 行動裝置體驗再優化
- 匯率來源多元化與快取

## 貢獻指南
歡迎任何人提出 issue、pull request 或建議！
1. 請先 fork 本專案再進行修改。
2. 提交 PR 前請確認所有功能可正常運作。
3. 建議以簡體/繁體/英文皆可討論。
4. 有任何問題可直接聯絡作者。

## 授權條款
本專案採用 MIT License 授權，歡迎自由使用、修改與商業應用，但請保留原作者資訊。

---

感謝您的支持與參與！

如有建議或問題，歡迎來信或於 GitHub 提出 issue！ 