"""
CordGuard AI Module

This module provides AI-powered malicious text detection capabilities using OpenAI's GPT models.
It includes classes for handling OpenAI API responses and performing malicious text detection.

Key Components:
    - OpenAIResponse: Class for structured API responses
    - OpenAIMaliciousTextDetector: Main detector class using OpenAI API

Dependencies:
    - openai: OpenAI API client
    - os: Environment variable access
    - json: JSON parsing/serialization
    - logging: Application logging

Environment Variables:
    OPENAI_API_KEY: OpenAI API key for authentication

Author: v0id_user <contact@v0id.me>
Security Contact: CordGuard Security Team <security@cordguard.org>
Maintained by: Abjad Tech Platform <hello@abjad.cc>
Version: 1.0.0
"""

import openai
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class OpenAIResponse:
    """
    Structured response class for OpenAI API results.
    
    Attributes:
        malicious (bool): Whether the analyzed text is malicious
        reason (str): Explanation for the malicious/non-malicious determination
        confidence (int): Confidence score from 0-100 for the determination

    Methods:
        from_dict: Creates an OpenAIResponse instance from a dictionary
        get_dict: Converts the response object to a dictionary
    """

    malicious: bool
    reason: str 
    confidence: int

    @staticmethod
    def from_dict(dict: dict) -> 'OpenAIResponse':
        """
        Creates an OpenAIResponse instance from a dictionary.

        Args:
            dict (dict): Dictionary containing malicious, reason and confidence keys

        Returns:
            OpenAIResponse: New instance populated with dictionary values
        """
        openai_response = OpenAIResponse()
        openai_response.malicious = dict["malicious"]
        openai_response.reason = dict["reason"]
        openai_response.confidence = dict["confidence"]
        return openai_response

    def get_dict(self):
        """
        Converts the response object to a dictionary format.

        Returns:
            dict: Dictionary containing malicious, reason and confidence values
        """
        return {
            "malicious": self.malicious,
            "reason": self.reason,
            "confidence": self.confidence
        }

class OpenAIMaliciousTextDetector:
    """
    Detector class that uses OpenAI's API to analyze text for malicious content.

    The detector uses a pre-defined prompt and GPT-4 to analyze text and determine
    if it contains malicious content. Results include confidence scores and reasoning.

    Attributes:
        client (openai.OpenAI): OpenAI API client instance
        prompt (str): Pre-defined prompt loaded from PROMPT file

    Methods:
        detect: Analyzes text for malicious content using OpenAI API
    """

    def __init__(self, model="gpt-4o", auto_model=False, key=None):
        """
        Initialize the detector with OpenAI API credentials.

        Args:
            key (str, optional): OpenAI API key. If None, reads from environment variable.

        Raises:
            ValueError: If no API key is provided or found in environment
        """
        if key is None:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set")
        self.client = openai.OpenAI()
        self.model = model
        try:
            with open("PROMPT", "r") as file:
                content = file.read()
                if not content.strip():
                    raise ValueError("PROMPT file is empty")
                self.prompt = content
        except FileNotFoundError:
            raise ValueError("PROMPT file not found")
        self.auto_model = auto_model
        logging.info("OpenAIMaliciousTextDetector initialized with prompt loaded.")
    def calculate_token_count(self, text: str) -> int:
        """
        Calculate the token count of the text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            int: Estimated token count
        """
        # Rough estimation: ~4 chars per token
        return len(text) // 4

    def detect(self, text: str) -> OpenAIResponse:
        """
        Analyze text for malicious content using OpenAI's API.

        Makes an API call to OpenAI with the text and a predefined prompt,
        expecting a structured JSON response about maliciousness.

        Args:
            text (str): The text to analyze for malicious content

        Returns:
            OpenAIResponse: Structured response containing analysis results

        Note:
            Uses GPT-4 model and enforces a specific JSON schema for responses
        """
        logging.info("Detecting malicious text...")
        HARDCODED_MINI_TOKEN_COUNT = 2048
        HARDCODED_MINI_COST = 0.001
        HARDCODED_O_COST = 0.01
        if self.auto_model:
            # Calculate tokens and costs
            tokens = self.calculate_token_count(text)
            
            # GPT-4o: $0.01/1K tokens, more accurate
            # GPT-4o-mini: $0.001/1K tokens, less accurate
            gpt4o_cost = (tokens / HARDCODED_MINI_TOKEN_COUNT) * HARDCODED_O_COST
            gpt4o_mini_cost = (tokens / HARDCODED_MINI_TOKEN_COUNT) * HARDCODED_MINI_COST
            
            # Use mini for larger texts to save costs
            if tokens > HARDCODED_MINI_TOKEN_COUNT:
                self.model = "gpt-4o-mini"
                logging.info(f"Using gpt-4o-mini for {tokens} tokens (cost: ~${gpt4o_mini_cost:.4f})")
            else:
                self.model = "gpt-4o" 
                logging.info(f"Using gpt-4o for {tokens} tokens (cost: ~${gpt4o_cost:.4f})")

        completion = self.client.chat.completions.create(
            model=self.model,
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
        logging.info("Received response from OpenAI API.")
        aiResponse = completion.choices[0].message.model_dump_json()
        jsonResponse = json.loads(aiResponse)
        content = json.loads(jsonResponse["content"])
        
        openai_response = OpenAIResponse()
        openai_response.malicious = content["malicious"]
        openai_response.reason = content["reason"]
        openai_response.confidence = content["confidence"]
        logging.info(f"Detection result: {openai_response.get_dict()}")
        return openai_response
