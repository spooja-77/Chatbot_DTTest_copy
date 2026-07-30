import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys
import io
from datetime import datetime

from groq import Groq

# ── SSL fix: nuke ALL cert env vars so httpx uses certifi directly ────────────
for _var in ("SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE"):
    os.environ.pop(_var, None)   # remove unconditionally — stale paths cause [Errno 2]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAISE - Rane Artificial Intelligence for Smart Engineering",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme: navy blue / light lavender — matches the RANE I4.0 dashboard ───────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');
:root{
    --bg:#e6e6f5;
    --surface:#ffffff;
    --border:#c9c9e8;
    --accent:#12127a;
    --accent2:#1a7a3c;
    --text:#1a1a3d;
    --muted:#6e6e8c;
    --header-navy:#12127a;
    --header-navy-dark:#0d0d5e;
}
html,body,[class*="css"]{font-family:'Syne',sans-serif;background:var(--bg)!important;color:var(--text);}
.stApp{background:var(--bg)!important;}
.main-header{display:flex;align-items:center;gap:14px;padding:16px 22px;background:var(--header-navy);border-radius:8px;margin-bottom:20px;box-shadow:0 2px 6px rgba(0,0,0,0.2);}
.main-header .logo{font-size:2.2rem;}
.main-header h1{margin:0;font-size:1.7rem;font-weight:800;color:#ffffff;letter-spacing:-0.5px;}
.main-header p{margin:0;font-size:0.8rem;color:#d8d8f0;font-family:'JetBrains Mono',monospace;}
.msg-user{background:#eef0fb;border:1px solid #c3c8ec;border-radius:18px 18px 4px 18px;padding:14px 18px;margin:8px 0 8px 60px;color:var(--text);font-size:0.95rem;line-height:1.6;box-shadow:0 2px 8px rgba(18,18,122,0.08);}
.msg-bot{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:4px 18px 18px 18px;padding:14px 18px;margin:8px 60px 8px 0;color:var(--text);font-size:0.95rem;line-height:1.7;box-shadow:0 1px 4px rgba(0,0,0,0.06);}
.msg-bot code{background:#f0f0fa;border:1px solid var(--border);border-radius:4px;padding:1px 6px;font-family:'JetBrains Mono',monospace;font-size:0.85rem;color:var(--accent);}
.msg-bot pre{background:#f5f5fc;border:1px solid var(--border);border-radius:8px;padding:12px;overflow-x:auto;font-family:'JetBrains Mono',monospace;font-size:0.82rem;}
.msg-meta{font-size:0.72rem;color:var(--muted);font-family:'JetBrains Mono',monospace;margin-bottom:4px;}
.kpi-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px;}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px 14px;border-top:3px solid var(--accent);box-shadow:0 1px 4px rgba(0,0,0,0.06);}
.kpi-label{font-size:0.7rem;color:var(--muted);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px;}
.kpi-value{font-size:1.4rem;font-weight:800;color:var(--accent);margin-top:2px;}
section[data-testid="stSidebar"]{background:var(--header-navy)!important;border-right:1px solid var(--border);}
section[data-testid="stSidebar"] *{color:#f0f0fa!important;}
section[data-testid="stSidebar"] hr{border-color:rgba(255,255,255,0.2)!important;}
.stButton>button{background:transparent!important;border:1px solid #ffffff!important;color:#ffffff!important;font-family:'JetBrains Mono',monospace!important;font-size:0.8rem!important;border-radius:6px!important;padding:4px 12px!important;transition:all 0.2s!important;}
.stButton>button:hover{background:#ffffff!important;color:var(--accent)!important;}
.stTextInput>div>div>input,.stChatInput textarea{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;}
.personality-active{display:inline-block;padding:3px 10px;background:rgba(255,255,255,0.15);border:1px solid #ffffff;border-radius:20px;font-size:0.72rem;color:#ffffff;font-family:'JetBrains Mono',monospace;}
.status-dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;display:inline-block;margin-right:6px;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
.machine-tag{display:inline-block;padding:2px 8px;background:rgba(18,18,122,0.08);border:1px solid var(--accent);border-radius:12px;font-size:0.68rem;color:var(--accent);font-family:'JetBrains Mono',monospace;margin:2px;}
.col-mapper{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:10px;}
.col-mapper-title{font-size:0.75rem;font-weight:700;color:var(--accent);font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
/* Sidebar-specific overrides: KPI/machine-tag content still needs dark text on white cards even though the sidebar background is navy */
section[data-testid="stSidebar"] .kpi-card,
section[data-testid="stSidebar"] .kpi-card *{color:var(--text)!important;}
section[data-testid="stSidebar"] .kpi-value{color:var(--accent)!important;}
section[data-testid="stSidebar"] .machine-tag{color:var(--accent)!important;background:rgba(255,255,255,0.85)!important;}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
MAX_UPLOAD_MB    = 200
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
NONE_OPTION      = "— not in my data —"

# Logical fields the app cares about, with display labels
LOGICAL_FIELDS = {
    "machine_id":       "Machine ID",
    "machine_name":     "Machine Name",
    "down_time":        "Downtime (numeric, seconds/mins)",
    "breakdown_reason": "Breakdown / Failure Reason",
    "global_reason":    "Global Reason Category (Man/Machine…)",
    "shift":            "Shift",
    "type":             "Event Type (Planned / Unplanned)",
    "start_time":       "Start Time",
    "stop_time":        "Stop Time",
}

# Built-in aliases tried before asking the user
COL_ALIASES = {
    "machine_id":       ["Machine_ID","machine_id","MachineID","Machine ID","MACHINE_ID","machine"],
    "machine_name":     ["Machine_Name","machine_name","MachineName","Machine Name","MACHINE_NAME"],
    "start_time":       ["Start_time","start_time","StartTime","Start Time","START_TIME","start"],
    "stop_time":        ["Stop_time","stop_time","StopTime","Stop Time","STOP_TIME","stop"],
    "down_time":        ["down_time","DownTime","Downtime","DOWN_TIME","duration","Duration",
                         "Downtime_sec","downtime_sec","DT","dt","time_down","Time_Down"],
    "breakdown_reason": ["Breakdown_Reason","breakdown_reason","BreakdownReason","Breakdown Reason",
                         "Reason","reason","Failure_Reason","failure_reason","fault","Fault"],
    "global_reason":    ["Global_reason","global_reason","GlobalReason","Global Reason","GLOBAL_REASON",
                         "Category","category","Loss_Category","loss_category"],
    "shift":            ["Shift","shift","SHIFT","Shift_Name","shift_name"],
    "type":             ["type","Type","TYPE","event_type","Event_Type","planned","Planned"],
}


def resolve_col(df: pd.DataFrame, key: str, col_map: dict | None = None) -> str | None:
    """
    Return actual column name for a logical key.
    col_map (user overrides from session state) is checked first.
    """
    if col_map and key in col_map and col_map[key] != NONE_OPTION:
        c = col_map[key]
        if c in df.columns:
            return c
    for candidate in COL_ALIASES.get(key, []):
        if candidate in df.columns:
            return candidate
    return None


# ── Data helpers ──────────────────────────────────────────────────────────────
def fmt_duration(seconds: float) -> str:
    """Convert seconds to human-friendly string: e.g. 1h 28m or 45m 10s"""
    seconds = int(round(seconds))
    h, rem  = divmod(seconds, 3600)
    m, s    = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m" if m > 0 else f"{h}h"
    elif m > 0:
        return f"{m}m {s}s" if s > 0 else f"{m}m"
    else:
        return f"{s}s"


def normalise_df(df: pd.DataFrame, col_map: dict | None = None) -> pd.DataFrame:
    for key in ["start_time", "stop_time"]:
        col = resolve_col(df, key, col_map)
        if col:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    dt_col = resolve_col(df, "down_time", col_map)
    if dt_col:
        df[dt_col] = pd.to_numeric(df[dt_col], errors="coerce")
    return df


def read_excel_bytes(content: bytes, sheet_name=0) -> tuple[pd.DataFrame | None, str | None]:
    buf = io.BytesIO(content)
    try:
        df = pd.read_excel(buf, sheet_name=sheet_name)
        return df, None
    except Exception as e:
        return None, str(e)


def get_sheet_names(content: bytes) -> list[str]:
    try:
        xl = pd.ExcelFile(io.BytesIO(content))
        return xl.sheet_names
    except Exception:
        return []


def auto_detect_col_map(df: pd.DataFrame) -> dict:
    """Try aliases; for unresolved fields return NONE_OPTION."""
    result = {}
    for key in LOGICAL_FIELDS:
        found = None
        for candidate in COL_ALIASES.get(key, []):
            if candidate in df.columns:
                found = candidate
                break
        result[key] = found if found else NONE_OPTION
    return result


# ── Context builder ───────────────────────────────────────────────────────────
def _ranked_table(series: pd.Series, label: str, fmt_fn=None) -> str:
    """Return a ranked list string from a Series (index=name, values=numeric)."""
    if series.empty:
        return "  (no data)"
    rows = []
    for rank, (name, val) in enumerate(series.sort_values(ascending=False).items(), 1):
        disp = fmt_fn(val) if fmt_fn else str(val)
        rows.append(f"  #{rank}  {name}: {disp}")
    return "\n".join(rows)


def get_machine_info(df: pd.DataFrame, col_map: dict) -> dict:
    """Legacy helper kept for compat — main context uses build_data_context."""
    return {}


def build_data_context(df: pd.DataFrame, col_map: dict) -> str:
    def rc(k): return resolve_col(df, k, col_map)
    dt_col = rc("down_time"); br_col = rc("breakdown_reason")
    gl_col = rc("global_reason"); sh_col = rc("shift")
    tp_col = rc("type"); st_col = rc("start_time")
    id_col = rc("machine_id"); nm_col = rc("machine_name")
    key_col = nm_col or id_col

    # ── All aggregations computed in Python — LLM must NOT re-compute from raw rows ──
    total_dt = float(df[dt_col].sum())  if dt_col else 0.0
    avg_dt   = float(df[dt_col].mean()) if dt_col else 0.0

    # Per-machine aggregations (sorted highest → lowest)
    machine_dt_ranked   = (
        df.groupby(key_col)[dt_col].sum().sort_values(ascending=False)
        if key_col and dt_col else pd.Series(dtype=float)
    )
    machine_evt_ranked  = (
        df.groupby(key_col)[dt_col].count().sort_values(ascending=False)
        if key_col and dt_col else pd.Series(dtype=float)
    )

    # Per-shift aggregations
    shift_dt_ranked = (
        df.groupby(sh_col)[dt_col].sum().sort_values(ascending=False)
        if sh_col and dt_col else pd.Series(dtype=float)
    )
    shift_evt_ranked = (
        df.groupby(sh_col)[dt_col].count().sort_values(ascending=False)
        if sh_col and dt_col else pd.Series(dtype=float)
    )

    # Per-reason aggregations
    reason_dt_ranked = (
        df.groupby(br_col)[dt_col].sum().sort_values(ascending=False)
        if br_col and dt_col else pd.Series(dtype=float)
    )
    global_dt_ranked = (
        df.groupby(gl_col)[dt_col].sum().sort_values(ascending=False)
        if gl_col and dt_col else pd.Series(dtype=float)
    )

    # Planned vs Unplanned
    type_map = {3: "Unplanned", 4: "Planned", "Unplanned": "Unplanned", "Planned": "Planned",
                "unplanned": "Unplanned", "planned": "Planned", 0: "Unplanned", 1: "Planned"}
    by_type = df[tp_col].map(type_map).value_counts().to_dict() if tp_col else {}
    unplanned_dt = (
        df.loc[df[tp_col].isin([3, "Unplanned", "unplanned"]), dt_col].sum()
        if tp_col and dt_col else 0
    )
    planned_dt = (
        df.loc[df[tp_col].isin([4, 1, "Planned", "planned"]), dt_col].sum()
        if tp_col and dt_col else 0
    )

    date_range = f"{df[st_col].min()} to {df[st_col].max()}" if st_col else "N/A"
    machines   = df[key_col].dropna().unique().tolist() if key_col else []

    # Per-machine detailed breakdown (top reason per machine)
    machine_detail_lines = []
    if key_col and dt_col:
        for machine, grp in df.groupby(key_col):
            m_total  = float(grp[dt_col].sum())
            m_events = len(grp)
            m_avg    = float(grp[dt_col].mean())
            top_r    = (grp.groupby(br_col)[dt_col].sum().idxmax()
                        if br_col and not grp.empty else "N/A")
            top_gl   = (grp.groupby(gl_col)[dt_col].sum().idxmax()
                        if gl_col and not grp.empty else "N/A")
            by_sh    = (grp.groupby(sh_col)[dt_col].sum().sort_values(ascending=False).to_dict()
                        if sh_col else {})
            machine_detail_lines.append(
                f"  Machine: {machine}\n"
                f"    Total downtime   : {m_total:,.0f} sec ({fmt_duration(m_total)})\n"
                f"    Event count      : {m_events}\n"
                f"    Avg per event    : {m_avg:.1f} sec ({fmt_duration(m_avg)})\n"
                f"    Top reason       : {top_r}\n"
                f"    Top global cat   : {top_gl}\n"
                f"    Downtime by shift: {json.dumps(by_sh, default=str)}"
            )
    machine_detail_block = "\n\n".join(machine_detail_lines) if machine_detail_lines else "  (no machine data)"

    top_reason = reason_dt_ranked.index[0] if not reason_dt_ranked.empty else "N/A"
    top_global = global_dt_ranked.index[0] if not global_dt_ranked.empty else "N/A"
    top_machine_by_dt = machine_dt_ranked.index[0] if not machine_dt_ranked.empty else "N/A"
    top_shift_by_dt   = shift_dt_ranked.index[0]   if not shift_dt_ranked.empty   else "N/A"

    return f"""\
=== FACTORY DOWNTIME DATABASE CONTEXT ===
IMPORTANT: ALL SECTIONS BELOW ARE PRE-COMPUTED AGGREGATIONS.
DO NOT guess or re-derive from raw rows — use these numbers directly.

Total records: {len(df)}
Date range: {date_range}
Columns available: {", ".join(df.columns.tolist())}
Unique machines ({len(machines)}): {machines}
Shifts: {df[sh_col].unique().tolist() if sh_col else 'N/A'}

--- OVERALL AGGREGATE STATS ---
Total downtime : {total_dt:,.0f} sec  ({fmt_duration(total_dt)})
Average per event: {avg_dt:.1f} sec  ({fmt_duration(avg_dt)})
Worst machine (highest DT): {top_machine_by_dt}
Worst shift   (highest DT): {top_shift_by_dt}
Top breakdown reason: {top_reason}
Top global reason category: {top_global}

--- MACHINES RANKED BY TOTAL DOWNTIME (seconds, high → low) ---
{_ranked_table(machine_dt_ranked, 'machine', fmt_duration)}

--- MACHINES RANKED BY EVENT COUNT (high → low) ---
{_ranked_table(machine_evt_ranked, 'machine')}

--- SHIFTS RANKED BY TOTAL DOWNTIME (seconds, high → low) ---
{_ranked_table(shift_dt_ranked, 'shift', fmt_duration)}

--- SHIFTS RANKED BY EVENT COUNT (high → low) ---
{_ranked_table(shift_evt_ranked, 'shift')}

--- BREAKDOWN REASONS RANKED BY TOTAL DOWNTIME (seconds, high → low) ---
{_ranked_table(reason_dt_ranked, 'reason', fmt_duration)}

--- GLOBAL REASON CATEGORIES RANKED BY TOTAL DOWNTIME (high → low) ---
{_ranked_table(global_dt_ranked, 'global_reason', fmt_duration)}

--- PLANNED vs UNPLANNED ---
Event counts: {json.dumps(by_type, default=str)}
Unplanned total downtime: {unplanned_dt:,.0f} sec ({fmt_duration(unplanned_dt)})
Planned total downtime  : {planned_dt:,.0f} sec ({fmt_duration(planned_dt)})

--- PER-MACHINE DETAILED BREAKDOWN ---
{machine_detail_block}

--- ACTIVE COLUMN MAPPING ---
Machine ID col: {id_col} | Machine Name col: {nm_col}
Downtime col: {dt_col} | Breakdown Reason col: {br_col}
Global Reason col: {gl_col} | Shift col: {sh_col}
Type col: {tp_col} | Start col: {st_col}
=== END CONTEXT ==="""


def compute_kpis(df: pd.DataFrame, col_map: dict) -> dict:
    def rc(k): return resolve_col(df, k, col_map)
    dt_col = rc("down_time"); tp_col = rc("type")
    br_col = rc("breakdown_reason")
    nm_col = rc("machine_name"); id_col = rc("machine_id")

    total_sec    = df[dt_col].sum() if dt_col else 0
    unplanned    = 0
    if tp_col:
        mask = df[tp_col].isin([3, "Unplanned", "unplanned", "UNPLANNED"])
        unplanned = int(mask.sum())
    top_reason   = df.groupby(br_col)[dt_col].sum().idxmax() if br_col and dt_col else "N/A"
    key_col      = nm_col or id_col
    num_machines = df[key_col].nunique() if key_col else 0
    return {
        "total_hours": fmt_duration(total_sec),
        "events":      str(len(df)),
        "unplanned":   f"{unplanned}/{len(df)}",
        "top_cause":   str(top_reason).replace(" ", "\u00a0")[:22],
        "machines":    str(num_machines),
    }


# ── Personalities & LLM ───────────────────────────────────────────────────────
PERSONALITIES = {
    "🔬 Analyst":   ("analyst",   "Precise manufacturing analyst. Use bullet-points, exact numbers, percentages. Lead with the key metric."),
    "🤖 Engineer":  ("engineer",  "Seasoned factory floor engineer. Give practical root-cause and corrective action advice. Be direct."),
    "📊 Executive": ("executive", "C-suite operations advisor. Translate data into cost, OEE, and ROI impact. Keep it concise."),
}

SYSTEM_TEMPLATE = """You are DownBot, an expert industrial AI assistant.
Deep expertise in OEE, Six Sigma, TPM, and lean manufacturing.

PERSONALITY: {personality_desc}

LIVE DATA:
{data_context}

CRITICAL RULES — READ CAREFULLY:
1. ALWAYS use the pre-computed ranked sections (e.g. "MACHINES RANKED BY TOTAL DOWNTIME",
   "SHIFTS RANKED BY TOTAL DOWNTIME", "PER-MACHINE DETAILED BREAKDOWN", etc.).
   NEVER read individual raw rows and pick the first one — that is WRONG.
2. To answer "which X has most/least downtime", read the #1 entry from the matching RANKED section.
3. To compare all machines/shifts/reasons, use the corresponding RANKED table in full.
4. Numeric values are in seconds in the context; always convert and display as "Xh Ym" format.
   Never report decimal hours (0.88h) — always use fmt like "1h 28m" or "45m 10s".
5. Reference machine names and IDs together when both exist.
6. Use markdown: **bold** key terms, `code` for IDs, tables for comparisons.
7. Proactively surface related insights the user didn't ask for.
8. End analytical answers with a "💡 Recommendation:" section.
9. If a column is listed as 'None' in the mapping, acknowledge that data is unavailable.
"""

SUGGESTED_QUESTIONS = [
    "Which shift had the most downtime?",
    "Which machine has the highest total downtime?",
    "Compare all machines by downtime hours",
    "What's the top unplanned breakdown reason?",
    "Compare Man vs Method vs Material losses",
    "Which machine had the longest single downtime event?",
    "Show me a summary of all machine performance",
    "What % of downtime is planned vs unplanned?",
    "Which machines need urgent attention?",
    "Any anomalies I should investigate?",
]


def get_api_key():
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        try:
            key = st.secrets["GROQ_API_KEY"].strip()
        except Exception:
            pass
    return key

def get_client():
    return get_api_key() or None   # just returns the key string; kept for compat checks

def chat_llm(client, messages, system_prompt):
    """Call Groq REST API directly via requests — bypasses all httpx/SSL issues."""
    import requests, certifi
    api_key = get_api_key()
    if not api_key:
        return "⚠️ GROQ_API_KEY not configured."

    payload = {
        "model": "llama-3.3-70b-versatile",
        "max_tokens": 1500,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
    }
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            verify=certifi.where(),
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.SSLError:
        # Last resort: disable SSL verification
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            verify=False,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ API error: {e}"


# ── Session state ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "messages": [],
    "personality": "🔬 Analyst",
    "pending_question": None,
    "uploaded_df": None,          # raw DataFrame
    "col_map": {},                # user column mapping
    "mapping_confirmed": True,   # has user clicked "Confirm mapping"?
    "_excel_bytes": None,
    "_sheets": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

client = get_client()

# ── Active dataframe + col_map ────────────────────────────────────────────────
df     = st.session_state.uploaded_df if st.session_state.uploaded_df is not None else pd.DataFrame()
col_map = st.session_state.col_map

data_ctx = build_data_context(df, col_map) if not df.empty else "No data loaded."
kpis     = compute_kpis(df, col_map)       if not df.empty else {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:1.3rem;font-weight:800;margin-bottom:4px;">⚙️ DownBot</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.72rem;color:#d8d8f0;font-family:JetBrains Mono,monospace;margin-bottom:14px;">'
        f'<span class="status-dot"></span>LIVE · {len(df)} events loaded</div>',
        unsafe_allow_html=True,
    )

    # Personality
    st.markdown("**Personality Mode**")
    for label in PERSONALITIES:
        if st.button(label, key=f"pers_{label}", use_container_width=True):
            st.session_state.personality = label
            st.rerun()
    pid, pdesc = PERSONALITIES[st.session_state.personality]
    st.markdown(f'<div class="personality-active">{st.session_state.personality} active</div>', unsafe_allow_html=True)

    st.divider()

    # KPIs
    if kpis and st.session_state.mapping_confirmed:
        st.markdown("**📊 KPIs**")
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-label">Total Downtime</div><div class="kpi-value">{kpis['total_hours']}</div></div>
            <div class="kpi-card"><div class="kpi-label">Events</div><div class="kpi-value">{kpis['events']}</div></div>
            <div class="kpi-card"><div class="kpi-label">Unplanned</div><div class="kpi-value">{kpis['unplanned']}</div></div>
            <div class="kpi-card"><div class="kpi-label">Machines</div><div class="kpi-value">{kpis['machines']}</div></div>
        </div>
        <div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:10px 14px;border-top:3px solid var(--accent2);margin-bottom:10px;">
            <div class="kpi-label" style="color:var(--muted);">Top Cause</div>
            <div style="font-size:0.82rem;font-weight:700;color:var(--accent2);margin-top:2px;">{kpis['top_cause']}</div>
        </div>
        """, unsafe_allow_html=True)

        nm_col = resolve_col(df, "machine_name", col_map)
        id_col_v = resolve_col(df, "machine_id", col_map)
        kc = nm_col or id_col_v
        if kc:
            st.markdown("**🏭 Machines in dataset**")
            chips = "".join(f'<span class="machine-tag">{m}</span>'
                            for m in sorted(df[kc].dropna().astype(str).unique()))
            st.markdown(chips, unsafe_allow_html=True)

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Upload
    st.markdown(f"**📂 Upload Your Data** *(max {MAX_UPLOAD_MB} MB)*")
    uploaded = st.file_uploader("Drop Excel file here", type=["xlsx","xlsm","xltx"],
                                 label_visibility="collapsed")

    # ── Sheet selector ────────────────────────────────────────────────────────
    if st.session_state._sheets:
        sheets = st.session_state._sheets
        chosen = st.selectbox("📑 Select sheet:", sheets, key="sheet_select")
        if st.button("Load this sheet", use_container_width=True):
            raw_df, err = read_excel_bytes(st.session_state._excel_bytes, sheet_name=chosen)
            if err:
                st.error(f"Failed: {err}")
            else:
                detected_map = auto_detect_col_map(raw_df)
                raw_df = normalise_df(raw_df, detected_map)   # ← ensure numeric/datetime types
                st.session_state.uploaded_df     = raw_df
                st.session_state.col_map         = detected_map
                st.session_state.mapping_confirmed = True
                st.session_state._sheets         = None
                st.session_state._excel_bytes    = None
                st.session_state.messages        = []
                st.rerun()

    elif uploaded is not None:
        raw_bytes = uploaded.read()
        if len(raw_bytes) > MAX_UPLOAD_BYTES:
            st.error(f"File too large ({len(raw_bytes)/1024/1024:.1f} MB). Limit is {MAX_UPLOAD_MB} MB.")
        else:
            sheets = get_sheet_names(raw_bytes)
            if len(sheets) > 1:
                st.session_state._excel_bytes = raw_bytes
                st.session_state._sheets      = sheets
                st.info("Multiple sheets detected — pick one above.")
                st.rerun()
            else:
                raw_df, err = read_excel_bytes(raw_bytes, sheet_name=0)
                if err:
                    st.error(f"Could not read file: {err}")
                else:
                    detected_map = auto_detect_col_map(raw_df)
                    raw_df = normalise_df(raw_df, detected_map)   # ← ensure numeric/datetime types
                    st.session_state.uploaded_df     = raw_df
                    st.session_state.col_map         = detected_map
                    st.session_state.mapping_confirmed = True
                    st.session_state.messages        = []
                    st.rerun()

    if st.session_state.uploaded_df is not None:
        if st.button("↩️ Reset / upload new file", use_container_width=True):
            for k in ["uploaded_df","col_map","mapping_confirmed","messages","_excel_bytes","_sheets"]:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div class="logo">⚙️</div>
  <div>
    <h1>DownBot — Factory Intelligence</h1>
    <p>RAG-powered downtime analysis · Ask anything about your manufacturing data</p>
  </div>
</div>
""", unsafe_allow_html=True)

if not get_api_key():
    st.error("⚠️ GROQ_API_KEY not found. Add it to `.streamlit/secrets.toml`.")
    st.code('GROQ_API_KEY = "gsk_..."', language="toml")
    st.stop()




if df.empty:
    st.info("👈 Upload an Excel file from the sidebar to get started.")
    st.stop()

# ── Recalculate context with confirmed mapping ────────────────────────────────
data_ctx = build_data_context(df, col_map)
kpis     = compute_kpis(df, col_map)

# ── Chat ──────────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    nm_col   = resolve_col(df, "machine_name", col_map)
    id_col_v = resolve_col(df, "machine_id", col_map)
    kc       = nm_col or id_col_v
    n_m      = df[kc].nunique() if kc else "?"
    st.markdown(f"""
    <div class="msg-bot">
    👋 <strong>Welcome to DownBot!</strong><br><br>
    Data loaded — <strong>{len(df)} events</strong> across <strong>{n_m} machines</strong>.<br>
    Your column mapping is confirmed. Ask me anything about your downtime data! 🔍
    </div>
    """, unsafe_allow_html=True)

# ── Suggested question buttons ────────────────────────────────────────────────
st.markdown("**💬 Suggested Questions**")
cols = st.columns(2)
for i, q in enumerate(SUGGESTED_QUESTIONS):
    if cols[i % 2].button(q, key=f"sugg_{i}"):
        st.session_state.pending_question = q
        st.rerun()

# ── Render message history ────────────────────────────────────────────────────
for msg in st.session_state.messages:
    role    = msg["role"]
    content = msg["content"]
    ts      = msg.get("ts", "")
    if role == "user":
        st.markdown(
            f'<div class="msg-meta" style="text-align:right;">You · {ts}</div>'
            f'<div class="msg-user">{content}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="msg-meta">⚙️ DownBot · {ts}</div>'
            f'<div class="msg-bot">{content}</div>',
            unsafe_allow_html=True,
        )

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about your downtime data…")
question   = st.session_state.pending_question or user_input
if st.session_state.pending_question:
    st.session_state.pending_question = None

if question:
    ts = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": question, "ts": ts})
    _, pdesc = PERSONALITIES[st.session_state.personality]
    system_prompt = SYSTEM_TEMPLATE.format(personality_desc=pdesc, data_context=data_ctx)
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    with st.spinner("Analysing…"):
        try:
            answer = chat_llm(None, history, system_prompt)
        except Exception as e:
            answer = f"⚠️ API error: {e}"
    st.session_state.messages.append({"role": "assistant", "content": answer, "ts": ts})
    st.rerun()