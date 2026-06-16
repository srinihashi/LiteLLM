import os
import json
from typing import Literal, Optional, List
from litellm import LiteLLMLoggingObj
from litellm.integrations.custom_guardrail import CustomGuardrail
from litellm.types.utils import GenericGuardrailAPIInputs
from httpx._models import Response
from litellm.llms.custom_httpx.http_handler import (
    get_async_httpx_client,
    httpxSpecialProvider,
)

class myCustomGuardrailAPI(CustomGuardrail):
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, **kwargs):
        self.api_key = api_key or os.getenv("MY_GUARDRAIL_API_KEY")
        self.api_base = api_base or os.getenv("MY_GUARDRAIL_BASE_API_URL", "https://api.myguardrail.com")
        super().__init__(**kwargs)

    async def apply_guardrail(
        self,
        inputs: GenericGuardrailAPIInputs,
        request_data: dict,
        input_type: Literal["request", "response"],
        logging_obj: Optional["LiteLLMLoggingObj"] = None,
) -> GenericGuardrailAPIInputs:
        """
        Checks the input text for PII data using a microservice endpoint which uses regex patterns.
        Returns a list of detected PII types.
        """        
        texts = inputs.get("texts", [])
        text: str = ""
        for text in texts:
            print(text)
        result = await self._check_with_api(text, request_data)
        if result.get("action") == "BLOCK":
            raise Exception(f"Content blocked:  Policy violation - ", result.get("reason"))
        return inputs

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
