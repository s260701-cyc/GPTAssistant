"""Customer-service text polishing service powered by ChatGPT."""

from __future__ import annotations

from services.chatgpt_controller import controller


class PolishService:
    """Build prompts for customer-service replies."""

    async def polish(self, text: str) -> str:
        """Polish text into a polite customer-service reply."""
        if not text.strip():
            raise ValueError("請輸入要修飾的文字。")
        prompt = (
            "請將以下文字修飾成客服回覆。\n\n"
            "要求：\n\n"
            "保持原意\n\n"
            "語氣自然\n\n"
            "禮貌\n\n"
            "親切\n\n"
            "不可增加不存在資訊\n\n"
            "只輸出修飾後內容\n\n"
            f"文字：{text.strip()}"
        )
        return await controller.send_prompt(prompt)
