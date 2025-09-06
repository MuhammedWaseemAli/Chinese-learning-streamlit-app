import streamlit as st
import pandas as pd
import base64
from io import BytesIO
import random
import time
import os

# Try to import gTTS, with fallback if not available
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    st.warning("⚠️ Text-to-speech functionality is not available. Audio features will be disabled.")

# Check if Excel file exists
EXCEL_FILE = "china.xlsx"
if os.path.exists(EXCEL_FILE):
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        # Create sample data if file can't be read
        df = pd.DataFrame({
            'English Word': ['Hello', 'Thank you', 'Goodbye', 'Water', 'Food'],
            'Traditional Chinese Word': ['你好', '謝謝', '再見', '水', '食物'],
            'Pinyin': ['nǐ hǎo', 'xiè xiè', 'zài jiàn', 'shuǐ', 'shí wù'],
            'Category': ['Greetings', 'Greetings', 'Greetings', 'Basic', 'Food']
        })
else:
    st.error("❌ Excel file 'china.xlsx' not found. Please upload your Chinese vocabulary file.")
    # Create sample data for demonstration
    df = pd.DataFrame({
        'English Word': ['Hello', 'Thank you', 'Goodbye', 'Water', 'Food', 'Mother', 'Father', 'Red', 'Blue', 'One'],
        'Traditional Chinese Word': ['你好', '謝謝', '再見', '水', '食物', '媽媽', '爸爸', '紅色', '藍色', '一'],
        'Pinyin': ['nǐ hǎo', 'xiè xiè', 'zài jiàn', 'shuǐ', 'shí wù', 'mā ma', 'bà ba', 'hóng sè', 'lán sè', 'yī'],
        'Category': ['Greetings', 'Greetings', 'Greetings', 'Basic', 'Food', 'Family', 'Family', 'Colors', 'Colors', 'Numbers']
    })
    st.info("📝 Using sample data for demonstration. Upload your own 'china.xlsx' file to use your vocabulary.")

# Initialize session state for quiz
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'speech_active' not in st.session_state:
    st.session_state.speech_active = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'quiz_options' not in st.session_state:
    st.session_state.quiz_options = []
if 'correct_answer' not in st.session_state:
    st.session_state.correct_answer = ""
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_total' not in st.session_state:
    st.session_state.quiz_total = 0
if 'quiz_answered' not in st.session_state:
    st.session_state.quiz_answered = False
if 'quiz_category' not in st.session_state:
    st.session_state.quiz_category = "All"
if 'quiz_difficulty' not in st.session_state:
    st.session_state.quiz_difficulty = "Easy"
if 'current_speech' not in st.session_state:
    st.session_state.current_speech = []
if 'speech_settings' not in st.session_state:
    st.session_state.speech_settings = {'sentences': 5, 'speed': 'normal', 'include_pinyin': True}

# Function to generate audio safely
def generate_audio_safely(text, lang='zh-tw', slow=False):
    """Generate audio with error handling"""
    if not TTS_AVAILABLE:
        st.warning("🔇 Audio functionality is not available in this deployment.")
        return None
    
    try:
        tts = gTTS(text=text, lang=lang, slow=slow)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return base64.b64encode(mp3_fp.read()).decode()
    except Exception as e:
        st.error(f"❌ Error generating audio: {str(e)}")
        return None

# 🎨 Enhanced Custom CSS with beautiful aesthetics
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating Chinese characters with enhanced animation */
    .floating-text {
        position: fixed;
        font-size: 32px;
        font-weight: 700;
        color: rgba(255,255,255,0.15);
        animation: float 20s infinite linear;
        z-index: -1;
        font-family: 'Noto Sans TC', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        pointer-events: none;
    }
    
    @keyframes float {
        0% { 
            transform: translateY(100vh) translateX(0) rotate(0deg); 
            opacity: 0; 
            filter: blur(2px);
        }
        10% { opacity: 0.8; filter: blur(0px); }
        90% { opacity: 0.8; filter: blur(0px); }
        100% { 
            transform: translateY(-20vh) translateX(100px) rotate(360deg); 
            opacity: 0; 
            filter: blur(2px);
        }
    }
    
    /* Custom title styling */
    .main-title {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #6c5ce7);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin: 2rem 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Container styling */
    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Word card styling */
    .word-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .word-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.8) 100%);
    }
    
    /* Text styling */
    .english-word {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .chinese-word {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Noto Sans TC', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .pinyin-word {
        font-size: 1.1rem;
        font-weight: 500;
        color: #7f8c8d;
        font-style: italic;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
    }
    
    .category-tag {
        display: inline-block;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Stats cards */
    .stats-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.6));
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        margin: 0.5rem;
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Inter', sans-serif;
    }
    
    .stats-label {
        font-size: 1rem;
        color: #7f8c8d;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        margin-top: 0.5rem;
    }
    
    /* Disable audio warning */
    .audio-disabled {
        background: linear-gradient(45deg, #95a5a6, #7f8c8d);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        font-size: 1rem;
        cursor: not-allowed;
        opacity: 0.6;
        font-weight: 600;
        border: none;
    }
    
    /* Hide streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Enhanced floating characters with more variety
characters = [
    ("愛", "Love"), ("學", "Learn"), ("和", "Peace"), ("力", "Strength"), 
    ("夢", "Dream"), ("水", "Water"), ("天", "Sky"), ("地", "Earth"), 
    ("人", "Person"), ("心", "Heart"), ("美", "Beauty"), ("光", "Light"),
    ("風", "Wind"), ("花", "Flower"), ("月", "Moon"), ("星", "Star"),
    ("海", "Ocean"), ("山", "Mountain"), ("雲", "Cloud"), ("雨", "Rain")
]

# Create floating characters with staggered timing
for i in range(6):  # Reduced number for better performance
    char, meaning = random.choice(characters)
    delay = random.uniform(0, 15)
    left_pos = random.randint(0, 95)
    st.markdown(
        f'''<div class="floating-text" style="
            left:{left_pos}%; 
            animation-delay: {delay}s;
            font-size: {random.randint(28, 40)}px;
        ">{char}</div>''',
        unsafe_allow_html=True
    )

# 🌟 Enhanced App Title
st.markdown('<h1 class="main-title">🇹🇼 Learn Traditional Chinese</h1>', unsafe_allow_html=True)

# Show deployment status
if not TTS_AVAILABLE:
    st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.2); border: 2px solid #ffc107; border-radius: 15px; padding: 1rem; margin: 1rem 0; text-align: center;">
            <h4 style="color: #f57c00; margin-bottom: 0.5rem;">🔇 Limited Audio Mode</h4>
            <p style="color: #ef6c00; margin: 0;">Audio features are disabled in this deployment. Visual learning features are fully available!</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<p style="text-align: center; font-size: 1.2rem; color: rgba(255,255,255,0.9); font-weight: 500; margin-bottom: 2rem;">Discover the beauty of Traditional Chinese with interactive learning, quizzes & vocabulary practice</p>', unsafe_allow_html=True)

# Navigation tabs
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📚 Learn Words", key="learn_tab", help="Browse and learn Chinese words"):
        st.session_state.quiz_active = False
        st.session_state.speech_active = False

with col2:
    if st.button("🧠 Quiz Mode", key="quiz_tab", help="Test your knowledge with interactive quizzes"):
        st.session_state.quiz_active = True
        st.session_state.speech_active = False

with col3:
    if st.button("🎤 Speech Practice", key="speech_tab", help="Practice with randomly generated Chinese speeches"):
        st.session_state.quiz_active = False
        st.session_state.speech_active = True

with col4:
    if st.button("📊 Progress", key="progress_tab", help="View your learning progress"):
        st.session_state.quiz_active = False
        st.session_state.speech_active = False

# Stats section
total_words = len(df)
categories = len(df["Category"].unique())
speech_sentences = len(df[df["Category"].str.contains("speech", case=False, na=False)])
accuracy = round((st.session_state.quiz_score / max(st.session_state.quiz_total, 1)) * 100, 1) if st.session_state.quiz_total > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{total_words}</div>
            <div class="stats-label">Total Words</div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{categories}</div>
            <div class="stats-label">Categories</div>
        </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{speech_sentences}</div>
            <div class="stats-label">Speech Sentences</div>
        </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{st.session_state.quiz_total}</div>
            <div class="stats-label">Quiz Attempts</div>
        </div>
    ''', unsafe_allow_html=True)

with col5:
    st.markdown(f'''
        <div class="stats-card">
            <div class="stats-number">{accuracy}%</div>
            <div class="stats-label">Accuracy</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quiz Mode
if st.session_state.quiz_active:
    st.markdown("""
        <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 25px; padding: 2rem; margin: 1rem 0; box-shadow: 0 15px 35px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 800; margin-bottom: 2rem;">
                🧠 Chinese Word Quiz Challenge
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Quiz settings
    col1, col2 = st.columns(2)
    
    with col1:
        quiz_category = st.selectbox(
            "🎯 Quiz Category", 
            ["All"] + sorted(df["Category"].unique().tolist()),
            key="quiz_category_select",
            help="Choose category for focused learning"
        )
        st.session_state.quiz_category = quiz_category
    
    with col2:
        quiz_difficulty = st.selectbox(
            "⚡ Difficulty Level",
            ["Easy", "Medium", "Hard"],
            key="quiz_difficulty_select",
            help="Easy: 2 options, Medium: 3 options, Hard: 4 options"
        )
        st.session_state.quiz_difficulty = quiz_difficulty
    
    # Score display
    if st.session_state.quiz_total > 0:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4caf50, #66bb6a); color: white; border-radius: 20px; padding: 1rem 2rem; text-align: center; margin: 1rem 0; box-shadow: 0 10px 30px rgba(76, 175, 80, 0.3);">
                🏆 Score: {st.session_state.quiz_score} / {st.session_state.quiz_total} ({accuracy}% Accuracy)
            </div>
        """, unsafe_allow_html=True)
    
    def generate_quiz_question():
        # Filter dataframe based on category (exclude speech sentences from quiz)
        quiz_df = df[~df["Category"].str.contains("speech", case=False, na=False)].copy()
        if st.session_state.quiz_category != "All":
            quiz_df = quiz_df[quiz_df["Category"] == st.session_state.quiz_category]
        
        if len(quiz_df) == 0:
            return None
        
        # Select correct answer
        correct_word = quiz_df.sample(1).iloc[0]
        st.session_state.current_question = correct_word
        st.session_state.correct_answer = correct_word["English Word"]
        
        # Generate wrong options
        num_options = 2 if st.session_state.quiz_difficulty == "Easy" else 3 if st.session_state.quiz_difficulty == "Medium" else 4
        other_words = quiz_df[quiz_df["English Word"] != correct_word["English Word"]].sample(min(num_options - 1, len(quiz_df) - 1))
        
        # Create options list
        options = [correct_word["English Word"]] + other_words["English Word"].tolist()
        random.shuffle(options)
        st.session_state.quiz_options = options
        st.session_state.quiz_answered = False
    
    # Generate new question button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 New Question", key="new_question", help="Generate a new quiz question"):
            generate_quiz_question()
    
    # Display current question
    if st.session_state.current_question is not None:
        question = st.session_state.current_question
        
        # Display Chinese word
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 25px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.1);">
                <h3 style="color: #7f8c8d; font-family: 'Inter', sans-serif; font-weight: 500; margin-bottom: 1rem;">
                    {"🎧" if TTS_AVAILABLE else "👁️"} Select the correct English translation:
                </h3>
                <div style="font-size: 4rem; font-weight: 800; background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-family: 'Noto Sans TC', sans-serif; margin: 2rem 0;">
                    {question["Traditional Chinese Word"]}
                </div>
                <div style="font-size: 1.5rem; color: #7f8c8d; font-style: italic; margin-bottom: 2rem;">
                    {question["Pinyin"]}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Audio button (if available)
        if TTS_AVAILABLE:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔊 Play Audio", key="quiz_audio", help="Listen to the pronunciation"):
                    b64 = generate_audio_safely(question["Traditional Chinese Word"])
                    if b64:
                        st.markdown(f"""
                            <audio autoplay="true">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """, unsafe_allow_html=True)
        else:
            st.info("🔇 Audio not available - rely on the Pinyin pronunciation guide!")
        
        # Display options
        st.markdown('<div style="margin: 2rem 0;">', unsafe_allow_html=True)
        
        for i, option in enumerate(st.session_state.quiz_options):
            if st.button(
                option, 
                key=f"option_{i}_{option}",
                help=f"Select {option} as your answer",
                disabled=st.session_state.quiz_answered
            ):
                st.session_state.quiz_answered = True
                st.session_state.quiz_total += 1
                
                if option == st.session_state.correct_answer:
                    st.session_state.quiz_score += 1
                    st.success("🎉 Correct! Well done!")
                    st.balloons()
                else:
                    st.error(f"❌ Incorrect! The correct answer is: {st.session_state.correct_answer}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # No question loaded
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.9); border-radius: 20px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
                <h3 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 600;">Ready to Test Your Knowledge?</h3>
                <p style="color: #7f8c8d; font-family: 'Inter', sans-serif; margin: 1rem 0;">Click "New Question" to start your Chinese learning quiz!</p>
            </div>
        """, unsafe_allow_html=True)

# Learning Mode (Dictionary/Browse)
else:
    # Enhanced search and filter section
    st.markdown("""
        <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; margin: 1rem 0; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.3);">
            <h3 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1.5rem; text-align: center;">🔍 Find Your Words</h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        category = st.selectbox(
            "📚 Select Category", 
            ["All"] + sorted(df["Category"].unique().tolist()),
            help="Choose a specific category to focus your learning"
        )

    with col2:
        search_word = st.text_input(
            "🔎 Search Words", 
            placeholder="Search in English, Chinese, or Pinyin...",
            help="Type any part of a word to find it instantly"
        )

    # Filter dataframe
    filtered_df = df.copy()
    if category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == category]

    if search_word:
        filtered_df = filtered_df[
            filtered_df["English Word"].str.contains(search_word, case=False, na=False) |
            filtered_df["Traditional Chinese Word"].str.contains(search_word, case=False, na=False) |
            filtered_df["Pinyin"].str.contains(search_word, case=False, na=False)
        ]

    # Results info
    st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <span style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.5rem 1.5rem; border-radius: 25px; font-weight: 600; font-family: 'Inter', sans-serif; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                📖 Showing {len(filtered_df)} words
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Enhanced word cards
    if len(filtered_df) > 0:
        for i, row in filtered_df.iterrows():
            # Color schemes for categories
            color_schemes = {
                "Greetings": ["#ff6b6b", "#ffa726"],
                "Family": ["#4ecdc4", "#45b7d1"],
                "Food": ["#f093fb", "#f5576c"],
                "Numbers": ["#a8e6cf", "#56ab91"],
                "Colors": ["#ff8a80", "#ffab91"],
                "Animals": ["#ce93d8", "#ba68c8"],
                "Time": ["#90caf9", "#42a5f5"],
                "Weather": ["#fff176", "#ffcc02"]
            }
            
            category_colors = color_schemes.get(row["Category"], ["#667eea", "#764ba2"])
            
            st.markdown(f"""
                <div class="word-card" style="border-left: 5px solid {category_colors[0]};">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                        <div style="flex: 1; min-width: 200px;">
                            <div class="english-word">{row["English Word"]}</div>
                            <div class="chinese-word">{row["Traditional Chinese Word"]}</div>
                            <div class="pinyin-word">{row["Pinyin"]}</div>
                            <div style="margin-top: 1rem;">
                                <span class="category-tag" style="background: linear-gradient(45deg, {category_colors[0]}, {category_colors[1]});">
                                    {row["Category"]}
                                </span>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center;">
            """, unsafe_allow_html=True)
            
            # Enhanced audio button
            if TTS_AVAILABLE:
                if st.button("🔊 Listen", key=f"btn_{i}", help="Click to hear pronunciation"):
                    b64 = generate_audio_safely(row["Traditional Chinese Word"])
                    if b64:
                        st.markdown(f"""
                            <div style="text-align: center; margin: 1rem 0;">
                                <div style="background: linear-gradient(45deg, #4facfe, #00f2fe); color: white; padding: 1rem 2rem; border-radius: 25px; display: inline-block; box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);">
                                    🎵 Playing: <strong>{row["Traditional Chinese Word"]}</strong>
                                </div>
                            </div>
                            <audio autoplay="true">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """, unsafe_allow_html=True)
                        st.success("🎉 Audio played successfully!")
            else:
                st.markdown("""
                    <button class="audio-disabled" disabled>
                        🔇 Audio Disabled
                    </button>
                """, unsafe_allow_html=True)
            
            st.markdown("</div></div></div>", unsafe_allow_html=True)

    else:
        # No results found
        st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.9); border-radius: 20px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">😔</div>
                <h3 style="color: #7f8c8d; font-family: 'Inter', sans-serif; font-weight: 600;">No words found</h3>
                <p style="color: #95a5a6; font-family: 'Inter', sans-serif;">Try adjusting your search or category filter</p>
            </div>
        """, unsafe_allow_html=True)

    # Random word of the day feature
    if st.button("🎲 Random Word Challenge", help="Get a random word to practice!"):
        random_word = df.sample(1).iloc[0]
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 25px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);">
                <h3 style="margin-bottom: 1rem; font-family: 'Inter', sans-serif;">🌟 Word of the Moment</h3>
                <div style="font-size: 3rem; margin: 1rem 0; font-family: 'Noto Sans TC', sans-serif;">{random_word["Traditional Chinese Word"]}</div>
                <div style="font-size: 1.5rem; margin: 0.5rem 0; opacity: 0.9;">{random_word["English Word"]}</div>
                <div style="font-size: 1.2rem; font-style: italic; opacity: 0.8;">{random_word["Pinyin"]}</div>
                <div style="margin-top: 1rem;">
                    <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                        {random_word["Category"]}
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)

# Footer with additional features
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.1);">
        <h4 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1rem;">✨ Learning Tips</h4>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 1rem;">
            <div style="flex: 1; min-width: 200px; padding: 1rem; background: linear-gradient(45deg, rgba(255,107,107,0.1), rgba(255,167,38,0.1)); border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
                <strong>Practice Daily</strong><br>
                <small style="color: #7f8c8d;">Consistency is key to mastering Chinese</small>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem; background: linear-gradient(45deg, rgba(78,205,196,0.1), rgba(69,183,209,0.1)); border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🗣️</div>
                <strong>Visual Learning</strong><br>
                <small style="color: #7f8c8d;">Use Pinyin to learn correct pronunciation</small>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 1rem; background: linear-gradient(45deg, rgba(108,92,231,0.1), rgba(116,75,162,0.1)); border-radius: 15px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                <strong>Take Quizzes</strong><br>
                <small style="color: #7f8c8d;">Test your knowledge with interactive quizzes</small>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Reset quiz score button
if st.session_state.quiz_total > 0:
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Reset Quiz Progress", help="Clear your quiz history and start fresh"):
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = 0
            st.session_state.current_question = None
            st.session_state.quiz_answered = False
            st.success("✅ Quiz progress has been reset!")
            time.sleep(1)
            st.rerun()

# File upload section for custom vocabulary
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
    <div style="background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 20px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.1);">
        <h4 style="color: #2c3e50; font-family: 'Inter', sans-serif; font-weight: 700; margin-bottom: 1rem;">📁 Upload Your Own Vocabulary</h4>
        <p style="color: #7f8c8d; margin-bottom: 1.5rem;">Upload an Excel file (.xlsx) with columns: English Word, Traditional Chinese Word, Pinyin, Category</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your vocabulary file", 
    type=['xlsx'],
    help="Upload an Excel file with your Chinese vocabulary"
)

if uploaded_file is not None:
    try:
        new_df = pd.read_excel(uploaded_file)
        required_columns = ['English Word', 'Traditional Chinese Word', 'Pinyin', 'Category']
        
        if all(col in new_df.columns for col in required_columns):
            df = new_df  # Replace the dataframe
            st.success(f"✅ Successfully loaded {len(df)} words from your file!")
            st.balloons()
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ Missing required columns. Please ensure your Excel file has: {', '.join(required_columns)}")
            
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")

# Deployment instructions
with st.expander("🚀 Deployment Help"):
    st.markdown("""
    ### Having deployment issues? Here are the fixes:
    
    **1. Requirements.txt Issues:**
    - Make sure `gTTS==2.5.1` is in your requirements.txt
    - Remove the `runtime.txt` file (it's not needed)
    
    **2. Missing Excel File:**
    - Upload your `china.xlsx` file to the root of your repository
    - Or use the file upload feature above to add your vocabulary
    
    **3. Audio Not Working:**
    - This version includes fallback modes when gTTS isn't available
    - The app will work without audio features in deployment environments
    
    **4. For Streamlit Cloud:**
    ```
    streamlit==1.35.0
    pandas==2.2.2
    numpy==1.26.4
    matplotlib==3.9.1
    altair==5.3.0
    gTTS==2.5.1
    openpyxl==3.1.5
    requests>=2.28.0
    urllib3>=1.26.0
    six>=1.16.0
    ```
    
    **5. GitHub Repository Structure:**
    ```
    your-repo/
    ├── streamlit_app.py
    ├── requirements.txt
    ├── china.xlsx (optional)
    └── packages.txt (only if needed: ffmpeg)
    ```
    """)

# Progressive loading animation for better UX
time.sleep(0.1)
