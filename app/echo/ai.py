from openai import AsyncClient
from core.config import settings


class AI:
    def __init__(self, prompt: str, system_prompt: str, history, limit: int = 10):
        self.client = AsyncClient(
            base_url=settings.DEEPSEEK_BASE_URL,
            api_key=settings.DEEPSEEK_API_KEY,
        )
        self.prompt = prompt
        self.history = history
        self.system_prompt = system_prompt
        self.limit = limit

    async def send(self):
        messages = [{"role": "system", "content": self.system_prompt}]

        # Берем только последние limit сообщений из истории
        history_slice = self.history[-self.limit :] if self.limit > 0 else []

        for el in history_slice:
            messages.append(
                {
                    "role": "user",
                    "content": el.question,
                }
            )
            if el.answer:
                messages.append(
                    {
                        "role": "assistant",
                        "content": el.answer,
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": self.prompt,
            }
        )

        result = await self.client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
        )

        return result.choices[0].message.content
