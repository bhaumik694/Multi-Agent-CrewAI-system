

from crewai import Crew
from tasks import analyze_task, write_task, format_task,explore_task
from agents import repo_explorer,content_writer, formatter,system_analyzer
from github_utils import extract_repo_info
import sys

# 👉 Allow both CLI input and manual input
if len(sys.argv) > 1:
    repo_url = sys.argv[1]
else:
    repo_url = input("Enter GitHub repo URL: ")

print("\n🔍 Fetching repository data...")
repo_data = extract_repo_info(repo_url)

# 👉 Debug print (VERY useful)
print("\n📦 Extracted Repo Data:")
print(repo_data)

# 👉 Create crew
crew = Crew(
    agents=[repo_explorer,content_writer, formatter,system_analyzer],
    tasks=[explore_task,analyze_task, write_task, format_task],
    verbose=True
)

print("\n🚀 Starting Crew Execution...\n")

# 👉 Run crew
result = crew.kickoff(inputs={
    "repo_data": repo_data["files"],
    "structure": repo_data["structure"]
})

# 👉 Save output
with open("README_generated.md", "w", encoding="utf-8") as f:
    f.write(str(result))   # ensure string

print("\n✅ README generated successfully!")
print("📄 Saved as README_generated.md")