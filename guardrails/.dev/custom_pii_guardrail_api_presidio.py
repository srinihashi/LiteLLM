
from httpx._models import Response


import os
import json
from typing import Literal, Optional, List
from litellm import LiteLLMLoggingObj
from litellm.integrations.custom_guardrail import CustomGuardrail
#from litellm.llms.vertex_ai.vertex_ai_non_gemini import TextStreamer
#from litellm.types.guardrails import PiiEntityType
from litellm.types.utils import GenericGuardrailAPIInputs
#from litellm._logging import verbose_proxy_logger
from litellm.llms.custom_httpx.http_handler import (
    get_async_httpx_client,
    httpxSpecialProvider,
)

class myCustomGuardrailAPIPresidio(CustomGuardrail):
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
        Check text content against your guardrail rules.
        Raise an exception to block the request.
        Return the text (optionally modified) to allow it through.
        """ 
        print("ALL OBJECTS")
        print("INPUTS: ", inputs)
        print("REQUEST_DATA: ", request_data)
        print("INPUT_TYPE: ", input_type)
        print("LOGGING_OBJ: ", logging_obj)
       
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
#            "Authorization": f"Bearer {self.api_key}",
        }
        
        response = await async_client.post(
            f"{self.api_base}/presidio",
            headers=headers,
            json={"text": text},
            timeout=5,
        )
        
        # print the content from the response
        #print("RESPONSE: ", response)
        print(response)
        response.raise_for_status()
        return response.json()
        #return response
        #action: str = "ALLOW"
        #reason: str = "PII Not detected"
        #
        #return {"action": action,
        #        "reason": reason
        #}
