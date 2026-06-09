import json
from openai import OpenAI
from typing import Dict, Any

class LocalLLMEngine:
    """Handles communication with the local LM Studio server."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        # The SDK requires an api_key string, but local servers ignore it.
        # We pass a dummy value to satisfy the library.
        self.client = OpenAI(base_url=base_url, api_key="lm-studio-local")
        
        # Dynamically fetch the loaded model from LM Studio so we don't hardcode it
        try:
            models = self.client.models.list()
            if not models.data:
                raise RuntimeError("No models found. Please load a model in LM Studio.")
            self.model_id = models.data[0].id
            print(f"Connected to local model: {self.model_id}")
        except Exception as e:
            raise ConnectionError(f"Could not connect to LM Studio: {e}")
    
    def extract_entities(self, raw_text: str, expected_schema: dict) -> Dict[str, Any]:
        """
        Sends unstructured text to Qwen2.5-3B and forces a structured JSON return
        based on the dynamic schema provided in the config file.
        """
        system_prompt = (
            "You are a strict data extraction engine. Analyze the input text and extract information "
            f"matching this exact JSON schema: {json.dumps(expected_schema)}\n"
            "CRITICAL: Return ONLY raw, valid JSON. Do not wrap the response in markdown code blocks (e.g., do not use ```json). "
            "Do not include any conversational filler, explanations, or introductory text."
        )
        
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text}
            ],
            temperature=0.0  # Set to 0.0 for maximum determinism in ETL
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            print("Pipeline Warning: Failed to parse JSON. Raw output was:", raw_output)
            return {"error": "Invalid JSON returned", "raw": raw_output}


    def extract_entities_o(self, raw_text: str) -> Dict[str, Any]:
        """
        Sends unstructured text to Qwen2.5-3B and forces a structured JSON return.
        """
        # Define a schema so the 3B model knows exactly what keys to create
        json_schema = {
            "transaction_id": "string or null",
            "client_name": "string or null",
            "amount_usd": "number or null",
            "status_or_event": "string detailing the core action or error description"
        }

        system_prompt = (
            "You are a strict data extraction engine. Analyze the input text and extract information "
            f"matching this exact JSON schema: {json.dumps(json_schema)}\n"
            "CRITICAL: Return ONLY raw, valid JSON. Do not wrap the response in markdown code blocks (e.g., do not use ```json). "
            "Do not include any conversational filler, explanations, or introductory text."
        )
        
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_text}
            ],
            temperature=0.0  # Set to 0.0 for maximum determinism in ETL
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            print("Pipeline Warning: Failed to parse JSON. Raw output was:", raw_output)
            return {"error": "Invalid JSON returned", "raw": raw_output}

# --- Pipeline Execution Execution ---
if __name__ == "__main__":
    # Initialize the LLM transformation layer
    engine = LocalLLMEngine()
    
    # Simulating raw data extracted from a source system
    raw_source_data = "Customer John Doe from Pune purchased a premium laptop on 2026-06-07. Order ID: 9948A."
    print("\n[Ingestion] Processing raw text...")
    
    # Transforming unstructured text into structured columns
    structured_data = engine.extract_entities(raw_source_data)
    
    print("\n[Transformation] Extracted JSON payload ready for database load:")
    print(json.dumps(structured_data, indent=2))