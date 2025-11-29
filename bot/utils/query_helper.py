"""
輔助函數：創建模擬 Query 對象
用於將回覆鍵盤按鈕轉換為類似 CallbackQuery 的處理
"""
from telegram import Update


def create_mock_query(update: Update):
    """創建模擬的 CallbackQuery 對象，用於處理回覆鍵盤"""
    class MockQuery:
        def __init__(self, message):
            self.message = message
            self.data = None
            self.from_user = message.from_user if message else None
        
        async def edit_message_text(self, *args, **kwargs):
            """模擬 edit_message_text，實際調用 reply_text"""
            if self.message:
                return await self.message.reply_text(*args, **kwargs)
        
        async def answer(self, *args, **kwargs):
            """模擬 answer，不做任何操作"""
            pass
    
    return MockQuery(update.message) if update.message else None
