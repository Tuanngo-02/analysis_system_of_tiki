import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time

# =========================
# Page Configuration
# =========================
st.set_page_config(
    page_title="Product Review Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Custom CSS
# =========================
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --success: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --info: #3b82f6;
        --light: #f3f4f6;
        --dark: #1f2937;
    }
    
    /* Global styles */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0 !important;
    }
    
    /* Custom card */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        border-left: 4px solid #6366f1;
    }
    
    .card-success {
        border-left: 4px solid #10b981;
    }
    
    .card-danger {
        border-left: 4px solid #ef4444;
    }
    
    /* Header styles */
    h1, h2, h3 {
        color: #1f2937;
        font-weight: 700;
    }
    
    h1 {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 30px !important;
    }
    
    /* Button styles */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        padding: 20px;
        border-radius: 12px;
        border: 2px solid rgba(99, 102, 241, 0.1);
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 8px !important;
        border: 2px solid #e5e7eb !important;
        padding: 10px !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #6366f1, transparent);
        margin: 20px 0 !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Alert boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Load data with loading state
# =========================
@st.cache_resource
def load_data():
    return pd.read_csv("reviews_with_sentiment.csv")

# Show loading spinner while loading data
with st.spinner("⏳ Đang tải dữ liệu..."):
    df = load_data()

# =========================
# User Database
# =========================
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
    "user2": {"password": "user123", "role": "user"}
}

# =========================
# Initialize Session State
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

if "last_action" not in st.session_state:
    st.session_state.last_action = None

# =========================
# Toast Notification
# =========================
def show_toast(message, type="success", duration=3):
    """Show toast notification"""
    if type == "success":
        st.success(f"✅ {message}")
    elif type == "error":
        st.error(f"❌ {message}")
    elif type == "warning":
        st.warning(f"⚠️ {message}")
    else:
        st.info(f"ℹ️ {message}")

# =========================
# Helper Functions
# =========================
def get_product_stats(df_product):
    """Lấy thống kê cảm xúc của sản phẩm"""
    positive = (df_product['predicted_sentiment'] == 1).sum()
    negative = (df_product['predicted_sentiment'] == 0).sum()
    total = len(df_product)
    
    positive_percent = (positive / total * 100) if total > 0 else 0
    negative_percent = (negative / total * 100) if total > 0 else 0
    
    return {
        'positive': positive,
        'negative': negative,
        'total': total,
        'positive_percent': positive_percent,
        'negative_percent': negative_percent
    }

def plot_comparison(product_id1, product_id2, stats1, stats2):
    """Vẽ biểu đồ so sánh hai sản phẩm"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('white')
    
    # Biểu đồ 1
    colors1 = ['#10b981', '#ef4444']
    ax1.pie(
        [stats1['positive'], stats1['negative']],
        labels=['Positive', 'Negative'],
        autopct='%1.1f%%',
        colors=colors1,
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    ax1.set_title(f"Product {product_id1}", fontsize=14, fontweight='bold', color='#1f2937')
    
    # Biểu đồ 2
    ax2.pie(
        [stats2['positive'], stats2['negative']],
        labels=['Positive', 'Negative'],
        autopct='%1.1f%%',
        colors=colors1,
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    ax2.set_title(f"Product {product_id2}", fontsize=14, fontweight='bold', color='#1f2937')
    
    return fig

def plot_bar_comparison(product_id1, product_id2, stats1, stats2):
    """Vẽ biểu đồ cột so sánh"""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('white')
    
    x = np.arange(2)
    width = 0.35
    
    products = [product_id1, product_id2]
    positive_percents = [stats1['positive_percent'], stats2['positive_percent']]
    negative_percents = [stats1['negative_percent'], stats2['negative_percent']]
    
    bars1 = ax.bar(x - width/2, positive_percents, width, label='Positive', color='#10b981')
    bars2 = ax.bar(x + width/2, negative_percents, width, label='Negative', color='#ef4444')
    
    ax.set_ylabel('Phần trăm (%)', fontsize=12, fontweight='bold')
    ax.set_title('So sánh Sentiment giữa hai sản phẩm', fontsize=14, fontweight='bold', color='#1f2937')
    ax.set_xticks(x)
    ax.set_xticklabels(products)
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    return fig

# =========================
# Login Page
# =========================
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔐 Login</h1>", unsafe_allow_html=True)
              
        username = st.text_input("👤 Username", placeholder="Nhập username")
        password = st.text_input("🔑 Password", type="password", placeholder="Nhập password")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Login", use_container_width=True):
                if username in USERS_DB and USERS_DB[username]["password"] == password:
                    with st.spinner("🔄 Đang đăng nhập..."):
                        time.sleep(1)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = USERS_DB[username]["role"]
                    show_toast(f"Chào mừng {username}!", "success")
                    time.sleep(1)
                    st.rerun()
                else:
                    show_toast("Username hoặc password sai!", "error")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #6366f1, #8b5cf6); 
                           color: white; padding: 15px; border-radius: 8px; text-align: center;'>
                <b>👑 Admin</b><br>
                admin<br>
                admin123
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #3b82f6, #06b6d4); 
                           color: white; padding: 15px; border-radius: 8px; text-align: center;'>
                <b>👤 User 1</b><br>
                user1<br>
                user123
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div style='background: linear-gradient(135deg, #8b5cf6, #d946ef); 
                           color: white; padding: 15px; border-radius: 8px; text-align: center;'>
                <b>👤 User 2</b><br>
                user2<br>
                user123
                </div>
            """, unsafe_allow_html=True)

# =========================
# ADMIN DASHBOARD
# =========================
def admin_dashboard():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("<h1>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            show_toast("Đã đăng xuất", "info")
            time.sleep(1)
            st.rerun()
    
    st.write(f"👤 **{st.session_state.username}** ({st.session_state.role})")
    st.divider()
    
    # Loading data
    with st.spinner("📊 Đang tính toán thống kê..."):
        # Overall Statistics
        total_products = df['product_id'].nunique()
        total_reviews = len(df)
        positive_reviews = (df['predicted_sentiment'] == 1).sum()
        negative_reviews = (df['predicted_sentiment'] == 0).sum()
        time.sleep(0.5)
    
    st.markdown("<h2>📈 Tổng Quan</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Tổng sản phẩm", f"{total_products}", delta=None)
    
    with col2:
        st.metric("💬 Tổng reviews", f"{total_reviews}", delta=None)
    
    with col3:
        st.metric("😊 Positive", f"{positive_reviews}", delta=f"{(positive_reviews/total_reviews*100):.1f}%")
    
    with col4:
        st.metric("😞 Negative", f"{negative_reviews}", delta=f"{(negative_reviews/total_reviews*100):.1f}%")
    
    st.divider()
    
    # Product List with Stats
    st.markdown("<h2>📋 Danh sách sản phẩm</h2>", unsafe_allow_html=True)
    
    with st.spinner("⏳ Đang tải dữ liệu sản phẩm..."):
        # Get unique product info
        product_info = df.drop_duplicates(subset=['product_id'])[['product_id', 'product_name', 'category']].sort_values('product_id')
        
        # Calculate stats per product
        product_stats = []
        
        for _, row in product_info.iterrows():
            product_id = row['product_id']
            df_product = df[df['product_id'] == product_id]
            stats = get_product_stats(df_product)
            
            product_stats.append({
                'Product ID': str(product_id),
                'Product Name': row['product_name'],
                'Category': row['category'],
                'Total Reviews': stats['total'],
                'Positive': stats['positive'],
                'Negative': stats['negative'],
                'Positive %': f"{stats['positive_percent']:.2f}%",
                'Negative %': f"{stats['negative_percent']:.2f}%"
            })
        
        product_df = pd.DataFrame(product_stats)
    
    # Search and Filter
    st.markdown("**🔍 Tìm kiếm và Lọc**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_product_id = st.text_input("Tìm kiếm Product ID", key="search_pid", placeholder="Nhập Product ID")
    
    with col2:
        search_product_name = st.text_input("Tìm kiếm Product Name", key="search_pname", placeholder="Nhập tên sản phẩm")
    
    with col3:
        search_category = st.text_input("Tìm kiếm Category", key="search_cat", placeholder="Nhập danh mục")
    
    # Apply filters
    filtered_df = product_df.copy()
    
    if search_product_id:
        filtered_df = filtered_df[filtered_df['Product ID'].str.contains(search_product_id, case=False, na=False)]
    
    if search_product_name:
        filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_product_name, case=False, na=False)]
    
    if search_category:
        filtered_df = filtered_df[filtered_df['Category'].str.contains(search_category, case=False, na=False)]
    
    # Sorting options
    st.markdown("**📊 Sắp xếp**")
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox(
            "Sắp xếp theo",
            ["Product ID", "Product Name", "Category", "Total Reviews", "Positive", "Negative"]
        )
    
    with col2:
        sort_order = st.radio("Thứ tự", ["Giảm dần", "Tăng dần"], horizontal=True)
    
    ascending = sort_order == "Tăng dần"
    
    try:
        filtered_df_sorted = filtered_df.sort_values(
            by=sort_by,
            ascending=ascending
        )
    except:
        filtered_df_sorted = filtered_df
    
    st.markdown(f"**Hiển thị {len(filtered_df_sorted)} / {len(product_df)} sản phẩm**")
    st.dataframe(filtered_df_sorted, use_container_width=True, hide_index=True)
    
    if len(filtered_df_sorted) > 0:
        show_toast(f"Đã tải {len(filtered_df_sorted)} sản phẩm", "success")
    
    st.divider()
    
    # Overall Sentiment Chart
    st.markdown("<h2>📊 Biểu đồ Sentiment</h2>", unsafe_allow_html=True)
    
    with st.spinner("📈 Đang vẽ biểu đồ..."):
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('white')
            ax.pie(
                [positive_reviews, negative_reviews],
                labels=['Positive', 'Negative'],
                autopct='%1.1f%%',
                colors=['#10b981', '#ef4444'],
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2}
            )
            ax.set_title('Tỷ lệ Sentiment tổng thể', fontsize=14, fontweight='bold', color='#1f2937')
            st.pyplot(fig)
        
        with col2:
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor('white')
            sentiment_by_product = df.groupby('product_id')['predicted_sentiment'].apply(
                lambda x: (x == 1).sum() / len(x) * 100
            ).sort_values(ascending=False).head(10)
            
            bars = ax.barh(sentiment_by_product.index.astype(str), sentiment_by_product.values, color='#6366f1')
            ax.set_xlabel('Positive Percentage (%)', fontsize=12, fontweight='bold')
            ax.set_title('Top 10 sản phẩm có điểm cao nhất', fontsize=14, fontweight='bold', color='#1f2937')
            ax.set_xlim(0, 100)
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)
    
    st.divider()
    
    # Search Product Details
    st.markdown("<h2>🔍 Chi tiết sản phẩm</h2>", unsafe_allow_html=True)
    
    detail_search_id = st.text_input("Tìm kiếm Product ID để xem chi tiết", key="detail_search_pid", placeholder="Nhập Product ID")
    
    if detail_search_id:
        with st.spinner("⏳ Đang tải chi tiết sản phẩm..."):
            df_search = df[df['product_id'].astype(str) == detail_search_id]
            
            if len(df_search) == 0:
                show_toast("Không tìm thấy sản phẩm", "warning")
            else:
                stats = get_product_stats(df_search)
                
                # Get product info
                product_name = df_search['product_name'].iloc[0]
                category = df_search['category'].iloc[0]
                
                st.markdown(f"**📦 Tên sản phẩm:** {product_name}")
                st.markdown(f"**🏷️ Danh mục:** {category}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💬 Total Reviews", stats['total'])
                
                with col2:
                    st.metric("😊 Positive", f"{stats['positive_percent']:.2f}%")
                
                with col3:
                    st.metric("😞 Negative", f"{stats['negative_percent']:.2f}%")
                
                st.markdown("**📝 Danh sách Reviews:**")
                st.dataframe(
                    df_search[['review_text', 'predicted_sentiment']],
                    use_container_width=True
                )
                
                show_toast("Tải chi tiết thành công", "success")

# =========================
# USER INTERFACE
# =========================
def user_interface():
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("<h1>📱 Product Review Analysis</h1>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            show_toast("Đã đăng xuất", "info")
            time.sleep(1)
            st.rerun()
    
    st.write(f"👋 Xin chào **{st.session_state.username}**!")
    st.divider()
    
    # Navigation
    page = st.sidebar.radio(
        "📊 Chọn tính năng",
        ["Phân tích sản phẩm", "So sánh sản phẩm"]
    )
    
    # =========================
    # Page 1: Analyze single product
    # =========================
    if page == "Phân tích sản phẩm":
        st.markdown("<h2>📊 Phân tích cảm xúc sản phẩm</h2>", unsafe_allow_html=True)
        
        product_id = st.text_input("Nhập Product ID", placeholder="Nhập ID sản phẩm")
        
        if st.button("🔍 Phân tích", use_container_width=True):
            if product_id.strip() == "":
                show_toast("Vui lòng nhập Product ID", "warning")
            else:
                with st.spinner("⏳ Đang phân tích..."):
                    df_product = df[df['product_id'].astype(str) == product_id]
                    time.sleep(0.5)
                    
                    if len(df_product) == 0:
                        show_toast("Không tìm thấy sản phẩm", "error")
                    else:
                        stats = get_product_stats(df_product)
                        
                        st.markdown("<h3>📈 Kết quả phân tích</h3>", unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("😊 Positive", f"{stats['positive_percent']:.2f}%", f"+{stats['positive']} reviews")
                        with col2:
                            st.metric("😞 Negative", f"{stats['negative_percent']:.2f}%", f"+{stats['negative']} reviews")
                        with col3:
                            st.metric("💬 Tổng reviews", stats['total'])
                        
                        fig, ax = plt.subplots()
                        fig.patch.set_facecolor('white')
                        ax.pie(
                            [stats['positive'], stats['negative']],
                            labels=['Positive', 'Negative'],
                            autopct='%1.1f%%',
                            colors=['#10b981', '#ef4444'],
                            startangle=90,
                            wedgeprops={'edgecolor': 'white', 'linewidth': 2}
                        )
                        ax.set_title('Tỷ lệ Sentiment', fontsize=14, fontweight='bold', color='#1f2937')
                        st.pyplot(fig)
                        
                        st.markdown("<h3>📝 Danh sách review</h3>", unsafe_allow_html=True)
                        st.dataframe(
                            df_product[['review_text', 'predicted_sentiment']],
                            use_container_width=True
                        )
                        
                        show_toast("Phân tích hoàn tất", "success")
    
    # =========================
    # Page 2: Compare two products
    # =========================
    else:
        st.markdown("<h2>⚖️ So sánh hai sản phẩm</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_id1 = st.text_input("Nhập Product ID 1", key="pid1", placeholder="ID sản phẩm 1")
        
        with col2:
            product_id2 = st.text_input("Nhập Product ID 2", key="pid2", placeholder="ID sản phẩm 2")
        
        if st.button("⚖️ So sánh", use_container_width=True):
            if product_id1.strip() == "" or product_id2.strip() == "":
                show_toast("Vui lòng nhập cả hai Product ID", "warning")
            elif product_id1 == product_id2:
                show_toast("Vui lòng nhập hai sản phẩm khác nhau", "warning")
            else:
                with st.spinner("⏳ Đang so sánh..."):
                    df_product1 = df[df['product_id'].astype(str) == product_id1]
                    df_product2 = df[df['product_id'].astype(str) == product_id2]
                    time.sleep(0.5)
                    
                    if len(df_product1) == 0:
                        show_toast(f"Không tìm thấy sản phẩm {product_id1}", "error")
                    elif len(df_product2) == 0:
                        show_toast(f"Không tìm thấy sản phẩm {product_id2}", "error")
                    else:
                        stats1 = get_product_stats(df_product1)
                        stats2 = get_product_stats(df_product2)
                        
                        # Metrics comparison
                        st.markdown("<h3>📊 So sánh thống kê</h3>", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**📦 Product {product_id1}**")
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("😊 Positive", f"{stats1['positive_percent']:.2f}%")
                            with col_b:
                                st.metric("😞 Negative", f"{stats1['negative_percent']:.2f}%")
                            with col_c:
                                st.metric("💬 Reviews", stats1['total'])
                        
                        with col2:
                            st.markdown(f"**📦 Product {product_id2}**")
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("😊 Positive", f"{stats2['positive_percent']:.2f}%")
                            with col_b:
                                st.metric("😞 Negative", f"{stats2['negative_percent']:.2f}%")
                            with col_c:
                                st.metric("💬 Reviews", stats2['total'])
                        
                        # Pie charts
                        st.markdown("<h3>📈 Biểu đồ cảm xúc</h3>", unsafe_allow_html=True)
                        fig = plot_comparison(product_id1, product_id2, stats1, stats2)
                        st.pyplot(fig)
                        
                        # Bar chart comparison
                        st.markdown("<h3>📊 So sánh phần trăm</h3>", unsafe_allow_html=True)
                        fig = plot_bar_comparison(product_id1, product_id2, stats1, stats2)
                        st.pyplot(fig)
                        
                        # Verdict
                        st.markdown("<h3>🎯 Kết luận</h3>", unsafe_allow_html=True)
                        
                        diff = stats1['positive_percent'] - stats2['positive_percent']
                        
                        if abs(diff) < 5:
                            st.info(f"ℹ️ Cả hai sản phẩm có mức độ hài lòng tương đương (~{abs(diff):.1f}% khác biệt)")
                        elif diff > 0:
                            st.success(f"✅ **Product {product_id1}** có mức độ hài lòng cao hơn {abs(diff):.1f}%")
                        else:
                            st.success(f"✅ **Product {product_id2}** có mức độ hài lòng cao hơn {abs(diff):.1f}%")
                        
                        # Reviews comparison
                        st.markdown("<h3>📝 Danh sách review</h3>", unsafe_allow_html=True)
                        
                        tab1, tab2 = st.tabs([f"📦 Product {product_id1}", f"📦 Product {product_id2}"])
                        
                        with tab1:
                            st.write(f"**Tổng {len(df_product1)} reviews**")
                            st.dataframe(
                                df_product1[['review_text', 'predicted_sentiment']],
                                use_container_width=True
                            )
                        
                        with tab2:
                            st.write(f"**Tổng {len(df_product2)} reviews**")
                            st.dataframe(
                                df_product2[['review_text', 'predicted_sentiment']],
                                use_container_width=True
                            )
                        
                        show_toast("So sánh hoàn tất", "success")

# =========================
# Main App
# =========================
if not st.session_state.logged_in:
    login_page()
elif st.session_state.role == "admin":
    admin_dashboard()
else:
    user_interface()
