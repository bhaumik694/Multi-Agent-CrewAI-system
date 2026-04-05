from crewai import Task
from agents import (
    repo_explorer,
    system_analyzer,
    content_writer,
    formatter
)


# 🔥 1. EXPLORE — STRUCTURE ONLY
explore_task = Task(
    description="""
    You are analyzing ONLY the repository structure.

    Repository structure:
    {structure}

    DO NOT read file content.

    Your job:
    - Identify major folders (backend, frontend, src, etc.)
    - Identify architecture pattern (API, fullstack, ML, script)
    - Identify possible entry points (main.py, app.py, index.js, server.js)

    OUTPUT:
    - High-level structure summary
    - Possible entry points
    """,
    expected_output="Clear structural understanding of the repository.",
    agent=repo_explorer
)


# 🔥 2. ANALYZE — DOES EVERYTHING (select + read + verify + analyze)
analyze_task = Task(
    description="""
    You are analyzing a real codebase.

    Repository structure:
    {structure}

    Repository files (path → code):
    {repo_data}

    FOLLOW THIS EXACT PROCESS:

    STEP 1: Identify ENTRY POINT
    - Find where execution starts (main.py, app.py, server.js, etc.)
    - If multiple, pick the primary one

    STEP 2: TRACE EXECUTION FLOW
    - What runs first?
    - What functions are called?
    - What modules are imported?

    STEP 3: FOLLOW DATA FLOW
    - What is the input?
    - How is it processed?
    - What is the output?

    STEP 4: IDENTIFY SYSTEM COMPONENTS
    - APIs (FastAPI/Flask routes)
    - Database usage
    - External services (Twilio, Supabase, etc.)
    - Models (if ML)

    STEP 5: BUILD SYSTEM UNDERSTANDING

    OUTPUT:

    1. PROJECT PURPOSE (based on actual behavior)
    2. CORE FILES AND WHAT THEY DO
    3. TECH STACK (ONLY from imports)
    4. FEATURES (ONLY implemented)
    5. COMPLETE WORKFLOW (step-by-step)
    6. REAL-WORLD USE CASE

    STRICT RULES:
    - Every statement must come from code
    - If something is unclear → say "Not enough evidence in code"
    - DO NOT guess
    - DO NOT assume
    """,
    expected_output="Deep, code-driven understanding of the system.",
    agent=system_analyzer
)

# 🔥 3. WRITE — README GENERATION
write_task = Task(
    description="""
    Using the analysis above,

    Generate a professional README.

    INCLUDE:

    - Overview → what system DOES
    - Features → only real ones
    - Tech Stack → only confirmed
    - Installation → or "Not specified"
    - Usage → actual execution flow
    - Project Structure → key files explained

    STYLE:
    - Developer tone
    - Clear and direct
    - No buzzwords

    RULES:
    - No hallucination
    - No assumptions
    - If missing → "Not specified"
    """,
    expected_output="High-quality README content.",
    agent=content_writer
)


# 🔥 4. FORMAT — FINAL OUTPUT
format_task = Task(
    description="""
    Format into:

    # 🚀 Project Title

    ## 📌 Overview
    ## ✨ Features
    ## 🛠 Tech Stack
    ## ⚙️ Installation
    ## ▶️ Usage
    ## 📂 Project Structure
    ## 🤝 Contributing
    ## 📜 License

    RULES:
    - Clean markdown
    - Proper spacing
    - Bullet points
    - No repetition
    """,
    expected_output="Final clean README.md file.",
    agent=formatter
)