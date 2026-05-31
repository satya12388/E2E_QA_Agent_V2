from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from sarvam import SarvamLLM
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import ChatOllama as browserollama


load_dotenv()

def get_model(provider="groq", temperature=0):
    """
    Factory function to fetch AI models.
    Supported providers: 'sarvam', 'groq', 'openai'
    """
    
    if provider == "sarvam":
        # Sarvam uses OpenAI-compatible headers
        return SarvamLLM(
            model="Sarvam 105b", # or "sarvam-m" for the larger model
            # temperature=temperature,     
        )
    
    elif provider == "groq":
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=temperature,
            # reasoning_format="hidden"
        )
    
    elif provider == "ollama":
        return ChatOllama(
            model="gemma4:e2b",
            temperature=temperature,
            reasoning=False
        )
    
    elif provider == "ollamaBrowser":
        return browserollama(
            model="gemma4:e2b",
            timeout=120,
            ollama_options={
                "num_ctx": 8192,       
                "temperature": 0.0,
                "num_predict": 1024,
                "reasoning":False
            }
        )
    
    elif provider == "google":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            model_kwargs={
                "generation_config": {
                    "thinking_config": {"thinking_budget": 0}
                }
            }
        )
    
    else:
        raise ValueError(f"Provider {provider} not supported.")