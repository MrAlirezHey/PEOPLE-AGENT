from linkedin_api import Linkedin
from selenium import webdriver
from dotenv import load_dotenv
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)
linkdin_email=os.getenv("linkdin_email")
password=os.getenv('paswword')
api=Linkedin(linkdin_email,password=password)

username='grkashani'

porfile=api.get_profile(username)
#job=api.get_job(username)
skill=api.get_profile_skills(username)
job_skill=api.get_job_skills(username)
print(porfile['summary'])
#print(f'_______________{job}')
print(f'_______________{skill}')
for item in skill:
    print(item['name'])


def linkdin_search(user_name:str):
    profile=api.get_profile(username)
    skill=api.get_profile_skills(username)
    skills_string=', '.join([item['name'] for item in skill])
    combined_string = f"Skills: {skills_string}\nSummary: {profile['summary']}"
    return combined_string

