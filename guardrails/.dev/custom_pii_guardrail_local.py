import os
import re
from typing import Literal, Optional, List
from litellm import LiteLLMLoggingObj
from litellm.integrations.custom_guardrail import CustomGuardrail
from litellm.integrations.prometheus import STATUS_CODE
from litellm.types.utils import GenericGuardrailAPIInputs
from openai.types.responses import response

# Define a dictionary of common PII regex patterns
PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "US_PHONE": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "US_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
}

class myCustomGuardrailLocal(CustomGuardrail):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def apply_guardrail(
        self,
        inputs: GenericGuardrailAPIInputs,
        request_data: dict,
        input_type: Literal["request", "response"],
        logging_obj: Optional["LiteLLMLoggingObj"] = None,
    ) -> GenericGuardrailAPIInputs:
        """
        Check text content against your guardrail rules (PII detection).
        Raise an exception to block the request, 
        else return the text to allow it through.
        """
        texts = inputs.get("texts", [])
        text: str = ""
        for text in texts:
            print(text)
        
        result = await self._check_for_pii_and_block(text)
        if result.get("action") == "BLOCK":
            raise Exception(f"Content blocked:  PII Policy violation - ", result.get("reason"))
        return inputs

    async def _check_for_pii_and_block(self, text) -> dict:
        """
        Checks the input text for PII data using regex patterns.
        Returns a list of detected PII types.
        """
        action: str = "ALLOW"
        detected_pii = []

        # Loop through each PII type and its matching regex pattern
        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.finditer(pattern, text)        
            for match in matches:
                detected_pii.append({
                    "type": pii_type
                })
        # If PII is detected, return a block action with reason
        if detected_pii:
            action = "BLOCK"

        # Return the result as a dictionary
        return {
            "action": action,
            "reason": detected_pii
        }
