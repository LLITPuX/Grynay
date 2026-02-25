import os
from dotenv import load_dotenv
from fastmcp import FastMCP

# Optional: Add any pre-startup configuration here
load_dotenv()

# Create the MCP server
mcp = FastMCP("llm-provider-mcp")

def call_gemini(prompt: str, system_prompt: str, model: str) -> str:
    from google import genai
    from google.genai import types
    from google.oauth2.credentials import Credentials
    import os
    
    token_path = os.environ.get("GEMINI_TOKEN_PATH", "credentials/token.json")
    
    if not os.path.exists(token_path):
        return f"Error: Token file not found at {token_path}. Please generate it via OAuth and place it in the credentials folder."
        
    try:
        creds = Credentials.from_authorized_user_file(token_path)
        client = genai.Client(credentials=creds)
        
        config = None
        if system_prompt:
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )
        return response.text
    except Exception as e:
        return f"Gemini API Error: {str(e)}"

def call_openai(prompt: str, system_prompt: str, model: str) -> str:
    from openai import OpenAI
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY not configured."
        
    client = OpenAI(api_key=api_key)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"OpenAI API Error: {str(e)}"

@mcp.tool()
async def run_agent_task(prompt: str, system_prompt: str = None, context: list = None, model: str = "gemini-2.5-flash-thinking-exp") -> str:
    """
    Run an agent task via the specified LLM provider.
    """
    print(f"[run_agent_task] Received request for model: {model}")
    print(f"[run_agent_task] Prompt length: {len(prompt)}, System prompt length: {len(system_prompt) if system_prompt else 0}")
    
    model_lower = model.lower()
    
    if "gemini" in model_lower:
        return call_gemini(prompt, system_prompt, model)
    elif "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
        return call_openai(prompt, system_prompt, model)
    else:
        return f"Error: Unsupported model identifier '{model}'. Must contain 'gemini' or 'gpt'/'o1'/'o3'."

if __name__ == "__main__":
    import sys
    if "--sse" in sys.argv:
        mcp.run(transport="sse", host="0.0.0.0", port=8001)
    else:
        mcp.run()
