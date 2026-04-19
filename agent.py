import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from search import gather_research
from report import generate_report

load_dotenv()


def save_report(topic, report_text):
    """Save the report as a markdown file."""
    os.makedirs("outputs", exist_ok=True)
    filename = topic.lower().replace(" ", "_")[:40]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filepath = f"outputs/{filename}_{timestamp}.md"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Market Research Report: {topic}\n")
        f.write(f"*Generated on {datetime.now().strftime('%B %d, %Y')}*\n\n")
        f.write(report_text)

    return filepath


def run_agent(topic):
    print(f"\n Starting research agent for: '{topic}'")
    print("=" * 50)

    print("\n Phase 1: Gathering web research...")
    research_data = gather_research(topic)
    print(f" Collected data from {len(research_data)} sources")

    print("\n Phase 2: Generating report with Gemini...")
    report = generate_report(topic, research_data)

    print("\n Phase 3: Saving report...")
    filepath = save_report(topic, report)
    print(f" Report saved to: {filepath}")

    print("\n" + "=" * 50)
    print(report)
    return filepath


if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter a business name or topic to research: ")

    run_agent(topic)
