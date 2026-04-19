from google import genai
import os
import json
import re


def generate_report(topic: str, research_data: list) -> dict:
    """Use Gemini to turn raw research into a structured report + chart data."""

    if not research_data:
        raise ValueError("No research data was collected. Cannot generate report.")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    context = ""
    for item in research_data:
        context += f"\n\n--- Source: {item['url']} ---\n"
        context += item["content"]

    prompt = f"""
You are a professional business research analyst.

Using the research data below, analyze: **{topic}**

Return ONLY a valid JSON object with exactly this structure. No markdown, no preamble, no explanation — just the raw JSON:

{{
    "report": {{
        
        "executive_summary": "3-4 sentence overview paragraph",
        "overview": "Company/topic overview paragraph covering what it is, what it does, founding, size",
        "overview_facts": {{
        "founded": "year or N/A",
        "headquarters": "city, country or N/A",
        "company_size": "e.g. 500-1000 employees or N/A",
        "industry": "industry name"
        }},
        "target_market": "paragraph about who they serve, demographics, pain points",
        "competitors": "paragraph about competitive landscape and main competitors",
        "trends": "paragraph about current market trends shaping this space",
        "business_model": "paragraph about how they make money and pricing",
        "swot": {{
        "strengths": ["strength 1", "strength 2", "strength 3"],
        "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
        "opportunities": ["opportunity 1", "opportunity 2", "opportunity 3"],
        "threats": ["threat 1", "threat 2", "threat 3"]
        
        }},
        
        "key_takeaways": ["takeaway 1", "takeaway 2", "takeaway 3", "takeaway 4"]
    }},
    
    "charts": {{
        "audience_segments": [
        {{"label": "Segment name", "value": 40}},
        {{"label": "Segment name", "value": 35}},
        {{"label": "Segment name", "value": 25}}
        ],
        
        "competitive_radar": {{
        "labels": ["Price Competitiveness", "Feature Depth", "Market Share", "Brand Strength", "Innovation"],
        "datasets": [
            {{
            "name": "{topic}",
            "values": [70, 85, 60, 75, 80]
            }},
            {{
            "name": "Top Competitor",
            "values": [65, 70, 80, 85, 65]
            }}
        ]
        }},
    "trend_lines": {{
        "labels": ["2021", "2022", "2023", "2024", "2025"],
        "datasets": [
            {{"name": "Trend 1 name", "values": [20, 35, 50, 70, 85]}},
            {{"name": "Trend 2 name", "values": [10, 20, 40, 55, 70]}},
            {{"name": "Trend 3 name", "values": [5, 15, 25, 40, 60]}}
        ]
        }},
        "revenue_breakdown": [
        {{"label": "Revenue stream 1", "value": 60}},
        {{"label": "Revenue stream 2", "value": 25}},
        {{"label": "Revenue stream 3", "value": 15}}
        ],
        "competitor_table": [
        {{
            "name": "Competitor name",
            "strength": "Key strength",
            "weakness": "Key weakness",
            "position": "Market leader / Challenger / Niche"
        }}
    ]
    }}
}}

Use real data from the research sources. For chart values, use your best estimates based on available data.
All values in audience_segments, revenue_breakdown must sum to 100.
Radar values must be between 0 and 100.

--- RESEARCH DATA ---
{context[:12000]}
"""

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)

    raw = response.text.strip()

    # Strip markdown code fences if Gemini wraps the JSON
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini returned invalid JSON: {e}\n\nRaw response: {raw[:500]}"
        )
