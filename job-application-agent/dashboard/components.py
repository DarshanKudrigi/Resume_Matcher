import streamlit as st
import pandas as pd


def render_header():
    st.markdown("""
    <div class="main-header">
        <p class="main-title">🤖 Job Application Agent</p>
        <p class="main-sub">Automated scraping · LLM scoring · Smart filtering · Live tracking</p>
        <span class="badge">Playwright</span>
        <span class="badge">Groq LLM</span>
        <span class="badge">Google Sheets</span>
        <span class="badge">Streamlit</span>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar(run_callback, clear_callback):
    with st.sidebar:
        st.markdown("## 🤖 Job Agent")
        st.markdown("---")
        st.markdown("### ⚙️ Controls")

        if st.button("▶ Run Agent Now", use_container_width=True, type="primary"):
            with st.spinner("🔍 Running pipeline..."):
                run_callback()
            st.success("✅ Done!")
            st.rerun()

        if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
            clear_callback()
            st.success("Sheet cleared!")
            st.rerun()

        st.markdown("---")
        st.markdown("### 🎯 Search Settings")
        st.markdown("""
        **Keywords:** AI Engineer, ML Engineer
        **Location:** Bengaluru
        **Min Score:** 65%
        **Auto-apply:** 85%+
        """)

        st.markdown("---")
        st.markdown("### 📊 Pipeline Steps")
        st.markdown("""
        1. 🌐 Scrape LinkedIn
        2. 🧠 Score with LLM
        3. 📋 Log to Sheets
        """)


def render_metrics(df: pd.DataFrame):
    total     = len(df)
    apply_cnt = len(df[df["Recommendation"] == "apply"])
    maybe_cnt = len(df[df["Recommendation"] == "maybe"])
    avg_score = df["Score_num"].mean()
    top_score = df["Score_num"].max()

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("📋 Total Tracked", total)
    m2.metric("✅ Apply",         apply_cnt)
    m3.metric("🤔 Maybe",         maybe_cnt)
    m4.metric("📈 Avg Score",     f"{avg_score:.0f}%")
    m5.metric("🏆 Top Score",     f"{top_score:.0f}%")


def render_charts(df: pd.DataFrame):
    col_chart, col_rec = st.columns([2, 1])

    with col_chart:
        st.markdown('<p class="section-title">📊 Score Distribution</p>',
                    unsafe_allow_html=True)
        bins = {"50–60%": 0, "60–70%": 0, "70–80%": 0,
                "80–90%": 0, "90–100%": 0}
        for s in df["Score_num"]:
            if s < 60:   bins["50–60%"]   += 1
            elif s < 70: bins["60–70%"]   += 1
            elif s < 80: bins["70–80%"]   += 1
            elif s < 90: bins["80–90%"]   += 1
            else:        bins["90–100%"]  += 1
        chart_df = pd.DataFrame({"Range": bins.keys(), "Count": bins.values()})
        st.bar_chart(chart_df.set_index("Range"))

    with col_rec:
        st.markdown('<p class="section-title">🎯 Recommendations</p>',
                    unsafe_allow_html=True)
        total = len(df)
        for rec, count in df["Recommendation"].value_counts().items():
            color = ("#4caf82" if rec == "apply"
                     else "#f0a500" if rec == "maybe"
                     else "#e05c5c")
            pct = count / total * 100
            st.markdown(f"""
            <div style="margin-bottom:12px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="color:{color};font-weight:600;
                          text-transform:uppercase;font-size:0.85rem;">{rec}</span>
                    <span style="color:#9098b1;">{count} jobs ({pct:.0f}%)</span>
                </div>
                <div style="background:#2d2f3e;border-radius:4px;height:8px;">
                    <div style="background:{color};width:{pct}%;
                         height:8px;border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_job_table(df: pd.DataFrame):
    st.markdown('<p class="section-title">💼 Job Pipeline</p>',
                unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        rec_filter = st.multiselect(
            "Recommendation",
            options=["apply", "maybe", "skip"],
            default=["apply", "maybe"]
        )
    with f2:
        status_filter = st.multiselect(
            "Status",
            options=df["Status"].unique().tolist(),
            default=df["Status"].unique().tolist()
        )
    with f3:
        min_score = st.slider("Min score", 0, 100, 65, step=5)

    filtered = df[
        df["Recommendation"].isin(rec_filter) &
        df["Status"].isin(status_filter) &
        (df["Score_num"] >= min_score)
    ].sort_values("Score_num", ascending=False)

    st.dataframe(
        filtered[[
            "Title", "Company", "Location",
            "Match Score", "Recommendation",
            "Matched Skills", "Missing Skills",
            "Status", "URL"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL":            st.column_config.LinkColumn("URL"),
            "Match Score":    st.column_config.TextColumn("Score"),
            "Matched Skills": st.column_config.TextColumn("✅ Matched"),
            "Missing Skills": st.column_config.TextColumn("❌ Missing"),
        },
        height=450
    )
    st.caption(f"Showing {len(filtered)} of {len(df)} jobs · sorted by score")

def render_status_updater(df: pd.DataFrame):
    st.markdown('<p class="section-title">✏️ Update Job Status</p>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1e2130;border:1px solid #3d4060;
                border-radius:12px;padding:1.2rem;margin-bottom:1rem;">
        <p style="color:#9098b1;font-size:0.85rem;margin:0 0 1rem 0;">
            Select a job and update its status in your Google Sheet
        </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        job_options = {
            f"{row['Title']} at {row['Company']}": row['ID']
            for _, row in df.iterrows()
        }
        selected_label = st.selectbox(
            "Select a job",
            options=list(job_options.keys())
        )

    with col2:
        new_status = st.selectbox(
            "New status",
            options=["new", "applied", "interview", "offer", "rejected"],
            format_func=lambda x: {
                "new": "🆕 New",
                "applied": "📨 Applied",
                "interview": "🎤 Interview",
                "offer": "🎉 Offer",
                "rejected": "❌ Rejected"
            }.get(x, x)
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        update_clicked = st.button(
            "Update ✓",
            use_container_width=True,
            type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if update_clicked and selected_label:
        from tracker.sheets_tracker import update_job_status
        job_id = job_options[selected_label]
        update_job_status(job_id, new_status.split(" ")[-1] if " " in new_status else new_status)
        st.success(f"✅ **{selected_label.split(' at ')[0]}** updated to **{new_status}**")
        st.rerun()