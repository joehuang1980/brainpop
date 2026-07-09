# brainpop

BrainPOP 學習紀錄頁面。

## 雲端進度同步

目前前端會優先向 Google Apps Script 讀取進度，失敗時才退回瀏覽器本機紀錄。若要真正跨裝置共用進度，GAS 需要支援以下 API：

你提供的試算表欄位為：

- 時間
- 觀看者
- Level
- Unit
- Lesson
- 抽中角色
- 獲得積分

前端已在 POST payload 中同時送出上述中文欄位鍵名，GAS 可直接依欄位順序 append。

### 讀取進度

- Method: GET
- Query: action=getProgress&viewer=Olivia
- Response JSON:

```json
{
	"success": true,
	"progress": {
		"Level 1": ["Unit 1::1. The Friends", "Unit 1::2. Magic Show"],
		"Level 2": [],
		"Level 3": []
	}
}
```

### 寫入觀看紀錄與進度

- Method: POST
- Body JSON:

```json
{
	"action": "recordWatch",
	"timestamp": "2026-07-09T03:21:00.000Z",
	"viewer": "Olivia",
	"level": "Level 1",
	"unit": "Unit 1",
	"lesson": "1. The Friends",
	"lessonId": "Unit 1::1. The Friends",
	"character": "Mario",
	"points": 5,
	"時間": "2026-07-09T03:21:00.000Z",
	"觀看者": "Olivia",
	"Level": "Level 1",
	"Unit": "Unit 1",
	"Lesson": "1. The Friends",
	"抽中角色": "Mario",
	"獲得積分": 5,
	"progress": {
		"Level 1": ["Unit 1::1. The Friends"],
		"Level 2": [],
		"Level 3": []
	}
}
```

可選擇讓 POST 也回傳最新進度：

```json
{
	"success": true,
	"progress": {
		"Level 1": ["Unit 1::1. The Friends"],
		"Level 2": [],
		"Level 3": []
	}
}
```
