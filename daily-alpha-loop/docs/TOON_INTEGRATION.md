# TOON Integration in Daily Alpha Loop

## Overview
This project uses **TOON (Token-Oriented Object Notation)** for AI communication. TOON is a token-optimized data serialization format designed to reduce LLM token usage by ~40% compared to standard JSON.

## How It Works
1. **Prompting:** We instruct the AI to return data in TOON format instead of JSON.
2. **Parsing:** A native Python parser (`parse_toon` in `unified_fetcher_v3.py`) converts the TOON text back into standard Python dictionaries.
3. **Storage:** The data is saved as standard JSON for the frontend to consume.

## TOON Syntax Used
We utilize two main TOON features for maximum efficiency:

### 1. Tabular Arrays
For lists of objects, we use a CSV-like syntax with a schema definition:
```toon
breakthroughs[4]{title,why_it_matters}:
  "Title 1","Why it matters 1"
  "Title 2","Why it matters 2"
```
This avoids repeating keys like `{"title": "...", "why_it_matters": "..."}` for every item.

### 2. Simple Arrays
For lists of values:
```toon
drivers[5]: driver1, driver2, driver3, driver4, driver5
```

## Benefits
*   **Cost Savings:** ~40% reduction in output tokens.
*   **Higher Density:** Allows us to request "8-minute briefs" (double the content) within the same context window.
*   **Speed:** Faster generation due to fewer tokens.

## GitHub Pages Compatibility
This integration is **fully compatible** with GitHub Pages. The TOON processing happens entirely in the backend (GitHub Actions). The frontend continues to receive standard JSON files (`latest.json`), so no frontend changes are required.
