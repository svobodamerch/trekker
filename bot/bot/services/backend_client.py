import httpx
from bot.config import settings


class BackendClient:
    def __init__(self):
        self.base_url = settings.api_base_url
        self.client = httpx.AsyncClient()

    async def create_user(self, telegram_user_id: str, username: str | None, first_name: str | None):
        """Create or get user via auth endpoint."""
        # Mock init data for bot-initiated auth
        init_data = f"user_id={telegram_user_id}&username={username or ''}&first_name={first_name or ''}"
        
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/telegram",
                json={"init_data": init_data},
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Backend error: {e}")
            return None

    async def close(self):
        await self.client.aclose()
