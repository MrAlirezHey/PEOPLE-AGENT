from typing import Annotated , TypedDict ,List,Dict,Any,Optional
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode,tools_condition
from pydantic import BaseModel ,Field,ConfigDict
from langchain.agents import Tool
from mem0 import Memory
from langgraph.checkpoint.memory import MemorySaver 
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from tavily import TavilyClient
import logging

import uuid
import os
import sys
import requests
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from linkedin_api import Linkedin

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)
linkdin_email=os.getenv("linkdin_email")
password=os.getenv('paswword')
api=Linkedin(linkdin_email,password=password)
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY')
if not TAVILY_API_KEY:
    raise ValueError("Tavily API key not found in .env file.")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
def web_serach(State):
    try:
        logging.info(f"Performing web search for query: '{State['web_search_quary_chat']}'")
        response = tavily_client.search(query=State['web_search_quary_chat'], search_depth="advanced", max_results=3)
        query_resp = " ".join([result.get('content', '') for result in response.get('results', [])])
        logging.info(f"Found 3 results.")
        new_state={'web_search_chat_resp':query_resp}
        
    except Exception as e:
        logging.error(f"An error occurred during Tavily API call: {e}", exc_info=True)
        return [{"error": "Failed to perform web search.", "details": str(e)}]





def get_github_user_repos(github_username: str, max_repos: int = 10) -> dict:
    url = f"https://api.github.com/users/{github_username}/repos?sort=updated&per_page={max_repos}"

    try:

        response = requests.get(url)

        if response.status_code != 200:
            return {"error": f"Failed to fetch repositories for {github_username}. Status code: {response.status_code}"}

        repos_data = response.json()

        for repo in repos_data:
            repo_name = repo.get("name")
         
            readme_content = get_github_readme(github_username, repo_name)
            if readme_content:
                
                combined_readme += f"### {repo_name} README\n{readme_content}\n\n"
            else:
                print(f"README.md not found for {repo_name}, skipping.")
        
        return combined_readme

    except Exception as e:
        return {"error": str(e)}

def get_github_readme(github_username: str, repo_name: str) -> str:
    
    url = f"https://api.github.com/repos/{github_username}/{repo_name}/readme"

    try:
        
        response = requests.get(url)

        
        if response.status_code == 404:
            return None

        if response.status_code != 200:
            return f"Failed to fetch README for {repo_name}. Status code: {response.status_code}"

        
        readme_data = response.json()
        readme_content_base64 = readme_data.get("content", "")

        
        readme_content = base64.b64decode(readme_content_base64).decode("utf-8")

        return readme_content

    except Exception as e:
        return f"Error fetching README for {repo_name}: {str(e)}"


github_username = "MrAlirezHey"  
repos_info = get_github_user_repos(github_username)

def linkdin_search(user_name:str):
    if 'linkedin.com/in/' in user_name:
        user_name = user_name.split('linkedin.com/in/')[1].split('/')[0]
    profile=api.get_profile(user_name)
    skill=api.get_profile_skills(user_name)
    skills_string=', '.join([item['name'] for item in skill])
    combined_string = f"Skills: {skills_string}\nSummary: {profile['summary']}"
    return combined_string
