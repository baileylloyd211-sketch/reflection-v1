# app.py
import streamlit as st
from dataclasses import dataclass
from typing import Dict, List, Tuple

# -----------------------------
# Page + Styling
# -----------------------------
st.set_page_config(
    page_title="Reflection | GiveItToGot",
    page_icon="🪞",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
:root{
  --bg:#0b0f14;
  --panel:#111827;
  --panel2:#0f172a;
  --text:#e5e7eb;
  --muted:#9ca3af;
  --accent:#60a5fa;
  --accent2:#f472b6;
  --good:#34d399;
  --warn:#fbbf24;
  --bad:#fb7185;
  --border: rgba(255,255,255,.08);
  --shadow: 0 16px 40px rgba(0,0,0,.35);
  --radius: 18px;
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}
html, body, [class*="css"] { font-family: var(--sans); }
.stApp { background: radial-gradient(1200px 700px at 50% -100px, #1f2937 0%, var(--bg) 55%); color: var(--text); }
a { color: var(--accent); text-decoration: none; }
.small { color: var(--muted); font-size: 0.95rem; }
.brand { letter-spacing: .08em; font-weight: 700; font-size: .85rem; color: var(--muted); text-transform: uppercase; }
.panel {
  background: linear-gradient(180deg, rgba(17,24,39,.95) 0%, rgba(15,23,42,.92) 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px 18px;
  box-shadow: var(--shadow);
}
.title {
  font-size: 2.0rem;
  font-weight: 800;
  margin: 0 0 6px 0;
}
.subtitle { color: var(--muted); margin: 0 0 14px 0; line-height: 1.5; }
.hr { height: 1px; background: var(--border); margin: 16px 0; }
.pill {
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  background: rgba(96,165,250,.12);
  border: 1px solid rgba(96,165,250,.22);
  color: #cfe5ff;
  font-size: .85rem; margin-right: 8px; margin-bottom: 8px;
}
.btnrow { display:flex; gap:10px; flex-wrap:wrap; margin-top: 10px; }
.caption { font-size: .92rem; color: var(--muted); }
.progressWrap { margin-top: 8px; }
.mirrorStage {
  position: relative;
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,.10);
  background: radial-gradient(900px 380px at 50% 5%, rgba(96,165,250,.20) 0%, rgba(244,114,182,.10) 35%, rgba(17,24,39,.95) 72%);
  box-shadow: 0 25px 70px rgba(0,0,0,.45);
  overflow: hidden;
  padding: 22px 18px;
}
.curtainLeft, .curtainRight{
  position:absolute; top:0; bottom:0; width:52%;
  background: linear-gradient(180deg, #7f1d1d 0%, #450a0a 100%);
  filter: saturate(1.2);
}
.curtainLeft{ left:0; clip-path: polygon(0 0, 100% 0, 85% 100%, 0 100%); }
.curtainRight{ right:0; clip-path: polygon(15% 100%, 100% 0, 100% 100%, 0 100%); }
.curtainFold{
  position:absolute; top:-40px; bottom:-40px; width:20px;
  background: rgba(255,255,255,.10);
  filter: blur(0.2px);
}
.curtainLeft .curtainFold{ right: 36px; }
.curtainRight .curtainFold{ left: 36px; }
.stageInner { position: relative; z-index: 2; }
.lipstick {
  font-family: "Comic Sans MS", "Brush Script MT", cursive;
  font-size: 1.55rem;
  color: rgba(255,255,255,.92);
  text-shadow: 0 2px 0 rgba(0,0,0,.35);
}
.lipstick strong { color: rgba(244,114,182,.95); }
.mirrorGlass{
  background: linear-gradient(145deg, rgba(255,255,255,.10), rgba(255,255,255,.03));
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 18px;
  padding: 16px 14px;
  margin-top: 12px;
}
.scoreGrid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}
.metric {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px 12px;
  background: rgba(15,23,42,.65);
}
.metric .k { color: var(--muted); font-size: .85rem; margin-bottom: 6px; }
.metric .v { font-weight: 800; font-size: 1.1rem; }
.footer { margin-top: 22px; color: var(--muted); font-size: .9rem; text-align:center; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Quiz Model
# -----------------------------
DIMENSIONS = ["Integrity", "Empathy", "Agency", "Restraint"]

@dataclass
class Option:
    label: str
    delta: Dict[str, int]

@dataclass
class Question:
    prompt: str
    options: List[Option]

def opt(label: str, I=0, E=0, A=0, R=0) -> Option:
    return Option(label=label, delta={"Integrity": I, "Empathy": E, "Agency": A, "Restraint": R})

QUESTIONS: List[Question] = [
    Question(
        "Someone misunderstood you in public. Your first move is…",
        [
            opt("Correct them politely, fast, then move on.", I=2, E=1, A=1, R=2),
            opt("Let it slide. Not worth it.", I=0, E=1, A=-1, R=2),
            opt("Make a joke that still clears it up.", I=1, E=2, A=1, R=1),
            opt("Snap back. They should’ve known better.", I=-2, E=-2, A=2, R=-2),
        ],
    ),
    Question(
        "A friend is late again. You’re thinking…",
        [
            opt("‘We need a system. This keeps happening.’", I=2, E=0, A=2, R=1),
            opt("‘They’re dealing with something. I’ll be patient.’", I=0, E=2, A=-1, R=2),
            opt("‘I’ll roast them when they show up.’", I=0, E=1, A=1, R=0),
            opt("‘I’m done. Respect is not optional.’", I=2, E=-1, A=2, R=1),
        ],
    ),
    Question(
        "You catch yourself exaggerating a story to sound cooler.",
        [
            opt("You correct it immediately (even if it ruins the vibe).", I=3, E=0, A=0, R=2),
            opt("You leave it… but feel weird later.", I=-1, E=0, A=0, R=1),
            opt("You double down. ‘It’s entertainment.’", I=-2, E=0, A=1, R=-1),
            opt("You pivot into humor so nobody takes it as fact.", I=0, E=1, A=1, R=1),
        ],
    ),
    Question(
        "Someone gives you constructive criticism. You…",
        [
            opt("Ask for specifics and take notes.", I=2, E=1, A=2, R=2),
            opt("Smile, then ignore it forever.", I=-1, E=1, A=-2, R=1),
            opt("Defend yourself first, reflect later.", I=0, E=0, A=1, R=-1),
            opt("Take it personally and spiral.", I=-2, E=0, A=-2, R=-1),
        ],
    ),
    Question(
        "When you mess up, your default is…",
        [
            opt("Own it, fix it, move on.", I=3, E=1, A=2, R=2),
            opt("Explain it so people understand your intent.", I=1, E=1, A=0, R=1),
            opt("Hide it and hope it disappears.", I=-2, E=0, A=-2, R=2),
            opt("Blame the situation (because… come on).", I=-2, E=-1, A=1, R=-1),
        ],
    ),
    Question(
        "You’re in a group chat argument. You’re most likely to…",
        [
            opt("Try to clarify definitions and reduce heat.", I=2, E=2, A=1, R=2),
            opt("Drop one line that ends it. Then mute.", I=1, E=0, A=2, R=2),
            opt("Keep replying because you’re ‘not done.’", I=0, E=-1, A=2, R=-2),
            opt("Watch silently and judge everyone.", I=0, E=-1, A=-1, R=2),
        ],
    ),
    Question(
        "A stranger is rude to you. Your inner voice says…",
        [
            opt("‘They’re carrying something. Not mine.’", I=1, E=2, A=0, R=2),
            opt("‘I can out-class this moment.’", I=2, E=0, A=1, R=2),
            opt("‘Let’s go. We’re doing this today.’", I=-1, E=-2, A=2, R=-2),
            opt("‘I’ll get them back quietly later.’", I=-2, E=-1, A=1, R=0),
        ],
    ),
    Question(
        "You’re given authority. You tend to…",
        [
            opt("Set clear expectations and follow-through.", I=2, E=1, A=2, R=2),
            opt("Avoid conflict and let things slide.", I=-1, E=1, A=-2, R=1),
            opt("Take over everything because it’s faster.", I=0, E=-1, A=2, R=0),
            opt("Use the power to ‘teach a lesson.’", I=-2, E=-2, A=1, R=-2),
        ],
    ),
    Question(
        "You see a rule that makes no sense.",
        [
            opt("You follow it until you can change it properly.", I=2, E=0, A=1, R=2),
            opt("You break it (quietly) because it’s dumb.", I=-1, E=0, A=2, R=-1),
            opt("You ask who it protects and why it exists.", I=2, E=1, A=1, R=2),
            opt("You rant about it for 20 minutes.", I=0, E=0, A=0, R=-2),
        ],
    ),
    Question(
        "Someone you love is upset. You usually…",
        [
            opt("Listen first, then offer help.", I=1, E=3, A=0, R=2),
            opt("Try to fix the problem immediately.", I=1, E=0, A=2, R=1),
            opt("Get uncomfortable and change the subject.", I=-1, E=-1, A=-1, R=1),
            opt("Match their intensity (because fairness).", I=-1, E=-1, A=2, R=-2),
        ],
    ),
    Question(
        "You’re late. You tell people…",
        [
            opt("The truth, with the real reason.", I=3, E=0, A=0, R=2),
            opt("A lighter version that sounds better.", I=-1, E=0, A=0, R=1),
            opt("Nothing. You just show up and act normal.", I=-2, E=-1, A=-1, R=1),
            opt("A joke that admits it without begging forgiveness.", I=0, E=1, A=1, R=1),
        ],
    ),
    Question(
        "When someone succeeds, you feel…",
        [
            opt("Genuinely happy for them.", I=1, E=2, A=0, R=2),
            opt("Motivated. ‘My turn.’", I=1, E=0, A=2, R=1),
            opt("Suspicious. ‘What’s the catch?’", I=-1, E=-1, A=0, R=2),
            opt("Annoyed. ‘They don’t deserve that.’", I=-2, E=-2, A=0, R=-1),
        ],
    ),
    Question(
        "You find out you were wrong in a debate.",
        [
            opt("You say: ‘Yep. I was wrong.’", I=3, E=1, A=1, R=2),
            opt("You change the topic fast.", I=-2, E=0, A=-1, R=1),
            opt("You argue ‘technically’ you weren’t wrong.", I=-1, E=-1, A=1, R=-1),
            opt("You laugh and give the other person their win.", I=1, E=2, A=0, R=2),
        ],
    ),
    Question(
        "You’re overwhelmed. Your pattern is…",
        [
            opt("Make a list. Start with the smallest win.", I=2, E=0, A=2, R=2),
            opt("Disappear until it stops.", I=-2, E=0, A=-2, R=2),
            opt("Power through and get snappy.", I=0, E=-1, A=2, R=-2),
            opt("Ask for help even if it’s uncomfortable.", I=2, E=2, A=0, R=1),
        ],
    ),
    Question(
        "A boundary gets crossed. You…",
        [
            opt("Address it directly, calmly.", I=2, E=1, A=2, R=2),
            opt("Let it slide, then resent it later.", I=-2, E=-1, A=-1, R=1),
            opt("Go nuclear. Make sure it never happens again.", I=0, E=-2, A=2, R=-2),
            opt("Make it a joke, but the message is clear.", I=1, E=1, A=1, R=1),
        ],
    ),
    Question(
        "You promise something. You’re…",
        [
            opt("Reliable. If you said it, it’s happening.", I=3, E=0, A=2, R=2),
            opt("Optimistic… then busy… then apologetic.", I=-1, E=1, A=0, R=0),
            opt("Careful not to promise unless you’re sure.", I=2, E=0, A=1, R=2),
            opt("A wild card. Depends on how you feel.", I=-2, E=0, A=-1, R=-2),
        ],
    ),
    Question(
        "You catch someone lying. You…",
        [
            opt("Ask questions until the truth shows itself.", I=2, E=1, A=1, R=2),
            opt("Call it out immediately.", I=2, E=0, A=2, R=0),
            opt("Clock it, store it, adjust your trust.", I=2, E=0, A=0, R=2),
            opt("Lie back (because we’re playing now).", I=-3, E=-2, A=2, R=-2),
        ],
    ),
    Question(
        "A plan fails. Your first reaction is…",
        [
            opt("‘Okay—what did we learn?’", I=2, E=1, A=2, R=2),
            opt("‘Who messed this up?’", I=-2, E=-1, A=1, R=-1),
            opt("‘I should’ve done it myself.’", I=0, E=-1, A=2, R=0),
            opt("‘It was doomed anyway.’", I=-2, E=0, A=-2, R=1),
        ],
    ),
    Question(
        "You walk into a room of strangers. You tend to…",
        [
            opt("Read the room first, then engage.", I=1, E=1, A=0, R=2),
            opt("Break the ice—make it easy for everyone.", I=1, E=2, A=1, R=1),
            opt("Command attention (intentionally or not).", I=0, E=-1, A=2, R=-1),
            opt("Stay guarded until you feel safe.", I=1, E=0, A=-1, R=2),
        ],
    ),
    Question(
        "At your best, people would describe you as…",
        [
            opt("Solid. Consistent. Real.", I=3, E=0, A=1, R=2),
            opt("Warm. Easy to trust.", I=1, E=3, A=0, R=1),
            opt("Driven. Gets results.", I=1, E=0, A=3, R=0),
            opt("Unbothered. Hard to shake.", I=1, E=0, A=0, R=3),
        ],
    ),
]

ARCHETYPES = [
    {
        "name": "The Anchor",
        "tagline": "Steady, accountable, and quietly dangerous in a good way.",
        "when_healthy": "People feel safe around you because you’re consistent. You don’t need chaos to feel alive.",
        "shadow": "When stressed, you can become rigid and dismissive—like feelings are an obstacle.",
        "upgrade": "Say the truth sooner, with warmth. You’ll lose less time cleaning up misunderstandings.",
        "rule": "Consistency is charisma.",
        "signature_dims": ("Integrity", "Restraint"),
    },
    {
        "name": "The Radiator",
        "tagline": "Warm, connective, and socially magnetic.",
        "when_healthy": "You make people feel seen. You can turn tension into connection.",
        "shadow": "When stressed, you over-accommodate or people-please—then privately resent it.",
        "upgrade": "Trade hinting for clear asks. Directness will protect your generosity.",
        "rule": "Soft doesn’t mean weak.",
        "signature_dims": ("Empathy", "Integrity"),
    },
    {
        "name": "The Engine",
        "tagline": "High agency. Big momentum. You move reality.",
        "when_healthy": "You get results and pull others forward. You’re allergic to stagnation.",
        "shadow": "When stressed, you get sharp, controlling, and impatient—like everyone is in your way.",
        "upgrade": "Slow down for 10 seconds before you speak when irritated. Your influence will double.",
        "rule": "Speed is useful. Precision is power.",
        "signature_dims": ("Agency", "Integrity"),
    },
    {
        "name": "The Spark",
        "tagline": "Bold, reactive, funny, and unpredictable—in a way that makes life interesting.",
        "when_healthy": "You energize rooms and say what others won’t. You’re honest in a raw way.",
        "shadow": "When stressed, you burn bridges for sport (and call it ‘truth’).",
        "upgrade": "Aim your fire at problems, not people. You’ll keep your edge and gain trust.",
        "rule": "Your tone writes your story.",
        "signature_dims": ("Agency", "Empathy"),
    },
]

def empty_scores() -> Dict[str, int]:
    return {d: 0 for d in DIMENSIONS}

def compute_scores(answers: List[int]) -> Dict[str, int]:
    scores = empty_scores()
    for qi, oi in enumerate(answers):
        option = QUESTIONS[qi].options[oi]
        for k, v in option.delta.items():
            scores[k] += v
    return scores

def pick_archetype(scores: Dict[str, int]) -> Tuple[dict, Dict[str, int]]:
    # Normalize to 0-100-ish for display
    # Raw range roughly: [-60, +60]; shift +60 => [0,120]
    scaled = {k: max(0, min(120, v + 60)) for k, v in scores.items()}
    # Find dominant dimension pair match
    best = None
    best_score = -10**9
    for a in ARCHETYPES:
        d1, d2 = a["signature_dims"]
        s = scaled[d1] + scaled[d2]
        # small tie-breaker: total positive balance
        s += sum(scaled.values()) * 0.02
        if s > best_score:
            best_score = s
            best = a
    return best, scaled

# -----------------------------
# State
# -----------------------------
if "step" not in st.session_state:
    st.session_state.step = "curtain_1"
if "answers" not in st.session_state:
    st.session_state.answers = [-1] * len(QUESTIONS)
if "q_index" not in st.session_state:
    st.session_state.q_index = 0

def go(step: str):
    st.session_state.step = step

def reset():
    st.session_state.step = "curtain_1"
    st.session_state.answers = [-1] * len(QUESTIONS)
    st.session_state.q_index = 0

# -----------------------------
# Header
# -----------------------------
st.markdown(
    f"""
<div class="panel">
  <div class="brand">Brought to you by GiveItToGot</div>
  <div class="title">Reflection</div>
  <div class="subtitle">A question in front of a curtain. Want to see your reflection?</div>
  <div class="small">Contact: <a href="mailto:baileylloyd211@gmail.com">baileylloyd211@gmail.com</a></div>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Curtain Screens
# -----------------------------
if st.session_state.step == "curtain_1":
    st.markdown(
        """
<div class="mirrorStage">
  <div class="curtainLeft"><div class="curtainFold"></div></div>
  <div class="curtainRight"><div class="curtainFold"></div></div>
  <div class="stageInner">
    <div class="lipstick">
      <strong>Want to see your reflection?</strong><br/>
      One tap and the curtain moves.
    </div>
    <div class="mirrorGlass">
      <div class="caption">
        This is the part where most people say “yeah… obviously.”<br/>
        So—go ahead.
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Pull the curtain ▶", use_container_width=True):
            go("curtain_2")
    with c2:
        if st.button("Reset", use_container_width=True):
            reset()

elif st.session_state.step == "curtain_2":
    st.markdown(
        """
<div class="panel">
  <div class="subtitle" style="margin-bottom:8px;">
    That’s what I thought. Most people do.
  </div>
  <div class="small">
    But if I showed you what you <em>do</em>… who would be the first person you’d tell about your reflection?
  </div>
  <div class="hr"></div>
  <div class="small">
    Will your appearance matter the next time you ask to see yourself?
    Will the world be a better place now that you know who you are?
    Will you say “I’ve always known that,” or does it matter either way?
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("Show me the questions", use_container_width=True):
        go("quiz")

# -----------------------------
# Quiz UI
# -----------------------------
elif st.session_state.step == "quiz":
    qi = st.session_state.q_index
    total = len(QUESTIONS)

    # Progress
    answered = sum(1 for a in st.session_state.answers if a != -1)
    st.markdown('<div class="progressWrap"></div>', unsafe_allow_html=True)
    st.progress(answered / total)

    q = QUESTIONS[qi]
    st.markdown(
        f"""
<div class="panel">
  <div class="pill">Question {qi+1} / {total}</div>
  <div style="font-size:1.25rem; font-weight:800; margin-top:8px;">{q.prompt}</div>
  <div class="hr"></div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Current selection
    key = f"q_{qi}"
    options = [o.label for o in q.options]
    default_index = st.session_state.answers[qi] if st.session_state.answers[qi] != -1 else 0

    choice = st.radio(
        "Pick the one that’s most like you:",
        options,
        index=default_index,
        key=key,
        label_visibility="collapsed",
    )

    # Save selection
    st.session_state.answers[qi] = options.index(choice)

    # Nav buttons
    left, mid, right = st.columns([1, 1, 1])
    with left:
        if st.button("◀ Back", use_container_width=True, disabled=(qi == 0)):
            st.session_state.q_index = max(0, qi - 1)
            st.rerun()
    with mid:
        if st.button("Reset", use_container_width=True):
            reset()
            st.rerun()
    with right:
        if qi < total - 1:
            if st.button("Next ▶", use_container_width=True):
                st.session_state.q_index = min(total - 1, qi + 1)
                st.rerun()
        else:
            if st.button("Reveal my reflection 🪞", use_container_width=True):
                go("result")
                st.rerun()

# -----------------------------
# Result Screen (Mirror + Lipstick)
# -----------------------------
elif st.session_state.step == "result":
    # Ensure all answered (if user jumped around)
    if any(a == -1 for a in st.session_state.answers):
        st.warning("Finish all questions to reveal the mirror.")
    else:
        raw_scores = compute_scores(st.session_state.answers)
        archetype, scaled = pick_archetype(raw_scores)

        # Compute a spicy one-liner based on strongest/weakest dims
        best_dim = max(scaled.items(), key=lambda x: x[1])[0]
        worst_dim = min(scaled.items(), key=lambda x: x[1])[0]

        one_liners = {
            ("Integrity", "Empathy"): "You tell the truth… but you don’t have to make it hurt.",
            ("Integrity", "Agency"): "You mean well—and you move fast. Just don’t outrun your own standards.",
            ("Integrity", "Restraint"): "Your discipline is loud even when you’re quiet.",
            ("Empathy", "Integrity"): "You can read people. Don’t let that become permission to ignore yourself.",
            ("Empathy", "Agency"): "You can lead with heart—just don’t lead with guilt.",
            ("Empathy", "Restraint"): "You’re calm enough to be dangerous (in the best way).",
            ("Agency", "Integrity"): "You can build anything. Make sure you’re building the right thing.",
            ("Agency", "Empathy"): "You’re powerful. Aim that power like you respect people.",
            ("Agency", "Restraint"): "You’re the gas pedal. Learn the brakes and you’ll be unstoppable.",
            ("Restraint", "Integrity"): "You’re hard to shake. That’s rare.",
            ("Restraint", "Empathy"): "You keep your cool—now let people in a little.",
            ("Restraint", "Agency"): "You’re controlled and capable. That combination changes outcomes.",
        }
        line = one_liners.get((best_dim, worst_dim), "You’re more consistent than you think—and more readable than you want.")

        st.markdown(
            f"""
<div class="mirrorStage">
  <div class="stageInner">
    <div class="lipstick">
      Got something stuck in your teeth?<br/>
      <strong>Well… here you go.</strong>
    </div>

    <div class="mirrorGlass">
      <div class="lipstick" style="font-size:1.35rem;">
        <strong>{archetype["name"]}</strong><br/>
        {archetype["tagline"]}
      </div>
      <div class="hr"></div>
      <div class="caption" style="font-size:1.02rem;">
        {line}
      </div>
      <div class="hr"></div>
      <div class="caption"><strong>When you’re healthy:</strong> {archetype["when_healthy"]}</div>
      <div class="caption" style="margin-top:8px;"><strong>When you’re stressed:</strong> {archetype["shadow"]}</div>
      <div class="caption" style="margin-top:8px;"><strong>One upgrade:</strong> {archetype["upgrade"]}</div>
      <div class="caption" style="margin-top:8px;"><strong>Rule:</strong> {archetype["rule"]}</div>

      <div class="scoreGrid">
        <div class="metric"><div class="k">Integrity</div><div class="v">{scaled["Integrity"]}/120</div></div>
        <div class="metric"><div class="k">Empathy</div><div class="v">{scaled["Empathy"]}/120</div></div>
        <div class="metric"><div class="k">Agency</div><div class="v">{scaled["Agency"]}/120</div></div>
        <div class="metric"><div class="k">Restraint</div><div class="v">{scaled["Restraint"]}/120</div></div>
      </div>
    </div>

    <div class="footer">
      Curtains pulled back. Mirror’s honest.<br/>
      Brought to you by <strong>GiveItToGot</strong> — <a href="mailto:baileylloyd211@gmail.com">baileylloyd211@gmail.com</a>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Run it again", use_container_width=True):
                reset()
                st.rerun()
        with c2:
            if st.button("Jump to questions", use_container_width=True):
                go("quiz")
                st.rerun()
