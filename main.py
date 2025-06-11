from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import re
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CareerBot backend is live!"}

def enhance_linkedin_section(section_type: str, user_content: str, additional_info: Optional[str] = None) -> str:
    """
    Generates enhanced LinkedIn content based on the section type and user input.
    """
    base_prompt = ""
    
    if section_type == "headline":
        base_prompt = f"""Rewrite this LinkedIn headline to be more compelling and optimized for ATS:
Original Headline: {user_content}
Desired Career/Job: {additional_info}

Please provide:
1. 3 improved headline versions
2. Explanation of changes made
3. Keywords to include for better visibility"""
    
    elif section_type == "about":
        base_prompt = f"""Rewrite this LinkedIn 'About' section to be more engaging and professional:
Original About: {user_content}
Desired Tone: {additional_info}

Please:
1. Keep it concise (2-3 paragraphs)
2. Highlight key achievements
3. Include relevant keywords
4. Maintain a {additional_info} tone"""
    
    elif section_type == "experience":
        base_prompt = f"""Enhance this LinkedIn experience description:
Original Experience: {user_content}
Aspects to Highlight: {additional_info}

Please:
1. Use bullet points for readability
2. Quantify achievements where possible
3. Focus on {additional_info}
4. Include action verbs"""
    
    elif section_type == "skills":
        base_prompt = f"""Optimize these skills for LinkedIn:
Original Skills: {user_content}
Target Job/Industry: {additional_info}

Please:
1. Categorize skills (Technical, Soft, etc.)
2. Suggest relevant skills to add
3. Recommend skills order
4. Identify top 5 skills to feature"""
    
    elif section_type == "feedback":
        base_prompt = f"""Provide comprehensive feedback on this LinkedIn profile:
Profile Summary: {user_content}
Focus Areas: {additional_info}

Please analyze:
1. Completeness
2. Keyword optimization
3. Professionalism
4. Specific feedback on {additional_info}
5. Overall impression"""
    
    return base_prompt

@app.post("/get_response")
async def get_response(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        history = data.get("history", [])[-5:]  # get last 5 messages

        if not user_input:
            return {"response": "Please enter a valid message."}

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        # Check if this is part of LinkedIn Enhancer flow
        is_linkedin_enhancer = any(
            msg.get("text", "").startswith("Help me enhance my LinkedIn profile") 
            for msg in history
        )

        if is_linkedin_enhancer:
            # Determine which stage of LinkedIn enhancement we're in
            if "Improve my headline" in user_input:
                if "<Please paste" not in user_input:
                    return {"response": "Now, please mention your desired career or job title:"}
            
            elif "Improve my about section" in user_input:
                if "<Please paste" not in user_input:
                    return {"response": "What specific tone would you like for your about section? (e.g., professional, creative, technical)"}
            
            elif "Improve my experience section" in user_input:
                if "<Please paste" not in user_input:
                    return {"response": "What aspects of your experience would you like to highlight? (e.g., achievements, responsibilities, skills)"}
            
            elif "Optimize my skills section" in user_input:
                if "<Please paste" not in user_input:
                    return {"response": "What specific job or industry are you targeting with these skills?"}
            
            elif "Give me overall profile feedback" in user_input:
                if "<Please paste" not in user_input:
                    return {"response": "What specific aspects would you like feedback on? (e.g., completeness, professionalism, keyword optimization)"}
            
            # After collecting all information, generate the enhanced content
            if "Here is my exact" not in user_input and not any(
                q in user_input for q in [
                    "Help me enhance",
                    "Improve my headline",
                    "Improve my about section",
                    "Improve my experience section",
                    "Optimize my skills section",
                    "Give me overall profile feedback"
                ]
            ):
                # This is the final input (career/job/tone/etc.)
                # Find the previous message to determine which section we're enhancing
                prev_msgs = [msg.get("text", "") for msg in history]
                section_type = ""
                
                if "headline" in prev_msgs[-1]:
                    section_type = "headline"
                elif "about section" in prev_msgs[-1]:
                    section_type = "about"
                elif "experience section" in prev_msgs[-1]:
                    section_type = "experience"
                elif "skills section" in prev_msgs[-1]:
                    section_type = "skills"
                elif "profile feedback" in prev_msgs[-1]:
                    section_type = "feedback"
                
                if section_type:
                    # Get the original content from the message before last
                    original_content = prev_msgs[-2].split("Here is my exact")[1].split(":")[1].strip()
                    
                    # Create the specialized prompt
                    prompt = enhance_linkedin_section(section_type, original_content, user_input)
                    
                    # Add context to help the model understand this is LinkedIn-specific
                    prompt = f"[INST] You are a LinkedIn profile expert. {prompt} [/INST]"
                    
                    payload = {
                        "model": "mistralai/Mistral-7B-Instruct-v0.1",
                        "prompt": prompt,
                        "max_tokens": 1000,
                        "temperature": 0.5,
                        "top_p": 0.9
                    }
                    
                    response = requests.post(
                        "https://api.together.xyz/v1/completions",
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    output = result.get("choices", [{}])[0].get("text", "").strip()
                    
                    # Add navigation options
                    if output:
                        output += "\n\n[Actions]\n"
                        output += "1. [Jump to another section]\n"
                        output += "2. [Finish LinkedIn enhancement]"
                    
                    return {"response": output or "No response generated."}

        # Regular chat handling
        formatted_history = ""
        for msg in history:
            role = "user" if msg["sender"] == "You" else "assistant"
            formatted_history += f"{role}: {msg['text']}\n"

        prompt = f"[INST] You are CareerBot, an AI assistant that helps with career guidance.\n{formatted_history}user: {user_input} [/INST]"

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 700,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post("https://api.together.xyz/v1/completions", json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        output = result.get("choices", [{}])[0].get("text", "").strip()

        return {"response": output or "No response generated."}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"response": f"⚠️ Error: {str(e)}"}
