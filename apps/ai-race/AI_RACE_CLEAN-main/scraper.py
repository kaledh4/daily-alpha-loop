import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import datetime
import os
import ssl

# 1. Configuration: Mapping Domains to arXiv Search Queries
# cat: category (e.g., quant-ph = Quantum Physics, cond-mat = Condensed Matter)
DOMAINS = {
    "Advanced Manufacturing": "cat:cs.RO OR cat:cs.SY",  # Robotics & Systems Control
    "Biotechnology": "cat:q-bio.BM OR cat:q-bio.GN",    # Biomolecules & Genomics
    "Critical Materials": "all:\"rare earth\" OR all:\"critical materials\"",
    "Nuclear Energy": "cat:nucl-ex OR cat:nucl-th",      # Nuclear Experiment/Theory
    "Quantum Info Science": "cat:quant-ph",
    "Semiconductors": "cat:cond-mat.mes-hall OR cat:cs.ET" # Mesoscale Physics/Emerging Tech
}

OUTPUT_FILE = "mission_data.json"

def fetch_arxiv_data(query, max_results=10):
    base_url = "http://export.arxiv.org/api/query?"
    # Sort by submitted date descending to get latest breakthroughs
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    url = base_url + urllib.parse.urlencode(params)
    
    try:
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(url, context=context)
        data = response.read().decode('utf-8')
        return ET.fromstring(data)
    except Exception as e:
        print(f"Error fetching {query}: {e}")
        return None

def generate_ai_briefing(domains_data):
    """Generate AI strategic briefing using OpenRouter API"""
    try:
        # Get API key from environment variable (only from GitHub Actions secrets)
        api_key = os.environ.get('OPENROUTER_KEY') or os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            print("Warning: OPENROUTER_API_KEY not set. AI briefing will be unavailable.")
            print("To enable AI analysis, set up your OpenRouter API key as described in the README.")
            return "*AI analysis temporarily unavailable. Research data is current.*"
        
        print(f"Using API key: {api_key[:10]}...")  # Log first 10 chars for debugging (without revealing the full key)
        
        # Prepare the data for AI analysis with the enhanced prompt
        system_prompt = """ROLE:
You are the Chief Strategy Officer for a high-stakes mission control center. Your goal is not to summarize news, but to synthesize raw data into actionable intelligence, predict downstream effects, and assign confidence levels to your assessments.

CORE DIRECTIVES:
1. NO FLUFF: Avoid phrases like "The article discusses..." or "It is important to note..." State facts and implications directly.
2. BLUF FORMAT: Every section must start with a Bottom Line Up Front—the single most critical insight delivered immediately.
3. ENTITY EXTRACTION: You must extract specific technical entities (e.g., "Nb3TeCl8", "Kleinkram", "Toric Codes") rather than generic terms (e.g., "new materials", "software tools").
4. CONFIDENCE SCORING: You must assign a confidence score (0-100%) to every prediction, based on the volume and recency of the data provided.
5. STOCK RECOMMENDATIONS: Identify 5 publicly traded companies most likely to benefit from these breakthroughs within 12 months.

TONE:
Authoritative, Clinical, Urgent. Use military/scientific brevity."""

        user_prompt = "<RAW_DATA>\n"
        
        for domain_name, domain_data in domains_data.items():
            user_prompt += f"## {domain_name}\n"
            user_prompt += f"Total Papers: {domain_data['total_volume']}\n\n"
            
            for i, paper in enumerate(domain_data['recent_papers'], 1):
                user_prompt += f"Paper #{i}:\n"
                user_prompt += f"  Title: {paper['title']}\n"
                user_prompt += f"  Date: {paper['date']}\n"
                user_prompt += f"  Summary: {paper['summary']}\n\n"
        
        user_prompt += "</RAW_DATA>\n\n"
        user_prompt += """<INSTRUCTIONS>
Perform the following reasoning steps silently before generating the final output:

STEP 1: NOISE FILTERING
- Discard any paper/article older than 18 months unless it is a foundational breakthrough.
- Group inputs by specific sub-domain (e.g., separate "Generative AI" from "Robotics" within the Tech category).

STEP 2: PATTERN RECOGNITION
- Identify 3 "Cross-Domain Signals" where two unrelated fields (e.g., Nuclear Physics and AI) share a common keyword or methodology.
- Extract the "Golden Entities"—the specific proper nouns (chemical formulas, project names, software versions) that drive these trends.

STEP 3: RED TEAMING (ADVERSARIAL REVIEW)
- Critique your own findings. If you identified a trend, ask: "Is this just hype? What is the failure mode?"
- Downgrade the confidence score if the data comes from a single source.

STEP 4: STOCK IDENTIFICATION
- Identify 5 publicly traded companies that are most positioned to benefit from these breakthroughs.
- For each company, explain why they're relevant and assign a confidence score (0-100%).

STEP 5: OUTPUT GENERATION
- Generate the final response using the simplified markdown structure below.
</INSTRUCTIONS>

<OUTPUT_FORMAT>

## 🔥 KEY TAKEAWAY
BLUF: [One-sentence summary of the most critical insight]

## 🏭 INDUSTRY BREAKDOWNS
### [Domain Name]
BLUF: [Key insight for this domain]
1. [Key entity 1]: [Brief description]
2. [Key entity 2]: [Brief description]
3. [Key entity 3]: [Brief description]

### [Next Domain]
...

## 🔗 CROSS-DOMAIN CONNECTIONS
1. [Connection 1]: [Brief explanation]
2. [Connection 2]: [Brief explanation]
3. [Connection 3]: [Brief explanation]

## 💡 KEY PREDICTIONS
- [Prediction 1] ([Confidence]% confidence)
- [Prediction 2] ([Confidence]% confidence)
- [Prediction 3] ([Confidence]% confidence)

## 📈 STOCK PICKS
1. [Company Name] ([Ticker]): [Why relevant] ([Confidence]% confidence)
2. [Company Name] ([Ticker]): [Why relevant] ([Confidence]% confidence)
3. [Company Name] ([Ticker]): [Why relevant] ([Confidence]% confidence)
4. [Company Name] ([Ticker]): [Why relevant] ([Confidence]% confidence)
5. [Company Name] ([Ticker]): [Why relevant] ([Confidence]% confidence)

## 📊 SAUDI TASI OPPORTUNITIES
1. [Company Name] ([Ticker].SR): [Sector connection] - [Why relevant] ([Confidence]% confidence)
2. [Company Name] ([Ticker].SR): [Sector connection] - [Why relevant] ([Confidence]% confidence)
3. [Company Name] ([Ticker].SR): [Sector connection] - [Why relevant] ([Confidence]% confidence)
4. [Company Name] ([Ticker].SR): [Sector connection] - [Why relevant] ([Confidence]% confidence)
5. [Company Name] ([Ticker].SR): [Sector connection] - [Why relevant] ([Confidence]% confidence)

## ⚠️ RISKS & LIMITATIONS
- [Risk 1]: [Brief explanation]
- [Risk 2]: [Brief explanation]

## 🏷️ TRENDING KEYWORDS
[Keyword 1], [Keyword 2], [Keyword 3], [Keyword 4], [Keyword 5], [Keyword 6], [Keyword 7], [Keyword 8], [Keyword 9], [Keyword 10]

<<<ARABIC_TRANSLATION>>>
[CRITICAL: You MUST provide a COMPLETE Arabic translation of ALL sections above. Do NOT skip or summarize.
REQUIRED sections in Arabic (same length as English):
1. 🔥 KEY TAKEAWAY
2. 🏭 INDUSTRY BREAKDOWNS (ALL domains)
3. 🔗 CROSS-DOMAIN CONNECTIONS
4. 💡 KEY PREDICTIONS
5. 📈 STOCK PICKS - ALL 5 companies with tickers like (NVDA)
6. 📊 SAUDI TASI OPPORTUNITIES - ALL 5 companies with tickers like (1211.SR)
7. ⚠️ RISKS & LIMITATIONS
8. 🏷️ TRENDING KEYWORDS
Keep ALL company tickers in English format. Arabic translation should be EQUAL in length to English version.]
</OUTPUT_FORMAT>"""
        
        # Make API request to OpenRouter
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://kaledh4.github.io/AI_RACE_CLEAN/",  # Optional, for OpenRouter analytics
            "X-Title": "Genesis Mission Control"  # Optional, for OpenRouter analytics
        }
        
        # Use the correct model name for Grok - INCREASED max_tokens for full bilingual output
        data = {
            "model": "x-ai/grok-4.1-fast:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        print("Sending request to OpenRouter API...")
        
        # Convert to JSON and make request
        import urllib.request
        import json as json_lib
        
        req = urllib.request.Request(url, 
                                   data=json_lib.dumps(data).encode('utf-8'), 
                                   headers=headers)
        
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(req, context=context)
        result = json_lib.loads(response.read().decode('utf-8'))
        
        print("Received response from OpenRouter API")
        
        # Extract the AI response
        if 'choices' in result and len(result['choices']) > 0:
            ai_briefing = result['choices'][0]['message']['content']
            print("AI briefing generated successfully")
            return ai_briefing
        else:
            print(f"Unexpected API response format: {result}")
            return "*AI analysis temporarily unavailable. Research data is current.*"
        
    except Exception as e:
        print(f"Error generating AI briefing: {e}")
        import traceback
        traceback.print_exc()
        return "*AI analysis temporarily unavailable. Research data is current.*"

def main():
    dashboard_data = {
        "generated_at": datetime.datetime.now().isoformat(),
        "domains": {}
    }

    print("--- Starting Genesis Data Extraction ---")

    for domain_name, query in DOMAINS.items():
        print(f"Processing: {domain_name}...")
        root = fetch_arxiv_data(query)
        
        if root:
            # Extract Total Results (Volume of new research)
            # arXiv API provides 'opensearch:totalResults'
            total_results_elem = root.find("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
            total_results = int(total_results_elem.text) if total_results_elem is not None else 0
            
            entries = []
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                summary_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
                published_elem = entry.find("{http://www.w3.org/2005/Atom}published")
                link_elem = entry.find("{http://www.w3.org/2005/Atom}id")
                
                title = title_elem.text.strip().replace('\n', ' ') if title_elem is not None else "Unknown Title"
                summary = summary_elem.text.strip().replace('\n', ' ') if summary_elem is not None else "No summary available"
                published = published_elem.text[:10] if published_elem is not None else "Unknown Date"
                link = link_elem.text if link_elem is not None else "#"
                
                entries.append({
                    "title": title,
                    "summary": summary[:200] + "...", # Truncate summary for mobile
                    "date": published,
                    "link": link
                })

            dashboard_data["domains"][domain_name] = {
                "total_volume": total_results, # Proxy for "Advancement"
                "recent_papers": entries
            }

    # Generate AI strategic briefing
    print("Generating AI strategic briefing...")
    ai_briefing = generate_ai_briefing(dashboard_data["domains"])
    dashboard_data["ai_briefing"] = ai_briefing

    # Save to JSON for the frontend to consume
    with open(OUTPUT_FILE, "w") as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"Success. Data saved to {OUTPUT_FILE}")
    print(f"AI Briefing Status: {'Generated successfully' if not ai_briefing.startswith('*AI analysis') else 'Using fallback message'}")

if __name__ == "__main__":
    main()
