from openai import AsyncClient
from core.config import settings


class AI:
    def __init__(self, prompt: str, system_prompt: str, history):
        self.client = AsyncClient(
            base_url=settings.DEEPSEEK_BASE_URL,
            api_key=settings.DEEPSEEK_API_KEY,
        )
        self.prompt = prompt
        self.history = history
        self.system_prompt = system_prompt

    async def send(self):
        result = await self.client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": self.system_prompt},
                self.history,
                {
                    "role": "user",
                    "content": self.prompt,
                },
            ],
        )

        return result.choices[0].message.content
