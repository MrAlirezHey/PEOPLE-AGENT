import os
from openai import OpenAI
from mem0 import Memory
import os
from dotenv import load_dotenv
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)
Api_key=os.getenv("GAP_GAP_API_KEY")
mem_api=os.getenv('MEM_API')


config = {
    "llm": {
        "provider": "openai",
        
        "config": {
            'openrouter_base_url' :'https://api.gapgpt.app/v1',
            "api_key":Api_key,
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key":Api_key,
            "model": "text-embedding-3-large"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "embedding_model_dims": 3072,
        }
    },
    "version": "v1.1",
}

class PersonalTravelAssistant:
    def __init__(self):
        self.client = OpenAI(base_url='https://api.gapgpt.app/v1',api_key='sk-5Au1uXjPPG7Z7SirxaV56Xdcg8n61S7Yj2U7ULCppWw4ZDaD')
        self.memory = Memory.from_config(config)
        self.messages = [{"role": "system", "content": "You are a personal AI Assistant."}]

    def ask_question(self, question, user_id):
        # Fetch previous related memories
        previous_memories = self.search_memories(question, user_id=user_id)

        # Build the prompt
        system_message = "You are a personal AI Assistant."

        if previous_memories:
            prompt = f"{system_message}\n\nUser input: {question}\nPrevious memories: {', '.join(previous_memories)}"
        else:
            prompt = f"{system_message}\n\nUser input: {question}"

        # Generate response using Responses API
        response = self.client.responses.create(
            model="gpt-4o",
            input=prompt
        )

        # Extract answer from the response
        answer = response.output[0].content[0].text

        # Store the question in memory
        self.memory.add(question, user_id=user_id)
        return answer

    def get_memories(self, user_id):
        memories = self.memory.get_all(user_id=user_id)
        return [m['memory'] for m in memories['results']]

    def search_memories(self, query, user_id):
        memories = self.memory.search(query)
        return [m['memory'] for m in memories['results']]

# Usage example
user_id = "traveler_123"
ai_assistant = PersonalTravelAssistant()

def main():
    while True:
        question = input("Question: ")
        if question.lower() in ['q', 'exit']:
            print("Exiting...")
            break

        answer = ai_assistant.ask_question(question, user_id=user_id)
        print(f"Answer: {answer}")
        memories = ai_assistant.get_memories(user_id=user_id)
        print("Memories:")
        for memory in memories:
            print(f"- {memory}")
        print("-----")

if __name__ == "__main__":
    main()