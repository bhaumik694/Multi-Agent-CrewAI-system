import sys
from pathlib import Path

from crewai import Crew

from tasks import (
    explore_task,
    backend_task,
    frontend_task,
    analyze_task,
    write_task,
    format_task,
)

from agents import (
    repo_explorer,
    backend_analyzer,
    frontend_analyzer,
    system_analyzer,
    content_writer,
    formatter,
)

from github_utils import extract_repo_info


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_FILE = "README_generated.md"


# ============================================================
# GET REPOSITORY URL
# ============================================================

def get_repo_url():

    if len(sys.argv) > 1:
        return sys.argv[1].strip()

    return input(
        "Enter GitHub repo URL: "
    ).strip()


# ============================================================
# DISPLAY REPOSITORY INFORMATION
# ============================================================

def print_repo_summary(repo_data):

    print("\n" + "=" * 60)
    print("📊 REPOSITORY SUMMARY")
    print("=" * 60)

    print(
        f"Repository        : "
        f"{repo_data['repo_name']}"
    )

    print(
        f"Files sent to LLM : "
        f"{len(repo_data['files'])}"
    )

    print(
        f"Structure size     : "
        f"{len(repo_data['structure'])} characters"
    )

    print("\n📁 Files being analyzed:")

    for path in repo_data["files"]:
        print(f"   • {path}")

    print("=" * 60)


# ============================================================
# CREATE CREW
# ============================================================

def create_crew():

    return Crew(
        agents=[
            repo_explorer,
            backend_analyzer,
            frontend_analyzer,
            system_analyzer,
            content_writer,
            formatter,
        ],

        tasks=[
            explore_task,
            backend_task,
            frontend_task,
            analyze_task,
            write_task,
            format_task,
        ],

        verbose=True,
    )


# ============================================================
# SAVE FINAL README
# ============================================================

def save_readme(result):

    # CrewAI's final output is normally the output
    # of the final task.
    final_output = getattr(
        result,
        "raw",
        None
    )

    if not final_output:

        final_output = str(result)

    final_output = final_output.strip()

    if not final_output:

        raise ValueError(
            "CrewAI returned an empty README."
        )

    output_path = Path(
        OUTPUT_FILE
    )

    output_path.write_text(
        final_output,
        encoding="utf-8"
    )

    return output_path


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("🤖 MULTI-AGENT README GENERATOR")
    print("=" * 60)

    # --------------------------------------------------------
    # Get repository
    # --------------------------------------------------------

    repo_url = get_repo_url()

    if not repo_url:

        print(
            "\n❌ No repository URL provided."
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Extract repository
    # --------------------------------------------------------

    print(
        "\n🔍 Fetching repository data..."
    )

    try:

        repo_data = extract_repo_info(
            repo_url
        )

    except Exception as e:

        print(
            "\n❌ Failed to extract repository:"
        )

        print(e)

        sys.exit(1)

    if not repo_data["files"]:

        print(
            "\n❌ No usable source files were found."
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_repo_summary(
        repo_data
    )

    # --------------------------------------------------------
    # Create Crew
    # --------------------------------------------------------

    print(
        "\n🧠 Building multi-agent pipeline..."
    )

    crew = create_crew()

    # --------------------------------------------------------
    # Start execution
    # --------------------------------------------------------

    print(
        "\n🚀 Starting Multi-Agent "
        "Repository Analysis...\n"
    )

    try:

        result = crew.kickoff(
            inputs={
                "repo_data": repo_data["files"],
                "structure": repo_data["structure"],
            }
        )

    except Exception as e:

        print(
            "\n❌ Crew execution failed."
        )

        print(
            "\nError:"
        )

        print(e)

        print(
            "\n💡 The GitHub extraction worked correctly."
        )

        print(
            "The failure happened during the "
            "CrewAI pipeline."
        )

        sys.exit(1)

    # --------------------------------------------------------
    # Save README
    # --------------------------------------------------------

    try:

        output_path = save_readme(
            result
        )

    except Exception as e:

        print(
            "\n❌ Failed to save README:"
        )

        print(e)

        sys.exit(1)

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("✅ README GENERATED SUCCESSFULLY")
    print("=" * 60)

    print(
        f"📄 Output: {output_path.resolve()}"
    )

    print(
        "\n🎉 Multi-agent analysis completed."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()