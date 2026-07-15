"""Streamlit entry point for local Windows ChatGPT automation tools."""

from __future__ import annotations

import logging

import streamlit as st

from api.handlers import address_service, polish_service, roc_date_service
from services.chatgpt_controller import controller
from services.roc_date_service import RocDateError
from utils.async_runner import runner
from utils.logging_config import setup_logging

setup_logging()
LOGGER = logging.getLogger(__name__)


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
            LOGGER.exception("Address completion failed")
            st.error(f"地址補全失敗：{exc}")

with st.container(border=True):
    st.header("客服文字修飾")
    text = st.text_area("輸入文字", placeholder="例如：資料有問題請重傳")
    if st.button("修飾", use_container_width=True):
        try:
            with st.spinner("等待 ChatGPT 回覆中..."):
                st.info(runner.run(polish_service.polish(text)))
        except Exception as exc:
            LOGGER.exception("Polish failed")
            st.error(f"文字修飾失敗：{exc}")

with st.container(border=True):
    st.header("ChatGPT 控制")
    col1, col2, col3 = st.columns(3)
    if col1.button("重新整理", use_container_width=True):
        runner.run(controller.refresh())
        st.success("已重新整理 ChatGPT。")
    if col2.button("開啟新對話", use_container_width=True):
        runner.run(controller.new_chat())
        st.success("已開啟新對話。")
    if col3.button("停止自動化", use_container_width=True):
        runner.run(controller.stop())
        st.warning("已停止目前自動化任務，Chrome 仍保持開啟。")
