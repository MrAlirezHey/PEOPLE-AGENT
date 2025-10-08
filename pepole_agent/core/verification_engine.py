import requests
import base64

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
                repos_info[repo_name] = readme_content
            else:
                print(f"README.md not found for {repo_name}, skipping.")
        
        return repos_info

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


for repo, readme in repos_info.items():
    print(f"Repository: {repo}\nREADME:\n{readme[:1000]}...\n") 
