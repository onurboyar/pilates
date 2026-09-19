import random
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Japanese Anatomy Cards",
    page_icon="🫀",
    layout="centered",
)


# ============================================================
# CSV SETTINGS
# ============================================================

CSV_PATH = (
    Path(__file__).parent
    / "japanese_anatomy_candidates_enriched_vi.csv"
)


# ============================================================
# LOAD CSV
# ============================================================

@st.cache_data
def load_cards():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Could not find CSV file:\n{CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    required_columns = [
        "word",
        "reading",
        "english_meaning",
        "vietnamese_meaning",
        "vietnamese_explanation",
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing)
        )

    # Replace NaN values with empty strings
    df = df.fillna("")

    # Clean text columns
    text_columns = [
        "word",
        "reading",
        "english_meaning",
        "vietnamese_meaning",
        "vietnamese_explanation",
        "source",
        "notes",
    ]

    for col in text_columns:

        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
            )

    # Remove empty rows
    df = df[
        df["word"] != ""
    ].copy()

    df = df.reset_index(drop=True)

    # Internal card ID
    df["card_id"] = range(len(df))

    return df


try:

    df = load_cards()

except Exception as e:

    st.error(str(e))
    st.stop()


CARDS = df.to_dict("records")


# ============================================================
# SESSION STATE
# ============================================================

if "order" not in st.session_state:

    st.session_state.order = list(
        range(len(CARDS))
    )

    random.shuffle(
        st.session_state.order
    )


if "position" not in st.session_state:
    st.session_state.position = 0


if "show_answer" not in st.session_state:
    st.session_state.show_answer = False


if "learned" not in st.session_state:
    st.session_state.learned = set()


if "again_count" not in st.session_state:
    st.session_state.again_count = 0


if "hard_count" not in st.session_state:
    st.session_state.hard_count = 0


if "good_count" not in st.session_state:
    st.session_state.good_count = 0


if "easy_count" not in st.session_state:
    st.session_state.easy_count = 0


if "total_reviews" not in st.session_state:
    st.session_state.total_reviews = 0


# ============================================================
# FUNCTIONS
# ============================================================

def reset_progress():

    st.session_state.order = list(
        range(len(CARDS))
    )

    random.shuffle(
        st.session_state.order
    )

    st.session_state.position = 0

    st.session_state.show_answer = False

    st.session_state.learned = set()

    st.session_state.again_count = 0
    st.session_state.hard_count = 0
    st.session_state.good_count = 0
    st.session_state.easy_count = 0

    st.session_state.total_reviews = 0


def next_card(active_ids):

    if not active_ids:
        return

    st.session_state.position += 1

    if st.session_state.position >= len(active_ids):
        st.session_state.position = 0

    st.session_state.show_answer = False


def previous_card(active_ids):

    if not active_ids:
        return

    st.session_state.position -= 1

    if st.session_state.position < 0:
        st.session_state.position = len(active_ids) - 1

    st.session_state.show_answer = False


def rate_card(
    rating,
    current_id,
    active_ids,
):

    st.session_state.total_reviews += 1

    if rating == "Again":

        st.session_state.again_count += 1

        st.session_state.learned.discard(
            current_id
        )

    elif rating == "Hard":

        st.session_state.hard_count += 1

    elif rating == "Good":

        st.session_state.good_count += 1

        st.session_state.learned.add(
            current_id
        )

    elif rating == "Easy":

        st.session_state.easy_count += 1

        st.session_state.learned.add(
            current_id
        )

    next_card(active_ids)


# ============================================================
# HEADER
# ============================================================

st.title("🫀 Japanese Anatomy Cards")

st.write(
    "Learn Japanese anatomy vocabulary "
    "with English and Vietnamese explanations."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Study settings")


# ============================================================
# SOURCE FILTER
# ============================================================

if "source" in df.columns:

    available_sources = sorted(
        [
            x
            for x in df["source"].unique()
            if x != ""
        ]
    )

else:

    available_sources = []


if available_sources:

    selected_sources = (
        st.sidebar.multiselect(
            "Source documents",
            options=available_sources,
            default=available_sources,
        )
    )

else:

    selected_sources = []


# ============================================================
# DISPLAY SETTINGS
# ============================================================

show_reading = st.sidebar.toggle(
    "Show reading",
    value=True,
)

show_english = st.sidebar.toggle(
    "Show English",
    value=True,
)

show_vietnamese = st.sidebar.toggle(
    "Show Vietnamese",
    value=True,
)

show_source = st.sidebar.toggle(
    "Show source",
    value=False,
)

show_notes = st.sidebar.toggle(
    "Show notes",
    value=True,
)


st.sidebar.divider()


# ============================================================
# ACTIVE DECK
# ============================================================

active_ids = []


for card_id in st.session_state.order:

    card = CARDS[card_id]

    if available_sources:

        if (
            card.get("source", "")
            not in selected_sources
        ):
            continue

    active_ids.append(
        card_id
    )


if not active_ids:

    st.warning(
        "No cards match the selected filters."
    )

    st.stop()


if (
    st.session_state.position
    >= len(active_ids)
):

    st.session_state.position = 0


current_id = active_ids[
    st.session_state.position
]

card = CARDS[current_id]


# ============================================================
# SIDEBAR PROGRESS
# ============================================================

learned_active = len(
    [
        card_id
        for card_id in active_ids
        if card_id in st.session_state.learned
    ]
)


st.sidebar.subheader(
    "Progress"
)


st.sidebar.metric(
    "Cards",
    len(active_ids),
)


st.sidebar.metric(
    "Reviews",
    st.session_state.total_reviews,
)


st.sidebar.metric(
    "Learned",
    learned_active,
)


progress = (
    learned_active
    / len(active_ids)
)


st.sidebar.progress(
    progress
)


st.sidebar.caption(
    f"{learned_active} / "
    f"{len(active_ids)} learned"
)


st.sidebar.divider()


if st.sidebar.button(
    "🔀 Shuffle cards",
    use_container_width=True,
):

    random.shuffle(
        st.session_state.order
    )

    st.session_state.position = 0

    st.session_state.show_answer = False

    st.rerun()


if st.sidebar.button(
    "♻️ Reset progress",
    use_container_width=True,
):

    reset_progress()

    st.rerun()


# ============================================================
# CARD PROGRESS
# ============================================================

st.progress(
    (
        st.session_state.position + 1
    )
    / len(active_ids)
)


st.caption(
    f"Card "
    f"{st.session_state.position + 1} "
    f"of {len(active_ids)}"
)


# ============================================================
# FLASHCARD
# ============================================================

with st.container(
    border=True
):

    # ========================================================
    # FRONT
    # ========================================================

    if not st.session_state.show_answer:

        st.header(
            card["word"]
        )

        st.write("")

        st.write(
            "**What does this mean?**"
        )

        st.write("")

        if st.button(
            "👀 Show answer",
            type="primary",
            use_container_width=True,
        ):

            st.session_state.show_answer = True

            st.rerun()


    # ========================================================
    # BACK
    # ========================================================

    else:

        st.header(
            card["word"]
        )


        # ----------------------------------------------------
        # JAPANESE READING
        # ----------------------------------------------------

        if (
            show_reading
            and card.get("reading", "")
        ):

            st.subheader(
                card["reading"]
            )


        # ----------------------------------------------------
        # ENGLISH
        # ----------------------------------------------------

        if show_english:

            st.divider()

            st.subheader(
                "🇬🇧 English"
            )

            if card.get(
                "english_meaning",
                ""
            ):

                st.write(
                    card[
                        "english_meaning"
                    ]
                )

            else:

                st.caption(
                    "No English meaning available."
                )


        # ----------------------------------------------------
        # VIETNAMESE
        # ----------------------------------------------------

        if show_vietnamese:

            st.divider()

            st.subheader(
                "🇻🇳 Tiếng Việt"
            )

            vietnamese_meaning = (
                card.get(
                    "vietnamese_meaning",
                    ""
                )
            )

            vietnamese_explanation = (
                card.get(
                    "vietnamese_explanation",
                    ""
                )
            )


            if vietnamese_meaning:

                st.markdown(
                    f"### {vietnamese_meaning}"
                )


            if vietnamese_explanation:

                st.write(
                    vietnamese_explanation
                )


            if (
                not vietnamese_meaning
                and not vietnamese_explanation
            ):

                st.caption(
                    "Không có giải thích tiếng Việt."
                )


        # ----------------------------------------------------
        # NOTES
        # ----------------------------------------------------

        if (
            show_notes
            and card.get("notes", "")
        ):

            st.divider()

            st.subheader(
                "📝 Notes"
            )

            st.write(
                card["notes"]
            )


        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        if show_source:

            source = card.get(
                "source",
                ""
            )

            page = card.get(
                "page",
                ""
            )


            if source:

                st.divider()

                st.caption(
                    f"Source: {source}"
                )


                if str(page).strip():

                    st.caption(
                        f"Page: {page}"
                    )


# ============================================================
# RATING BUTTONS
# ============================================================

if st.session_state.show_answer:

    st.write("")

    st.write(
        "### How well did you remember it?"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        if st.button(
            "🔴 Again",
            use_container_width=True,
        ):

            rate_card(
                "Again",
                current_id,
                active_ids,
            )

            st.rerun()


    with col2:

        if st.button(
            "🟠 Hard",
            use_container_width=True,
        ):

            rate_card(
                "Hard",
                current_id,
                active_ids,
            )

            st.rerun()


    with col3:

        if st.button(
            "🟢 Good",
            use_container_width=True,
        ):

            rate_card(
                "Good",
                current_id,
                active_ids,
            )

            st.rerun()


    with col4:

        if st.button(
            "🔵 Easy",
            use_container_width=True,
        ):

            rate_card(
                "Easy",
                current_id,
                active_ids,
            )

            st.rerun()


# ============================================================
# NAVIGATION
# ============================================================

st.write("")
st.divider()


nav1, nav2, nav3 = (
    st.columns(3)
)


with nav1:

    if st.button(
        "⬅ Previous",
        use_container_width=True,
    ):

        previous_card(
            active_ids
        )

        st.rerun()


with nav2:

    if st.button(
        "🎲 Random",
        use_container_width=True,
    ):

        st.session_state.position = (
            random.randrange(
                len(active_ids)
            )
        )

        st.session_state.show_answer = False

        st.rerun()


with nav3:

    if st.button(
        "Next ➡",
        use_container_width=True,
    ):

        next_card(
            active_ids
        )

        st.rerun()


# ============================================================
# STUDY STATISTICS
# ============================================================

with st.expander(
    "📊 Study statistics"
):

    stat1, stat2, stat3, stat4 = (
        st.columns(4)
    )


    stat1.metric(
        "Again",
        st.session_state.again_count,
    )


    stat2.metric(
        "Hard",
        st.session_state.hard_count,
    )


    stat3.metric(
        "Good",
        st.session_state.good_count,
    )


    stat4.metric(
        "Easy",
        st.session_state.easy_count,
    )


    if (
        st.session_state.total_reviews
        > 0
    ):

        remembered = (
            st.session_state.good_count
            + st.session_state.easy_count
        )

        success_rate = (
            remembered
            / st.session_state.total_reviews
            * 100
        )


        st.write(
            "Remembered correctly: "
            f"**{success_rate:.1f}%**"
        )


# ============================================================
# VOCABULARY BROWSER
# ============================================================

with st.expander(
    "📚 Browse vocabulary"
):

    search = st.text_input(
        "Search Japanese, reading, English, Vietnamese, or notes"
    )


    search = (
        search
        .strip()
        .lower()
    )


    results = []


    for item in CARDS:

        searchable = " ".join(
            [
                str(
                    item.get(
                        "word",
                        ""
                    )
                ),
                str(
                    item.get(
                        "reading",
                        ""
                    )
                ),
                str(
                    item.get(
                        "english_meaning",
                        ""
                    )
                ),
                str(
                    item.get(
                        "vietnamese_meaning",
                        ""
                    )
                ),
                str(
                    item.get(
                        "vietnamese_explanation",
                        ""
                    )
                ),
                str(
                    item.get(
                        "notes",
                        ""
                    )
                ),
            ]
        ).lower()


        if (
            search == ""
            or search in searchable
        ):

            results.append(
                item
            )


    st.write(
        f"Found **{len(results)}** words."
    )


    for item in results:

        learned = (
            item["card_id"]
            in st.session_state.learned
        )


        symbol = (
            "✅"
            if learned
            else "⬜"
        )


        with st.container(
            border=True
        ):

            st.subheader(
                f"{symbol} "
                f"{item['word']}"
            )


            # Japanese reading
            if item.get(
                "reading",
                ""
            ):

                st.write(
                    f"**Reading:** "
                    f"{item['reading']}"
                )


            # English
            if item.get(
                "english_meaning",
                ""
            ):

                st.write(
                    "🇬🇧 "
                    f"**{item['english_meaning']}**"
                )


            # Vietnamese meaning
            if item.get(
                "vietnamese_meaning",
                ""
            ):

                st.write(
                    "🇻🇳 "
                    f"**{item['vietnamese_meaning']}**"
                )


            # Vietnamese explanation
            if item.get(
                "vietnamese_explanation",
                ""
            ):

                st.write(
                    item[
                        "vietnamese_explanation"
                    ]
                )


            # Notes
            if item.get(
                "notes",
                ""
            ):

                st.caption(
                    f"Note: "
                    f"{item['notes']}"
                )


            # Source
            source = item.get(
                "source",
                ""
            )

            page = item.get(
                "page",
                ""
            )


            if source:

                source_text = (
                    f"Source: {source}"
                )


                if str(page).strip():

                    source_text += (
                        f" — page {page}"
                    )


                st.caption(
                    source_text
                )
