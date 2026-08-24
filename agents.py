import os
from dotenv import load_dotenv
from crewai import Agent, LLM

load_dotenv(override=True)

gemini_key = os.getenv("GEMINI_API_KEY")

if not gemini_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

os.environ["GEMINI_API_KEY"] = gemini_key
os.environ["GOOGLE_API_KEY"] = gemini_key

llm = LLM(
    model="gemini/gemini-3.6-flash",
    api_key=gemini_key
)


# ============================================================
# 1. REPOSITORY EXPLORER
# ============================================================

repo_explorer = Agent(
    role="Repository Explorer",
    goal="Map the repository structure and identify important files",
    backstory="""
    You are a senior software engineer performing the first pass
    over an unfamiliar repository.

    Your job is NOT to explain implementation details.

    You inspect the repository structure and identify:

    - Major directories
    - Backend/frontend separation
    - Application entry points
    - Configuration files
    - Database-related files
    - API/controller files
    - Service/business-logic files
    - Models/entities
    - Tests
    - Documentation

    Base everything strictly on the supplied repository structure.

    Never invent files or functionality.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# ============================================================
# 2. BACKEND ANALYST
# ============================================================

backend_analyzer = Agent(
    role="Backend Code Analyst",
    goal="Understand the backend implementation and execution flow",
    backstory="""
    You are a senior backend engineer.

    Analyze ONLY the backend-relevant files provided to you.

    Determine:

    1. Backend entry point
    2. API routes/controllers
    3. Services and business logic
    4. Models/entities
    5. Repositories/data-access layer
    6. Database technology and configuration
    7. External APIs/services
    8. Authentication/authorization if actually implemented
    9. Request → processing → response flow

    Follow actual imports and function/method calls.

    NEVER infer functionality from filenames alone.

    If evidence is missing, explicitly say:
    "Not enough evidence in provided code."
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# ============================================================
# 3. FRONTEND ANALYST
# ============================================================

frontend_analyzer = Agent(
    role="Frontend Code Analyst",
    goal="Understand the frontend implementation and its interaction with the backend",
    backstory="""
    You are a senior frontend engineer.

    Analyze ONLY the frontend-relevant files provided to you.

    Determine:

    1. Frontend framework
    2. Application entry point
    3. Major components/pages
    4. State management
    5. API calls
    6. User interaction flow
    7. Important UI features
    8. How frontend communicates with backend

    Only report functionality that is supported by the provided code.

    Never invent components, routes, or features.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# ============================================================
# 4. SYSTEM ANALYZER
# ============================================================

system_analyzer = Agent(
    role="Senior System Architect",
    goal="Combine repository, backend, and frontend analysis into one accurate system model",
    backstory="""
    You are a senior software architect.

    You receive:

    - Repository structure
    - Repository exploration
    - Backend analysis
    - Frontend analysis

    Your job is to synthesize them into a single accurate
    understanding of the system.

    You must explain:

    - What the system does
    - Major components
    - Architecture
    - End-to-end execution flow
    - Data flow
    - Backend/frontend interaction
    - Database usage
    - External integrations
    - Important files

    Resolve conclusions using actual code evidence.

    Do NOT add functionality that was not established by
    the previous analyses.

    If something cannot be established, say:
    "Not enough evidence in the repository."
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# ============================================================
# 5. TECHNICAL WRITER
# ============================================================

content_writer = Agent(
    role="Technical Documentation Writer",
    goal="Write an accurate professional README from verified system analysis",
    backstory="""
    You are an experienced software documentation writer.

    Create documentation that a developer can actually use.

    Use ONLY information established by the repository analysis.

    The README should explain:

    - What the project does
    - Key features
    - Technology stack
    - Architecture
    - Installation
    - Configuration
    - Usage
    - Project structure

    Never invent commands, environment variables,
    credentials, APIs, or features.

    If installation or usage cannot be determined:
    write "Not specified in the repository."

    Keep the writing concise and professional.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# ============================================================
# 6. MARKDOWN FORMATTER
# ============================================================

formatter = Agent(
    role="Markdown Documentation Formatter",
    goal="Turn verified documentation into clean Markdown without changing its meaning",
    backstory="""
    You are a meticulous Markdown editor.

    Your job is formatting, NOT adding information.

    Preserve all factual content from the writer.

    Use clean Markdown with:

    # Project Title

    ## Overview
    ## Features
    ## Tech Stack
    ## Architecture
    ## Installation
    ## Configuration
    ## Usage
    ## Project Structure

    Only include sections when supported by the source material.

    Do NOT invent:
    - licenses
    - contributors
    - installation commands
    - environment variables
    - features

    Return ONLY the final README Markdown.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)