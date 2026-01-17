import os
import base64
import asyncio
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Load .env
load_dotenv()

# ==============================================================
# Pydantic Models
# ==============================================================

class Brand(BaseModel):
    name: str
    alt_name: str
    tagline: str
    colors: List[str]
    brand_tone: str
    logo_prompt: str
    logo_url: Optional[str] = None

class Financials(BaseModel):
    total_cost: str
    projected_revenue: str
    roi: str
    burn_rate: str
    break_even_month: str
    runway: str

class PitchSlides(BaseModel):
    problem: str
    solution: str
    market: str
    model: str
    brand_ask: str

class Pitch(BaseModel):
    elevator_pitch: str
    slides: PitchSlides

class RealWorldScenario(BaseModel):
    user_story: str
    pain_point_solved: str
    day_in_life: str

class StartupPack(BaseModel):
    startup_summary: str
    competitors: List[str]
    brand: Brand
    financials: Financials
    real_world_scenario: Optional[RealWorldScenario] = None
    pitch: Pitch

class DomainCheckResult(BaseModel):
    domain: str
    tld: str
    availability: str
    comment: str

class DomainSuggestionPack(BaseModel):
    domains: List[DomainCheckResult]

class CompetitorRow(BaseModel):
    name: str
    type: str
    strengths: str
    weaknesses: str
    differentiation: str
    pricing_hint: str

class CompetitorMatrixPack(BaseModel):
    rows: List[CompetitorRow]

# ==============================================================
# LLM Setup
# ==============================================================

from langchain_openai import ChatOpenAI

def _get_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY missing in .env")
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=api_key
    )

# ==============================================================
# Stability AI Logo (Sync -> Async Wrapper)
# ==============================================================

def _generate_logo_sync(brand_name: str, logo_prompt: str, colors: List[str], tone: str) -> Optional[str]:
    """Synchronous call to Stability AI."""
    stability_key = os.getenv("STABILITY_API_KEY")
    if not stability_key:
        print("[LOGO] STABILITY_API_KEY not set → skipping.")
        return None

    try:
        endpoint = "https://api.stability.ai/v2beta/stable-image/generate/core"
        prompt = (
            f"{logo_prompt}. Brand name: {brand_name}. "
            f"Tone: {tone}. Colors: {', '.join(colors)}. "
            "Style: modern, minimalist, premium, vector logo, highly detailed, centered, white background."
        )
        print(f"[LOGO] Calling Stability for: {brand_name}")
        
        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Accept": "image/*",
        }
        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
        }
        resp = requests.post(endpoint, headers=headers, files=files)
        
        if resp.status_code != 200:
            print("[LOGO] Stability API error:", resp.text[:200])
            return None

        image_base64 = base64.b64encode(resp.content).decode("utf-8")
        return f"data:image/png;base64,{image_base64}"
    except Exception as e:
        print("[LOGO] Exception:", e)
        return None

async def generate_logo_async(brand_name: str, logo_prompt: str, colors: List[str], tone: str) -> Optional[str]:
    """Run sync blocking requests in a thread."""
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(
            pool, _generate_logo_sync, brand_name, logo_prompt, colors, tone
        )

# ==============================================================
# Helper Async Tasks
# ==============================================================

async def get_real_world_scenario_async(idea: str) -> Optional[RealWorldScenario]:
    try:
        llm = _get_llm()
        structured = llm.with_structured_output(RealWorldScenario)
        prompt = f"""
        Idea: {idea}
        Generate a vivid, consumer-centric real-world scenario.
        - User Story: Who is the user?
        - Pain Point: What sucks for them right now?
        - Day in Life: How does this product change their day?
        """
        print(f"[SCENARIO] Generating for {idea}...")
        scenario = await structured.ainvoke([HumanMessage(content=prompt)])
        return scenario
    except Exception as e:
        print("[SCENARIO] Error:", e)
        return None

async def get_competitor_matrix_async(idea: str, summary: str) -> List[Dict[str, Any]]:
    try:
        llm = _get_llm()
        structured = llm.with_structured_output(CompetitorMatrixPack)
        prompt = f"""
        Idea: {idea}
        Summary: {summary}
        Generate competitor matrix (3-5 rows).
        """
        print("[COMPETITORS] Generating matrix...")
        pack: CompetitorMatrixPack = await structured.ainvoke([HumanMessage(content=prompt)])
        return pack.model_dump().get("rows", [])
    except Exception as e:
        print("[COMPETITORS] Error:", e)
        return []

# ==============================================================
# Markdown Builder
# ==============================================================

def build_reply_markdown(pack: StartupPack) -> str:
    lines = []
    lines.append("## 🚀 Startup Summary")
    lines.append(pack.startup_summary.strip())
    lines.append("")

    if pack.real_world_scenario:
        s = pack.real_world_scenario
        lines.append("## 🌍 Real World Scenario")
        lines.append(f"### 👤 User Story")
        lines.append(s.user_story)
        lines.append(f"### 😫 The Pain Point")
        lines.append(s.pain_point_solved)
        lines.append(f"### ☀️ A Day in the Life")
        lines.append(s.day_in_life)
        lines.append("")

    lines.append("### 🧩 Competitors")
    for c in pack.competitors:
        lines.append(f"- {c}")
    lines.append("")

    b = pack.brand
    lines.append("### 🎨 Brand Identity")
    lines.append(f"- **Name:** {b.name}")
    lines.append(f"- **Tagline:** {b.tagline}")
    lines.append(f"- **Tone:** {b.brand_tone}")
    lines.append(f"- **Colors:** {', '.join(b.colors)}")
    lines.append("")
    
    f = pack.financials
    lines.append("### 💰 Financial Overview")
    lines.append(f"- **Cost:** {f.total_cost}")
    lines.append(f"- **Revenue:** {f.projected_revenue}")
    lines.append(f"- **ROI:** {f.roi}")
    lines.append(f"- **Burn:** {f.burn_rate}")
    lines.append(f"- **Runway:** {f.runway}")
    lines.append("")

    p = pack.pitch
    lines.append("### 🎤 Elevator Pitch")
    lines.append(p.elevator_pitch.strip())
    lines.append("")
    lines.append("### 📊 Pitch Deck Outline")
    lines.append(f"**1. Problem** – {p.slides.problem}")
    lines.append(f"**2. Solution** – {p.slides.solution}")
    lines.append(f"**3. Market** – {p.slides.market}")
    lines.append(f"**4. Model** – {p.slides.model}")
    lines.append(f"**5. Ask** – {p.slides.brand_ask}")
    lines.append("")

    return "\n".join(lines)

# ==============================================================
# Main Orchestrator (Async)
# ==============================================================

async def get_venture_response(idea: str) -> Dict[str, Any]:
    if not idea or not idea.strip():
        raise ValueError("Startup idea is empty.")

    print("[CORE] 1. Generating StartupPack (Main)...")
    llm = _get_llm()
    structured = llm.with_structured_output(StartupPack)
    
    messages = [
        SystemMessage(content="You are VentureMind.AI. Generate a consumer-centric startup pack. Focus on specific user needs. Use clear headings."),
        HumanMessage(content=f"User idea: {idea}")
    ]
    
    # 1. Main Pack (Must happen first to get brand name/tone)
    pack: StartupPack = await structured.ainvoke(messages)
    print("[CORE] Main Pack Generated. Starting Parallel Tasks...")

    # 2. Parallelize Aux Tasks
    # - Logo (needs brand details)
    # - Domains (needs brand name)
    # - Competitors (needs summary)
    
    logo_task = generate_logo_async(
        pack.brand.name,
        pack.brand.logo_prompt,
        pack.brand.colors,
        pack.brand.brand_tone
    )
    
    scenario_task = get_real_world_scenario_async(idea)
    
    competitor_task = get_competitor_matrix_async(idea, pack.startup_summary)

    # 3. Wait for all
    logo_url, scenario_obj, competitor_matrix = await asyncio.gather(
        logo_task, scenario_task, competitor_task
    )

    if logo_url:
        pack.brand.logo_url = logo_url
    
    if scenario_obj:
        pack.real_world_scenario = scenario_obj

    print("[CORE] All tasks complete. Building response.")
    
    reply_markdown = build_reply_markdown(pack)

    return {
        "reply_markdown": reply_markdown,
        "startup_pack": pack.model_dump(),
        "domains": [], # Removed
        "competitor_matrix": competitor_matrix,
    }
