#!/usr/bin/env python
# coding: utf-8

# # Datenanalyse 

# In diesem Notebook wird die vorbereitete Tabelle mit den Spielen der Season 2021/2022 und zugehörigen Sentimentwerten analysiert. Dafür werden zuerst Diagramme zu alle Spiele und anschließend zu einzelnen Teams erstellt. Das Ziel ist so zu überpüfen, ob ein Zusammenhang zwischen Stimmung und Spielausgang besteht. 

# In[1]:


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
import ipywidgets as widgets
from scipy.stats import ttest_ind


# In[2]:


df_summary = pd.read_csv('summary_2021.csv')


# ## Auswertung Season 

# Die nachfolgende Treemap ist eine erste Übersicht über die reguläre Season. Es werden die fünf Mannschaften dargestellt, welche pro Woche den höchsten durchschnittlichen Sentiment-Score erreicht haben. 

# In[3]:


df_top = df_summary[['week', 'team_by_entity', 'avg_score']].sort_values(by=['week','avg_score'], ascending=False).groupby('week').head(5)


# In[4]:


df_top


# In[5]:


df = px.data.tips()
fig = px.treemap(df_top, path=[px.Constant("all"), 'week', 'team_by_entity'], values='avg_score')
fig.update_traces(root_color="lightgrey")
fig.show()


# Die Größe der Fläche lässt darauf schließen, dass Woche 8 und Woche 12 die Wochen mit den höchsten durchschnittlichen Sentimenscores waren. Dagegen weisen Woche 10 und Woche 3 deutlich geringer durchschnittliche Sentimentwerte auf. 
# In Woche 8 und 12 sind 49ers die Mannschaft mit den höchsten und Jaguars die Mannschaft mit den zweithöchsten Sentiment-Score Dies wird im nachfolgenden Linienplot überprüft: 

# In[6]:


fig = px.line(df_summary, x="week", y="avg_score", color = "team_by_entity")
fig.show()


# In dem obenstehenden Plot werden die durchschnittlichen Sentiment-Scores aller Teams über die Season 2021/2022 dargestellt. Mit der Legende können einzelnen Mannschaften ein- oder ausgeblendet werden. 
# 
# In der Regel liegen die Sentiment-Scores aller Mannschaften zwischen -0.2 und 0.3. Auffällig sind lokale Hochpunkte bei den Vikings in Woche 18, bei den Jaguars in Woche 8 und bei den 49ers in Woche 12, wie auch in der Treemap gezeigt. 
# Lokale Tiefpunkte befinden sich bei den Lions in Woche 6, bei den Patriots in Woche 18 und bei den Panthers in Woche 17.  
# 
# Im vorhergenden Graphen ist erkennbar, dass ab Woche 4 wesentlich mehr Streuung in den Avg-Scores enthalten ist. Dies kann an der Kappungsgrenze auf 80 Kommentare je Video ab Woche 4 liegen. D.h. die Anzahl der Kommentare könnte einen Einfluss auf die Streuung des Durchschnittswerts haben.
# Daher wird nachfolgend die Anzahl der Kommentare untersucht.

# In[7]:


fig = px.bar(df_summary, x='week',  y=["count_neutral", "count_pos", "count_neg"])
fig.show()


# Wie vermutet, übersteigt die Anzahl der Kommentare bis Woche 4 deutlich alle anderen Wochen. Das kann zur Verzerrrung des Ergebnisses führen. Aus diesem Grund werden nachfolgend nur die Wochen 5-18 betrachetet.  

# In[8]:


df_summary = df_summary[df_summary['week'] > 4]


# Betrachtet man die restlichen Wochen, verteilen sich die Kommentare der Mannschaften auf ein Sepkturm von 66 (Jaguars) und 239  (Bills) Kommentaren pro Team. Dabei erhielten die Bills die meisten positiven und neutralen Kommentare. Die Texans dagegen führen das Balkendiagram mit den meisten negativen Kommentaren an. 

# In[9]:


fig = px.bar(df_summary, x='team_by_entity',  y=["count_neutral", "count_pos", "count_neg"])
fig.show()


# Die oben erwähnten lokalen Mimimum- und Maximumpunkte werden im folgenden näher untersucht. 
# * Maximum
#     * Vikings in Woche 18
#     * Jaguars in Woche 8
#     * 49ers in Woche 12
# * Minimum 
#     * Lions in Woche 6
#     * Patriots in Woche 18 
#     * Panthers in Woche 17
# 

# In[10]:


panthers = df_summary[df_summary["team_by_entity"]=="Panthers"]

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Bar(name='Postiv', x=panthers.week, y=panthers.count_pos))
    
fig.add_trace(go.Bar(name='Negative', x=panthers.week, y=panthers.count_neg)
)

fig.add_trace(go.Bar(name='Neutral', x=panthers.week, y=panthers.count_neutral)
)

fig.add_trace(
    go.Scatter(x=panthers.week, y=panthers.avg_score, name="Average Score"),
    secondary_y=True,
)

# Add figure title
fig.update_layout(
    title_text="Example Panthers"
)

# Set x-axis title
fig.update_xaxes(title_text="Week")

# Set y-axes titles
fig.update_yaxes(title_text="<b>primary</b> Count comments", secondary_y=False)
fig.update_yaxes(title_text="<b>secondary</b> Average Sentiment Score", secondary_y=True)

fig.show()


# Bei dem erwähnten Spiel der Panthers steht der geringe Sentimentscore mit einer sehr geringen Anzahl an Kommentaren im Zusammenhang (ein negativer Kommentar). Bei den lokalen Extrempunkten der Jaguars, 49ers und Patriots ist es ähnlich. Durch die Kommentargrenze konnten hier zuwenig Kommentare mit der jeweiligen Entität ausgewertet werden. 
# Für die Spiele der Lions und Vikings liegen an den Ausreißern fünf oder mehr Kommentare vor. Für die weitere Analyse werden nur Spiele mit mindestens fünf Kommentaren betrachtet, um die Verzerrung zu minimieren. Optimal wäre ein Abruf aller Kommentare und deren Auswertung zu Entitäten ohne Kommentargrenze.

# In[11]:


df_summary= df_summary[df_summary['count_neg']+df_summary['count_pos']+df_summary['count_neg']>5]
df_summary


# Um die Leistung eines NFL-Teams zu bewerten, wird in der NFL der PCT verwendet. Der PCT beschreibt den prozentualen Anteil gewonnener Spiele in der regulären Season. Dieser wird im folgenden für alle Mannschaften berechnet mit der oben genannten Einschränkung von min. fünf Kommentaren. 

# In[24]:


def count_outcome(inp_series, outcome_value): 
    try: 
        count = inp_series.value_counts()[outcome_value]
    except: 
        count = 0
    return count


# In[25]:


pct= df_summary.groupby(['team_by_entity']).agg(
                                    win=('outcome', lambda x: count_outcome(x, 'win')),
                                    total=('outcome', 'count'), 
                                    score=('avg_score', 'mean'))
pct['percentage'] = pct['win']/pct['total']


# In[20]:


pct.reset_index(inplace=True)


# In[21]:


pct


# Es soll untersucht werden, ob ein Zusammenhang zwischen dem durchschnittlichen Sentiment und dem PCT, bezogen auf die Gesamtleistung, in der Season besteht. Dafür wird im ersten Schritt die Beziehung graphisch in einem Scatterplot untersucht. Die Punkteverteilung und die eingezeichnet Trendlinie lässt einen linearen Zusammenhang vermuten. 

# In[15]:


fig = px.scatter(pct, x= "percentage", y="score", hover_data=['team_by_entity'], trendline="ols", trendline_color_override="red")
fig.show()


# Im zweiten Schritt wird der Zusammenhang mit einem linearen Regression-Modell überprüft. Dazu wird eine in plotly integrierte statsmodel-Funktion genutzt. Der Fokus der Regressionsbewertung liegt auf R-squared und P-Value zu x1. 

# In[22]:


results = px.get_trendline_results(fig)
print(results)


# In[23]:


results.px_fit_results.iloc[0].summary()


# In der Bewertung des Modells bestätigt der P-Wert einen linearen Zusammenhang. Der R-squared ist jedoch sehr niedrig. Aus diesem Grund lässt sich ein Zusammenhang zwischen dem durchschnittlichen Sentimentscore und Leistung der Mannschaft nicht eindeutig nachweisen. Möglicherweise wird die Güte des Modells (R-squared) deutlich besser, wenn wie oben beschrieben alle Kommentare zur Analyse genutzt werden.

# ## Auswertung Mannschaft

# In den bisherigen Abschnitten wird die gesamte Season betrachtet. Im Kapitel "Auswertung Mannschaft" liegt der Fokus auf einer Mannschaft und deren Leistung im Verlauf der Season. Über das Dropdown-Menü-Widget kann eine Mannschaft ausgewählt werden. Standardmäßig sind Los Angeles Chargers ausgewählt. 

# In[35]:


liste_teams = df_summary['team_by_entity'].unique()


# In[36]:


widget = widgets.Dropdown(
    options= liste_teams,
    value='Chargers',
    description='Number:',
    disabled=False,
)


# In[37]:


display(widget)


# In[38]:


widget.value


# In[39]:


team_df = df_summary[df_summary['team_by_entity'] == widget.value]
team_df


# Ím ersten Plot wird der Anteil an positiven, negativen und neutralen Kommentaren pro Spiel dargestellt. 

# In[56]:


fig = go.Figure()

fig.add_trace(go.Scatter(
    x=team_df['week'], y=team_df['count_pos'],
    mode='lines',
    line=dict(width=0.5, color='rgb(184, 247, 212)'),
    stackgroup='one',
    groupnorm='percent', # sets the normalization for the sum of the stackgroup
    name = "positive"
))
fig.add_trace(go.Scatter(
    x=team_df['week'], y=team_df['count_neutral'],
    mode='lines',
    line=dict(width=0.5, color='rgb(111, 231, 219)'),
    stackgroup='one', 
    name = "neutral"
))
fig.add_trace(go.Scatter(
    x=team_df['week'], y=team_df['count_neg'],
    mode='lines',
    line=dict(width=0.5, color='rgb(127, 166, 238)'),
    stackgroup='one', 
    name = "negative"
))

fig.update_layout(
    showlegend=True,
    xaxis_type='category',
    xaxis_title= "week",
    yaxis_title="percentage comments",
    yaxis=dict(
        type='linear',
        range=[1, 100],
        ticksuffix='%'))

fig.show()


# In Woche 8 erhielten die Chargers zum Beispiel prozentual die meisten negativen Kommentare und in Woche 14 die meisten positven Kommentare. Die Flächenverhältnisse vermitteln eine schwankende Stimmung im Zeitverlauf. 
# Im Folgenden soll untersucht werden, ob es ein Zusammenhang mit den Spielergebnissen in dieser Season gibt.  

# In[57]:


team_df['total_number'] = team_df['count_pos']+team_df['count_neg']+team_df['count_neutral']


# In[58]:


fig = px.scatter(team_df, x="week", y="count_pos", color="outcome", size = 'total_number')
fig.show()


# Der Scatterplot stellt die Woche, die Anzahl der positiven Kommentare, den Ausgang und die gesamte Anzahl an Kommentaren (Bubble-Größe) dar. Die meisten positiven Kommentare verbunden mit einem Sieg gab es in Woche 13. In der Woche 12 ohne postive Kommentare haben die Chargers verloren. Ein Zusammenhang lässt sich trotzdem nicht klar sehen, da zum Beispiel Woche 17 siegreich, aber mit wenigen positiven Kommentaren war. Die Bubble-Größe lässt, aber auch auf wenige Kommentare in dieser Woche schließen.  
# Hinweis: Woche 7, Woche 9 und Woche 10 fehlen, da weniger als 5 Kommentare mit Entität Chargers ausgelesen wurden.

# In[59]:


fig = px.box(team_df, x="outcome", y="avg_score")
fig.show()


# In den Bloxplot-Diagrammen wird die Verteilung des Average-Sentimentscores pro Spiel nach Sieg und Niederlage gruppiert. Der Median der siegreichen Spiele ist deutlich höher als der der Niederlagen-Box. Der obere Whisker der Niederlagen liegt unter diesem.  Die Verteilungen von Win und Defeat lassen einen Unterschied vermuten, welcher nachfolgend noch durch einen t-Test untersucht wird.

# Der t-Test wird wie folgt interpretiert: 
# 
# Nullhypothese: Es gibt **keinen** signifikanten Sentiment-Unterschied bei Sieg oder Niederlage.  
# AltHypothese: Es gibt **einen** signifikanten Sentiment-Unterschied bei Sieg oder Niederlage.

# In[70]:


group1 = team_df[team_df['outcome']== 'win']
group2 = team_df[team_df['outcome']== 'defeat']
pvalue= ttest_ind(group1['avg_score'], group2['avg_score']).pvalue
if (pvalue < 0.05):
    print (pvalue)
    print ("Es gibt einen signifikaten Unterschied zwischen Sieg und Niederlage in der Stimmung. Die Nullhypothese wird verworfen.")
else:
    print (pvalue)
    print ("Es gibt keinen signifikaten Unterschied zwischen Sieg und Niederlage in der Stimmung.Die Nullhypothese wird nicht verworfen.")


# Wie bei den bisherigen Betrachtungen ist zu bedenken, dass die Kommentaranzahl gering ist. Ebenfalls wurde eine Normalverteilung nur angenommen. 
