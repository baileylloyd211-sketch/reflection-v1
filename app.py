import os
import re
import textwrap
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import streamlit as st

# Stripe is optional at dev time; app will run without it if paywall disabled.
try:
    import stripe
except Exception:
    stripe = None

# -----------------------------
# Config
# -----------------------------
st.set_page_config(
    page_title="GiveItToGot | Problem Solver",
    page_icon="⬛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CONTACT_EMAIL = "baileylloyd211@gmail.com"

# Set this to your privacy policy URL (already exists on GiveItToGot)
PRIVACY_POLICY_URL = st.secrets.get("PRIVACY_POLICY_URL", "").strip()

# Paywall settings
PAYWALL_ENABLED = bool(st.secrets.get("PAYWALL_ENABLED", False))
APP_PUBLIC_URL = st.secrets.get("APP_PUBLIC_URL", "").strip()  # e.g. https://your-app.streamlit.app

# Stripe settings (required if PAYWALL_ENABLED)
STRIPE_SECRET_KEY = st.secrets.get("STRIPE_SECRET_KEY", "").strip()
STRIPE_PRICE_ID = st.secrets.get("STRIPE_PRICE_ID", "").strip()
STRIPE_SUCCESS_URL = st.secrets.get("STRIPE_SUCCESS_URL", "").strip()  # e.g. https://your-app.../?paid=1
STRIPE_CANCEL_URL = st.secrets.get("STRIPE_CANCEL_URL", "").strip()

# -----------------------------
# Styling: black/white/gray + minimal red
# -----------------------------
CSS = """
<style>
:root{
  --bg: #0b0b0c;
  --panel: #111114;
  --panel2:#151518;
  --text: #f2f2f2;
  --muted:#b7b7b7;
  --border: rgba(255,255,255,.10);
  --shadow: 0 18px 50px rgba(0,0,0,.55);
  --radius: 14px;
  --red: #ff2d2d;
}

html, body, [class*="css"] { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }
.stApp {
  background: radial-gradient(900px 450px at 50% -120px, rgba(255,255,255,.08) 0%, var(--bg) 60%);
  color: var(--text);
}
a { color: var(--text); text-decoration: underline; text-decoration-color: rgba(255,45,45,.65); }
small, .muted { color: var(--muted); }

.card {
  background: linear-gradient(180deg, rgba(17,17,20,.95) 0%, rgba(21,21,24,.92) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 16px;
  box-shadow: var(--shadow);
}

.h1 { font-size: 1.55rem; font-weight: 800; margin: 0 0 8px 0; letter-spacing: .02em; }
.h2 { font-size: 1.05rem; font-weight: 750; margin: 0 0 10px 0; color: var(--text); }
.hr { height: 1px; background: var(--border); margin: 14px 0; }

.red { color: var(--red); font-weight: 800; letter-spacing: .02em; }
.badge {
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,45,45,.35);
  background: rgba(255,45,45,.08);
  color: var(--text);
  font-size: .85rem;
}
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }

textarea, input, .stTextInput>div>div>input {
  background: rgba(0,0,0,.25) !important;
}

.stButton>button {
  width: 100%;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.06);
  color: var(--text);
  padding: 10px 12px;
}
.stButton>button:hover {
  border: 1px solid rgba(255,45,45,.45);
  background: rgba(255,45,45,.08);
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def clean_text(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def too_vague(s: str) -> bool:
    """Lightweight vagueness filter. Not perfect, but blocks the worst inputs."""
    s_low = clean_text(s).lower()
    vague = [
        "toxic", "bad vibe", "vibes", "stress", "anxiety", "depressed", "motivation",
        "confidence", "they don't respect", "unheard", "not fair", "everything",
        "complicated", "idk", "i don't know",
    ]
    if len(s_low) < 12:
        return True
    return any(v in s_low for v in vague)

def format_bullets(lines):
    return "\n".join([f"- {l}" for l in lines if l.strip()])

@dataclass
class Case:
    goal: str
    time_horizon: str
    success_criteria: str
    obstacle: str
    problem: str
    power: str
    emotions: str
    history: str
    constraints: str

def solve_case(case: Case) -> Dict[str, str]:
    """
    Deterministic-ish solver: produces
    - clarifying frame
    - next actions
    - impossibility proof if blocked
    """
    # 1) Determine if goal is properly defined
    issues = []
    if too_vague(case.goal):
        issues.append("Goal is vague. Make it measurable.")
    if too_vague(case.success_criteria):
        issues.append("Success criteria is vague. Define a visible finish line.")
    if too_vague(case.obstacle):
        issues.append("Obstacle is vague. Name an observable blocker.")
    if too_vague(case.problem):
        issues.append("Problem statement is vague. Describe what is failing in observable terms.")
    if too_vague(case.constraints):
        issues.append("Constraints are vague. List what you cannot do, and any deadlines or boundaries.")

    # 2) Identify likely category of blocker
    power_low = clean_text(case.power).lower()
    constraints_low = clean_text(case.constraints).lower()
    emotions_low = clean_text(case.emotions).lower()
    history_low = clean_text(case.history).lower()

    # Heuristics (simple but useful)
    external_power_block = any(k in power_low for k in ["they decide", "they control", "approval", "permission", "budget owner", "manager", "vp", "board"]) \
        and any(k in constraints_low for k in ["can't", "cannot", "not allowed", "policy", "legal", "hr", "contract", "compliance"])

    must_escalate = any(k in constraints_low for k in ["must escalate", "has to be escalated", "required escalation", "non-negotiable escalation"])
    time_urgent = any(k in constraints_low for k in ["today", "now", "immediately", "this week", "24", "48 hours", "deadline"])
    avoidance_risk = any(k in emotions_low for k in ["fear", "guilt", "shame", "anger", "resent", "anxious"])

    # 3) Produce outputs
    frame = []
    frame.append(f"Goal: {case.goal}")
    frame.append(f"Horizon: {case.time_horizon}")
    frame.append(f"Success: {case.success_criteria}")
    frame.append(f"Biggest obstacle: {case.obstacle}")
    frame.append(f"Observable problem: {case.problem}")
    frame.append(f"Power dynamics: {case.power}")
    frame.append(f"Constraints: {case.constraints}")

    # If input is too vague, return a tight correction checklist (black-and-white).
    if issues:
        return {
            "status": "NEEDS_CLARITY",
            "summary": "Inputs are not operational yet. Fix these before strategy.",
            "frame": "\n".join(frame),
            "output": format_bullets(issues),
        }

    # 4) Determine “possible vs impossible under constraints”
    # If external power is required and user can't access leverage, declare it blocked unless they can gain leverage.
    if external_power_block and not must_escalate:
        return {
            "status": "BLOCKED_BY_AUTHORITY",
            "summary": "This goal is blocked by authority you don’t currently control.",
            "frame": "\n".join(frame),
            "output": format_bullets([
                "Decide: (A) change the goal to one you control, or (B) acquire leverage.",
                "Leverage options: get explicit sponsor, secure written requirements, or negotiate scope/terms.",
                "If you cannot gain authority or sponsor within the horizon, the original goal is impossible under constraints.",
            ]),
        }

    # If escalation is required/urgent, give escalation plan with damage control.
    if must_escalate or time_urgent:
        steps = [
            "Write a 6-sentence escalation brief (facts only): what failed, impact, timeline, attempted fixes, request, deadline.",
            "Name the decision you need in one line. Do not ask for ‘thoughts’.",
            "Propose 2 options: (1) fastest safe path, (2) fallback path. Each with cost.",
            "Set a hard response deadline aligned to your horizon.",
            "After escalation: execute immediately; report progress at a fixed cadence.",
        ]
        if avoidance_risk:
            steps.insert(0, "State the emotion privately (fear/anger/guilt). Then act anyway. Emotion is not an input to the decision.")
        if "hr" in constraints_low:
            steps.append("If HR is involved: keep it factual, documented, and policy-aligned. No character judgments.")

        return {
            "status": "ACTIONABLE",
            "summary": "Escalation path is valid. Make it clean, factual, and time-bound.",
            "frame": "\n".join(frame),
            "output": format_bullets(steps),
        }

    # Otherwise: standard solve
    steps = [
        "Convert obstacle into a smallest next action you can complete in <30 minutes.",
        "Remove ambiguity: define who does what by when (names/roles, deliverables, dates).",
        "Create a single source of truth (one doc / one thread).",
        "If the same failure happened before: change the system, not the speech.",
    ]
    if "miss" in history_low or "again" in history_low or "pattern" in history_low:
        steps.append("Because this is recurring: add a constraint (checkpoints, approvals, or automatic reminders).")
    if avoidance_risk:
        steps.append("Your emotion is a distortion risk. Don’t negotiate with it—ship the next action anyway.")

    # Impossibility clause
    steps.append("If after 2 cycles the constraint remains unchanged, declare: impossible under current constraints, and rewrite the goal.")

    return {
        "status": "ACTIONABLE",
        "summary": "You can move this forward with controlled execution.",
        "frame": "\n".join(frame),
        "output": format_bullets(steps),
    }

# -----------------------------
# Stripe Paywall
# -----------------------------
def stripe_configured() -> bool:
    if not PAYWALL_ENABLED:
        return False
    return (
        stripe is not None
        and STRIPE_SECRET_KEY
        and STRIPE_PRICE_ID
        and STRIPE_SUCCESS_URL
        and STRIPE_CANCEL_URL
    )

def create_checkout_session() -> str:
    """
    Creates a Stripe Checkout Session and returns the URL.
    """
    stripe.api_key = STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        mode="subscription",  # change to "payment" for one-time
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=STRIPE_SUCCESS_URL + "&session_id={CHECKOUT_SESSION_ID}",
        cancel_url=STRIPE_CANCEL_URL,
        allow_promotion_codes=True,
    )
    return session.url

def verify_checkout_session(session_id: str) -> bool:
    """
    Verifies the session payment status.
    For subscriptions, check session.payment_status and/or subscription status.
    """
    stripe.api_key = STRIPE_SECRET_KEY
    sess = stripe.checkout.Session.retrieve(session_id)
    # For one-time payments: payment_status == "paid"
    # For subscriptions: payment_status often "paid" as well for the first invoice; subscription object exists.
    paid = (getattr(sess, "payment_status", "") == "paid")
    return bool(paid)

def paywall_gate() -> None:
    """
    Shows paywall UI and blocks rest of app unless unlocked.
    """
    # Already unlocked in session
    if st.session_state.get("paid", False):
        return

    # Verify if user returned from Stripe
    qp = st.query_params
    paid_flag = qp.get("paid", "0")
    session_id = qp.get("session_id", "")

    if paid_flag == "1" and session_id and stripe_configured():
        try:
            if verify_checkout_session(session_id):
                st.session_state.paid = True
                return
        except Exception:
            pass

    # Paywall screen
    st.markdown(
        f"""
        <div class="card">
          <div class="h1">Access Required</div>
          <div class="muted">
            To use the tool, purchase access. Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
          </div>
          <div class="hr"></div>
          <div class="muted">
            You will be redirected to Stripe Checkout.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not stripe_configured():
        st.error("Stripe is not configured. Set Stripe secrets to enable the paywall.")
        st.stop()

    if st.button("Continue to Stripe Checkout"):
        try:
            url = create_checkout_session()
            st.link_button("Open Checkout", url)
            st.stop()
        except Exception as e:
            st.error(f"Checkout error: {e}")
            st.stop()

    st.stop()

# -----------------------------
# Header (minimal, serious)
# -----------------------------
st.markdown(
    f"""
    <div class="card">
      <div class="h1">Problem Solver</div>
      <div class="muted">
        Contact: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Paywall (if enabled)
if PAYWALL_ENABLED:
    paywall_gate()

# -----------------------------
# Tabs: Solve | Privacy | Embed
# -----------------------------
tab_solve, tab_privacy, tab_embed = st.tabs(["Solve", "Privacy", "Embed"])

with tab_solve:
    st.markdown(
        """
        <div class="card">
          <div class="h2"><span class="red">Black & white</span> inputs. Real outputs.</div>
          <div class="muted">Finish with a next action, or prove the goal is impossible under current constraints.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("case_form", clear_on_submit=False):
        st.markdown("### Goal")
        goal = st.text_input("What are you trying to accomplish?", placeholder="Example: Ship v1 landing page")
        time_horizon = st.text_input("By when?", placeholder="Example: Friday 5pm")
        success_criteria = st.text_input("What does success look like (observable)?", placeholder="Example: Page live + checkout works")

        st.markdown("### Biggest obstacle")
        obstacle = st.text_area("Name the single biggest obstacle right now.", height=90, placeholder="Example: Payment flow not implemented")

        st.markdown("### Required context")
        problem = st.text_area("Problem (observable failure).", height=90, placeholder="Example: Users cannot pay; no Stripe checkout integrated")
        power = st.text_area("Power dynamics (who can change what).", height=90, placeholder="Example: I control code; Stripe account owner controls keys")
        emotions = st.text_area("Emotional stakes (what may distort judgment).", height=90, placeholder="Example: Fear of shipping something broken")
        history = st.text_area("History (patterns, frequency).", height=90, placeholder="Example: I've delayed this twice; kept rebuilding UI")
        constraints = st.text_area("Constraints (what you cannot do + deadlines/boundaries).", height=90, placeholder="Example: Must launch this week; cannot hire contractor")

        submitted = st.form_submit_button("Run")

    if submitted:
        case = Case(
            goal=clean_text(goal),
            time_horizon=clean_text(time_horizon),
            success_criteria=clean_text(success_criteria),
            obstacle=clean_text(obstacle),
            problem=clean_text(problem),
            power=clean_text(power),
            emotions=clean_text(emotions),
            history=clean_text(history),
            constraints=clean_text(constraints),
        )
        result = solve_case(case)

        st.markdown(
            f"""
            <div class="card">
              <div class="badge">{result["status"]}</div>
              <div class="hr"></div>
              <div class="h2">{result["summary"]}</div>
              <div class="hr"></div>
              <div class="mono" style="white-space: pre-wrap; line-height: 1.45;">{result["frame"]}</div>
              <div class="hr"></div>
              <div class="mono" style="white-space: pre-wrap; line-height: 1.55;">{result["output"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab_privacy:
    st.markdown(
        f"""
        <div class="card">
          <div class="h2">Privacy</div>
          <div class="muted">This app embeds your existing policy.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not PRIVACY_POLICY_URL:
        st.error("Set PRIVACY_POLICY_URL in secrets to embed your privacy policy page.")
    else:
        # Streamlit iframe
        st.components.v1.iframe(PRIVACY_POLICY_URL, height=760, scrolling=True)

with tab_embed:
    st.markdown(
        """
        <div class="card">
          <div class="h2">Embed</div>
          <div class="muted">Use this iframe to embed the app elsewhere.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not APP_PUBLIC_URL:
        st.error("Set APP_PUBLIC_URL in secrets to generate the embed snippet.")
    else:
        snippet = f"""<iframe src="{APP_PUBLIC_URL}" width="100%" height="820" frameborder="0"></iframe>"""
        st.code(snippet, language="html")
        st.markdown(
            '<div class="muted">Note: some platforms block iframes. If it fails, embed a link instead.</div>',
            unsafe_allow_html=True,
        )
