"""Address completion service powered by ChatGPT web automation."""

from __future__ import annotations

from services.chatgpt_controller import controller


class AddressService:
    """Build prompts for address completion."""

    async def complete(self, address: str) -> str:
        """Ask ChatGPT to complete a Taiwanese address including village/li."""
        if not address.strip():
            raise ValueError("請輸入地址。")
        prompt = (
            "請補齊此地址的完整地址（包含村里）。\n\n"
            "若無法確認請直接回答：\n\n"
            "查無法確認之里別\n\n"
            "不可猜測。\n\n"
            f"地址：{address.strip()}"
        )
        return await controller.send_prompt(prompt)
