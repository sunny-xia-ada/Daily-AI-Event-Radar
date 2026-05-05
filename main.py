import argparse
import csv
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
from dotenv import load_dotenv

# Optional OpenAI integration for scoring
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class Event:
    def __init__(self, title, date, location, organizer, url, description, source):
        self.title = title
        self.date = date or "Unknown"
        self.location = location or "Unknown"
        self.organizer = organizer
        self.url = url
        self.description = description
        self.sources = [source]
        self.relevance_score = 0
        self.category = "Uncategorized"
        self.recommendation = "Low Priority"
        self.why_it_matters = ""
        self.source_confidence = "low"

    def normalize_string(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return " ".join(text.split())

    @property
    def normalized_title(self):
        return self.normalize_string(self.title)
    
    @property
    def normalized_date(self):
        return self.normalize_string(self.date)

    @property
    def normalized_location(self):
        return self.normalize_string(self.location)

    def merge_with(self, other):
        # Merge sources
        for s in other.sources:
            if s not in self.sources:
                self.sources.append(s)
        # Keep longest description
        if len(other.description or "") > len(self.description or ""):
            self.description = other.description
        # Better URL (e.g., not a search redirect)
        if other.url and ("google.com" not in other.url or not self.url):
            self.url = other.url
        # Better location
        if len(other.location or "") > len(self.location or ""):
            self.location = other.location

    def to_dict(self):
        return {
            "title": self.title,
            "date": self.date,
            "location": self.location,
            "organizer": self.organizer,
            "url": self.url,
            "description": self.description,
            "sources": self.sources,
            "relevance_score": self.relevance_score,
            "category": self.category,
            "recommendation": self.recommendation,
            "why_it_matters": self.why_it_matters,
            "source_confidence": self.source_confidence
        }


def score_events(events: List[Event]):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not HAS_OPENAI:
        logger.warning("OPENAI_API_KEY missing or openai not installed. Using fallback keyword scoring.")
        for e in events:
            score_event_fallback(e)
        return

    client = OpenAI(api_key=api_key)
    
    system_prompt = """
    You are an expert technical event curator in Seattle. Score the event relevance from 1 to 10.
    
    STRONGLY PREFER (Score 7-10):
    - AI agents, LLM apps, agentic workflows, open-source AI, AI engineering
    - Hands-on workshops, hackathons, builder-focused meetups
    - Hosted by strong technical communities or companies
    - Located in the Seattle area
    
    PENALIZE (Score 1-4):
    - Generic "AI for business" events
    - Beginner-only ChatGPT tutorials
    - Pure marketing webinars
    - Online-only events outside the Seattle area or non-local events
    - Generic networking mixers with no technical substance
    
    Output JSON with fields:
    {
      "relevance_score": 8,
      "category": "AI Engineering",
      "recommendation": "Best Matches",
      "why_it_matters": "A highly technical hackathon on building agentic workflows."
    }
    Recommendations must be one of: "Best Matches", "Maybe Worth Checking", "Low Priority / Skip".
    """

    for event in events:
        try:
            content = f"Title: {event.title}\nDate: {event.date}\nLocation: {event.location}\nDesc: {event.description}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content}
                ],
                max_tokens=150,
                temperature=0.2
            )
            data = json.loads(response.choices[0].message.content)
            event.relevance_score = data.get("relevance_score", 0)
            event.category = data.get("category", "Unknown")
            rec = data.get("recommendation", "Low Priority / Skip")
            if rec not in ["Best Matches", "Maybe Worth Checking", "Low Priority / Skip"]:
                rec = "Low Priority / Skip"
            event.recommendation = rec
            event.why_it_matters = data.get("why_it_matters", "")
        except Exception as e:
            logger.error(f"Error scoring event {event.title}: {e}")
            score_event_fallback(event)

def score_event_fallback(event: Event):
    # Very naive fallback if OpenAI fails
    score = 5
    text = f"{event.title} {event.description} {event.location}".lower()
    
    if "agent" in text or "llm" in text or "open-source" in text or "hackathon" in text or "builder" in text:
        score += 3
    if "seattle" in text or "bellevue" in text:
        score += 2
    if "business" in text or "marketing" in text or "beginner" in text:
        score -= 3
        
    score = max(1, min(10, score))
    event.relevance_score = score
    if score >= 7:
        event.recommendation = "Best Matches"
    elif score >= 4:
        event.recommendation = "Maybe Worth Checking"
    else:
        event.recommendation = "Low Priority / Skip"
    event.why_it_matters = "Scored via basic keyword fallback."


def fetch_from_luma(days: int) -> List[Event]:
    return []

def fetch_from_meetup(days: int) -> List[Event]:
    key = os.getenv("MEETUP_API_KEY")
    if not key:
        raise ValueError("MEETUP_API_KEY missing")
    return []

def fetch_from_eventbrite(days: int) -> List[Event]:
    key = os.getenv("EVENTBRITE_API_KEY")
    if not key:
        raise ValueError("EVENTBRITE_API_KEY missing")
    return []

def fetch_from_tavily(days: int) -> List[Event]:
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        raise ValueError("TAVILY_API_KEY missing")
    
    queries = [
        "Seattle AI agents event",
        "Seattle LLM meetup",
        "Seattle AI builders event",
        "Bellevue AI agents meetup",
        "Redmond AI hackathon",
        "Microsoft Reactor Redmond AI event",
        "AI Tinkerers Seattle",
        "Seattle open source AI event",
        "Seattle GenAI meetup",
        "Databricks Bellevue AI event",
        "GitHub AI event Seattle"
    ]
    
    headers = {"Content-Type": "application/json"}
    events = []
    
    now = datetime.now()
    max_date = now + timedelta(days=days)
    
    for query in queries:
        try:
            payload = {
                "api_key": key,
                "query": query,
                "search_depth": "basic",
                "include_images": False,
                "include_answer": False,
                "max_results": 5
            }
            resp = requests.post("https://api.tavily.com/search", json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
            
            for res in results:
                url = res.get("url")
                if not url: continue
                
                page_title = res.get("title", "")
                page_desc = res.get("content", "")
                
                try:
                    page_resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
                    if page_resp.status_code == 200:
                        soup = BeautifulSoup(page_resp.text, 'html.parser')
                        if soup.title:
                            page_title = soup.title.string or page_title
                        
                        meta_desc = soup.find("meta", attrs={"name": "description"})
                        if meta_desc:
                            page_desc = meta_desc.get("content", page_desc)
                            
                        og_desc = soup.find("meta", property="og:description")
                        if og_desc:
                            page_desc = og_desc.get("content", page_desc)
                except Exception:
                    pass
                
                parsed_date = None
                date_str = "Unknown"
                try:
                    # Fuzzy date parsing from description or title
                    parsed_date = date_parser.parse(page_desc + " " + page_title, fuzzy=True)
                    if parsed_date:
                        date_str = parsed_date.strftime("%Y-%m-%d")
                except Exception:
                    pass
                    
                if parsed_date:
                    if parsed_date < now - timedelta(days=1) or parsed_date > max_date:
                        continue
                
                loc_str = "Unknown"
                text_to_check = (page_desc + " " + page_title).lower()
                if "seattle" in text_to_check: loc_str = "Seattle, WA"
                elif "bellevue" in text_to_check: loc_str = "Bellevue, WA"
                elif "redmond" in text_to_check: loc_str = "Redmond, WA"
                elif "online" in text_to_check or "virtual" in text_to_check: loc_str = "Online"
                
                e = Event(
                    title=page_title,
                    date=date_str,
                    location=loc_str,
                    organizer="Unknown",
                    url=url,
                    description=page_desc,
                    source="tavily"
                )
                
                if date_str != "Unknown" and loc_str != "Unknown":
                    e.source_confidence = "high"
                elif date_str != "Unknown" or loc_str != "Unknown":
                    e.source_confidence = "medium"
                else:
                    e.source_confidence = "low"
                    
                events.append(e)
                
        except Exception as e:
            logger.error(f"Tavily query failed: {query} - {e}")
            
    return events


def deduplicate_events(events: List[Event]) -> List[Event]:
    unique_events = []
    for e in events:
        found = False
        for u in unique_events:
            # Match based on normalized title and date
            if (e.normalized_title == u.normalized_title) and (e.normalized_date == u.normalized_date):
                u.merge_with(e)
                found = True
                break
        if not found:
            unique_events.append(e)
    return unique_events

def generate_markdown_report(events: List[Event], run_notes: Dict[str, Any], filepath: str):
    best_matches = [e for e in events if e.recommendation == "Best Matches"]
    maybe = [e for e in events if e.recommendation == "Maybe Worth Checking"]
    low = [e for e in events if e.recommendation == "Low Priority / Skip"]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Seattle AI Event Radar — {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("## Summary\n\n")
        f.write(f"* Total events found: {len(events)}\n")
        f.write(f"* Best matches: {len(best_matches)}\n")
        f.write(f"* Maybe worth checking: {len(maybe)}\n")
        f.write(f"* Low priority / skip: {len(low)}\n")
        f.write(f"* Sources checked: {', '.join(run_notes['success_sources'])}\n")
        
        f.write("\n* Run notes:\n")
        f.write(f"  * Successful: {', '.join(run_notes['success_sources'])}\n")
        if run_notes['skipped_sources']:
            f.write(f"  * Skipped (Missing Keys): {', '.join(run_notes['skipped_sources'])}\n")
        if run_notes['failed_sources']:
            f.write(f"  * Failed: {', '.join(run_notes['failed_sources'])}\n")
            
        def write_event_section(title, ev_list, short=False):
            f.write(f"\n## {title}\n\n")
            # Sort by score desc
            ev_list.sort(key=lambda x: x.relevance_score, reverse=True)
            for ev in ev_list:
                f.write(f"### {ev.title}\n\n")
                if not short:
                    f.write(f"* Date: {ev.date}\n")
                    f.write(f"* Time: TBD\n")
                    f.write(f"* Location: {ev.location}\n")
                    f.write(f"* Organizer: {ev.organizer}\n")
                    f.write(f"* Source: {', '.join(ev.sources)}\n")
                    f.write(f"* Relevance: {ev.relevance_score}/10\n")
                    f.write(f"* Category: {ev.category}\n")
                    f.write(f"* Confidence: {ev.source_confidence}\n")
                    f.write(f"* Recommendation: {ev.recommendation}\n")
                    f.write(f"* Why it matters: {ev.why_it_matters}\n")
                    f.write(f"* Link: {ev.url}\n\n")
                else:
                    f.write(f"* Date: {ev.date} | Location: {ev.location} | Confidence: {ev.source_confidence} | Link: {ev.url}\n\n")
        
        write_event_section("Best Matches", best_matches)
        write_event_section("Maybe Worth Checking", maybe)
        write_event_section("Low Priority / Skip", low, short=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--min-score", type=int, default=3)
    parser.add_argument("--source", type=str, default="all")
    args = parser.parse_args()

    # Output directory
    os.makedirs("outputs", exist_ok=True)
    
    sources = {"luma": fetch_from_luma, "meetup": fetch_from_meetup, "eventbrite": fetch_from_eventbrite, "tavily": fetch_from_tavily}
    if args.source != "all":
        sources = {args.source: sources.get(args.source)}

    all_events = []
    run_notes = {"success_sources": [], "skipped_sources": [], "failed_sources": []}

    for name, fetch_func in sources.items():
        if fetch_func:
            try:
                evs = fetch_func(args.days)
                all_events.extend(evs)
                run_notes["success_sources"].append(name)
            except ValueError as e:
                logger.warning(f"Skipping {name}: {e}")
                run_notes["skipped_sources"].append(f"{name} ({e})")
            except Exception as e:
                logger.error(f"Source {name} failed: {e}")
                run_notes["failed_sources"].append(name)

    logger.info(f"Fetched {len(all_events)} raw events.")
    unique_events = deduplicate_events(all_events)
    logger.info(f"Deduplicated to {len(unique_events)} events.")
    
    score_events(unique_events)
    
    filtered_events = [e for e in unique_events if e.relevance_score >= args.min_score]

    # Outputs
    # 1. JSON
    with open("outputs/events.json", "w") as f:
        json.dump([e.to_dict() for e in filtered_events], f, indent=2)

    # 2. CSV
    if filtered_events:
        keys = filtered_events[0].to_dict().keys()
        with open("outputs/events.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for e in filtered_events:
                d = e.to_dict()
                d["sources"] = ", ".join(d["sources"])
                writer.writerow(d)

    # 3. MD
    generate_markdown_report(filtered_events, run_notes, "outputs/report.md")

    logger.info("Run complete. Outputs saved to outputs/")

if __name__ == "__main__":
    main()
