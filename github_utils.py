import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)


# ============================================================
# CONFIG
# ============================================================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if GITHUB_TOKEN:
    GITHUB_HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


# Maximum number of files sent to the LLM
MAX_FILES = 12

# Maximum characters per file
MAX_CHARS_PER_FILE = 3000


# ============================================================
# FOLDERS TO IGNORE
# ============================================================

IGNORE_FOLDERS = {
    ".git",
    ".github",
    ".idea",
    ".vscode",

    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",

    "node_modules",
    "dist",
    "build",

    "target",
    "out",

    "venv",
    ".venv",
    "env",

    "coverage",
    ".coverage",

    "catboost_info",
    "notebook",
}


# ============================================================
# FILES TO IGNORE
# ============================================================

IGNORE_FILES = {
    # Existing/generated documentation
    "readme.md",
    "readme.txt",
    "readme.rst",
    "readme_generated.md",

    # Git
    ".gitignore",
    ".gitattributes",

    # Maven wrappers
    "mvnw",
    "mvnw.cmd",

    # Dependency lock files
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "uv.lock",

    # Misc
    ".dockerignore",
}


# ============================================================
# LOW-VALUE CONFIG FILES
# ============================================================

LOW_VALUE_FILES = {
    "eslint.config.js",
    "eslint.config.cjs",
    "eslint.config.ts",
    "postcss.config.js",
    "postcss.config.cjs",
    "tailwind.config.js",
    "tailwind.config.ts",
}


# ============================================================
# ALLOWED EXTENSIONS
# ============================================================

ALLOWED_EXTENSIONS = {
    # Python
    ".py",

    # JavaScript / TypeScript
    ".js",
    ".jsx",
    ".ts",
    ".tsx",

    # Java / JVM
    ".java",
    ".kt",
    ".scala",

    # C / C++
    ".c",
    ".cpp",
    ".h",
    ".hpp",

    # C#
    ".cs",

    # Go
    ".go",

    # Rust
    ".rs",

    # PHP / Ruby / Swift
    ".php",
    ".rb",
    ".swift",

    # Configuration / dependencies
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".properties",
}


# ============================================================
# REPOSITORY FILE DISCOVERY
# ============================================================

def get_all_files(owner, repo, path=""):
    """
    Recursively fetch all relevant repository files
    from GitHub's Contents API.
    """

    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/{path}"
    )

    try:
        response = requests.get(
            url,
            headers=GITHUB_HEADERS,
            timeout=15,
        )

    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

    if response.status_code != 200:
        print(f"❌ Failed to fetch: {url}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        return []

    data = response.json()

    if not isinstance(data, list):
        return []

    all_files = []

    for item in data:

        item_type = item.get("type")
        item_path = item.get("path", "")

        # ----------------------------------------------------
        # FILE
        # ----------------------------------------------------

        if item_type == "file":

            filename = item_path.split("/")[-1].lower()

            if filename in IGNORE_FILES:
                continue

            all_files.append(item)

        # ----------------------------------------------------
        # DIRECTORY
        # ----------------------------------------------------

        elif item_type == "dir":

            folder_name = item_path.split("/")[-1].lower()

            if folder_name in IGNORE_FOLDERS:
                continue

            all_files.extend(
                get_all_files(
                    owner,
                    repo,
                    item_path,
                )
            )

    return all_files


# ============================================================
# REPOSITORY TREE
# ============================================================

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

        result += (
            "  " * indent
            + f"- {key}\n"
        )

        result += tree_to_string(
            value,
            indent + 1,
        )

    return result


# ============================================================
# DOWNLOAD FILE
# ============================================================

def download_file(url):

    try:

        response = requests.get(
            url,
            headers=GITHUB_HEADERS,
            timeout=15,
        )

        if response.status_code == 200:
            return response.text

        print(
            f"⚠️ Failed to download file "
            f"({response.status_code}): {url}"
        )

    except requests.RequestException as e:

        print(
            f"⚠️ File download failed: {e}"
        )

    return None


# ============================================================
# FILE SCORING
# ============================================================

def score_file(file):

    path = file["path"].lower()
    name = path.split("/")[-1]
    extension = os.path.splitext(name)[1]

    score = 0

    # --------------------------------------------------------
    # README / GENERATED DOCS
    # --------------------------------------------------------

    if name in {
        "readme.md",
        "readme.txt",
        "readme.rst",
        "readme_generated.md",
    }:
        return -10000

    # --------------------------------------------------------
    # LOW-VALUE TOOLING
    # --------------------------------------------------------

    if name in LOW_VALUE_FILES:
        return 5

    # --------------------------------------------------------
    # DEPENDENCY / BUILD FILES
    # --------------------------------------------------------

    dependency_files = {
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "cargo.toml",
        "go.mod",
        "composer.json",
    }

    if name in dependency_files:
        score += 100

    # --------------------------------------------------------
    # ENTRY POINTS
    # --------------------------------------------------------

    entry_points = {
        # Python
        "main.py",
        "app.py",
        "server.py",
        "index.py",

        # JavaScript / TypeScript
        "index.js",
        "index.ts",
        "server.js",
        "server.ts",

        # Java
        "main.java",
        "application.java",

        # Go
        "main.go",

        # C#
        "program.cs",
    }

    if name in entry_points:
        score += 150

    # --------------------------------------------------------
    # CONFIGURATION
    # --------------------------------------------------------

    config_files = {
        "application.yml",
        "application.yaml",
        "application.properties",

        "config.py",
        "settings.py",

        "vite.config.js",
        "vite.config.ts",

        "next.config.js",
        "next.config.ts",

        "tsconfig.json",
    }

    if name in config_files:
        score += 60

    # --------------------------------------------------------
    # BACKEND ARCHITECTURE
    # --------------------------------------------------------

    backend_keywords = {
        "controller": 100,
        "router": 95,
        "route": 90,

        "service": 95,

        "repository": 90,
        "repo": 80,

        "entity": 85,
        "model": 80,

        "schema": 70,

        "middleware": 70,

        "database": 65,
        "db": 55,

        "auth": 65,
        "security": 65,
    }

    for keyword, points in backend_keywords.items():

        if keyword in name:
            score += points

    # --------------------------------------------------------
    # FRONTEND ARCHITECTURE
    # --------------------------------------------------------

    frontend_keywords = {
        "component": 90,
        "page": 85,
        "layout": 75,
        "hook": 75,
        "context": 70,
        "store": 70,
        "api": 75,
    }

    for keyword, points in frontend_keywords.items():

        if keyword in name:
            score += points

    # --------------------------------------------------------
    # TESTS
    # --------------------------------------------------------

    if (
        "test" in name
        or "/tests/" in path
        or "/test/" in path
        or "__tests__" in path
    ):
        score += 35

    # --------------------------------------------------------
    # SOURCE CODE BONUS
    # --------------------------------------------------------

    source_extensions = {
        ".py",
        ".java",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".cs",
        ".php",
        ".rb",
        ".swift",
    }

    if extension in source_extensions:
        score += 40

    # --------------------------------------------------------
    # IMPORTANT DIRECTORY BONUS
    # --------------------------------------------------------

    important_directories = {
        "/src/": 25,
        "/main/": 25,
        "/app/": 25,
        "/backend/": 25,
        "/frontend/": 25,
        "/server/": 25,
        "/api/": 25,

        "/components/": 20,
        "/services/": 20,
        "/controllers/": 20,
        "/models/": 20,
        "/repositories/": 20,
        "/entities/": 20,
    }

    for directory, points in important_directories.items():

        if directory in path:
            score += points

    return score


# ============================================================
# SELECT HIGH-VALUE FILES
# ============================================================

def select_files(files, max_files=MAX_FILES):

    candidates = []

    for file in files:

        path = file["path"].lower()
        name = path.split("/")[-1]

        # ----------------------------------------------------
        # NEVER SEND README TO THE MODEL
        # ----------------------------------------------------

        if name in IGNORE_FILES:
            continue

        # ----------------------------------------------------
        # SKIP UNSUPPORTED FILE TYPES
        # ----------------------------------------------------

        extension = os.path.splitext(path)[1]

        if extension not in ALLOWED_EXTENSIONS:
            continue

        score = score_file(file)

        candidates.append(
            (score, file)
        )

    # Highest score first
    candidates.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    selected = []
    selected_paths = set()

    for score, file in candidates:

        path = file["path"]

        if path in selected_paths:
            continue

        selected.append(file)
        selected_paths.add(path)

        if len(selected) >= max_files:
            break

    return selected


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_repo_info(repo_url):

    # --------------------------------------------------------
    # Parse GitHub URL
    # --------------------------------------------------------

    clean_url = (
        repo_url
        .replace(
            "https://github.com/",
            "",
        )
        .replace(
            "http://github.com/",
            "",
        )
        .strip("/")
    )

    parts = clean_url.split("/")

    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub repository URL."
        )

    owner = parts[0]
    repo = parts[1]

    # --------------------------------------------------------
    # Fetch repository
    # --------------------------------------------------------

    print(
        "\n🔍 Fetching repository files..."
    )

    if GITHUB_TOKEN:

        print(
            "🔐 Using authenticated GitHub API"
        )

    else:

        print(
            "⚠️ No GITHUB_TOKEN found"
        )

    files = get_all_files(
        owner,
        repo,
    )

    print(
        f"📂 Total files found: "
        f"{len(files)}"
    )

    # --------------------------------------------------------
    # Build repository tree
    # --------------------------------------------------------

    all_paths = [
        file["path"]
        for file in files
    ]

    tree = build_tree(
        all_paths
    )

    structure = tree_to_string(
        tree
    )

    # --------------------------------------------------------
    # Select files
    # --------------------------------------------------------

    selected_files = select_files(
        files,
        max_files=MAX_FILES,
    )

    print(
        "\n🎯 High-value files selected:"
    )

    for file in selected_files:

        score = score_file(file)

        print(
            f"   • {file['path']} "
            f"(score: {score})"
        )

    # --------------------------------------------------------
    # Download selected files
    # --------------------------------------------------------

    file_data = {}

    for file in selected_files:

        content = download_file(
            file["download_url"]
        )

        if not content:
            continue

        # Prevent giant files from consuming
        # the entire Gemini context.
        content = content[
            :MAX_CHARS_PER_FILE
        ]

        file_data[
            file["path"]
        ] = content

    print(
        f"\n📦 Files sent to LLM: "
        f"{len(file_data)}"
    )

    # --------------------------------------------------------
    # Return data
    # --------------------------------------------------------

    return {
        "repo_name": repo,
        "structure": structure,
        "files": file_data,
    }