import openai
import os
import json

class OpenAIResponse:
    malicious: bool
    reason: str
    confidence: int

    @staticmethod
    def from_dict(dict: dict) -> 'OpenAIResponse':
        openai_response = OpenAIResponse()
        openai_response.malicious = dict["malicious"]
        openai_response.reason = dict["reason"]
        openai_response.confidence = dict["confidence"]
        return openai_response

    def get_dict(self):
        return {
            "malicious": self.malicious,
            "reason": self.reason,
            "confidence": self.confidence
        }

class OpenAIMaliciousTextDetector:
    def __init__(self, key=None):
        if key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set")
        self.client = openai.OpenAI()
        with open("PROMPT", "r") as file:
            self.prompt = file.read()

    def detect(self, text: str) -> OpenAIResponse:
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "malicious_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "malicious": {
                                "description": "Whether the text is malicious",
                                "type": "boolean"
                            },
                            "reason": {
                                "description": "The reason for the decision",
                                "type": "string"
                            },
                            "confidence": {
                                "description": "The confidence level in the decision",
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 100
                            },
                            "additionalProperties": False
                        }
                    }
                }
            },
        )
        aiResponse = completion.choices[0].message.model_dump_json()
        jsonResponse = json.loads(aiResponse)
        content = json.loads(jsonResponse["content"])
        
        openai_response = OpenAIResponse()
        openai_response.malicious = content["malicious"]
        openai_response.reason = content["reason"]
        openai_response.confidence = content["confidence"]
        return openai_response
