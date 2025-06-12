from fastapi import FastAPI, Request 
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import re
import requests
import os
import json
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
    if section_type == "headline":
        return f"""Rewrite this LinkedIn headline to be more compelling and optimized for ATS:
Original Headline: {user_content}
Desired Career/Job: {additional_info}

Please provide:
1. 3 improved headline versions
2. Explanation of changes made
3. Keywords to include for better visibility"""
    
    elif section_type == "about":
        return f"""Rewrite this LinkedIn 'About' section to be more engaging and professional:
Original About: {user_content}
Desired Tone: {additional_info}

Please:
1. Keep it concise (2-3 paragraphs)
2. Highlight key achievements
3. Include relevant keywords
4. Maintain a {additional_info} tone"""
    
    elif section_type == "experience":
        return f"""Enhance this LinkedIn experience description:
Original Experience: {user_content}
Aspects to Highlight: {additional_info}

Please:
1. Use bullet points for readability
2. Quantify achievements where possible
3. Focus on {additional_info}
4. Include action verbs"""
    
    elif section_type == "skills":
        return f"""Optimize these skills for LinkedIn:
Original Skills: {user_content}
Target Job/Industry: {additional_info}

Please:
1. Categorize skills (Technical, Soft, etc.)
2. Suggest relevant skills to add
3. Recommend skills order
4. Identify top 5 skills to feature"""
    
    elif section_type == "comprehensive_feedback":
        headline = user_content.get("headline", "")
        about = user_content.get("about", "")
        experience = user_content.get("experience", "")
        skills = user_content.get("skills", "")
        desired_job = user_content.get("desiredJob", "")
        
        scores = {
            "Headline": min(100, max(60, len(headline) // 3)),
            "About": min(100, max(50, len(about) // 5)),
            "Experience": min(100, max(70, len(experience) // 4)),
            "Skills": min(100, max(65, len(skills) // 2)),
            "Overall": min(100, max(60, (len(headline) + len(about) + len(experience) + len(skills)) // 25)),
        }
        
        analysis_prompt = f"""Provide comprehensive LinkedIn profile feedback based on:
        
Current Headline: {headline}
About Section: {about}
Experience Section: {experience}
Skills Section: {skills}
Desired Career/Job: {desired_job}

Analysis Format:
1. **Profile Summary**: Brief overview
2. **Section-by-Section Analysis**:
   - Headline: /100 score - Key feedback
   - About: /100 score - Key feedback
   - Experience: /100 score - Key feedback
   - Skills: /100 score - Key feedback
3. **Top 3 Recommendations**
4. **Keyword Optimization** for "{desired_job}"
5. **Final Score**: /100 with justification"""

        return {
            "visualization": scores,
            "analysis": analysis_prompt
        }

@app.post("/get_response")
async def get_response(request: Request):
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        history = data.get("history", [])[-5:]

        if not user_input:
            return {"response": "Please enter a valid message."}

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        is_linkedin_enhancer = any(
            msg.get("text", "").startswith("Help me enhance my LinkedIn profile") 
            for msg in history
        )

        if is_linkedin_enhancer:
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
                    return {
                        "response": "Let's analyze your entire LinkedIn profile. First, please share your current headline:",
                        "feedback_flow": "awaiting_headline"
                    }
                else:
                    return {"response": "Please edit the message with your actual headline and send it again."}
            
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
                feedback_flow = data.get("feedback_flow")
                if feedback_flow:
                    if feedback_flow == "awaiting_headline":
                        return {
                            "response": "Great! Now please share your About section:",
                            "feedback_flow": "awaiting_about",
                            "headline": user_input
                        }
                    elif feedback_flow == "awaiting_about":
                        return {
                            "response": "Thank you. Next, please share your Experience section:",
                            "feedback_flow": "awaiting_experience",
                            "about": user_input
                        }
                    elif feedback_flow == "awaiting_experience":
                        return {
                            "response": "Got it. Now please share your Skills:",
                            "feedback_flow": "awaiting_skills",
                            "experience": user_input
                        }
                    elif feedback_flow == "awaiting_skills":
                        return {
                            "response": "Finally, what is your desired career/job title?",
                            "feedback_flow": "awaiting_job",
                            "skills": user_input
                        }
                    elif feedback_flow == "awaiting_job":
                        profile_data = {
                            "headline": data.get("headline"),
                            "about": data.get("about"),
                            "experience": data.get("experience"),
                            "skills": data.get("skills"),
                            "desired_job": user_input
                        }
                        
                        result = enhance_linkedin_section("comprehensive_feedback", profile_data)
                        prompt = f"[INST] You are a LinkedIn expert. {result['analysis']} [/INST]"
                        
                        payload = {
                            "model": "mistralai/Mistral-7B-Instruct-v0.1",
                            "prompt": prompt,
                            "max_tokens": 1500,
                            "temperature": 0.5,
                            "top_p": 0.9
                        }
                        
                        response = requests.post(
                            "https://api.together.xyz/v1/completions",
                            json=payload,
                            headers=headers
                        )
                        response.raise_for_status()
                        
                        llm_response = response.json()
                        output = llm_response.get("choices", [{}])[0].get("text", "").strip()
                        
                        return {
                            "response": output,
                            "visualization": result["visualization"]
                        }

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
                
                if section_type:
                    original_content = prev_msgs[-2].split("Here is my exact")[1].split(":")[1].strip()
                    prompt = enhance_linkedin_section(section_type, original_content, user_input)
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
                    
                    if output:
                        output += "\n\n[Actions]\n"
                        output += "1. [Jump to another section]\n"
                        output += "2. [Finish LinkedIn enhancement]"
                    
                    return {"response": output or "No response generated."}

        formatted_history = ""
        for msg in history:
            role = "user" if msg["sender"] == "You" else "assistant"
            formatted_history += f"{role}: {msg['text']}\n"

        prompt = f"[INST] You are CareerBot, an AI assistant that helps with career guidance. Only answer to career-related questions.\n{formatted_history}user: {user_input} [/INST]"

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
        output = output.replace('\n', '<br>')

        return {"response": output or "No response generated."}

    except Exception as e:
        print(f"[ERROR] {e}")
        return {"response": f"⚠️ Error: {str(e)}"}
