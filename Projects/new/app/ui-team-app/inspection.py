# inspection.py
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import pickle
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import seaborn as sns
from millify import millify  # shortens values (10_000 ---> 10k)
from streamlit_extras.metric_cards import style_metric_cards  # beautify metric card with css

############################################ FUNCTIONS ##################################################################

# Function to load data
def load_data():
    data = pd.read_csv(DATA_URL)
    return data

# Function to apply custom styling to the multiselect dropdown
def apply_custom_style(multiselect):
    multiselect = st.markdown(
        """
        <style>
            .multiselect-container .multiselect-selected-text {
                background-color: #f0f8ff; /* Light blue background */
                color: black; /* Black text */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    multiselect = st.markdown(
        """
        <style>
            .multiselect-container.dropdown-menu {
                background-color: black; /* black background */
                color: white
            }
        </style>
        """,
        unsafe_allow_html=True
    )

# Encoding Function
def encoding(item):
    if item in ['Pass', 'None']:
        return 1
    elif item in ['Minor', 'Fail', 'Within past year', 'Flagged']:
        return 2
    elif item in ['Within past 1-3 years', 'Major']:
        return 3
    elif item < 200:
        return 1
    elif 200 <= item <= 500:
        return 2
    else:
        return 3

# Prediction Function
def risk_predict(input_data):
    input_data = input_data.apply(lambda x: x.map(encoding))
    encoded_data = input_data.copy()
    cols = input_data.columns
    prediction = model.predict(input_data)
    prediction = pd.DataFrame(prediction, columns=['Prediction'])

    probability = model.predict_proba(input_data)
    column_titles = ['High %', 'Low %', 'Moderate %']
    pd.set_option('display.float_format', '{:.1f}'.format)
    pb_array = pd.DataFrame(probability * 100, columns=column_titles)
    pb_array = pb_array.round(1)

    if hasattr(model.best_estimator_, 'feature_importances_'):
        features = model.best_estimator_.feature_importances_
        feature_impo = pd.Series(features, index=cols)
        feature_impo = feature_impo.sort_values(ascending=False)
    else:
        feature_impo = pd.Series()
        st.warning("The selected model does not provide feature importances.")

    return prediction, pb_array, feature_impo, encoded_data

############################################ LOAD DATA ##################################################################

DATA_URL = "../../data/df_dashboard_predicted.csv"

df = load_data()
df = df.fillna('None')

############################################ LOAD MODEL ##################################################################

model_path = '../../models/RiskPredictor_XGB_v3.pkl'
with open(model_path, 'rb') as file:
    model = pickle.load(file)

############################################  WEBPAGE DESIGN ##################################################################

def inspection():
    st.sidebar.title("Filter Pane")

    dash_1 = st.container()
    with dash_1:
        st.markdown("<h2 style='text-align: center;'>Regulatory Compliance Dashboard</h2>", unsafe_allow_html=True)
        st.write("")

    st.markdown("""---""")
    st.sidebar.header("Please Filter Here:")

    with st.sidebar.expander("Select Filters"):
        infraction_type = st.multiselect(
            "Infraction Type:",
            options=df["Infraction Type"].unique(),
            default=df["Infraction Type"].unique()
        )
        apply_custom_style(infraction_type)

        infraction_timeline = st.multiselect(
            "Infraction Timeline:",
            options=df["Infraction Timeline"].unique(),
            default=df["Infraction Timeline"].unique(),
        )
        apply_custom_style(infraction_timeline)

        inspection_results = st.multiselect(
            "Inspection Results:",
            options=df["Inspection Results"].unique(),
            default=df["Inspection Results"].unique(),
        )
        apply_custom_style(inspection_results)

        predicted_risk_category = st.multiselect(
            "Risk Category:",
            options=df["Predicted Risk Category"].unique(),
            default=df["Predicted Risk Category"].unique(),
        )
        apply_custom_style(predicted_risk_category)

        sentiment_analysis = st.multiselect(
            "Sentiment Analysis:",
            options=df["Sentiment Analysis"].unique(),
            default=df["Sentiment Analysis"].unique(),
        )
        apply_custom_style(sentiment_analysis)

    df_selection = df.query(
        "`Infraction Type` == @infraction_type & `Infraction Timeline` == @infraction_timeline & `Inspection Results` == @inspection_results & `Predicted Risk Category` == @predicted_risk_category & `Sentiment Analysis` == @sentiment_analysis"
    )

    if df_selection.empty:
        st.warning("No data available based on the current filter settings!")
        st.stop()

    dash_2 = st.container()
    with dash_2:
        compliance_rate = round((df_selection[df_selection["Inspection Results"] == 'Pass'].shape[0] / df_selection["Entity ID"].count() * 100), 2)
        total_clients = int(df_selection["Annual Clients"].sum())
        repeat_offender_count = (df_selection["Infraction Type"] != 'None').sum()
        total_entities = df_selection["Entity ID"].count()
        repeat_offender_rate = round((repeat_offender_count / total_entities) * 100, 2)
        failure_count = (df_selection['Inspection Results'] == 'Fail').sum()
        total_count = df_selection['Entity ID'].count()
        inspection_failure_rate = round((failure_count / total_count) * 100, 2)

        columns = st.columns(4)

        with columns[0]:
            st.metric(label="Compliance Rate", value=f"{compliance_rate}%")
            style_metric_cards(background_color="#333840", border_left_color="#DBF227")

        with columns[1]:
            st.metric(label="Annual Clients", value=f"{total_clients:,}")
            style_metric_cards(background_color="#333840", border_left_color="#DBF227")

        with columns[2]:
            st.metric(label="Repeat Offender Rate", value=f"{repeat_offender_rate}%")
            style_metric_cards(background_color="#333840", border_left_color="#DBF227")

        with columns[3]:
            st.metric(label="Inspection Failure Rate", value=f"{inspection_failure_rate}%")
            style_metric_cards(background_color="#333840", border_left_color="#DBF227")

    st.write("#### Risk Category Distribution")
    grouped_data_risk = df_selection.groupby("Predicted Risk Category").size().reset_index(name="Entity Count")
    fig = px.scatter(grouped_data_risk, 
                     x="Predicted Risk Category", 
                     y="Entity Count", 
                     size="Entity Count", 
                     color="Predicted Risk Category",  
                     hover_name="Predicted Risk Category",
                     size_max=60)
    fig.update_layout(
                      xaxis_title="Predicted Risk Category",
                      yaxis_title="Count of Entities")
    st.plotly_chart(fig)

    st.markdown("""---""")
    st.write("#### Distribution of Sentiment Analysis with Inspection Results")
    grouped_data_ = df_selection.groupby(['Sentiment Analysis', 'Inspection Results']).size().reset_index(name='Count')

    color_discrete_map = {
        'Pass': 'rgba(101, 146, 98, 0.5)',   
        'Fail': 'rgba(255, 106, 116, 0.5)',  
        'None': 'rgba(176, 190, 197, 0.5)'   
    }

    fig = px.bar(grouped_data_, x='Sentiment Analysis', y='Count', color='Inspection Results', 
                 barmode='stack', color_discrete_map=color_discrete_map)

    fig.update_layout(
        xaxis_title='Sentiment Analysis',
        yaxis_title='Count of Entity ID',
        yaxis=dict(showgrid=False)
    )

    st.plotly_chart(fig)

    st.markdown("""---""")

    st.write(f"#### Client Volume Analysis by Risk and Inspection Outcomes")
    x_axis = st.selectbox("Select X-axis:", ["Inspection Results","Predicted Risk Category"])
    y_axis='Annual Clients'

    fig = px.scatter(df_selection, x=x_axis, y=y_axis, color=x_axis, title=f"{y_axis} vs {x_axis}")
    fig.update_layout(xaxis_title=x_axis, yaxis_title=y_axis)
    st.plotly_chart(fig)

    st.markdown("""---""")

    columns_to_remove = ['Entity ID','Total Risk Score','Phone Number','Address','Risk Category']
    df_feature_imp= df_selection.copy()
    df_feature_imp = df_feature_imp.drop(columns=columns_to_remove)

    for column in ['Infraction Type', 'Infraction Timeline', 'Public Complaints', 'Sentiment Analysis', 'Inspection Results']:
        df_feature_imp[column] = df_feature_imp[column].apply(encoding)

    y = df_feature_imp['Predicted Risk Category']
    X = df_feature_imp.drop(columns=['Predicted Risk Category'])  

    model_rf = RandomForestClassifier()
    model_rf.fit(X, y)

    feature_importances = pd.Series(model_rf.feature_importances_, index=X.columns).sort_values(ascending=False)

    feature_importances_percentage = (feature_importances / feature_importances.sum()) * 100

    plt.figure(figsize=(10, 8))
    sns.heatmap(feature_importances_percentage.to_frame(), annot=True, cmap="YlGnBu", fmt=".2f")
    plt.title('Feature Importance (%)')
    plt.xlabel('Features')
    plt.ylabel('Importance')
    st.pyplot(plt)

    st.markdown("""---""")
    table_columns = ["Entity ID","Annual Clients","Infraction Type","Infraction Timeline","Public Complaints","Sentiment Analysis","Inspection Results","Predicted Risk Category","Phone Number","Address"]
    table_data = df_selection[table_columns]
    st.write("#### Data Table")
    st.dataframe(table_data)

    st.markdown("""---""")
    st.markdown("<h1 style='font-size:35px;text-align:center;'>Make a Prediction</h1>", unsafe_allow_html=True)

    with st.expander("Enter Data Manually", expanded=True):
        st.markdown("<h1 style='font-size:20px;text-align:center;'>Select data from the dropdowns</h1>", unsafe_allow_html=True)
        
        clients = st.number_input("Number of clients served annually", min_value=0, step=1)
        infraction_type = st.selectbox("Infraction type", ["Major", "Minor", "None"])
        infraction_timeline = st.selectbox("Infraction timeline", ["Within past 1-3 years", "Within past year", "None"])
        public_complaints = st.selectbox("Public complaints", ["Major", "Minor", "None"])
        sentiment_analysis = st.selectbox("Sentiment analysis", ["Flagged", "None"])
        inspection_results = st.selectbox("Inspection results", ["Pass", "Fail", "None"])

        if st.button('Risk Analysis Result!', key='risk_analysis_button', help="Button to trigger risk analysis"):
            data = {'Annual Clients': [clients], 'Infraction Type': [infraction_type],
                    'Infraction Timeline': [infraction_timeline], 'Public Complaints': [public_complaints],
                    'Sentiment Analysis': [sentiment_analysis], 'Inspection Results': [inspection_results]}
            input_data = pd.DataFrame(data)
            st.write(input_data)
            predict, probability, feature, encoded_data = risk_predict(input_data)
            st.success("Risk Prediction & Probability:")
            concat_df = pd.concat([probability, predict], axis=1)
            st.write(concat_df)

            st.markdown("<h2 style='font-size:18px;text-align:center;'>Feature Importance</h2>", unsafe_allow_html=True)
            st.bar_chart(feature)
