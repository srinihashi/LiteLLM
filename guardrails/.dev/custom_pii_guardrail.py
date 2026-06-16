import os
from typing import Optional, List
from litellm.integrations.custom_guardrail import CustomGuardrail
from litellm.types.guardrails import PiiEntityType
from litellm._logging import verbose_proxy_logger
from litellm.llms.custom_httpx.http_handler import (
    get_async_httpx_client,
    httpxSpecialProvider,
)

class myCustomGuardrail(CustomGuardrail):
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, **kwargs):
        #self.api_key = api_key or os.getenv("MY_GUARDRAIL_API_KEY")
        self.api_base = api_base or os.getenv("MY_GUARDRAIL_BASE_API_URL", "https://api.myguardrail.com")
        super().__init__(**kwargs)

    async def apply_guardrail(
        self,
        text: str, # IMPORTANT: This is the text to check against your guardrail rules. It's extracted from the request or response across all LLM call types.
        language: Optional[str] = None, # ignore 
        entities: Optional[List[PiiEntityType]] = None, # ignore
        request_data: Optional[dict] = None, # ignore
    ) -> str:
        """
        Check text content against your guardrail rules.
        Raise an exception to block the request.
        Return the text (optionally modified) to allow it through.
        """
        result = await self._check_with_api(text, request_data)
        
        if result.get("action") == "BLOCK":
            raise Exception(f"Content blocked: {result.get('reason', 'Policy violation')}")
        
        return text

    async def _check_with_api(self, text: str, request_data: Optional[dict]) -> dict:
        async_client = get_async_httpx_client(llm_provider=httpxSpecialProvider.LoggingCallback)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        response = await async_client.post(
            f"{self.api_base}/check",
            headers=headers,
            json={"text": text},
            timeout=5,
        )
        
        response.raise_for_status()
        return response.json()