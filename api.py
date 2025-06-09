import requests
import json
import os
from typing import Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set")

MODEL_CONFIG = {
    'gemini': {
        'model': 'google/gemini-2.0-flash-exp:free',
        'name': 'Gemini',
        'color': 'blue'
    },
    'deepseek': {
        'model': 'deepseek/deepseek-r1:free',
        'name': 'DeepSeek',
        'color': 'indigo'
    },
    'llama': {
        'model': 'meta-llama/llama-4-maverick:free',
        'name': 'Llama',
        'color': 'purple'
    }
}

def query_openrouter(prompt: str, context: Dict[str, Any], model: str) -> str:
    """Query OpenRouter API with the given prompt and context"""
    try:
        if model not in MODEL_CONFIG:
            raise ValueError(f"Unknown model: {model}")
        
        full_prompt = (
            "Answer the following question based on the provided webpage content.\n\n"
            f"Webpage content:\n{format_context(context)}\n\n"
            f"Question: {prompt}"
        )
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "SmartScrape AI"        
        }
        
        payload = {
            "model": MODEL_CONFIG[model]['model'],
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer concisely and accurately based on the provided context."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        logger.info(f"Querying {MODEL_CONFIG[model]['name']} with prompt: {prompt[:100]}...")
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data['choices'][0]['message']['content']
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed for {model}: {str(e)}")
        return f"API Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error processing {model} response: {str(e)}")
        return f"Processing Error: {str(e)}"

def format_context(context: Dict[str, Any]) -> str:
    """Format the scraped content into a readable string for AI context"""
    formatted = []
    
    if context.get('titles'):
        formatted.append("## Titles\n" + "\n".join(f"- {title}" for title in context['titles']))
    
    if context.get('paragraphs'):
        formatted.append("## Main Content\n" + "\n\n".join(context['paragraphs']))
    
    if context.get('links'):
        formatted.append("## Links\n" + "\n".join(
            f"- [{link['text']}]({link['url']})" for link in context['links']
        ))
    
    if context.get('tables'):
        for i, table in enumerate(context['tables'], 1):
            table_str = [f"### Table {i}"]
            if table['headers']:
                table_str.append("| " + " | ".join(table['headers']) + " |")
                table_str.append("|" + "|".join(["---"] * len(table['headers'])) + "|")
            for row in table['rows']:
                table_str.append("| " + " | ".join(row) + " |")
            formatted.append("\n".join(table_str))
    
    return "\n\n".join(formatted)

def query_ai_models(question: str, context: Dict[str, Any], model: str = 'gemini') -> Dict[str, str]:
    """Query all three AI models through OpenRouter and return their responses"""
    responses = {}
    
    for model in MODEL_CONFIG:
        try:
            responses[model] = query_openrouter(question, context, model)
        except Exception as e:
            logger.error(f"Failed to query {model}: {str(e)}")
            responses[model] = f"Error: Failed to get response from {MODEL_CONFIG[model]['name']}"
    
    return responses
