import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
from datetime import date
import datetime
import psycopg2
import os

#establishing the connection
conn = psycopg2.connect(
   database="storm", user='postgres', password='wavestorm', host='127.0.0.1', port= '5432'
)
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Executing an MYSQL function using the execute() method
cursor.execute("select version()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print("Connection established to: ",data)

command = ("""select * from surf_report;""")

print(command)
cursor.execute(command)
conn.commit()

surf_report = cursor.fetchall()
conn.commit()

columns =  ['timestamp' ,
            'surf_min' ,
            'surf_max' ,
            'surf_optimalScore' ,
            'surf_plus' ,
            'surf_humanRelation' ,
            'surf_raw_min' ,
            'surf_raw_max' ,
            'speed',
            'direction',
            'directionType',
            'gust',
            'optimalScore',
            'temperature',
            'condition']

surf = pd.DataFrame(surf_report,columns=columns)

print(surf.head())

command = ("""select * from tides;""")

print(command)
cursor.execute(command)
conn.commit()

tides = cursor.fetchall()
conn.commit()

columns_tide =  ['timestamp' ,'tide','height']

tides = pd.DataFrame(tides,columns=columns_tide)

app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
#df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Other/Dash_Introduction/intro_bees.csv")

#df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
#df.reset_index(inplace=True)
print(surf[:5])
today = date.today()
date_list = [today - datetime.timedelta(days=x) for x in range(8)]
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Ocean Beach Surf Report", style={'text-align': 'center'}),


    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": date_list[0], "value": date_list[0]},
                     {"label": date_list[1], "value": date_list[1]},
                     {"label": date_list[2], "value": date_list[2]},
                     {"label": date_list[3], "value": date_list[3]},
                     {"label": date_list[3], "value": date_list[3]},
                     {"label": date_list[4], "value": date_list[4]},
                     {"label": date_list[5], "value": date_list[5]},
                     {"label": date_list[6], "value": date_list[6]},
                     {"label": date_list[7], "value": date_list[7]}],
                 multi=False,
                 value=date_list[0],
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={}),
    dcc.Graph(id='my_bee_map2', figure={}),
    dcc.Graph(id='my_bee_map3', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure'),
     Output(component_id='my_bee_map2', component_property='figure'),
     Output(component_id='my_bee_map3', component_property='figure'),],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    if option_slctd  is None: 
        container = "No Date selected"
        option_slctd = str(date_list[0])
        container = "Date selected: {}".format(option_slctd)
    else:
        container = "Date selected: {}".format(option_slctd)
    

    print(type(option_slctd))
    surff = surf.copy()
    surff = surff[(surff["timestamp"] > datetime.datetime.strptime(option_slctd, "%Y-%m-%d")) & (surff["timestamp"] <= datetime.datetime.strptime(option_slctd, "%Y-%m-%d")+ datetime.timedelta(days=1))]  
    tidess = tides.copy()
    tidess = tidess[(tidess["timestamp"] > datetime.datetime.strptime(option_slctd, "%Y-%m-%d")) & (tidess["timestamp"] <= datetime.datetime.strptime(option_slctd, "%Y-%m-%d")+ datetime.timedelta(days=1))]  
    # Plotly Express
    fig = px.bar(surff, x='timestamp', y=['surf_min','surf_max'], text="surf_humanRelation",color_discrete_map={
                "surf_min": "lightsalmon",
                "surf_max": "indianred"},barmode='group')

    fig2 = px.scatter(surff, x="timestamp", y="speed",text="directionType",hover_data=["direction","timestamp","speed"])
    fig2.update_traces(textposition='top center')
    #fig2.add_annotation(text="directionType", x="timestamp", y="speed", arrowhead=1, showarrow=True,ax="direction")
    #fig2.update_layout()
    fig2.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                    marker_colorbar_tickangle = 110,
                    marker_symbol='arrow-right',
                  selector=dict(mode='markers'))
    fig3 = px.line(tidess,x="timestamp",y="height",text="tide")
    fig3.update_traces(textposition='top center')
    return container, fig, fig2, fig3


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)