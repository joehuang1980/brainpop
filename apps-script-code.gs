// ========== Google Apps Script 程式碼 ==========
// 複製整個檔案內容到 Google Apps Script 編輯器
// 試算表 ID: 1S6_VSSN7dJ0UUT9P-QtbaGE8cTEhNoqIFRMAwbsrKe4
// ================================================

// ===== 設定區域 =====
const SHEET_ID = '1S6_VSSN7dJ0UUT9P-QtbaGE8cTEhNoqIFRMAwbsrKe4';
const WATCH_SHEET_NAME = '觀看記錄'; // 新建一個名為 '觀看記錄' 的工作表用來存觀看紀錄
const PROGRESS_SHEET_NAME = '進度追蹤'; // 新建一個名為 '進度追蹤' 的工作表用來存各觀看者的進度

// ===== 主入口函數 =====
function doGet(e) {
  const action = e.parameter.action;
  const viewer = e.parameter.viewer;

  try {
    if (action === 'getProgress') {
      if (!viewer) {
        return ContentService.createTextOutput(JSON.stringify({
          success: false,
          error: 'Missing viewer parameter'
        })).setMimeType(ContentService.MimeType.JSON);
      }

      const progress = getViewerProgress(viewer);
      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        progress: progress
      })).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: 'Unknown action'
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const action = payload.action;

    if (action === 'recordWatch') {
      // 寫入觀看紀錄
      recordWatchEntry(payload);

      // 更新進度追蹤
      if (payload.progress) {
        updateViewerProgress(payload.viewer, payload.progress);
      }

      // 回傳更新後的完整進度
      const updatedProgress = getViewerProgress(payload.viewer);
      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        progress: updatedProgress
      })).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: 'Unknown action'
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// ===== 核心功能函數 =====

/**
 * 記錄一筆觀看紀錄到試算表
 * payload 格式: {
 *   時間: ISO string,
 *   觀看者: string,
 *   Level: string,
 *   Unit: string,
 *   Lesson: string,
 *   抽中角色: string,
 *   獲得積分: number
 * }
 */
function recordWatchEntry(payload) {
  const sheet = getOrCreateSheet(WATCH_SHEET_NAME);
  const headers = ['時間', '觀看者', 'Level', 'Unit', 'Lesson', '抽中角色', '獲得積分'];

  // 若工作表是空的，先寫入表頭
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
  }

  // 新增一列觀看紀錄
  const newRow = [
    payload['時間'] || new Date().toISOString(),
    payload['觀看者'],
    payload['Level'],
    payload['Unit'],
    payload['Lesson'],
    payload['抽中角色'],
    payload['獲得積分']
  ];

  sheet.appendRow(newRow);
  SpreadsheetApp.flush();
}

/**
 * 取得特定觀看者的進度
 * 回傳格式: { "Level 1": [...lessons], "Level 2": [...], "Level 3": [...] }
 */
function getViewerProgress(viewer) {
  const sheet = getOrCreateSheet(PROGRESS_SHEET_NAME);
  const data = sheet.getDataRange().getValues();

  // 第一列是表頭，第一欄是觀看者名稱
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === viewer) {
      // 找到該觀看者，解析進度 JSON
      try {
        const progressJson = data[i][1];
        if (progressJson) {
          return JSON.parse(progressJson);
        }
      } catch (e) {
        // JSON 解析失敗，回傳空進度
      }
    }
  }

  // 若找不到或未初始化，回傳空進度
  return {
    'Level 1': [],
    'Level 2': [],
    'Level 3': []
  };
}

/**
 * 更新特定觀看者的進度
 */
function updateViewerProgress(viewer, progress) {
  const sheet = getOrCreateSheet(PROGRESS_SHEET_NAME);
  const data = sheet.getDataRange().getValues();

  // 若工作表是空的，先寫入表頭
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['觀看者', '進度 (JSON)']);
  }

  // 尋找該觀看者的列
  let found = false;
  for (let i = 1; i < data.length; i++) {
    if (data[i][0] === viewer) {
      // 更新該列的進度
      sheet.getRange(i + 1, 2).setValue(JSON.stringify(progress));
      found = true;
      break;
    }
  }

  // 若找不到，新增一列
  if (!found) {
    sheet.appendRow([viewer, JSON.stringify(progress)]);
  }

  SpreadsheetApp.flush();
}

// ===== 輔助函數 =====

/**
 * 取得或建立指定名稱的工作表
 */
function getOrCreateSheet(sheetName) {
  const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
  let sheet = spreadsheet.getSheetByName(sheetName);

  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName);
  }

  return sheet;
}

// ===== 測試用函數 =====

/**
 * 在 Apps Script 編輯器中執行此函數進行測試
 * 按下「執行」按鈕或 Ctrl+Enter
 */
function testGetProgress() {
  const progress = getViewerProgress('Olivia');
  Logger.log('Olivia 的進度:');
  Logger.log(JSON.stringify(progress, null, 2));
}

/**
 * 測試新增觀看紀錄
 */
function testRecordWatch() {
  const testPayload = {
    action: 'recordWatch',
    '時間': new Date().toISOString(),
    '觀看者': 'Olivia',
    'Level': 'Level 1',
    'Unit': 'Unit 1',
    'Lesson': '1. The Friends',
    '抽中角色': 'Mario',
    '獲得積分': 5,
    progress: {
      'Level 1': ['Unit 1::1. The Friends'],
      'Level 2': [],
      'Level 3': []
    }
  };

  recordWatchEntry(testPayload);
  updateViewerProgress(testPayload['觀看者'], testPayload.progress);
  Logger.log('測試記錄已新增');
}

/**
 * 測試模擬 doPost 的完整流程
 */
function testFullFlow() {
  const payload = {
    action: 'recordWatch',
    '時間': new Date().toISOString(),
    '觀看者': 'Lucas',
    'Level': 'Level 1',
    'Unit': 'Unit 2',
    'Lesson': '2. Magic Show',
    '抽中角色': 'Luigi',
    '獲得積分': 3,
    progress: {
      'Level 1': ['Unit 1::1. The Friends', 'Unit 2::2. Magic Show'],
      'Level 2': [],
      'Level 3': []
    }
  };

  recordWatchEntry(payload);
  updateViewerProgress(payload['觀看者'], payload.progress);

  const result = getViewerProgress(payload['觀看者']);
  Logger.log('最新進度:');
  Logger.log(JSON.stringify(result, null, 2));
}
