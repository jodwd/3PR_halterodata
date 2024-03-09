# package imports
import dash
from dash import dash_table, dcc, callback, State, html, clientside_callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import date
import os
import frontmatter
import platform
import sqlite3 as sql
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

# set file location
cwd = os.getcwd()
file_path_in = os.path.join(cwd, 'pages', 'articles')
date_format = '%B %#d, %G' if platform.system() == 'Windows' else '%B %-d, %G'

def create_article_card(post):
    '''Create clickable card to navigate to the article'''
    date_str = post.get('date').strftime(date_format)
    card = dbc.Card(
        html.A(
            [
                dbc.CardImg(src=f'{post.get("image")}', top=True),
                dbc.CardBody(
                    [
                        html.H4(
                            f'{post.get("title")}',
                            className='card-title'
                        ),
                        html.P(
                            f'{post.get("description")}',
                            className='card-text'
                        )
                    ]
                ),
                dbc.CardFooter(
                    f'{post.get("author")} - {date_str}',
                    class_name='mb-0'
                )
            ],
            href=post.get('permalink'),
            className='text-decoration-none text-body h-100 d-flex flex-column align-items-stretch'
        ),
        class_name='article-card h-100'
    )
    return card


def create_article_page(post):
    '''Create the layout of the article page'''
    date_str = post.get('date').strftime(date_format)

    image = post.get("image")
    layout = html.Div(
        dbc.Row(
            dbc.Col(
                [
                    #html.Img(
                    #    src=f'{image}',
                    #    className='w-100'
                    #),
                    html.H1(f'{post.get("title")}', id="article_title"),
                    html.Hr(),
                    html.P(f'{post.get("author")} - {date_str}'),
                    html.Hr(),
                    dcc.Markdown(
                        post.content,
                        className='markdown'
                    ),
                    html.Div([], id="article_dash_content")
                ],
                xs=12, sm=12, md=12, lg=12, xl=12

            )
        ),
        className="article_dash_style"
    )
    return layout


# iterate over items in article page
article_cards = []
article_files = os.listdir(file_path_in)
article_files.reverse()  # reverse the list so the article show up properly

for article_name in article_files:
    # read in contents of a given article
    article_path = os.path.join(file_path_in, article_name)
    with open(article_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    publish_date = post.get('date')

    # skip articles that aren't published yet or are the sample files
    if publish_date > date.today() or article_name.startswith('sample'):
        continue

    # format image for proper sharing
    sharing_image = post.get('image').lstrip('/assets/')

    # register the specific page for the article
    dash.register_page(
        post.get("title"),
        title=post.get("tab_title"),
        description=post.get("description"),
        image=sharing_image,
        path=post.get("permalink"),
        layout=create_article_page(post)
    )
    # create the article card and add it to the list of cards
    article_cards.append(create_article_card(post))


layout = html.Div(
    [
        dbc.Col([
            dbc.Button(" Blog ", id="title-box_blog", color="light", className="titlebox_blog", size="lg"),
        ], xs=6, sm=6, md=6, lg=2, xl=2),
        dbc.Row(
            [
                dbc.Col(
                    c,
                    xs=6, sm=4, md=3, lg=2, xl=2
                ) for c in article_cards
            ],
            class_name='g-3 my-1'
        ),
    html.Br(),
    html.Br(),
    html.Link(
        rel='stylesheet',
        href='/assets/04_blog.css'
    )
    ],
    id='app_code_blog',
    className='body'
)
@callback(
    [Output("title-box_blog", "color"),
    Output("app_code_blog", "className")],
    Input("bool_light", "on")
)

def light_mode_athl(on):
    if on == True:
        button_col = "secondary"
        css_body = "body_light"
    else:
        button_col = "light"
        css_body = "body"

    return button_col, css_body;

@callback(
    [Output("article_dash_content", "children")],
    Input("article_title", "children")
)

def article_content(title):

    art_content = []
    if title=='Analyse des Echecs':
        dfarr1_2 = qry_gen_analyse_ok_ko('Arr1', 'Arr2', '')
        dfarr2_3 = qry_gen_analyse_ok_ko('Arr2', 'Arr3', '')
        dfarr1_2_3 = qry_gen_analyse_ok_ko('Arr2', 'Arr3', 'and Arr1<0')
        dfepj1_2 = qry_gen_analyse_ok_ko('EpJ1', 'EpJ2', '')
        dfepj2_3 = qry_gen_analyse_ok_ko('EpJ2', 'EpJ3', '')
        dfepj1_2_3 = qry_gen_analyse_ok_ko('EpJ2', 'EpJ3', 'and Epj1<0')

        art_content = [
            html.P("Tirer après un échec n'est jamais très agréable, surtout après une 1ère barre, mais ."),
            html.P(),
            dbc.Row([
                dbc.Col([
                    dbc.Table.from_dataframe(dfarr1_2, responsive=True, striped=True, bordered=True, hover=True)
                ], xs=12, sm=12, md=6, lg=6, xl=6),
                dbc.Col([
                    dbc.Table.from_dataframe(dfarr2_3, responsive=True, striped=True, bordered=True, hover=True)
                ], xs=12, sm=12, md=6, lg=6, xl=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Table.from_dataframe(dfepj1_2, responsive=True, striped=True, bordered=True, hover=True)
                ], xs=12, sm=12, md=6, lg=6, xl=6),
                dbc.Col([
                    dbc.Table.from_dataframe(dfepj2_3, responsive=True, striped=True, bordered=True, hover=True)
                ], xs=12, sm=12, md=6, lg=6, xl=6)
            ]),
            html.P("Dans le cas où l'athlète a raté ses 2 premiers essais, la réussite au 3ème essai est logiquement plus faible."),
            html.P("Pour l'arraché ."),
            html.P("Pour l'épaulé-jeté autour de 90% des tentatives de la dernière chance se font à +0 ou +1. Les chances de réussite baissent rapidement dès les 2kg ajoutés."),
            dbc.Row([
                dbc.Col([
                    dbc.Table.from_dataframe(dfarr1_2_3, responsive=True, striped=True, bordered=True, hover=True)
                ], xs=12, sm=12, md=6, lg=6, xl=6),
                dbc.Col([
                    dbc.Table.from_dataframe(dfepj1_2_3, responsive=True, striped=True, bordered=True, hover=True)
                ], xs=12, sm=12, md=6, lg=6, xl=6)
            ]),
        ]

    return [art_content];

def qry_gen_analyse_ok_ko(mvmt1, mvmt2, double_echec):
    qry = """SELECT case when (ABS(""" + mvmt2 + """)-ABS(""" + mvmt1 + """))>5 then '6 ou +' else (ABS(""" + mvmt2 + """)-ABS(""" + mvmt1 + """)) end as "Progression",
                     count(1) as "Nb """ + mvmt1 + """ Ratés",
                     sum(case when """ + mvmt2 + """ >0 then 1 else 0 end) as "Nb """ + mvmt2 + """ OK",
                     cast(round(100*count(1)/tot."NbEssaisTotal",0) as int) || '%' as "% Tentatives",
                     cast(round(100*sum(case when """ + mvmt2 + """>0 then 1 else 0 end)/count(1),0) as int) || '%' as "% Réussite"
                    FROM ATHLETE as ath 
                    LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                    LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                    LEFT JOIN CLUB as clb on clb.Club = cat.CATClub

                    LEFT JOIN (
                        select 1 as "FakeCol", count(1) as "NbEssaisTotal"
                        FROM ATHLETE as ath 
                        LEFT JOIN COMPET_ATHLETE as cat on cat.AthleteID= ath.AthleteID 
                        LEFT JOIN COMPET as cmp on cmp.NomCompetition = cat.CATNomCompetition 
                        LEFT JOIN CLUB as clb on clb.Club = cat.CATClub
                        WHERE """ + mvmt1 + """<0 and abs(""" + mvmt2 + """)>0 """ + double_echec +""") as tot
                    on tot.FakeCol = 1


                  WHERE """ + mvmt1 + """<0 and abs(""" + mvmt2 + """)>0 """ + double_echec +"""
                  GROUP BY case when (ABS(""" + mvmt2 + """)-ABS(""" + mvmt1 + """))>5 then '6 ou +' else (ABS(""" + mvmt2 + """)-ABS(""" + mvmt1 + """)) end"""
    df = qry_result(qry)
    return df

def qry_result(qry):
    dirname = os.path.dirname(__file__)
    path_db = os.path.join(dirname, 'dataltero.db')
    conn = sql.connect(database=path_db)
    df = pd.read_sql_query(qry, conn)
    return df;

dash.register_page(__name__, name='3PR - Blog', title='3PR - Blog', image='/assets/3PR.png', description='Tableau de bord des performances des clubs d''haltérophilie français')
