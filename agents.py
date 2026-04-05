from crewai import Agent

llm = "groq/llama-3.1-8b-instant"


# 🔥 1. EXPLORER
repo_explorer = Agent(
    role="Repository Explorer",
    goal="Understand repository structure",
    backstory="""
    You are a senior engineer who scans repositories quickly
    to understand their structure and architecture.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# 🔥 2. ANALYZER
system_analyzer = Agent(
    role="Senior Code Analyst",
    goal="Deeply understand how the system works by reading code like a real developer",
    backstory="""
    You are a senior software engineer who specializes in understanding unfamiliar codebases.

    You DO NOT summarize blindly.

    You follow this strict thinking process:

    1. Identify entry point (main/app/server)
    2. Trace execution flow step-by-step
    3. Follow function calls across files
    4. Understand how data moves through the system
    5. Identify external integrations (APIs, DB, services)
    6. Build a mental model of the system

    You think in terms of:
    - "What happens first?"
    - "What calls what?"
    - "Where does data come from and go?"

    You NEVER:
    - guess from file names
    - assume features
    - hallucinate

    You ONLY explain what can be reasoned from actual code.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# 🔥 3. WRITER
content_writer = Agent(
    role="Technical Writer",
    goal="Write professional README files",
    backstory="""
    You are a developer who writes clear, concise, and realistic documentation.
    You avoid buzzwords and explain systems in a practical way.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)


# 🔥 4. FORMATTER
formatter = Agent(
    role="Markdown Formatter",
    goal="Format markdown cleanly",
    backstory="""
    You specialize in formatting content into clean,
    readable, and well-structured markdown files.
    """,
    verbose=True,
    llm=llm,
    allow_delegation=False
)