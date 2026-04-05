import requests

# 🚫 folders to ignore
IGNORE_FOLDERS = [
    "catboost_info",
    "notebook",
    "__pycache__",
    ".git",
    "node_modules",
    "dist",
    "build"
]

# 🎯 allowed extensions (broad but controlled)
ALLOWED_EXTENSIONS = [
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".json", ".md", ".yaml", ".yml"
]


# -----------------------------
# 📂 Get all files recursively
# -----------------------------
def get_all_files(owner, repo, path=""):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch: {url}")
        return []

    data = response.json()

    if not isinstance(data, list):
        return []

    all_files = []

    for item in data:
        if item["type"] == "file":
            all_files.append(item)

        elif item["type"] == "dir":
            if any(folder in item["path"] for folder in IGNORE_FOLDERS):
                continue

            all_files.extend(get_all_files(owner, repo, item["path"]))

    return all_files


# -----------------------------
# 🌳 Build tree
# -----------------------------
def build_tree(file_paths):
    tree = {}

    for path in file_paths:
        parts = path.split("/")
        current = tree

        for part in parts:
            current = current.setdefault(part, {})

    return tree


def tree_to_string(tree, indent=0):
    result = ""
    for key, value in tree.items():
        result += "  " * indent + f"- {key}\n"
        result += tree_to_string(value, indent + 1)
    return result


# -----------------------------
# 🚀 Main extraction
# -----------------------------
def extract_repo_info(repo_url):
    parts = repo_url.replace("https://github.com/", "").split("/")
    owner, repo = parts[0], parts[1]

    print("\n🔍 Fetching repository files...")
    files = get_all_files(owner, repo)
    print(f"📂 Total files found: {len(files)}")

    file_data = {}

    # 🔥 STEP 1: README first (high value)
    for file in files:
        if "readme" in file["path"].lower():
            try:
                content = requests.get(file["download_url"]).text
                file_data[file["path"]] = content[:1500]  # 🔥 reduced
            except:
                pass

    # 🔥 STEP 2: prioritize entry/core files
    priority_keywords = [
        "main", "app", "server", "index",
        "api", "route", "controller",
        "service", "model"
    ]

    for file in files:
        path = file["path"].lower()

        if not any(path.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            continue

        if file["path"] in file_data:
            continue

        if not any(keyword in path for keyword in priority_keywords):
            continue

        try:
            content = requests.get(file["download_url"]).text
            file_data[file["path"]] = content[:1200]  # 🔥 tighter
        except:
            pass

        if len(file_data) >= 8:  # 🔥 HARD LIMIT
            break

    # 🔥 STEP 3: fallback if too few files
    if len(file_data) < 4:
        print("⚠️ Using fallback sampling...")

        for file in files:
            path = file["path"].lower()

            if not any(path.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                continue

            if file["path"] in file_data:
                continue

            try:
                content = requests.get(file["download_url"]).text
                file_data[file["path"]] = content[:800]
            except:
                pass

            if len(file_data) >= 6:
                break

    print(f"📦 Files selected for LLM: {len(file_data)}")

    # 🔥 structure from ALL files (important)
    all_paths = [file["path"] for file in files]
    tree = build_tree(all_paths)
    structure = tree_to_string(tree)

    return {
        "repo_name": repo,
        "structure": structure,
        "files": file_data
    }