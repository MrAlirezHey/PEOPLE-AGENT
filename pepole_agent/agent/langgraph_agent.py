from typing import Annotated , TypedDict ,List,Dict,Any,Optional
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel ,Field,ConfigDict,root_validator
from langchain.agents import Tool 
from mem0 import Memory
from langgraph.checkpoint.memory import MemorySaver 
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage,ToolMessage,ToolCall
import uuid
import os
import openai
import sys
import cv2
from tavily import TavilyClient
import logging
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from guardrails import Guard
wrapped_client = wrap_openai(openai.Client(base_url='https://api.gapgpt.app/v1',api_key='sk-677jnZFMuOcsypqWyLyYgMKYihFQsJBtLz8MdDU2LINzL6EU'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#from core.memory import get_vector_from_text,get_user_memory,search_with_vector
from tools.base_tool import get_github_readme,get_github_user_repos,linkdin_search
from agent.explore_mode import load_eval_data,upload_data
from PIL import Image
from core.user_management import save_eval_resp
#from core.memory import search_with_vector,get_vector_from_text,get_user_memory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

Api_key=os.getenv("GAP_GAP_API_KEY")
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": 'gpt-4o-mini'
        }
    },
    "vector_store": {
        "provider": "supabase",
        "config": {
            "connection_string": os.environ['DATABASE_URL2'],
            "collection_name": "memories"
        }
    }    
}
memory = Memory.from_config(config)

class ChatOutput(BaseModel):
    response: str = Field(..., description="The question the agent asks the user, intended to gather more information for profile creation.")
    is_final: bool = Field(False, description="Indicates whether enough information has been collected for evaluation. Becomes True once sufficient data is gathered.")
    questions_asked: int = Field(0, description="The number of questions asked so far in this conversation.")
    web_search_req: bool = Field(False, description="Indicates whether additional information should be gathered through a web search. If set to True, the agent will perform a web search to collect more details about the user's claims, background, or experience. This helps ensure that the profile is as accurate and up-to-date as possible.")
    web_search_query_chat: Optional[str] = Field(None, description="The search query for gathering more information from the web.")
    github_link: Optional[str] = Field(None, description="GitHub username or full GitHub profile link. Only the username should be provided if possible.")
    linkdin_link: Optional[str] = Field(None, description="LinkedIn username or full LinkedIn profile link. Only the username should be provided if possible")

    @root_validator(pre=True)
    def check_web_search_query(cls, values):
        if values.get('web_search_query_chat'):
            values['web_search_req'] = True
        
        if values.get('github_link'):
            github_link = values.get('github_link')
        
            if 'github.com' in github_link:
                values['github_link'] = github_link.split('github.com/')[1].split('/')[0] 
       
      
        if values.get('linkedin_link'):
            linkedin_link = values.get('linkedin_link')
            
            if 'linkedin.com/in/' in linkedin_link:
                values['linkedin_link'] = linkedin_link.split('linkedin.com/in/')[1].split('/')[0]  # استخراج نام کاربری

        return values
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Can you provide your GitHub profile link?",
                "is_final": False,  
                "questions_asked": 5,
                "web_search_req": True,
                "web_search_query_chat": "What is the user's experience with Python?",  
                "github_link": "https://github.com/username",
                "linkdin_link": "https://www.linkedin.com/in/username"
            }
        }
class EvaluatorOutput(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="A numerical score between 0 and 1 based on the user's claims' quality and accuracy.")
    feedback: str = Field(..., description="A summary of the evaluation based on the user's claims and experience.")
    score_reason: str = Field(..., description="Explanation for why the score was given. Discusses the pros and cons of the user's performance.")
    issues_and_strengths: str = Field(..., description="List of problems and strengths identified during the evaluation.")
    summary: str = Field(..., description="A summary of the user's experience, skills, and background.")
    normalized_field: str = Field(..., description="Normalized field of interest. Example: If the user talks about LLM, NLP, or AI, the output should be 'AI Engineering' in lowercase.")
    claims_verified: List[str] = Field(default=[], description="List of claims that have been verified successfully.")
    strengths: Optional[List[str]] = Field(default=None, description="List of strengths identified during the evaluation.")
    class Config:
        json_schema_extra = {
            "example": {
                "score": 0.85,
                "feedback": "The user has strong technical knowledge and experience in Python, but there are some gaps in their claim verification. Their claims regarding GitHub contributions were not fully verified.",
                "score_reason": "The user demonstrated strong Python skills, but some claims could not be verified.",
                "issues_and_strengths": "Strengths: Strong Python skills, Weaknesses: GitHub contributions not verified.",
                "summary": "The user has 10 years of experience in Python, with a focus on machine learning and web development.",
                "normalized_field": "python",
                "claims_verified": ["10 years of Python experience", "Worked with machine learning models"],     
                "strengths": ["Strong understanding of Python", "Experience with machine learning"],
            }
        }
class AgentState(TypedDict):
    user_id: str
    messages : Annotated[list,add_messages]
    validation_turn:bool
    user_input_needed:bool
    end:bool
    web_search_req:bool
    web_search_quary_chat:Optional[str]
    web_search_chat_resp:Optional[str]
    github_link:Optional[str]
    linkdin_link:Optional[str]
    

#tool_search=Tool(
#    name='search',
#    func=serper.run,
#    description='ss'
#)
#tool_search.invoke('sss')
#web_search_tool = Tool(
#    name="web_search_tool",
#    func=web_serach,
#    description="""
#    This tool performs a web search to find publicly available professional profiles and resumes of individuals in similar fields. 
#    It collects data from various professional platforms such as LinkedIn, GitHub, and other networking websites to gather information on individuals with similar qualifications, experiences, and career paths.
#    
#    **Purpose**:
#    The main goal of this tool is to validate and cross-check a user's professional claims by comparing their experience, skills, and qualifications with other professionals in the same domain.
#    
#    **How It Works**:
#    - The tool searches the web using the user's provided query (such as job title, skills, or experience).
##    - It identifies relevant professional profiles and resumes of individuals who share similar experiences or work in similar industries.
#    - The gathered data is analyzed to evaluate whether the user's claims about their experience and expertise are consistent with industry standards and other professionals in their field.
#    
#    **Use Case**:
#    - **Experience Validation**: If the user claims to have several years of experience in a particular field, this tool can cross-reference their claims with other similar professionals' profiles.
#    - **Skill Comparison**: Extracting specific skills and qualifications from the resumes of other professionals to compare against the user's stated skills.
#    - **Professional Networking Insights**: By comparing the user's profile with others in the same field, this tool can provide valuable insights into the typical career trajectory and professional background required for specific roles.
#    
#    **Outcome**:
#    This tool provides a list of relevant professional profiles that help validate the user's experience and skills by comparing them to industry peers. This data can be used to adjust or verify the user's professional profile and help with more accurate scoring in the evaluation process.
#    """
#)
chat_agent=ChatOpenAI(base_url="https://api.gapgpt.app/v1",api_key=Api_key , model='gpt-4o-mini')


chat_agent=chat_agent.with_structured_output(ChatOutput)
eval_agent=ChatOpenAI(base_url="https://api.gapgpt.app/v1",api_key=Api_key , model='gpt-4o-mini')
#eval_agent=eval_agent.bind_tools([web_search_tool])
eval_agent=eval_agent.with_structured_output(EvaluatorOutput)
def chat_agent_node(State: AgentState) -> Dict[str,Any]:
    sys_message = f'''You are an intelligent agent whose primary responsibility is to collect accurate and valid information from the user to verify their claims and build a comprehensive profile.
Your main goal is to ask targeted, insightful questions based on the user's information and history to gather enough data to construct a detailed profile.

**Guardrails:**
1. You should never answer general or technical questions. If the user asks a question like "What is OOP?" or "How do I do X?", politely and respectfully tell them that your role is to collect information to build their profile and you are unable to answer general or technical questions. This helps maintain your focused role and prevents you from deviating from your responsibilities.

2. When asking questions, ensure they are framed in a friendly, non-interrogative manner. You should never make the user feel like they are being interrogated. Your questions should be warm, engaging, and designed to gather information for their profile.

**Information Collection Strategy:**
For collecting data, you use the following methods (At first serach a web for additional information):
WEB_SEARCH_INFORMATION={State.get('web_search_chat_resp')}

1. **Profession-Specific Challenges:**
    You should ask questions that assess the user's problem-solving ability in their field. These questions should be based on real-world, applicable challenges. For example:
    User: "I’ve been working with Python for 10 years."
    Your question: "I recently worked on a project that required processing large data concurrently. I used **asyncio** and **multiprocessing** to manage this, but encountered some issues when scaling. How do you think I could optimize this problem further?"
    Objective: Evaluate the user's ability to handle complex issues and their experience with advanced Python concepts.

2. **Asking about Mistakes and Best Practices:**
    You should ask the user about common mistakes in their field and best practices that lead to success. The question should be framed as if you're genuinely interested in learning and improving yourself. For example:
    User: "I have 3 years of experience working with CNC machines."
    Your question: "Given your 3 years of experience with CNC, what common mistakes do you think can lead to serious issues in this field? Also, what are the best practices you've found that help improve performance and efficiency? I’m really eager to learn more from your experience."

3. **Discussing the Most Difficult Challenges:**
    Ask the user to reflect on the hardest challenges they've faced and how they overcame them. This will give you insights into their problem-solving and coping skills. For example:
    User: "I have 4 years of experience in mechatronics."
    Your question: "That’s awesome that you have 4 years of experience in mechatronics! I’m really interested in learning from your experiences. What’s been the hardest challenge you’ve faced in this field so far? How did you overcome it?"

4. **Exploring Past Mistakes and Decisions:**
    Ask the user about mistakes they've made during their career and what they would change if they could go back. This will give you insights into their self-awareness and decision-making abilities. For example:
    User: "I have 5 years of experience in web design."
    Your question: "With five years of web design experience, you’ve likely encountered many challenges. If you could go back and undo one of the biggest mistakes you’ve made, what would it be? Also, what key decisions or practices helped you achieve success in this field?"

5. **Requesting GitHub and LinkedIn Profiles:**
    Since you're building a comprehensive profile for the user, it’s essential to request links to their professional social media accounts, such as GitHub and LinkedIn. This helps in validating their professional background and skills:
    Your question: "To help build a more complete profile, would you mind sharing your GitHub and LinkedIn profiles with me? It would really help in verifying your skills and past projects."

**Using Web Search for Updated Information:**
In addition to collecting information from the user's input, you can utilize the **web search tool** to gather more updated or specific details about the user’s background, skills, or experience. This will help in verifying claims or gathering information that may not have been provided directly by the user.

If you believe that you need more context or more accurate details about a certain claim, feel free to perform a web search using the **web search tool**. Once the search results are retrieved, you can ask the user follow-up questions based on the new insights gained from the search. For example:

- If the user claims to have worked on a specific project, but you'd like more details, use the web search tool to find more information about that project or technology.
- If the user mentions a skill but you're unsure about their expertise, search for more details about the tools, technologies, or methods associated with that skill, and ask more specific questions.

Once you have gathered updated information through the search, you can adapt your questions to be more targeted and relevant. You can also validate or refine the claims made by the user based on this additional data.

**Conversation Flow:**
In your conversation with the user, you should aim to ask all of these questions in a friendly and engaging manner. The goal is to collect enough information to build an accurate profile and understand the user’s professional journey. Once you feel you have gathered sufficient data, you should naturally conclude the conversation.

**Response Guidelines:**
- If the user speaks in Persian, respond in Persian.
- If the user speaks in English, respond in English.

**Final Note:** Your sole responsibility is to collect information for profile creation. You should not provide answers to any user questions unless the user directly asks about you.

    '''
    #if State.get('web_search_chat_resp'):
    #    sys_message+=f"you must to  use this information fo provide better question{State['web_search_chat_resp']}"
    found_system_message=False
    messages= State['messages']
    relevant_memories = memory.search(query=messages[-1].content, user_id=State['user_id'], limit=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
    sys_message+=f"\nUser Memories:\n{memories_str}"
    print(messages)
    for message in messages:
        if isinstance(message,SystemMessage):
            message.content=sys_message
            found_system_message=True
    
    if not found_system_message:
        messages=[SystemMessage(content=sys_message)]+messages
    up=[{'role':"user",'content':messages[-1].content}]
    response = chat_agent.invoke(messages)
    up.append({"role": "assistant", "content": response.response})
    memory.add(up, user_id=State['user_id'])
    print(up)
    
    
    print(response.web_search_req)
    print(response.web_search_query_chat)
    print(response.github_link)
    print(response.linkdin_link)
    return {"messages": [AIMessage(content=response.response)],
            'validation_turn':response.is_final,
            "web_search_req":response.web_search_req,
            "web_search_quary_chat":response.web_search_query_chat,
            'github_link':response.github_link,
            'linkdin_link':response.linkdin_link,
            "web_search_chat_resp":None
        }
def evaluator_agent(State:AgentState) -> AgentState:
    sys_message = """You are an intelligent agent responsible for evaluating the accuracy and honesty of a user's claims. Your goal is to:

    1. Assess the accuracy of the user's claims based on their previous interactions, profile information, and historical data.
    2. Use the web search tool to validate these claims, cross-reference any information, and gather additional relevant data from professional profiles (GitHub, LinkedIn).
    3. If the user claims 10 years of experience, verify this against their GitHub and LinkedIn profiles, as well as previous user messages.
    4. If the user's claims are contradictory (e.g., claiming 10 years of experience but lacking corresponding data or projects), reduce the score accordingly.
    5. For each claim, you will:
        - Check if the user's claim is consistent with their past messages and information.
        - Verify if the claim aligns with data available from their GitHub and LinkedIn profiles.
    6. Assign a credibility score between 0 and 1, where higher scores reflect stronger alignment with verified data, and lower scores reflect discrepancies or unverified claims.

    Consider the following:
    - **GitHub**: Review the user's repositories, contributions, and skills demonstrated through projects to verify the claims of experience.
    - **LinkedIn**: Look for endorsements, job history, and skills validation through professional recommendations and colleagues' feedback.
    - **Historical Messages**: Cross-reference claims with the information the user has previously provided to identify contradictions or inconsistencies.
    
    Your task is to ensure an objective, accurate evaluation based on all available sources.
    """


    user_message=[]#get_user_memory(State['user_id'])] 
    ai_message=[]
    history=memory.get_all(user_id=State['user_id'])
    history_str = "\n".join(f"- {entry['memory']}" for entry in history["results"])
    sys_message+=f" user all data :{history_str}"
    print(history_str)
    eval_message=[SystemMessage(content=sys_message)]
    for i ,item in enumerate(State['messages']):
        if isinstance(item,HumanMessage):
            eval_message.append(item)
            print(isinstance(item,HumanMessage))
    if State.get('github_link'):
        github_info=get_github_user_repos(State['github_link'])
    #eval_message=[SystemMessage(content=sys_message),HumanMessage(content=user_message)]
        if github_info:
            eval_message.append(HumanMessage(content=f"GitHub repositories info: {github_info}"))
    if State.get("linkdin_link"):
        linkdin_datails=linkdin_search(State['linkdin_link'])
        if linkdin_datails:
            eval_message.append(HumanMessage(content=f"linkdin info: {github_info}"))
    eval_result=eval_agent.invoke(eval_message)
    save_eval_resp(user_id=State['user_id'],
                    summary= eval_result.summary ,
                    score= eval_result.score,
                    score_reason= eval_result.score_reason,
                    field_of_interest=  eval_result.normalized_field.lower(),
                    issues_and_strengths= eval_result.issues_and_strengths,
                    github_link = State['github_link'] ,
                    linkedin_link =  State['linkdin_link'] 
    )
    upload_data(load_eval_data(State['user_id']))
    print(eval_result.score)
    new_state={
        'end':True,
        'user_input_needed':False,
        "validation_turn":False
    }
    return new_state
def foute_base_on_evaluation(State:AgentState)->str:
    last_message = State["messages"][-1]
    print(f'last message {last_message}')
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print('tools')
        return "tools"
    else:
        return 'END'
def chat_router(State:AgentState)->str :
    if State['web_search_req']:
        return "web"
    if State['validation_turn']:
        return "eval"
    else:
        return "END"
TAVILY_API_KEY=os.getenv('TAVILY_API_KEY')
if not TAVILY_API_KEY:
    raise ValueError("Tavily API key not found in .env file.")
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
def web_serach(State:AgentState)->AgentState:
    try:
        logging.info(f"Performing web search for query: '{State['web_search_quary_chat']}'")
        response = tavily_client.search(query=State['web_search_quary_chat'], search_depth="advanced", max_results=3)
        query_resp = " ".join([result.get('content', '') for result in response.get('results', [])])
        logging.info(f"Found 3 results.")
        new_state={'web_search_chat_resp':query_resp}
        return new_state
    except Exception as e:
        logging.error(f"An error occurred during Tavily API call: {e}", exc_info=True)
        return [{"error": "Failed to perform web search.", "details": str(e)}]
graph_builder=StateGraph(AgentState)
graph_builder.add_node('web',web_serach)
graph_builder.add_node('chat',chat_agent_node)
graph_builder.add_node('eval',evaluator_agent)
#graph_builder.add_node('tools',ToolNode(tools=[web_search_tool]))
graph_builder.add_conditional_edges('chat',chat_router,{'eval':'eval',
                                                        'web':'web',
                                                        'END':END})
graph_builder.add_conditional_edges('eval',foute_base_on_evaluation,{'END':END})                                                             
graph_builder.add_edge(START,'chat')
graph_builder.add_edge("web",'chat')
#graph_builder.add_edge('tools','eval')
checkpointer = MemorySaver()

graph=graph_builder.compile(checkpointer=checkpointer)
