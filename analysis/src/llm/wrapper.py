"""
Lightweight LLM Wrapper for Trend Refinement (Gemini / DeepSeek).

Supports fallback when API key is missing.
Attempts to use standard Google GenAI SDK if installed.
"""

import os
import json
import logging
import asyncio
import random

from src.config import settings

logger = logging.getLogger(__name__)

# SDK Flags
_HAS_GOOGLE_SDK_V1 = False # google-generativeai
_HAS_GOOGLE_SDK_V2 = False # google-genai

try:
    import google.generativeai as genai_v1
    _HAS_GOOGLE_SDK_V1 = True
except ImportError:
    pass

try:
    from google import genai as genai_v2
    _HAS_GOOGLE_SDK_V2 = True
except ImportError:
    pass

_GEMINI_MODELS = [
    "gemini-2.5-flash",
    "models/gemini-2.5-flash", 
]


def _smart_title_case(candidates: list[str]) -> list[str]:
    """
    Fallback quality gate: when LLM is unavailable, apply smart Title Case
    and basic deduplication to raw TF-IDF candidates.
    
    This ensures the dashboard NEVER shows raw lowercase junk like
    "subreddit message compose" or "ai tools".
    """
    seen = set()
    result = []
    
    for phrase in candidates:
        # Title case
        titled = phrase.strip().title()
        
        # Normalize for dedup (e.g. "Ai Tools" and "Ai Tool" -> keep first)
        normalized = titled.lower().rstrip("s")
        if normalized in seen:
            continue
        seen.add(normalized)
        
        # Fix common title case issues (AI, LLM, SEO, etc.)
        titled = (titled
            .replace("Ai ", "AI ")
            .replace(" Ai", " AI")
            .replace("Llm", "LLM")
            .replace("Seo", "SEO")
            .replace("Geo", "GEO")
            .replace("Api", "API")
            .replace("Gpu", "GPU")
            .replace("Cpu", "CPU")
            .replace("Vr ", "VR ")
            .replace("Ar ", "AR ")
            .replace("Ml ", "ML ")
            .replace("Nlp", "NLP")
            .replace("Saas", "SaaS")
            .replace("Iot", "IoT")
            .replace("Deepseek", "DeepSeek")
            .replace("Chatgpt", "ChatGPT")
            .replace("Openai", "OpenAI")
            .replace("Youtube", "YouTube")
            .replace("Tiktok", "TikTok")
        )
        
        result.append(titled)
    
    return result[:20]  # Cap at 20


def get_random_api_key() -> str | None:
    """
    Select a random API key from available environment variables.
    Supports GEMINI_API_KEYS (comma-separated), GEMINI_API_KEY, and GOOGLE_API_KEY.
    """
    # 1. Try multi-key list first
    multi_keys = settings.gemini_api_keys
    if multi_keys:
        keys = [k.strip() for k in multi_keys.split(",") if k.strip()]
        if keys:
            selected = random.choice(keys)
            return selected

    # 2. Fallback to single keys
    return settings.google_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


async def refine_trend_labels(candidates: list[str]) -> list[str]:
    """
    Use LLM to refine raw TF-IDF bigrams into dashboard-ready labels.
    Falls back to smart Title Case if LLM is unavailable.
    """
    api_key = get_random_api_key()
    if not api_key:
        logger.warning("[LLM Wrapper] No API Key found. Using fallback: Smart Title Case.")
        return _smart_title_case(candidates)

    if not (_HAS_GOOGLE_SDK_V1 or _HAS_GOOGLE_SDK_V2):
        logger.warning("[LLM Wrapper] No Google GenAI SDK found. Using fallback: Smart Title Case.")
        return _smart_title_case(candidates)

    try:
        # Prompt
        prompt_text = f"""
You are an expert market analyst. Refine these raw extracted trend keywords into high-quality, professional dashboard labels.

Rules:
1. ELIMINATE all generic, meaningless, or incomplete phrases (e.g., "ai tools", "this is", "instead of", "hard to believe", "with ai", "in ai").
2. KEEP only specific, distinct, and meaningful trends (e.g., "Claude Code", "Grok 3", "Sora vs Veo", "Agentic Workflows").
3. Group synonyms (e.g., "ai tools" + "tools using ai" -> "AI Productivity Tools").
4. If a keyword is too generic, DROP IT. Do not try to save it.
5. Limit output to the top 15 most high-signal trends.
6. Labels should be Title Case, short (2-5 words).

Raw Keywords:
{json.dumps(candidates[:60])}

Output strictly valid JSON list: ["Label 1", "Label 2"]
"""
        
        loop = asyncio.get_event_loop()
        text_response = ""
        last_error = None

        for model_name in _GEMINI_MODELS:
            try:
                # Try V2 (New SDK) first if available
                v2_success = False
                if _HAS_GOOGLE_SDK_V2:
                    try:
                        def call_v2():
                            client = genai_v2.Client(api_key=api_key)
                            return client.models.generate_content(
                                model=model_name,
                                contents=prompt_text,
                                config={"response_mime_type": "application/json"}
                            )
                        
                        response = await loop.run_in_executor(None, call_v2)
                        text_response = response.text
                        v2_success = True
                        logger.info(f"LLM refinement succeeded with model: {model_name} (SDK V2)")
                        break # Success
                    except Exception as e:
                        logger.warning(f"Model {model_name} failed with SDK V2: {e}")
                        last_error = e

                # Try V1 (Old SDK) if V2 failed/missing
                if not v2_success and _HAS_GOOGLE_SDK_V1:
                    try:
                        def call_v1():
                            genai_v1.configure(api_key=api_key)
                            model = genai_v1.GenerativeModel(model_name)
                            return model.generate_content(
                                prompt_text,
                                generation_config={"response_mime_type": "application/json"}
                            )
                        
                        response = await loop.run_in_executor(None, call_v1)
                        text_response = response.text
                        logger.info(f"LLM refinement succeeded with model: {model_name} (SDK V1)")
                        break # Success
                    except Exception as e:
                        logger.warning(f"Model {model_name} failed with SDK V1: {e}")
                        last_error = e
            
            except Exception as e:
                logger.warning(f"Unexpected error trying model {model_name}: {e}")
                last_error = e

        if not text_response:
            logger.warning(f"[LLM Wrapper] All LLM models failed ({last_error}). Using fallback: Smart Title Case.")
            return _smart_title_case(candidates)

        # Parse result
        clean_text = text_response.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        labels = json.loads(clean_text.strip())
        
        if isinstance(labels, list) and all(isinstance(x, str) for x in labels):
            logger.info(f"LLM refined {len(candidates)} keywords into {len(labels)} labels")
            return labels
        else:
            logger.warning("[LLM Wrapper] LLM returned invalid JSON. Using fallback: Smart Title Case.")
            return _smart_title_case(candidates)

    except Exception as e:
        logger.error(f"[LLM Wrapper] LLM refinement CRASHED: {e}. Using fallback: Smart Title Case.")
        return _smart_title_case(candidates)
