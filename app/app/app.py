#!/usr/bin/env python
import os
from dash import Dash, html
import sqlalchemy
import pandas as pd
from dotenv import load_dotenv
import dash_bootstrap_components as dbc

print(os.environ)
load_dotenv()

engine = sqlalchemy.create_engine(
    f'postgresql://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{os.environ["POSTGRES_HOSTNAME"]}:5432/{os.environ["POSTGRES_DB"]}'
)


def create_html_row(row: pd.Series):
    return html.Tr([html.Td(row["title"]), html.Td(html.Img(src=row["image_url"]))])


def serve_layout():
    df = pd.read_sql("SELECT * FROM reality LIMIT 500", con=engine)

    l = html.Div(
        [
            html.H1("List of available flats"),
            html.Table([create_html_row(row) for _, row in df.iterrows()]),
        ],
        style={"padding": "40px"},
    )

    return l


app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = serve_layout

if __name__ == "__main__":
    app.run(host="0.0.0.0")
