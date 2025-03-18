import pandas as pd
import plotly.express as px
import streamlit as st
import io
import base64

# Page config
st.set_page_config(
    page_title='VisuaLytix',
    page_icon='📊',
    layout='wide'
)

# Custom CSS for header and uploader
st.markdown(
    """
    <style>
    .header-container {
        text-align: center;
        padding: 20px;
        background-color: #f3f3f3;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        margin-top: 10px;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .title img {
        height: 50px;
        margin-right: 10px;
    }
    .subtitle {
        font-size: 18px;
        color: #757575;
    }
    .file-uploader-section {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f9f9f9;
        margin-top: 20px;
        cursor: pointer;
    }
    .file-uploader-section:hover {
        background-color: #e8f5e9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Upload Logo and Header Section
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


logo_base64 = get_base64_image("logo.png")

st.markdown(
    f"""
    <div class="header-container">
        <div class="title">
            <img src="data:image/png;base64,{logo_base64}" alt="Logo" style="width: 50px; margin-right: 10px;">
            <span style="font-size: 36px; font-weight: bold; color: #4CAF50;">VisuaLytix</span>
        </div>
        <p class="subtitle">Drop your Data — Visualized and Analyzed in Seconds</p>
    </div>
    """,
    unsafe_allow_html=True
)

# File uploader section
MAX_FILE_SIZE_MB = 15  # Set max file size to 15 MB

# Initialize session state for data, file name, and file content
if 'data' not in st.session_state:
    st.session_state.data = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'file_content' not in st.session_state:
    st.session_state.file_content = None

# File uploader
data = st.file_uploader(label="", type=['csv', 'xlsx'], key="custom_file_uploader")

# Load data only if new file uploaded
if data is not None:
    if data.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(f"❌ File size exceeds {MAX_FILE_SIZE_MB} MB. Please upload a smaller file.")
        st.stop()

    # Save file content to session state
    st.session_state.file_content = data.getvalue()
    st.session_state.file_name = data.name

    # Process and load file content
    if data.name.endswith('csv'):
        st.session_state.data = pd.read_csv(io.BytesIO(st.session_state.file_content))
    elif data.name.endswith('xlsx'):
        st.session_state.data = pd.read_excel(io.BytesIO(st.session_state.file_content))

# If file already uploaded and available in session state, reload data
elif st.session_state.file_content is not None:
    if st.session_state.file_name.endswith('csv'):
        st.session_state.data = pd.read_csv(io.BytesIO(st.session_state.file_content))
    elif st.session_state.file_name.endswith('xlsx'):
        st.session_state.data = pd.read_excel(io.BytesIO(st.session_state.file_content))

# Check if data is available
if st.session_state.data is not None:
    df = st.session_state.data
    st.success(f"✅ File '{st.session_state.file_name}' loaded successfully!")
    st.dataframe(df, use_container_width=True)
    st.write(f'Total Rows: {df.shape[0]}')
else:
    st.warning("⚠️ No file uploaded yet. Please upload a file to proceed.")
    st.stop()


# Dataset Overview Section
st.subheader(':rainbow[Dataset Overview]')
tab1, tab2, tab3, tab4 = st.tabs(['Summary', 'Rows Preview', 'Data Types', 'Columns'])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.write(f'Total Rows: {df.shape[0]}')
        st.write(f'Total Columns: {df.shape[1]}')
    with col2:
        st.subheader(':gray[Statistical Summary]')
        st.dataframe(df.describe())

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        toprows = st.slider('Top rows to view', 1, df.shape[0], key='topslider')
        st.dataframe(df.head(toprows))
    with col2:
        bottomrows = st.slider('Bottom rows to view', 1, df.shape[0], key='bottomslider')
        st.dataframe(df.tail(bottomrows))

with tab3:
    st.dataframe(df.dtypes)

with tab4:
    st.write(list(df.columns))

# Column Value Counts Section
st.subheader(':rainbow[Column Value Counts]')
with st.expander('📊 Value Count Analysis'):
    col1, col2 = st.columns(2)

    with col1:
        column = st.selectbox('🔎 Choose Column', options=list(df.columns))

    with col2:
        toprows = st.number_input('🔝 Top Rows to View', min_value=1, step=1, value=5)

    if st.button('🔍 Show Count'):
        result = df[column].value_counts().reset_index().head(toprows)
        result.columns = [column, 'Count']
        st.dataframe(result)

        st.subheader(':bar_chart: Visualizations')
        chart_type = st.selectbox('📊 Select Chart Type', ['Bar', 'Line', 'Pie'], index=0)

        # Bar Chart
        if chart_type == 'Bar':
            fig = px.bar(result, x=column, y='Count', text='Count', template='plotly_white',
                         title=f'Top {toprows} Values in {column}')
            st.plotly_chart(fig, use_container_width=True)

        # Line Chart
        elif chart_type == 'Line':
            fig = px.line(result, x=column, y='Count', text='Count', template='plotly_white',
                          title=f'Top {toprows} Values in {column}')
            st.plotly_chart(fig, use_container_width=True)

        # Pie Chart
        elif chart_type == 'Pie':
            fig = px.pie(result, names=column, values='Count', title=f'Distribution of {column}')
            st.plotly_chart(fig, use_container_width=True)

# Groupby Analysis Section
st.subheader(':rainbow[Groupby Analysis]')
with st.expander('🔎 Group and Aggregate Data'):
    col1, col2, col3 = st.columns(3)

    with col1:
        groupby_cols = st.multiselect('🧩 Group by Columns', options=list(df.columns))

    with col2:
        operation_col = st.selectbox('📊 Column for Aggregation',
                                     options=list(df.select_dtypes(include=['number']).columns))

    with col3:
        operation = st.selectbox('⚙️ Aggregation', options=['sum', 'max', 'min', 'mean', 'median', 'count'])

    if groupby_cols and operation_col and operation:
        try:
            result = df.groupby(groupby_cols, as_index=False).agg({operation_col: operation})
            st.dataframe(result)
            st.download_button('⬇️ Download Grouped Data', result.to_csv(index=False), 'groupby_result.csv')

            st.subheader(':chart_with_upwards_trend: Visualizations')
            fig = px.bar(result, x=groupby_cols[0], y=operation_col, color=groupby_cols[0],
                         title=f'{operation.capitalize()} of {operation_col} Grouped by {groupby_cols[0]}',
                         template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f'⚠️ Error during groupby operation: {str(e)}')

# Time Series Analysis Section
st.subheader(':clock1: Time Series Analysis')
with st.expander('📅 Analyze Trends Over Time'):
    col1, col2 = st.columns(2)

    with col1:
        date_col = st.selectbox('📅 Select Date/Time Column',
                                options=list(df.select_dtypes(include=['datetime64', 'object']).columns))

    with col2:
        metric_col = st.selectbox('📊 Select Metric Column',
                                  options=list(df.select_dtypes(include=['number']).columns))

    if st.button('📈 Perform Analysis'):
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            fig = px.line(df, x=date_col, y=metric_col, title=f'Time Series of {metric_col} Over Time',
                          template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f'⚠️ Error in time series analysis: {str(e)}')

# Correlation Analysis Section
st.subheader(':mag: Correlation Analysis')
with st.expander('📚 View Correlation Matrix'):
    if st.button('📊 Show Correlation'):
        try:
            corr_matrix = df.corr(numeric_only=True)
            st.write(corr_matrix.style.background_gradient(cmap='coolwarm').set_precision(2))
            fig = px.imshow(corr_matrix, text_auto=True, aspect='auto', template='plotly_white',
                            title='Correlation Matrix Heatmap')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f'⚠️ Error in correlation matrix: {str(e)}')

# Pivot Table Feature
st.subheader(':bar_chart: Pivot Table')
with st.expander('📊 Create Pivot Table'):
    index_col = st.selectbox('Select Index Column', options=list(df.columns))
    value_col = st.selectbox('Select Value Column', options=list(df.select_dtypes(include=['number']).columns))
    agg_func = st.selectbox('Choose Aggregation', ['sum', 'mean', 'count', 'max', 'min'])

    if st.button('Generate Pivot Table'):
        pivot_data = df.pivot_table(index=index_col, values=value_col, aggfunc=agg_func)
        st.dataframe(pivot_data)

# Custom Calculations Section
st.subheader(':rainbow[Custom Calculations]')
with st.expander('⚡ Perform Custom Calculations'):
    custom_formula = st.text_area('Enter custom formula using column names (e.g., A + B * 2)')
    if st.button('Apply Custom Calculation'):
        try:
            result = df.eval(custom_formula)
            st.write('Result of custom calculation:')
            st.dataframe(result)
            new_column_name = st.text_input('New Column Name')
            if st.button('Add as New Column') and new_column_name:
                df[new_column_name] = result
                st.success(f'Column "{new_column_name}" added successfully!')
                st.dataframe(df)
        except Exception as e:
            st.error(f'Error: {str(e)}')

# Export Data Section
st.subheader(':rainbow[Export Data]')
with st.expander('📥 Export Your Data'):
    export_format = st.selectbox('Choose export format', ['CSV', 'Excel', 'JSON'])
    if st.button('Export'):
        try:
            if export_format == 'CSV':
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="exported_data.csv">Download CSV File</a>'
            elif export_format == 'Excel':
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                b64 = base64.b64encode(output.getvalue()).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="exported_data.xlsx">Download Excel File</a>'
            else:
                json_data = df.to_json(orient='records')
                b64 = base64.b64encode(json_data.encode()).decode()
                href = f'<a href="data:file/json;base64,{b64}" download="exported_data.json">Download JSON File</a>'

            st.markdown(href, unsafe_allow_html=True)
            st.success('✅ File ready for download!')
        except Exception as e:
            st.error(f'⚠️ Error exporting data: {str(e)}')

# Reset to Original Data Option
if st.button('🔄 Reset to Original Data'):
    st.experimental_rerun()

else:
    st.warning("⚠️ No file uploaded yet. Please upload a file to proceed.")
