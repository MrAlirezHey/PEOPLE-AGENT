# PEOPLE-AGENT
# **PetaProc People Agent**

Welcome to the **PetaProc People Agent** project! This powerful multi-agent system is designed to validate user claims, profile creation, and professional matching. It leverages artificial intelligence to gather, verify, and evaluate user data, ensuring accurate and up-to-date profiles. Additionally, it connects users with others who share similar skills and expertise.

---

## **Table of Contents**

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [License](#license)

---

## **Overview**

**PetaProc People Agent** is an intelligent agent designed to help users create, validate, and improve their professional profiles. The system is built to:

- Ask users insightful questions to verify their claims about their professional experience.
- Evaluate user responses and assign a credibility score.
- Keep track of previous data and continuously update user profiles.
- Connect users with others in similar fields based on their skills and experience.

The project uses cutting-edge technology such as **LangGraph**, **LangChain**, and **OpenAI GPT-4** to perform these tasks efficiently and effectively.

---

## **Features**

- **Profile Validation**: The agent asks targeted questions to verify the claims made by the user about their professional background.
- **Score Generation**: Based on the responses, the agent evaluates the credibility of claims and assigns a score to the user’s profile.
- **Persistent Memory**: The system remembers user data over time and can update it as new information is gathered.
- **Profile Matching**: In Explore Mode, users can be connected to others with similar professional backgrounds and interests.

---

## **Tech Stack**

- **Python 3.x**
- **LangGraph** (for multi-agent logic)
- **LangChain** (for handling interactions with LLMs)
- **OpenAI GPT-4** (for advanced language model tasks)
- **Streamlit** (for the web-based user interface)
- **Qdrant** (for vector-based search)
- **Supabase** (for data storage)
- **Tavily API** (for web search functionalities)

---

## **Setup Instructions**

### 1. Clone the repository:

```bash
git clone https://github.com/yourusername/petaproc-people-agent.git
cd petaproc-people-agent
```
## 2. Install dependencies:

Make sure you have Python 3.x installed. Then, install the required Python packages:
```bash
pip install -r requirements.txt
```
## 3. Environment Configuration:

Create a .env file in the root of your project and add the following environment variables:
```bash
GAP_GAP_API_KEY=your_api_key_here
DATABASE_URL2=your_database_connection_string
TAVILY_API_KEY=your_tavily_api_key
```
Usage

To run the project, simply execute the following command:
```bash
streamlit run app.py
```
This will start the Streamlit app, which provides a web-based interface for interacting with the PetaProc People Agent.
How It Works
Agent Process

## Initial Interaction:

The agent first asks the user a series of targeted questions to gather information about their skills and experiences. This could include topics like their background in software development, problem-solving abilities, and professional challenges.

## Claim Validation:

Based on the user’s answers, the agent verifies the claims made by comparing them against public professional profiles (e.g., GitHub, LinkedIn) using web search tools.

## Score Assignment:

The agent evaluates the user’s credibility and assigns a score (0-1) based on the accuracy of their claims.

## Profile Memory:

The system remembers previous data provided by the user and continues to update the profile as new interactions occur, ensuring a continuously evolving, accurate profile.

Explore Mode:

In Explore Mode, users can be connected with other users in similar fields based on their profiles. This mode uses Qdrant and OpenAI embeddings to perform advanced vector searches for professional profile matching.

License

This project is licensed under the MIT License - see the LICENSE
 file for details.

Example:

Here’s an example flow in PetaProc People Agent:

User: "I have 5 years of experience with Python."

Agent: "Great! Can you tell me about a challenging project you worked on that involved Python? How did you tackle performance issues?"

User: "I worked on optimizing a Python web scraper that involved processing large amounts of data. I used async/await for concurrency."

Agent: "That sounds interesting! I’ll validate this claim by checking your GitHub profile for relevant projects."

Agent: The agent fetches data from GitHub, LinkedIn, and previous messages to validate the claim and assign a score.

## Contributing

We welcome contributions! Feel free to fork the repository, create a branch, and submit a pull request. If you find any issues or have suggestions, open an issue in the repository.

## Acknowledgments

OpenAI: For providing GPT-4 and other LLM capabilities.

LangChain & LangGraph: For the agent framework and language model handling.

Streamlit: For the UI framework.

Tavily: For the web search API.
