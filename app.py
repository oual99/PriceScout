import streamlit as st
import time
from src.agents.agents import (
    build_extracter_agent,
    build_researcher_agent,
    build_trust_scorer_agent,
    ranker_chain,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PriceScout",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #edf3ff;
}

.stApp {
    background: #07111f;
    background-image:
        radial-gradient(circle at top left, rgba(0,191,255,0.14), transparent 32%),
        radial-gradient(circle at bottom right, rgba(124,58,237,0.12), transparent 30%),
        linear-gradient(180deg, #07111f 0%, #0a1729 100%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f8fbff;
    margin: 0 0 1rem;
}
.hero h1 span {
    background: linear-gradient(135deg, #38bdf8, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #b5c3d9;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,189,248,0.35), transparent);
    margin: 2rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 22px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(14px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.28);
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(56,189,248,0.25) !important;
    border-radius: 12px !important;
    color: #f8fbff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 4px rgba(56,189,248,0.14) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #38bdf8 !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #38bdf8 0%, #8b5cf6 100%) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 8px 30px rgba(56,189,248,0.22) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 12px 35px rgba(56,189,248,0.32) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
    backdrop-filter: blur(10px);
}
.step-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56,189,248,0.18);
}
.step-card.active {
    border-color: rgba(56,189,248,0.45);
    background: rgba(56,189,248,0.06);
}
.step-card.done {
    border-color: rgba(34,197,94,0.28);
    background: rgba(34,197,94,0.05);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 18px 0 0 18px;
    background: rgba(255,255,255,0.06);
    transition: background 0.3s;
}
.step-card.active::before { background: #38bdf8; }
.step-card.done::before   { background: #22c55e; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #38bdf8;
    opacity: 0.85;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #f8fbff;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
}
.status-waiting  { color: #64748b; }
.status-running  { color: #38bdf8; }
.status-done     { color: #22c55e; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(12px);
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(56,189,248,0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #d8e2f0;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    backdrop-filter: blur(14px);
}
.feedback-panel {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    backdrop-filter: blur(14px);
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.orange {
    color: #38bdf8;
    border-bottom: 1px solid rgba(56,189,248,0.15);
}
.panel-label.green {
    color: #22c55e;
    border-bottom: 1px solid rgba(34,197,94,0.15);
}

/* ── Progress text ── */
.stSpinner > div { color: #38bdf8 !important; }

/* ── Expander ── */
details {
    background: rgba(255,255,255,0.02);
    border-radius: 14px;
    padding: 0.3rem 0.8rem;
    border: 1px solid rgba(255,255,255,0.06);
}
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #b5c3d9 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #f8fbff;
    margin: 2rem 0 1rem;
}

/* ── Toast-style notice ── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #7f93ad;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }

    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")

    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.82rem;color:#94a3b8;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Price<span>Scout</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — researching, extracting,
        trust-scoring, and ranking — to find and compare the best deal on any
        product across Moroccan online stores.
    </p>
</div>

<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:

    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    topic = st.text_input(
        "Product",
        placeholder="e.g. PS5 slim digital",
        key="topic_input",
        label_visibility="visible",
    )

    run_btn = st.button(
        "⚡ Run PriceScout Pipeline",
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#7f93ad;letter-spacing:0.1em;">
            TRY →
        </span>
    """, unsafe_allow_html=True)

    examples = [
        "PS5 slim digital",
        "iPhone 15 128GB",
        "Samsung Galaxy S24",
    ]

    for ex in examples:
        st.markdown(f"""
        <span style="
            background:rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:8px;
            padding:0.35rem 0.8rem;
            font-size:0.75rem;
            color:#d8e2f0;
            font-family:'DM Sans',sans-serif;
            cursor:default;
        ">
            {ex}
        </span>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:

    st.markdown(
        '<div class="section-heading">Pipeline</div>',
        unsafe_allow_html=True
    )

    r = st.session_state.results
    done = st.session_state.done

    def s(step):

        if not r:
            return "waiting"

        steps = ["researcher", "extracter", "trust_scorer", "ranker"]

        if step in r:
            return "done"

        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"

        return "waiting"

    step_card(
        "01",
        "Researcher",
        s("researcher"),
        "Searches Moroccan stores for listings"
    )

    step_card(
        "02",
        "Extracter",
        s("extracter"),
        "Scrapes pages & extracts price, stock, seller"
    )

    step_card(
        "03",
        "Trust Scorer",
        s("trust_scorer"),
        "Checks seller reputation & reviews"
    )

    step_card(
        "04",
        "Ranker & Formatter",
        s("ranker"),
        "Ranks by trust + price into a result table"
    )


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:

    if not topic.strip():
        st.warning("Please enter a research topic first.")

    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()


if st.session_state.running and not st.session_state.done:

    results = {}
    product_val = st.session_state.topic_input

    # ── Step 1: Researcher ──
    with st.spinner("🔎 Researcher is searching Moroccan stores…"):

        researcher_agent = build_researcher_agent()

        rr = researcher_agent.invoke({
            "messages": [
                ("user", f"Find pages selling this product: {product_val}")
            ]
        })

        results["researcher"] = rr["structured_response"].urls
        st.session_state.results = dict(results)

    # ── Step 2: Extracter ──
    with st.spinner("📄 Extracter is scraping listings…"):

        extracter_agent = build_extracter_agent()

        er = extracter_agent.invoke({
            "messages": [(
                "user",
                f"Scrape and extract product info (price, stock, seller) for "
                f"'{product_val}' from these URLs:\n"
                + "\n".join(results["researcher"])
            )]
        })

        results["extracter"] = er["structured_response"].listings
        st.session_state.results = dict(results)

    # ── Step 3: Trust Scorer ──
    with st.spinner("🛡️ Trust Scorer is checking seller reputations…"):

        sellers = sorted({listing.seller for listing in results["extracter"]})

        trust_scorer_agent = build_trust_scorer_agent()

        tr = trust_scorer_agent.invoke({
            "messages": [(
                "user",
                "Look up reviews/complaints and score the trustworthiness of "
                "these stores:\n" + "\n".join(sellers)
            )]
        })

        results["trust_scorer"] = tr["structured_response"].scores
        st.session_state.results = dict(results)

    # ── Step 4: Ranker & Formatter ──
    with st.spinner("🏆 Ranker is building the result table…"):

        listings_text = "\n".join(
            f"- {l.seller}: {l.price} (stock: {l.stock}) - {l.url}"
            for l in results["extracter"]
        )
        trust_scores_text = "\n".join(
            f"- {t.seller}: {t.score}/10 - {t.justification}"
            for t in results["trust_scorer"]
        )

        results["ranker"] = ranker_chain.invoke({
            "listings": listings_text,
            "trust_scores": trust_scores_text,
        })

        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True

    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="section-heading">Results</div>',
        unsafe_allow_html=True
    )

    # Raw outputs
    if "researcher" in r:
        with st.expander("🔎 URLs Found (raw)", expanded=False):

            urls_html = "<br>".join(r["researcher"])

            st.markdown(
                f'''
                <div class="result-panel">
                    <div class="result-panel-title">
                        Researcher Output
                    </div>

                    <div class="result-content">
                        {urls_html}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

    if "extracter" in r:
        with st.expander("📦 Listings Extracted (raw)", expanded=False):

            listings_html = "<br>".join(
                f"{l.seller} — {l.price} — stock: {l.stock} — {l.url}"
                for l in r["extracter"]
            )

            st.markdown(
                f'''
                <div class="result-panel">
                    <div class="result-panel-title">
                        Extracter Output
                    </div>

                    <div class="result-content">
                        {listings_html}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

    if "trust_scorer" in r:
        with st.expander("🛡️ Trust Scores (raw)", expanded=False):

            trust_html = "<br><br>".join(
                f"{t.seller} — {t.score}/10<br><em>{t.justification}</em>"
                for t in r["trust_scorer"]
            )

            st.markdown(
                f'''
                <div class="result-panel">
                    <div class="result-panel-title">
                        Trust Scorer Output
                    </div>

                    <div class="result-content">
                        {trust_html}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

    # Final result table
    if "ranker" in r:

        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">
                🏆 Result Table
            </div>
        """, unsafe_allow_html=True)

        st.markdown(r["ranker"])

        st.markdown("</div>", unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇ Download Result Table (.md)",
            data=r["ranker"],
            file_name=f"pricescout_results_{int(time.time())}.md",
            mime="text/markdown",
        )


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    PriceScout · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)