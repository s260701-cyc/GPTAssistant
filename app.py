"""Streamlit entry point for local Windows ChatGPT automation tools."""

from __future__ import annotations

import logging

import streamlit as st

from api.handlers import address_service, polish_service, roc_date_service
from services.chatgpt_controller import BrowserStartupError, controller
from services.roc_date_service import RocDateError
from utils.async_runner import runner
from utils.logging_config import setup_logging

setup_logging()
LOGGER = logging.getLogger(__name__)


def show_automation_error(context: str, exc: Exception) -> None:
    """Display automation errors without exposing a raw Streamlit traceback."""
    LOGGER.exception("%s failed", context)
    if isinstance(exc, BrowserStartupError):
        st.error(str(exc))
        return
    st.error(f"{context}失敗：{exc}")


st.set_page_config(page_title="ChatGPT 自動化工具", page_icon="🤖", layout="centered")
st.title("🤖 Windows Streamlit + Playwright + ChatGPT 自動化網站")
st.caption("使用本機 Chrome Persistent Context；不使用 OpenAI API。")

with st.container(border=True):
    st.header("民國年轉西元")
    roc_input = st.text_input("輸入民國日期", placeholder="例如：92/4/21、92年4月21日")
    if roc_input:
        try:
            st.success(roc_date_service.convert(roc_input))
        except RocDateError as exc:
            st.warning(str(exc))

with st.container(border=True):
    st.header("地址補全")
    address = st.text_input("輸入地址", placeholder="例如：斗六市文化路15號")
    if st.button("查詢", use_container_width=True):
        try:
            with st.spinner("等待 ChatGPT 回覆中..."):
                st.info(runner.run(address_service.complete(address)))
        except Exception as exc:
            show_automation_error("地址補全", exc)

with st.container(border=True):
    st.header("客服文字修飾")
    text = st.text_area("輸入文字", placeholder="例如：資料有問題請重傳")
    if st.button("修飾", use_container_width=True):
        try:
            with st.spinner("等待 ChatGPT 回覆中..."):
                st.info(runner.run(polish_service.polish(text)))
        except Exception as exc:
            show_automation_error("文字修飾", exc)

with st.container(border=True):
    st.header("ChatGPT 控制")
    col1, col2, col3 = st.columns(3)
    if col1.button("重新整理", use_container_width=True):
        try:
            runner.run(controller.refresh())
            st.success("已重新整理 ChatGPT。")
        except Exception as exc:
            show_automation_error("重新整理", exc)
    if col2.button("開啟新對話", use_container_width=True):
        try:
            runner.run(controller.new_chat())
            st.success("已開啟新對話。")
        except Exception as exc:
            show_automation_error("開啟新對話", exc)
    if col3.button("停止自動化", use_container_width=True):
        try:
            runner.run(controller.stop())
            st.warning("已停止目前自動化任務，Chrome 仍保持開啟。")
        except Exception as exc:
            show_automation_error("停止自動化", exc)
