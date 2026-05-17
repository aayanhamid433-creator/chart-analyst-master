import streamlit as st
import anthropic
import base64
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Chart Analyst Master",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .vip-badge {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: black;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 20px;
    }
    .signal-box {
        background: rgba(124, 58, 237, 0.1);
        border-left: 4px solid #7c3aed;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .entry-box {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .tp-box {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .sl-box {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

# Header
st.markdown("# 📊 CHART ANALYST MASTER")
st.markdown("### Cloud-based AI Trading Chart Analysis")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # API Key input
    api_key = st.text_input("Anthropic API Key", type="password", help="Get from https://console.anthropic.com")
    
    # Display history
    st.markdown("## 📋 Analysis History")
    if st.session_state.analysis_history:
        if st.button("🗑️ Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
        
        for i, analysis in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(f"📈 {analysis['pair']} - {analysis['timeframe']} ({analysis['timestamp']})"):
                st.json({
                    "Pair": analysis['pair'],
                    "Trend": analysis['trend'],
                    "Entry": analysis['entry_range'],
                    "SL": analysis['stop_loss'],
                    "TP1": analysis['tp1'],
                    "TP2": analysis['tp2'],
                    "TP3": analysis['tp3'],
                    "R:R": analysis['risk_reward'],
                    "Confidence": f"{analysis['confidence']}%"
                })
    else:
        st.info("No analysis history yet")

# Main content
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📤 Upload Chart")
    uploaded_file = st.file_uploader("Choose chart image", type=["jpg", "jpeg", "png", "gif"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Chart", use_column_width=True)
        st.success(f"✅ {uploaded_file.name}")
    
    st.markdown("### Optional Details")
    pair = st.text_input("Pair (e.g., XAUUSD)", placeholder="Auto-detect if blank")
    timeframe = st.selectbox("Timeframe", ["Auto-detect", "1m", "5m", "15m", "1h", "4h", "1d"])

with col2:
    st.markdown("## 🎯 Analysis Results")
    
    if st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        
        st.markdown('<div class="vip-badge">⭐ VIP SIGNAL</div>', unsafe_allow_html=True)
        
        col_pair, col_trend = st.columns(2)
        with col_pair:
            st.markdown(f"### {analysis['pair']}")
        with col_trend:
            trend_emoji = "🟢" if analysis['trend'] == "BULLISH" else "🔴" if analysis['trend'] == "BEARISH" else "↔️"
            st.markdown(f"### {trend_emoji} {analysis['trend']}")
        
        st.markdown('<div class="entry-box">', unsafe_allow_html=True)
        st.markdown(f"**Entry Range:** `{analysis['entry_range']}`")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_sl, col_tp1, col_tp2, col_tp3 = st.columns(4)
        
        with col_sl:
            st.markdown('<div class="sl-box">', unsafe_allow_html=True)
            st.markdown(f"**SL**\n\n`{analysis['stop_loss']}`")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_tp1:
            st.markdown('<div class="tp-box">', unsafe_allow_html=True)
            st.markdown(f"**TP1**\n\n`{analysis['tp1']}`")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_tp2:
            st.markdown('<div class="tp-box">', unsafe_allow_html=True)
            st.markdown(f"**TP2**\n\n`{analysis['tp2']}`")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_tp3:
            st.markdown('<div class="tp-box">', unsafe_allow_html=True)
            st.markdown(f"**TP3**\n\n`{analysis['tp3']}`")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="signal-box">', unsafe_allow_html=True)
        st.markdown(f"**Risk : Reward**\n\n`{analysis['risk_reward']}`")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"**Confidence:** {analysis['confidence']}%")
        
        with st.expander("📈 Full Analysis"):
            st.markdown(analysis['analysis'])

# Analyze button
if st.button("🚀 Analyze Chart", key="analyze_btn", use_container_width=True):
    if not api_key:
        st.error("❌ Please enter your Anthropic API key in the sidebar")
    elif not uploaded_file:
        st.error("❌ Please upload a chart image first")
    else:
        with st.spinner("🔍 Analyzing chart..."):
            try:
                # Read and encode image
                image_data = base64.standard_b64encode(uploaded_file.getvalue()).decode("utf-8")
                
                # Call Anthropic API
                client = anthropic.Anthropic(api_key=api_key)
                
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": f"image/{uploaded_file.type.split('/')[-1]}",
                                        "data": image_data,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": """Analyze this trading chart and provide analysis in JSON ONLY (no markdown):

{
  "pair": "SYMBOL",
  "timeframe": "1m/5m/15m/1h etc",
  "trend": "BULLISH/BEARISH/NEUTRAL",
  "entry_range": "price range (e.g., 4614-4615)",
  "stop_loss": "price",
  "tp1": "price",
  "tp2": "price",
  "tp3": "price",
  "risk_reward": "1:X format",
  "confidence": "0-100 (just number)",
  "analysis": "2-3 sentence analysis of the setup",
  "patterns_found": ["pattern1", "pattern2"],
  "support_levels": ["level1", "level2"],
  "resistance_levels": ["level1", "level2"]
}

Focus on:
1. Trend direction (HH/HL vs LL/LH)
2. Candlestick patterns (pin bar, engulfing, etc)
3. Support/resistance levels
4. Entry, Stop Loss, and 3 Take Profit levels
5. Risk/Reward ratio
6. Confidence level (60-95%)"""
                                }
                            ],
                        }
                    ],
                )
                
                # Parse response
                response_text = message.content[0].text
                
                # Extract JSON
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                analysis_data = json.loads(json_str)
                
                # Store analysis
                analysis_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Use provided pair/timeframe or detected ones
                if pair and pair.strip():
                    analysis_data['pair'] = pair.upper()
                if timeframe != "Auto-detect":
                    analysis_data['timeframe'] = timeframe
                
                st.session_state.current_analysis = analysis_data
                st.session_state.analysis_history.append(analysis_data)
                
                st.success("✅ Analysis complete!")
                st.rerun()
                
            except json.JSONDecodeError:
                st.error("❌ Failed to parse analysis. Please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Trading Tools Section
st.markdown("---")
st.markdown("## 🛠️ Trading Tools")

tool_col1, tool_col2, tool_col3 = st.columns(3)

with tool_col1:
    st.markdown("### 📐 Fibonacci Calculator")
    fib_high = st.number_input("High Price", key="fib_high")
    fib_low = st.number_input("Low Price", key="fib_low")
    if fib_high > fib_low:
        range_val = fib_high - fib_low
        st.markdown(f"""
        **Fibonacci Levels:**
        - 0.236: `{fib_high - (range_val * 0.236):.2f}`
        - 0.382: `{fib_high - (range_val * 0.382):.2f}`
        - 0.500: `{fib_high - (range_val * 0.500):.2f}`
        - 0.618: `{fib_high - (range_val * 0.618):.2f}`
        """)

with tool_col2:
    st.markdown("### 🎯 Stop Loss Calculator")
    entry_price = st.number_input("Entry Price", key="entry_sl")
    sl_price = st.number_input("Stop Loss Price", key="sl_price")
    pips = abs(entry_price - sl_price)
    st.markdown(f"**Risk:** `{pips:.2f}` pips")

with tool_col3:
    st.markdown("### 💰 Risk/Reward Calculator")
    entry_rr = st.number_input("Entry Price", key="entry_rr")
    sl_rr = st.number_input("SL Price", key="sl_rr")
    tp_rr = st.number_input("TP Price", key="tp_rr")
    
    if entry_rr and sl_rr and tp_rr:
        risk = abs(entry_rr - sl_rr)
        reward = abs(tp_rr - entry_rr)
        if risk > 0:
            ratio = reward / risk
            st.markdown(f"**R:R Ratio:** `1:{ratio:.2f}`")
