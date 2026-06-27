import streamlit as st
import time
from api_client import APIClient
import requests
from streamlit_lottie import st_lottie

# Page configuration MUST be the first Streamlit command
st.set_page_config(
    page_title="Goal Planner AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    """Loads custom CSS to enforce the premium aesthetic."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load CSS: {e}")

# Load custom CSS
load_css("frontend/style.css")

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_brain = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_V9t630.json")

# --- Goal Templates ---
GOAL_TEMPLATES = [
    {"title": "Run a Marathon", "category": "Fitness", "description": "Complete a full 42km marathon within 6 months, starting from a beginner level."},
    {"title": "Launch a SaaS Product", "category": "Business", "description": "Build and launch a software-as-a-service product with paying customers within 90 days."},
    {"title": "Learn Python Programming", "category": "Education", "description": "Go from zero to being able to build real projects in Python within 3 months."},
    {"title": "Save $10,000", "category": "Finance", "description": "Save $10,000 in an emergency fund over the next 12 months by cutting expenses and increasing income."},
    {"title": "Get Promoted at Work", "category": "Career", "description": "Earn a promotion to the next level within my company over the next 6 months."},
    {"title": "Write and Publish a Book", "category": "Personal Development", "description": "Write, edit, and self-publish a non-fiction book on my area of expertise within 4 months."},
    {"title": "Lose 15kg", "category": "Fitness", "description": "Lose 15kg of body fat through diet and exercise over the next 4 months in a sustainable way."},
    {"title": "Start a YouTube Channel", "category": "Business", "description": "Grow a YouTube channel to 1,000 subscribers within 6 months by posting weekly videos."},
]

# --- Initialize Session State ---
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = None
if 'is_generating' not in st.session_state:
    st.session_state.is_generating = False
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = False

# --- Sidebar (History & Navigation) ---
with st.sidebar:
    st.title("🎯 Goal Planner AI")
    page = st.radio("Navigation", ["Goal Planner", "System Dashboard"])
    st.markdown("---")
    
    st.subheader("📚 History")
    try:
        history = APIClient.get_history()
        if not history:
            st.info("No past goals found.")
        else:
            # Clear All button
            if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
                for item in history:
                    try:
                        APIClient.delete_goal(item['id'])
                    except Exception:
                        pass
                st.session_state.current_plan = None
                st.rerun()

            for item in history:
                short_title = item['title'][:22] + "..." if len(item['title']) > 22 else item['title']
                with st.expander(f"📌 {short_title}"):
                    st.write(f"**Category:** {item['category']}")
                    st.caption(f"Created: {item['created_at'][:10]}")
                    if st.button("🗑️ Delete", key=f"del_{item['id']}", use_container_width=True):
                        try:
                            APIClient.delete_goal(item['id'])
                            # Clear current plan if it was the deleted goal
                            if st.session_state.current_plan and st.session_state.current_plan.get('goal_id') == item['id']:
                                st.session_state.current_plan = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not delete: {e}")
    except Exception as e:
        st.error("Could not fetch history.")

        
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.8rem;'>Powered by MLOps & LLMOps</div>", unsafe_allow_html=True)

if page == "Goal Planner":
    # --- Main Layout ---
    st.title("Build Your Dream Goal")
    st.markdown("Define what you want to achieve, and our AI will engineer a personalized Brian Tracy 12-step plan.")

    # Form Layout
    col1, col2 = st.columns([2, 1])

    
    with col1:
        with st.container():
            st.markdown("### 📝 Goal Details")
            goal_title = st.text_input("What is your goal?", placeholder="e.g. Run a marathon, Launch a SaaS, Learn to play piano")
            goal_desc = st.text_area("Describe it in more detail (optional)", placeholder="Provide context to help the AI craft a better plan...")
            
            category = st.selectbox("Category", ["Fitness", "Career", "Business", "Education", "Finance", "Personal Development", "Other"])
            
            if st.button("✨ Generate AI Plan", use_container_width=True):
                if not goal_title:
                    st.error("Please provide a Goal Title!")
                else:
                    st.session_state.is_generating = True
                    st.session_state.feedback_submitted = False
                    
    with col2:
        st.markdown("### 💡 Tips for Success")
        st.info("**Be specific.** 'Lose weight' is okay, but 'Lose 10kg by running 3 times a week' yields much better AI plans.")
        st.success("**Use context.** The description field helps the AI understand your current situation and constraints.")
        st.markdown("---")
        st.markdown("### 🌐 AI Grounding")
        use_rag = st.toggle("🔍 Enable Web Search (RAG)", value=False, help="When enabled, the AI will search the web for up-to-date context before generating your plan. This makes the plan richer but slightly slower.")
        if use_rag:
            st.info("Web Search enabled! The AI will browse the internet for relevant resources before creating your plan.")
    
    st.markdown("---")
    
    # --- Plan Generation Logic ---
    if st.session_state.is_generating:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if lottie_brain:
            st_lottie(lottie_brain, height=150, key="loading")
        else:
            st.spinner("🧠 Orchestrating ML Prediction and LLM Generation...")
        st.markdown("<h4 style='text-align: center;'>🧠 Orchestrating ML Prediction and LLM Generation...</h4></div>", unsafe_allow_html=True)
        try:
            # Simulate a slight delay for dramatic effect
            time.sleep(1) 
            plan_response = APIClient.generate_goal_plan(
                title=goal_title,
                description=goal_desc,
                category=category,
                use_rag=use_rag
            )
            st.session_state.current_plan = plan_response
            st.session_state.is_generating = False
            st.rerun()
        except Exception as e:
            st.error(f"Failed to generate plan. Ensure Backend is running. Error: {e}")
            st.session_state.is_generating = False
    
    # --- Display Plan ---
    if st.session_state.current_plan:
        plan_data = st.session_state.current_plan
        meta = plan_data.get("metadata", {})
        
        st.markdown("## 🗺️ Your Customized Plan")
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        
        # Difficulty Badge Logic
        diff = meta.get('difficulty', 'Unknown')
        badge_class = "badge-medium"
        if diff == "Easy": badge_class = "badge-easy"
        if diff == "Hard": badge_class = "badge-hard"
        
        with m1:
            st.markdown(f"**Predicted Difficulty:** <span class='{badge_class}'>{diff}</span>", unsafe_allow_html=True)
        with m2:
            st.metric("Estimated Success", f"{meta.get('estimated_success_probability', 0):.1f}%")
        with m3:
            st.metric("Estimated Days", f"{meta.get('estimated_completion_time_days', 0)} days")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- Export to Markdown & ICS ---
        def generate_markdown(plan):
            md = f"# Goal: {goal_title}\n\n"
            md += f"**Predicted Difficulty:** {meta.get('difficulty', 'Unknown')}\n"
            md += f"**Estimated Success:** {meta.get('estimated_success_probability', 0):.1f}%\n"
            md += f"**Estimated Days:** {meta.get('estimated_completion_time_days', 0)}\n\n"
            md += "## 12-Step Plan\n"
            for s in plan.get("plan_data", {}).get("steps", []):
                status = "[x]" if s.get('is_completed') else "[ ]"
                md += f"- {status} **Step {s.get('step_number')}: {s.get('title')}**\n  - {s.get('action')}\n"
            return md

        def generate_ics(plan):
            import datetime
            now = datetime.datetime.now()
            ics_lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Goal Planner AI//EN"
            ]
            for s in plan.get("plan_data", {}).get("steps", []):
                dtstart = (now + datetime.timedelta(days=s.get('step_number')*7)).strftime("%Y%m%dT%H%M%SZ")
                dtend = (now + datetime.timedelta(days=s.get('step_number')*7, hours=1)).strftime("%Y%m%dT%H%M%SZ")
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:goal_{plan_data.get('goal_id')}_step_{s.get('step_number')}@goalplanner",
                    f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART:{dtstart}",
                    f"DTEND:{dtend}",
                    f"SUMMARY:Step {s.get('step_number')}: {s.get('title')}",
                    f"DESCRIPTION:{s.get('action')}",
                    "END:VEVENT"
                ])
            ics_lines.append("END:VCALENDAR")
            return "\r\n".join(ics_lines)

        d1, d2 = st.columns([1, 1])
        with d1:
            st.download_button(
                label="📄 Download Plan as Markdown",
                data=generate_markdown(plan_data),
                file_name=f"goal_plan_{plan_data.get('goal_id')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with d2:
            st.download_button(
                label="📅 Export Plan to Calendar (.ics)",
                data=generate_ics(plan_data),
                file_name=f"goal_plan_{plan_data.get('goal_id')}.ics",
                mime="text/calendar",
                use_container_width=True
            )
        
        # Steps Timeline
        steps = plan_data.get("plan_data", {}).get("steps", [])
        
        # Calculate Progress
        completed_count = sum(1 for step in steps if step.get('is_completed', False))
        total_steps = len(steps) if steps else 1
        progress = completed_count / total_steps
        
        st.markdown(f"**Progress:** {completed_count}/{len(steps)} Steps Completed")
        st.progress(progress)

        # 🏆 Completion Certificate
        if completed_count == len(steps) and len(steps) > 0:
            st.balloons()
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1e3a5f, #0f2027); border: 2px solid #f59e0b;
                        border-radius: 16px; padding: 40px; text-align: center; margin: 20px 0;">
                <div style="font-size: 3rem;">🏆</div>
                <h2 style="color: #f59e0b; margin: 8px 0;">Goal Achieved!</h2>
                <p style="color: #e2e8f0; font-size: 1.1rem;">You have completed all 12 steps of your Brian Tracy Goal Plan.</p>
                <h3 style="color: #ffffff; margin: 16px 0;">"{goal_title}"</h3>
                <p style="color: #94a3b8; font-size: 0.9rem;">Completed on {time.strftime('%B %d, %Y')}</p>
                <div style="margin-top: 16px; font-size: 0.85rem; color: #64748b; font-style: italic;">
                    "Success is not an accident. Success is the result of hard work, learning, studying,
                    sacrifice, and most of all, love of what you are doing." — Brian Tracy
                </div>
            </div>
            """, unsafe_allow_html=True)

            cert_text = f"""GOAL ACHIEVEMENT CERTIFICATE

Congratulations!

This certifies that all 12 steps of the Brian Tracy Goal Plan
have been successfully completed for the goal:

  "{goal_title}"

Completed: {time.strftime('%B %d, %Y')}

Brian Tracy 12-Step Methodology
Generated by Goal Planner AI
"""
            st.download_button(
                "📜 Download Certificate",
                data=cert_text,
                file_name=f"certificate_{plan_data.get('goal_id')}.txt",
                mime="text/plain"
            )

        for idx, step in enumerate(steps):
            is_checked = step.get('is_completed', False)
            
            # Use columns to put a checkbox next to the card
            c1, c2 = st.columns([0.05, 0.95])
            with c1:
                # Give a unique key
                checked = st.checkbox("", value=is_checked, key=f"step_{step.get('step_number')}_{plan_data.get('goal_id')}")
                if checked != is_checked:
                    # Update state
                    steps[idx]['is_completed'] = checked
                    # Save to DB
                    APIClient.update_goal_plan(plan_data.get('goal_id'), {"steps": steps})
                    st.rerun()
                    
            with c2:
                card_class = "step-card-completed" if is_checked else "step-card"
                opacity = "0.6" if is_checked else "1.0"
                st.markdown(f"""
                <div class="step-card" style="opacity: {opacity}; border-left: 4px solid {'#10b981' if is_checked else '#3b82f6'};">
                    <div class="step-number">Step {step.get('step_number')}</div>
                    <div class="step-title" style="text-decoration: {'line-through' if is_checked else 'none'};">{step.get('title')}</div>
                    <div class="step-action">{step.get('action')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("🤖 Ask AI about this step"):
                    q_key = f"q_{step.get('step_number')}_{plan_data.get('goal_id')}"
                    user_q = st.text_input("Need help? Ask the AI a question:", key=q_key)
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if st.button("Ask", key=f"btn_{q_key}"):
                            if user_q:
                                with st.spinner("AI is thinking..."):
                                    try:
                                        ans = APIClient.ask_ai(step.get('title'), step.get('action'), user_q)
                                        st.info(ans)
                                    except Exception as e:
                                        st.error(f"Failed to ask AI: {e}")
                            else:
                                st.warning("Please enter a question first.")
                    with btn_col2:
                        if st.button("⚠️ I failed this step — Replan", key=f"replan_{q_key}", type="secondary"):
                            with st.spinner("🔄 AI is re-engineering your plan..."):
                                try:
                                    all_steps = plan_data.get("plan_data", {}).get("steps", [])
                                    new_plan = APIClient.replan_goal(
                                        goal_id=plan_data.get('goal_id'),
                                        failed_step_number=step.get('step_number'),
                                        all_steps=all_steps
                                    )
                                    st.session_state.current_plan['plan_data'] = new_plan['plan_data']
                                    st.success("✅ Plan has been re-engineered based on your setback!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Replan failed: {e}")
            
        # --- Feedback Section ---
        st.markdown("---")
        st.markdown("### 🗣️ Help Us Improve")
        
        if st.session_state.feedback_submitted:
            st.success("Thank you for your feedback! It has been logged for future model fine-tuning.")
        else:
            f_col1, f_col2 = st.columns([1, 2])
            with f_col1:
                rating = st.selectbox("Rate this plan (1-5 Stars)", [5, 4, 3, 2, 1], index=0)
            with f_col2:
                comments = st.text_input("Any specific comments? (Optional)")
                
            if st.button("Submit Feedback"):
                try:
                    APIClient.submit_feedback(
                        goal_plan_id=plan_data.get('goal_id'), # Assuming goal_id == plan_id for this architecture
                        rating=rating,
                        comments=comments
                    )
                    st.session_state.feedback_submitted = True
                    st.rerun()
                except Exception as e:
                    st.error("Failed to submit feedback.")

elif page == "System Dashboard":
    st.title("📊 System Dashboard")
    st.markdown("Real-time MLOps and LLMOps metrics — live from the backend database.")

    try:
        metrics = APIClient.get_dashboard_metrics()
        history = APIClient.get_metrics_history()

        st.markdown("### 🚦 API & Reliability")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total API Requests", metrics["total_requests"])
        m2.metric("Error Rate", f"{metrics['error_rate']*100:.2f}%")
        m3.metric("Total Alerts Triggered", metrics["total_alerts"])

        st.markdown("---")
        st.markdown("### 🤖 ML & LLM Performance")
        m4, m5, m6 = st.columns(3)
        m4.metric("LLM Latency (avg)", f"{metrics['avg_llm_latency_ms']:.0f} ms")
        m5.metric("Total Tokens Processed", metrics["total_tokens_used"])
        m6.metric("Model Accuracy (Rolling)", f"{metrics['latest_model_accuracy']*100:.1f}%")

        # --- Charts ---
        st.markdown("---")
        st.markdown("### 📈 Live Time-Series Charts")

        llm_history = history.get("llm_history", [])
        drift_history = history.get("drift_history", [])

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**LLM Response Latency (ms) over time**")
            if llm_history:
                import pandas as pd
                df_llm = pd.DataFrame(llm_history).set_index("timestamp")[["latency_ms"]]
                st.line_chart(df_llm, use_container_width=True)
            else:
                st.info("No LLM data yet. Generate a goal plan to populate this chart.")

        with chart_col2:
            st.markdown("**Data Drift Score over time**")
            if drift_history:
                import pandas as pd
                df_drift = pd.DataFrame(drift_history).set_index("timestamp")[["drift_score"]]
                st.line_chart(df_drift, use_container_width=True)
            else:
                st.info("No drift data yet. Generate goal plans to start tracking drift.")

        # --- A/B Test Summary ---
        if llm_history:
            st.markdown("---")
            st.markdown("### 🎭 A/B Prompt Version Distribution")
            import pandas as pd
            df_ab = pd.DataFrame(llm_history)
            if "prompt_version" in df_ab.columns:
                ab_counts = df_ab["prompt_version"].value_counts().reset_index()
                ab_counts.columns = ["Prompt Version", "Count"]
                ab_col1, ab_col2 = st.columns([1, 2])
                with ab_col1:
                    st.dataframe(ab_counts, use_container_width=True, hide_index=True)
                with ab_col2:
                    st.bar_chart(df_ab["prompt_version"].value_counts(), use_container_width=True)

        # --- User Feedback Summary ---
        try:
            feedback = APIClient.get_feedback_summary()
            if feedback and feedback.get("total_ratings", 0) > 0:
                st.markdown("---")
                st.markdown("### ⭐ User Feedback Analysis")
                f1, f2 = st.columns([1, 2])
                with f1:
                    st.metric("Average User Rating", f"{feedback['average_rating']:.1f} / 5.0")
                    st.write(f"Based on {feedback['total_ratings']} ratings.")
                with f2:
                    dist = feedback.get("distribution", {})
                    if dist:
                        import pandas as pd
                        df_dist = pd.DataFrame(list(dist.items()), columns=["Stars", "Count"]).set_index("Stars")
                        st.bar_chart(df_dist, use_container_width=True)
        except Exception as e:
            pass

        st.markdown("---")
        st.markdown("### 📉 Data Drift Tracking")
        drift_col1, drift_col2 = st.columns([2, 1])
        with drift_col1:
            st.metric("Latest Feature Drift Score", f"{metrics['latest_drift_score']:.3f}", delta_color="inverse")
            if metrics['latest_drift_score'] > 0.05:
                st.warning("⚠️ Drift score elevated. Consider retraining the ML model.")
            else:
                st.success("✅ Data distribution is stable. No drift detected.")
        with drift_col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🔄 Trigger Model Retraining", type="primary", use_container_width=True):
                try:
                    APIClient.trigger_retrain()
                    st.success("🚀 Retraining job dispatched! Check your backend terminal for live logs.")
                except Exception as e:
                    st.error(f"Failed to trigger retraining: {e}")

    except Exception as e:
        st.error(f"Could not load dashboard metrics. Error: {e}")
