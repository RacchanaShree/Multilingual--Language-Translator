import streamlit as st
from googletrans import LANGUAGES
from main import TranslationService
from datetime import datetime

st.set_page_config(page_title="Language Translator", layout="wide")
# translator = Translator()
service = TranslationService()

# ---------------- SESSION STATE ----------------
defaults = {
    "source_lang": "auto",
    "target_lang": "en",
    "input_text": "",
    "output_text": "",
    "history": [],
    "last_detected_src": None,
    "user_edited_input": False,
    "last_run_input": "",
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- CALLBACK ----------------
def on_input_change():
    st.session_state.user_edited_input = True
    st.session_state.source_lang = "auto"
    st.session_state.last_detected_src = None



# ---------------- FUNCTIONS ----------------
def translate_text():
    text = st.session_state.input_text.strip()
    if not text:
        return

    # Detect if user changed input manually since last run
    if text != st.session_state.last_run_input:
        st.session_state.source_lang = "auto"
        # We also need to ensure the translator uses 'auto' this run
        detected_src_arg = "auto"
    else:
        detected_src_arg = st.session_state.source_lang

    try:

        # Use new service
        res = service.translate(
            text,
            target_language=st.session_state.target_lang,
            source_language=detected_src_arg
        )

        translated_text = res["translated_text"]
        detected_src_code = res["detected_source_language"]

        st.session_state.output_text = translated_text
        st.session_state.last_detected_src = detected_src_code
        st.session_state.user_edited_input = False
        st.session_state.last_run_input = text

        st.session_state.history.insert(0, {
            "time": datetime.now().strftime("%H:%M:%S"),
            "src": LANGUAGES.get(detected_src_code, detected_src_code),
            "dest": LANGUAGES.get(st.session_state.target_lang),
            "input": text,
            "output": translated_text
        })

    except Exception as e:
        st.error(f"Translation failed: {e}")
        st.session_state.output_text = ""


def swap_languages():
    src = st.session_state.source_lang
    tgt = st.session_state.target_lang

    if src == "auto":
        real_src = st.session_state.last_detected_src or tgt
    else:
        real_src = src

    st.session_state.source_lang = tgt
    st.session_state.target_lang = real_src

    st.session_state.input_text = st.session_state.output_text
    st.session_state.output_text = ""
    # Sync last_run_input so we don't trigger "auto" revert immediately
    st.session_state.last_run_input = st.session_state.input_text

    st.session_state.last_detected_src = None
    st.session_state.user_edited_input = False  # CRITICAL


# ---------------- UI ----------------
st.title("🌍 Language Translator")

col1, col2, col3 = st.columns([4, 1, 4])

with col1:
    st.selectbox(
        "Source language",
        options=["auto"] + list(LANGUAGES.keys()),
        format_func=lambda x: "Auto Detect" if x == "auto" else LANGUAGES[x],
        key="source_lang"
    )

with col2:
    st.write("")
    st.write("")
    st.button("🔁 Swap", on_click=swap_languages)

with col3:
    st.selectbox(
        "Target language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key="target_lang"
    )

st.text_area(
    "Input text",
    height=150,
    key="input_text",
    on_change=on_input_change
)

st.button("Translate", on_click=translate_text)

st.text_area(
    "Output text",
    height=150,
    key="output_text"
)

# ---------------- HISTORY ----------------
st.divider()
st.subheader("📜 Translation History")

for h in st.session_state.history[:5]:
    st.markdown(
        f"""
        **{h['time']}**  
        {h['src']} → {h['dest']}  
        Input: `{h['input']}`  
        Output: `{h['output']}`
        """
    )