"""
Lucky Red - UI 輔助工具
提供用戶界面相關的輔助函數
"""
from telegram import CallbackQuery
from typing import Optional


async def show_loading(query: CallbackQuery, message: str = "處理中..."):
    """
    顯示加載狀態
    
    Args:
        query: 回調查詢對象
        message: 加載消息
    """
    await query.answer(message, cache_time=0)


async def show_error(query: CallbackQuery, message: str, show_alert: bool = True):
    """
    顯示錯誤消息
    
    Args:
        query: 回調查詢對象
        message: 錯誤消息
        show_alert: 是否顯示為彈窗
    """
    await query.answer(message, show_alert=show_alert)


async def show_success(query: CallbackQuery, message: str = "操作成功"):
    """
    顯示成功消息
    
    Args:
        query: 回調查詢對象
        message: 成功消息
    """
    await query.answer(message, show_alert=False)
