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

    def __init__(self, key=None):
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
        with open("PROMPT", "r") as file:
            self.prompt = file.read()
        logging.info("OpenAIMaliciousTextDetector initialized with prompt loaded.")

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
