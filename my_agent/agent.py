"""
This file is where you will implement your agent.
The `root_agent` is used to evaluate your agent's performance.

Architecture: lightweight router → specialised sub-agents.
The router classifies each question and transfers it to the right sub-agent.
Each sub-agent carries only the tools it needs.
"""

from google.adk.agents import llm_agent
from google.adk.planners import BuiltInPlanner
from google.genai.types import GenerateContentConfig, ThinkingConfig

from my_agent.tools import (
    calculator,
    chess_best_move,
    fetch_webpage,
    read_image,
    read_pdf,
    web_search,
)

# ---------------------------------------------------------------------------
# Shared config helpers
# ---------------------------------------------------------------------------

_THINKING = BuiltInPlanner(thinking_config=ThinkingConfig(thinking_budget=5000))
_CFG = GenerateContentConfig(temperature=0.1)
_CFG_COLD = GenerateContentConfig(temperature=0.0)

_ANSWER_RULE = (
    "ANSWERING: Give ONLY the final answer in the most concise form possible. "
    "If the question asks for a number, respond with just the number. "
    "If it asks for a name, respond with just the name. "
    "Do NOT include explanations, reasoning, or extra text in your final answer."
)

# ---------------------------------------------------------------------------
# Sub-agents
# ---------------------------------------------------------------------------

math_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="math_agent",
    description=(
        "Handles ALL arithmetic and mathematical calculations: "
        "addition, subtraction, multiplication, division, exponents, square roots, modulo."
    ),
    instruction=(
        "You are a math specialist. Use the calculator tool for EVERY numeric calculation — "
        "never compute in your head.\n"
        "Chain multiple calculator calls for multi-step problems "
        "(e.g. compute area first, then take its square root).\n\n"
        + _ANSWER_RULE
    ),
    tools=[calculator],
    generate_content_config=_CFG,
    planner=_THINKING,
)

pdf_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="pdf_agent",
    description=(
        "Reads and analyses PDF files. Use when the question references a .pdf file path "
        "or a URL pointing to a PDF document."
    ),
    instruction=(
        "You are a PDF reading specialist.\n"
        "Call read_pdf with the exact file path or URL from the question. "
        "Read the full extracted text carefully before answering.\n\n"
        + _ANSWER_RULE
    ),
    tools=[read_pdf],
    generate_content_config=_CFG,
    planner=_THINKING,
)

search_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    description=(
        "Searches the web and fetches web pages. Use for questions about real-world facts, "
        "current events, historical data, changelogs, publications, or any question that "
        "requires looking up information online. Also use when the question provides a URL directly."
    ),
    instruction=(
        "You are a web research specialist.\n\n"
        "STRATEGY:\n"
        "- If the question provides a URL directly, call fetch_webpage on it immediately "
        "(no need to search first).\n"
        "- Otherwise call web_search first, then fetch_webpage on the most promising URL.\n"
        "- ALWAYS set search_term when calling fetch_webpage. Use the most specific identifier "
        "mentioned in or implied by the question — a class name, function name, version number, "
        "or exact phrase. For example:\n"
        "  · 'what base command received a bug fix' → search_term='BaseLabelPropagation' "
        "or the specific class name from the question context\n"
        "  · 'July 2017 changelog bug fix' → search_term='Other predictors'\n"
        "  · 'what changed in version X' → search_term='X.Y.Z' (the version number)\n"
        "  Do NOT use vague phrases like 'bug fix' or 'predictor base command' as search_term.\n"
        "- Pass search_term=\"\" only when you have no specific term and need the page intro.\n"
        "- If the result says the term was not found, retry with a different search_term "
        "or fetch a different URL.\n"
        "- Limit yourself to at most 3 web_search calls and 5 fetch_webpage calls total.\n\n"
        + _ANSWER_RULE
    ),
    tools=[web_search, fetch_webpage],
    generate_content_config=_CFG,
    planner=_THINKING,
)

vision_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="vision_agent",
    description=(
        "Reads and analyses image files (.png, .jpg, .jpeg, .webp, .gif). "
        "Use for questions that reference a non-chess image file."
    ),
    instruction=(
        "You are an image analysis specialist.\n"
        "Call read_image with the exact file path from the question and a specific, "
        "detailed question describing exactly what data or text you need to extract.\n\n"
        + _ANSWER_RULE
    ),
    tools=[read_image],
    generate_content_config=_CFG,
    planner=_THINKING,
)

chess_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="chess_agent",
    description=(
        "Analyses chess positions and finds the best move. "
        "Use when the question asks for the best chess move and provides a board image."
    ),
    instruction=(
        "You are a chess analysis specialist.\n\n"
        "STEPS:\n"
        "1. Call read_image with the board image file path. In your question, ask the model to "
        "describe each rank from rank 8 (top) to rank 1 (bottom), identifying every piece "
        "(K=king, Q=queen, R=rook, B=bishop, N=knight, P=pawn; uppercase=White, lowercase=black), "
        "and produce the full FEN string including side to move.\n"
        "2. Pass the FEN string to chess_best_move to get the engine's best move.\n\n"
        + _ANSWER_RULE
    ),
    tools=[read_image, chess_best_move],
    generate_content_config=_CFG,
    planner=_THINKING,
)

general_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="general_agent",
    description=(
        "Handles general knowledge questions, logic puzzles, language tasks, and reasoning "
        "problems that do not require any tools."
    ),
    instruction=(
        "You are a precise reasoning specialist.\n"
        "Think through ALL constraints in the question step-by-step before answering.\n"
        "Read carefully what the question is asking for and answer exactly that.\n\n"
        + _ANSWER_RULE
    ),
    tools=[],
    generate_content_config=_CFG,
    planner=_THINKING,
)

# ---------------------------------------------------------------------------
# Router (root_agent)
# ---------------------------------------------------------------------------

root_agent = llm_agent.Agent(
    model="gemini-2.5-flash",
    name="agent",
    description="Router that classifies questions and delegates to the right specialist agent.",
    instruction=(
        "You are a routing agent. Your ONLY job is to read the question and immediately "
        "transfer it to the correct specialist agent. Do NOT answer the question yourself.\n\n"
        "ROUTING RULES (pick the first rule that matches):\n"
        "- Question involves arithmetic, numbers, exponents, square roots, or any calculation "
        "→ transfer to math_agent\n"
        "- Question mentions a .pdf file path or PDF URL "
        "→ transfer to pdf_agent\n"
        "- Question asks about a chess position or best chess move "
        "→ transfer to chess_agent\n"
        "- Question references an image file (.png, .jpg, .jpeg, .webp, .gif) "
        "→ transfer to vision_agent\n"
        "- Question requires web lookup, real-world facts, current data, a changelog, "
        "a DOI, a URL, or any external information "
        "→ transfer to search_agent\n"
        "- Everything else (reasoning, logic puzzles, language, general knowledge) "
        "→ transfer to general_agent\n\n"
        "Transfer immediately. One transfer per question. Nothing else."
    ),
    tools=[],
    generate_content_config=_CFG_COLD,
    sub_agents=[
        math_agent,
        pdf_agent,
        search_agent,
        vision_agent,
        chess_agent,
        general_agent,
    ],
)
