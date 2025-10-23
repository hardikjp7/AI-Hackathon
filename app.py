import streamlit as st
import json
from groq import Groq
import pandas as pd
from datetime import datetime

# Sample curriculum data
CURRICULUM_DATA = {
    "Python Programming": {
        "topics": [
            {"id": 1, "name": "Python Basics", "prerequisites": [], "difficulty": "Beginner", "duration": "2 weeks"},
            {"id": 2, "name": "Data Structures", "prerequisites": [1], "difficulty": "Beginner", "duration": "3 weeks"},
            {"id": 3, "name": "Object-Oriented Programming", "prerequisites": [1, 2], "difficulty": "Intermediate", "duration": "3 weeks"},
            {"id": 4, "name": "File Handling & Exceptions", "prerequisites": [1], "difficulty": "Intermediate", "duration": "2 weeks"},
            {"id": 5, "name": "Libraries & Frameworks", "prerequisites": [3, 4], "difficulty": "Intermediate", "duration": "4 weeks"},
            {"id": 6, "name": "Web Development with Flask", "prerequisites": [5], "difficulty": "Advanced", "duration": "4 weeks"},
            {"id": 7, "name": "Data Science with Pandas", "prerequisites": [2, 5], "difficulty": "Advanced", "duration": "5 weeks"},
        ]
    },
    "Data Science": {
        "topics": [
            {"id": 1, "name": "Statistics Fundamentals", "prerequisites": [], "difficulty": "Beginner", "duration": "3 weeks"},
            {"id": 2, "name": "Python for Data Analysis", "prerequisites": [1], "difficulty": "Beginner", "duration": "3 weeks"},
            {"id": 3, "name": "Data Visualization", "prerequisites": [2], "difficulty": "Intermediate", "duration": "2 weeks"},
            {"id": 4, "name": "Machine Learning Basics", "prerequisites": [1, 2], "difficulty": "Intermediate", "duration": "4 weeks"},
            {"id": 5, "name": "Deep Learning", "prerequisites": [4], "difficulty": "Advanced", "duration": "6 weeks"},
            {"id": 6, "name": "Natural Language Processing", "prerequisites": [4], "difficulty": "Advanced", "duration": "5 weeks"},
        ]
    },
    "Web Development": {
        "topics": [
            {"id": 1, "name": "HTML & CSS", "prerequisites": [], "difficulty": "Beginner", "duration": "2 weeks"},
            {"id": 2, "name": "JavaScript Basics", "prerequisites": [1], "difficulty": "Beginner", "duration": "3 weeks"},
            {"id": 3, "name": "Responsive Design", "prerequisites": [1], "difficulty": "Intermediate", "duration": "2 weeks"},
            {"id": 4, "name": "React Fundamentals", "prerequisites": [2], "difficulty": "Intermediate", "duration": "4 weeks"},
            {"id": 5, "name": "Backend with Node.js", "prerequisites": [2], "difficulty": "Intermediate", "duration": "4 weeks"},
            {"id": 6, "name": "Database Management", "prerequisites": [5], "difficulty": "Intermediate", "duration": "3 weeks"},
            {"id": 7, "name": "Full Stack Projects", "prerequisites": [4, 6], "difficulty": "Advanced", "duration": "6 weeks"},
        ]
    }
}

# Sample student profiles
SAMPLE_PROFILES = {
    "Beginner Student": {
        "current_skills": ["Basic Computer Knowledge"],
        "skill_level": "Beginner",
        "time_available": "10 hours/week",
        "learning_style": "Visual with hands-on practice"
    },
    "Intermediate Programmer": {
        "current_skills": ["Python Basics", "Data Structures", "HTML/CSS"],
        "skill_level": "Intermediate",
        "time_available": "15 hours/week",
        "learning_style": "Project-based learning"
    },
    "Advanced Learner": {
        "current_skills": ["Python", "JavaScript", "SQL", "Basic ML"],
        "skill_level": "Advanced",
        "time_available": "20 hours/week",
        "learning_style": "Self-paced with real-world applications"
    }
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'learning_path' not in st.session_state:
        st.session_state.learning_path = None

def get_groq_response(api_key, user_input, student_profile, curriculum):
    """Get response from Groq LLM"""
    try:
        client = Groq(api_key=api_key)
        
        system_prompt = f"""You are an expert educational advisor AI that creates personalized learning paths.

Available Curriculum:
{json.dumps(curriculum, indent=2)}

Student Profile:
{json.dumps(student_profile, indent=2)}

Your task is to:
1. Understand the student's current skill level and goals
2. Recommend a personalized learning path from the available curriculum
3. Explain why each topic is recommended
4. Provide estimated timelines based on student's availability
5. Suggest prerequisite topics if needed

Be encouraging, specific, and provide actionable guidance."""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1500,
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def generate_learning_path_logic(student_profile, selected_track, curriculum):
    """Generate learning path based on logic"""
    topics = curriculum[selected_track]["topics"]
    skill_level = student_profile.get("skill_level", "Beginner")
    current_skills = student_profile.get("current_skills", [])
    
    # Filter topics based on skill level
    if skill_level == "Beginner":
        recommended = [t for t in topics if t["difficulty"] in ["Beginner"]]
    elif skill_level == "Intermediate":
        recommended = [t for t in topics if t["difficulty"] in ["Beginner", "Intermediate"]]
    else:
        recommended = topics
    
    # Sort by prerequisites
    path = []
    completed_ids = set()
    
    while len(path) < len(recommended):
        for topic in recommended:
            if topic not in path:
                prereqs_met = all(p in completed_ids for p in topic["prerequisites"])
                if prereqs_met:
                    path.append(topic)
                    completed_ids.add(topic["id"])
                    break
    
    return path

def main():
    st.set_page_config(page_title="Personalized Learning Path Recommender", layout="wide")
    
    initialize_session_state()
    
    st.title("🎓 Personalized Learning Path Recommender")
    st.markdown("Get AI-powered personalized learning recommendations tailored to your skills and goals")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input("Groq API Key", type="password", help="Enter your Groq API key")
        st.markdown("[Get API Key](https://console.groq.com/keys)")
        
        st.divider()
        
        # Student Profile Selection
        st.subheader("Student Profile")
        
        profile_option = st.radio(
            "Choose profile type:",
            ["Use Sample Profile", "Create Custom Profile"]
        )
        
        if profile_option == "Use Sample Profile":
            sample_name = st.selectbox("Select Sample Profile", list(SAMPLE_PROFILES.keys()))
            student_profile = SAMPLE_PROFILES[sample_name].copy()
        else:
            st.markdown("**Custom Profile**")
            current_skills = st.text_area(
                "Current Skills (comma-separated)",
                "Python Basics, HTML"
            )
            skill_level = st.select_slider(
                "Overall Skill Level",
                options=["Beginner", "Intermediate", "Advanced"]
            )
            time_available = st.text_input("Time Available per Week", "10 hours/week")
            learning_style = st.text_input("Preferred Learning Style", "Visual learning")
            
            student_profile = {
                "current_skills": [s.strip() for s in current_skills.split(",")],
                "skill_level": skill_level,
                "time_available": time_available,
                "learning_style": learning_style
            }
        
        st.divider()
        
        # Display current profile
        st.subheader("📋 Current Profile")
        st.json(student_profile)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("💬 Interactive AI Advisor")
        
        # Learning track selection
        selected_track = st.selectbox(
            "Select Learning Track:",
            list(CURRICULUM_DATA.keys())
        )
        
        # Display curriculum topics
        with st.expander("📚 View Curriculum Topics"):
            topics_df = pd.DataFrame(CURRICULUM_DATA[selected_track]["topics"])
            st.dataframe(topics_df, use_container_width=True)
        
        # User input
        user_goal = st.text_area(
            "What are your learning goals?",
            placeholder="E.g., I want to become a data scientist and build ML models...",
            height=100
        )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🤖 Get AI Recommendation", type="primary", use_container_width=True):
                if not api_key:
                    st.error("Please enter your Groq API key in the sidebar")
                elif not user_goal:
                    st.warning("Please describe your learning goals")
                else:
                    with st.spinner("Generating personalized recommendation..."):
                        response = get_groq_response(
                            api_key,
                            user_goal,
                            student_profile,
                            {selected_track: CURRICULUM_DATA[selected_track]}
                        )
                        st.session_state.chat_history.append({
                            "user": user_goal,
                            "assistant": response,
                            "timestamp": datetime.now().strftime("%H:%M:%S")
                        })
        
        with col_btn2:
            if st.button("🔧 Generate Logic-Based Path", use_container_width=True):
                with st.spinner("Generating learning path..."):
                    path = generate_learning_path_logic(
                        student_profile,
                        selected_track,
                        CURRICULUM_DATA
                    )
                    st.session_state.learning_path = path
        
        # Display chat history
        if st.session_state.chat_history:
            st.divider()
            st.subheader("Conversation History")
            for chat in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(f"**[{chat['timestamp']}]** {chat['user']}")
                with st.chat_message("assistant"):
                    st.write(chat['assistant'])
    
    with col2:
        st.header("🗺️ Your Learning Path")
        
        if st.session_state.learning_path:
            path = st.session_state.learning_path
            
            st.success(f"Generated {len(path)} topics for your learning journey!")
            
            total_weeks = sum(int(t['duration'].split()[0]) for t in path)
            st.metric("Estimated Total Duration", f"{total_weeks} weeks")
            
            st.divider()
            
            for idx, topic in enumerate(path, 1):
                with st.container():
                    col_num, col_content = st.columns([0.1, 0.9])
                    
                    with col_num:
                        if topic["difficulty"] == "Beginner":
                            st.markdown(f"### 🟢 {idx}")
                        elif topic["difficulty"] == "Intermediate":
                            st.markdown(f"### 🟡 {idx}")
                        else:
                            st.markdown(f"### 🔴 {idx}")
                    
                    with col_content:
                        st.markdown(f"### {topic['name']}")
                        st.markdown(f"**Difficulty:** {topic['difficulty']}")
                        st.markdown(f"**Duration:** {topic['duration']}")
                        
                        if topic["prerequisites"]:
                            prereq_names = [path[p-1]["name"] for p in topic["prerequisites"] if p <= len(path)]
                            if prereq_names:
                                st.markdown(f"**Prerequisites:** {', '.join(prereq_names)}")
                    
                    st.divider()
            
            # Download option
            if st.button("📥 Download Learning Path", use_container_width=True):
                path_json = json.dumps(path, indent=2)
                st.download_button(
                    label="Download as JSON",
                    data=path_json,
                    file_name="learning_path.json",
                    mime="application/json"
                )
        else:
            st.info("👆 Click 'Generate Logic-Based Path' or chat with the AI to get recommendations!")
            
            # Show sample visualization
            st.markdown("### How it works:")
            st.markdown("""
            1. **Profile Analysis**: We analyze your current skills and learning goals
            2. **Topic Mapping**: Match your profile with curriculum topics
            3. **Path Generation**: Create an optimized learning sequence
            4. **AI Enhancement**: Get personalized insights and recommendations
            """)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💡 Tip: For best results, describe your goals clearly and mention any specific technologies you want to learn</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
