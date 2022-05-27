import pathlib
import warnings

import dash
import geopandas as gpd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import cufflinks as cf  # needed for .iplot() method

warnings.filterwarnings('ignore')

# Initialize app
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, "
                                        "initial-scale=1.0"}
    ],
)
app.title = "CRAMPON App"
server = app.server

# Load data
APP_PATH = str(pathlib.Path(__file__).parent.resolve())

status_gdf = gpd.read_file(
    'https://crampon.glamos.ch/static/CH/glacier_status.geojson'
    )
status_gdf = status_gdf.sort_values('Area', ascending=False)

# some mapbox design
mapbox_kwargs = dict(range_color=[0, 100],
                     color_continuous_scale="Rainbow_r",
                     mapbox_style="carto-positron",
                     center={"lat": 46.5, "lon": 8.4},
                     zoom=7
                     )

PERCENTILES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

DEFAULT_OPACITY = 0.5

df = status_gdf
glac_figure = px.choropleth_mapbox(status_gdf,
                                   geojson=status_gdf.geometry,
                                   locations=status_gdf.index,
                                   color="pctl",
                                   opacity=DEFAULT_OPACITY,
                                   **mapbox_kwargs
                                   )

glac_figure.update_geos(fitbounds="locations", visible=True)
glac_figure.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
glac_figure.update_traces(marker_line_width=0)

# Spinner
spinners = html.Div(
    [
        dbc.Spinner(size="sm"),
        html.Hr(),
        dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"}),
    ]
)

# App layout
app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
                    href="https://plotly.com/dash/",
                ),
                html.A(
                    html.Img(id="OGGM-logo", src="https://oggm.org/img/logos/oggm_s_alpha.png", width=75, height=30),
                    href="https://github.com/OGGM/oggm/", className="logo", style={'marginLeft': 25, 'marginRight': 25}
                ),
                html.A(
                    html.Img(id="GLAMOS-logo", src="https://www.glamos.ch/theme/img/00_Logo_GLAMOS-04.png", width=95, height=30),
                    href="https://www.glamos.ch/", className="logo", style={'marginLeft': 25, 'marginRight': 25}
                ),
                html.A(
                    html.Img(id="ETH-logo", src="https://ethz.ch/etc/designs/ethz/img/header/ethz_logo_black.svg", width=90, height=30),
                    href="https://ethz.ch/en.html", className="logo", style={'marginLeft': 25, 'marginRight': 25}
                ),
                html.A(
                    html.Img(id="WSL-logo", src="https://www.hpc-ch.org/wp-content/uploads/2013/01/WSL-logo.png", width=30, height=30),
                    href="https://www.wsl.ch/", className="logo", style={'marginLeft': 25, 'marginRight': 25}
                ),
                html.A(
                    html.Img(id="GCOS-logo", src="https://www.wcrp-climate.org/images/logos_icones/GCOS_logo.png", width=90, height=30),
                    href="https://public.wmo.int/en/programmes/global-climate-observing-system", className="logo", style={'marginLeft': 25, 'marginRight': 25}
                ),
                html.A(
                    html.Button("App Source", className="link-button"),
                    href="https://github.com/jlandmann/crampon-dash-app",
                ),
                html.A(
                    html.Button("CRAMPON Source", className="link-button"),
                    href="https://github.com/jlandmann/crampon",
                ),
                html.H4(children="CRAMPON - Current glacier mass balance in Switzerland"),
                html.P(
                    id="description",
                    children="Glaciers are accumulating and losing mass each year. "
                             "This app shows how they are doing this year with "
                             "respect to average conditions",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Select the percentiles you want to display:",
                                ),
                                dcc.RangeSlider(
                                    id="pctl-slider",
                                    min=min(PERCENTILES), max=max(PERCENTILES),
                                    step=1, value=[0, 100], marks={
                                        str(pctl): {
                                            "label": str(pctl),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for pctl in PERCENTILES
                                    },
                                    tooltip={"placement": "bottom", "always_visible": True}
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                   "Current glacier status in Switzerland",
                                   id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="glacier-choropleth",
                                    figure=glac_figure
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Histogram of average mass loss (1981-2010)",
                                    "value": "show_avg_mass_loss_fischer",
                                },
                                {
                                    "label": "Histogram of percentiles at climatology",
                                    "value": "show_pctls_at_climatology",
                                },
                            ],
                            value="show_avg_mass_loss_fischer",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("glacier-choropleth", "figure"),
    [Input("pctl-slider", "value")],
    [State("glacier-choropleth", "figure")],
)
def display_choropleth(value, glac_figure):
    df = status_gdf[(status_gdf.pctl >= value[0]) &
                    (status_gdf.pctl < value[1])]

    print(f"{len(df)} glaciers selected.")

    glac_figure = px.choropleth_mapbox(df,
                                       geojson=df.geometry,
                                       locations=df.index,
                                       hover_name='popup_html',
                                       color="pctl",
                                       **mapbox_kwargs)
    glac_figure.update_geos(fitbounds="locations", visible=True)
    glac_figure.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    glac_figure.update_traces(marker_line_width=0)
    return glac_figure


@app.callback(
    Output("selected-data", "figure"),
    [
        Input("glacier-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("pctl-slider", "value"),
    ],
)
def display_selected_data(selectedData, chart_dropdown, pctl_minmax):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select glaciers",
                paper_bgcolor="#1f2630",
                plot_bgcolor="#1f2630",
                font=dict(color="#2cfec1"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )

    pts = selectedData["points"]
    fips = [str(pt["location"]) for pt in pts]
    int_fips = [int(f) for f in fips]

    dff = status_gdf[status_gdf.index.isin(int_fips)]

    # select also by the boundaries from the RangeSlider
    dff = dff[
        (dff['pctl'] >= pctl_minmax[0]) & (dff['pctl'] <= pctl_minmax[1])]

    if chart_dropdown == "show_pctls_at_climatology":
        title = "Percentile of current year at climatology"

        fig = dff['pctl'].iplot(kind="hist", title=title, asFigure=True)

        fig_layout = fig["layout"]
        fig_data = fig["data"]

        fig_data[0]["text"] = dff.values.tolist()
        fig_layout["yaxis"]["title"] = "Selected glaciers"
        fig_layout["xaxis"]["title"] = "Percentile of current ensemble median at climatological distribution"
        fig_data[0]["marker"]["color"] = "#2cfec1"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#1f2630"
        fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#2cfec1"
        fig_layout["title"] = f"<b>{len(fips)}</b> glaciers selected"
        fig_layout["title"]["font"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

    elif chart_dropdown == "show_avg_mass_loss_fischer":
        fig = dff['avg_specif'].iplot(
            kind="hist",
            asFigure=True,
        )

        fig_layout = fig["layout"]

        # See plot.ly/python/reference
        fig_layout["yaxis"]["title"] = "Selected glaciers"
        fig_layout["xaxis"]["title"] = "Average glacier mass loss " \
                                       "1981-2010 (m w.e.)"
        fig_layout["yaxis"]["fixedrange"] = True
        fig_layout["xaxis"]["fixedrange"] = False
        fig_layout["hovermode"] = "closest"
        fig_layout["title"] = f"<b>{len(fips)}</b> glaciers selected"
        fig_layout["legend"] = dict(orientation="v")
        fig_layout["autosize"] = True
        fig_layout["paper_bgcolor"] = "#1f2630"
        fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["yaxis"]["tickfont"]["color"] = "#2cfec1"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
    else:
        # should not happen
        raise NotImplementedError('Selection is not implemented.')

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

    # todo: caching
    # todo: loading spinners
    # todo: implement CRAMPON figure triggering on many glaciers /// popup when glacier is clicked
    # todo: fix plot headings and x/y labels
    # todo: take care of crash when no glaciers are selected
    # todo: plot with area of selected glaciers
    # todo: plot with number of selected glaciers
    # todo: plot with median height, min/max height, slope, aspect, SLR equivalent (?) etc.
