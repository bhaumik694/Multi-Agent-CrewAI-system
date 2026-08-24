from crewai import Task

from agents import (
    repo_explorer,
    backend_analyzer,
    frontend_analyzer,
    system_analyzer,
    content_writer,
    formatter
)


# ============================================================
# 1. REPOSITORY EXPLORER
# ============================================================

explore_task = Task(
    description="""
    Analyze ONLY the repository structure.

    Repository structure:
    {structure}

    Identify:

    - Major directories
    - Backend/frontend separation
    - Application entry points
    - Configuration files
    - Database-related files
    - API/controller files
    - Service/business logic
    - Models/entities
    - Tests
    - Important source files

    Do NOT analyze implementation details.

    Do NOT use or rely on an existing README.

    Do NOT invent functionality.

    Produce a concise structural map that can be used by
    the backend and frontend analysts.
    """,

    expected_output="""
    A structured repository map containing:

    1. Repository type
    2. Major directories
    3. Backend structure
    4. Frontend structure
    5. Entry points
    6. Important files
    7. Configuration/database/test files
    """,

    agent=repo_explorer
)


# ============================================================
# 2. BACKEND ANALYSIS
# ============================================================

backend_task = Task(
    description="""
    Analyze the backend implementation using the repository
    structure and source files.

    Repository structure:
    {structure}

    Repository source files:
    {repo_data}

    Analyze ONLY backend-relevant code.

    Determine:

    1. Backend framework and language
    2. Application entry point
    3. Controllers/routes
    4. Services
    5. Business logic
    6. Models/entities
    7. Repositories/data access
    8. Database
    9. External integrations
    10. Authentication/authorization if implemented
    11. Request → processing → response flow

    Follow actual imports, classes, methods, and calls.

    Do NOT infer behavior from filenames alone.

    Do NOT use an existing README as evidence.

    If something cannot be established from the provided
    source files, explicitly say:

    "Not enough evidence in provided code."
    """,

    expected_output="""
    Detailed evidence-based backend analysis covering:

    - Backend stack
    - Entry point
    - API layer
    - Service layer
    - Data layer
    - Database
    - External integrations
    - Backend execution flow
    - Important backend files
    """,

    agent=backend_analyzer,

    # Explorer output becomes available here
    context=[explore_task]
)


# ============================================================
# 3. FRONTEND ANALYSIS
# ============================================================

frontend_task = Task(
    description="""
    Analyze the frontend implementation using the repository
    structure and source files.

    Repository structure:
    {structure}

    Repository source files:
    {repo_data}

    Analyze ONLY frontend-relevant code.

    Determine:

    1. Frontend framework
    2. Application entry point
    3. Components/pages
    4. State management
    5. API calls
    6. User interaction flow
    7. Important UI functionality
    8. Frontend → backend communication

    Only report functionality supported by the source code.

    Do NOT use an existing README as evidence.

    Never invent components, routes, or functionality.

    If something cannot be established:

    "Not enough evidence in provided code."
    """,

    expected_output="""
    Detailed evidence-based frontend analysis covering:

    - Frontend stack
    - Entry point
    - Components/pages
    - State management
    - API communication
    - User flow
    - Frontend/backend interaction
    """,

    agent=frontend_analyzer,

    # Explorer output becomes available here
    context=[explore_task]
)


# ============================================================
# 4. SYSTEM ARCHITECT / SYNTHESIS
# ============================================================

analyze_task = Task(
    description="""
    Build the final technical understanding of the repository.

    Repository structure:
    {structure}

    Repository source files:
    {repo_data}

    Use the outputs of the repository explorer,
    backend analyst, and frontend analyst as evidence.

    Synthesize them into one accurate system model.

    Produce:

    1. PROJECT PURPOSE
    2. ARCHITECTURE
    3. MAJOR COMPONENTS
    4. CORE FILES
    5. TECH STACK
    6. IMPLEMENTED FEATURES
    7. END-TO-END WORKFLOW
    8. DATA FLOW
    9. DATABASE
    10. EXTERNAL INTEGRATIONS
    11. FRONTEND ↔ BACKEND INTERACTION

    IMPORTANT:

    - Resolve conflicts using the actual source code.
    - Do not blindly trust previous agent claims.
    - Do not use an existing README as evidence.
    - Do not invent functionality.
    - Do not assume features exist.

    If something cannot be established:

    "Not enough evidence in the repository."
    """,

    expected_output="""
    A complete evidence-based technical architecture
    and workflow description of the repository.
    """,

    agent=system_analyzer,

    context=[
        explore_task,
        backend_task,
        frontend_task
    ]
)


# ============================================================
# 5. README WRITER
# ============================================================

write_task = Task(
    description="""
    Write a professional README based ONLY on the verified
    system analysis.

    Use the system architecture analysis produced by the
    previous task.

    The README should include, when supported:

    - Overview
    - Features
    - Architecture
    - Tech Stack
    - Installation
    - Configuration
    - Usage
    - Project Structure

    Rules:

    - Never invent commands.
    - Never invent environment variables.
    - Never invent dependencies.
    - Never invent features.
    - Never invent API endpoints.
    - Never copy an existing README.
    - Do not claim a license unless the repository provides
      evidence for one.

    If information is unavailable, write:

    "Not specified in the repository."

    Keep the writing professional, concise, and developer-focused.
    """,

    expected_output="""
    Complete README content containing only verified
    repository information.
    """,

    agent=content_writer,

    context=[analyze_task]
)


# ============================================================
# 6. MARKDOWN FORMATTER
# ============================================================

format_task = Task(
    description="""
    Format the README draft into clean Markdown.

    Preserve the factual meaning of the writer's content.

    Requirements:

    - Clean headings
    - Consistent spacing
    - Appropriate bullet lists
    - Code blocks for commands/configuration
    - Remove repetition
    - Keep technical terminology unchanged
    - Do NOT add new information

    Preferred sections when applicable:

    # Project Title

    ## Overview

    ## Features

    ## Architecture

    ## Tech Stack

    ## Installation

    ## Configuration

    ## Usage

    ## Project Structure

    Only include sections supported by the source material.

    Do NOT invent:

    - License
    - Contributors
    - Installation commands
    - Environment variables
    - Features
    - API endpoints

    Return ONLY the final README Markdown.
    """,

    expected_output="""
    Final clean README Markdown.
    """,

    agent=formatter,

    context=[write_task]
)