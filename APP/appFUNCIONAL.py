import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
from influxdb_client import InfluxDBClient
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import colorlover as cl  # Importar colorlover para las escalas de colores

# Configuración de la conexión a InfluxDB
url = "http://localhost:8086"  # Cambia si tu InfluxDB está en otro lugar
token = "amate-dadesaltaveu-auth-token"  # Reemplaza con tu token
org = "amate"  # Reemplaza con tu organización
bucket = "dadesaltaveu"  # Reemplaza con tu bucket

# Crear el cliente de InfluxDB
client = InfluxDBClient(url=url, token=token, org=org)
query_api = client.query_api()

# Función para obtener la lista de device_id
def get_device_ids():
    query = f'''
    import "influxdata/influxdb/schema"
    schema.tagValues(
        bucket: "{bucket}",
        tag: "device_id"
    )
    '''
    try:
        tables = query_api.query(query)
        device_ids = []
        for table in tables:
            for record in table.records:
                device_ids.append(record.get_value())
        return device_ids
    except Exception as e:
        print(f"Error al obtener device_ids: {e}")
        return []

# Crear la aplicación Dash con el tema oscuro
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "Visualización de Datos de InfluxDB"

# Diseño de la aplicación
app.layout = dbc.Container(fluid=True, children=[
    # Fila superior: Control de zoom
    dbc.Row([
        dbc.Col([
            html.H2("Control de Zoom", className="text-center", style={'color': '#d4af37'}),
            dcc.Slider(
                id='zoom-slider',
                min=10,
                max=100,
                step=10,
                value=100,
                marks={i: f'{i}%' for i in range(10, 101, 10)},
                tooltip={'always_visible': False, 'placement': 'bottom'}
            )
        ])
    ], style={'padding': '20px'}),
    # Fila principal: Columnas izquierda, central y derecha
    dbc.Row([
        # Columna izquierda: Selección de dispositivo y rango de tiempo
        dbc.Col([
            html.H4("Seleccionar Dispositivo", style={'color': '#d4af37'}),
            dcc.Checklist(
                id='device-checklist',
                options=[{'label': device_id, 'value': device_id} for device_id in get_device_ids()],
                value=[],  # Por defecto, ninguna casilla está marcada
                labelStyle={'display': 'block'},
                style={'margin-bottom': '20px'}
            ),
            html.Label('Rango de Tiempo:'),
            dcc.Dropdown(
                id='time-range-dropdown',
                options=[
                    {'label': 'Últimos 10 minutos', 'value': '10m'},
                    {'label': 'Última hora', 'value': '1h'},
                    {'label': 'Últimas 24 horas', 'value': '24h'},
                ],
                value='10m',
                style={'margin-bottom': '20px'}
            ),
        ], width=2, style={'padding': '20px', 'background-color': '#1e1e1e'}),
        # Columna central: Visualización de datos
        dbc.Col([
            html.H4("Datos en Tiempo Real", id='data-header', style={'display': 'none', 'color': '#d4af37'}),
            html.Div(id='graphs-container', children=[], style={'display': 'none'}),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # Actualizar cada 1 segundo
                n_intervals=0
            )
        ], width=8),
        # Columna derecha: Descargar datos
        dbc.Col([
            html.H4("Descargar Datos", style={'color': '#d4af37'}),
            html.Label('Opciones de Descarga:'),
            html.Button('Descargar CSV', id='download-button', className='btn btn-primary'),
            dcc.Download(id='download-dataframe-csv'),
        ], width=2, style={'padding': '20px', 'background-color': '#1e1e1e'}),
    ])
])

# Función para obtener el color basado en el valor promedio
def get_average_color(values, min_value, max_value):
    if not values:
        return 'green'
    avg_value = sum(values) / len(values)
    normalized = (avg_value - min_value) / (max_value - min_value) if max_value > min_value else 0
    # Interpolar entre verde (0,255,0) y naranja (255,165,0)
    r = int(normalized * (255 - 0) + 0)
    g = int(normalized * (165 - 255) + 255)
    b = 0
    return f'rgba({r},{g},{b},0.6)'  # Añadir transparencia

# Función para obtener datos de InfluxDB
def get_data(device_id, field, time_range='10m'):
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -{time_range})
    |> filter(fn: (r) => r["device_id"] == "{device_id}")
    |> filter(fn: (r) => r._measurement == "Temperature")
    |> filter(fn: (r) => r._field == "{field}")
    |> sort(columns: ["_time"])
    '''
    try:
        tables = query_api.query(query)
        times = []
        values = []
        for table in tables:
            for record in table.records:
                times.append(record.get_time())
                values.append(record.get_value())
        return times, values
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return [], []

# Callback para actualizar las gráficas
@app.callback(
    [Output('graphs-container', 'children'),
     Output('graphs-container', 'style'),
     Output('data-header', 'style')],
    [Input('interval-component', 'n_intervals'),
     Input('device-checklist', 'value'),
     Input('time-range-dropdown', 'value'),
     Input('zoom-slider', 'value')]
)
def update_graphs(n_intervals, selected_device_ids, selected_time_range, zoom_value):
    # Si no hay dispositivos seleccionados, no mostramos las gráficas
    if not selected_device_ids:
        return [], {'display': 'none'}, {'display': 'none'}

    # Lista para almacenar las gráficas
    graphs = []

    for device_id in selected_device_ids:
        # Inicializar listas de datos para las gráficas del dispositivo actual
        data_temp_list = []
        data_nivell_list = []

        # Obtener datos de temperatura
        times_temp, values_temp = get_data(device_id, 'temperature', time_range=selected_time_range)
        # Obtener datos de nivell
        times_nivell, values_nivell = get_data(device_id, 'nivell', time_range=selected_time_range)

        # Aplicar zoom
        zoom_factor = zoom_value / 100  # Convertir el valor de zoom a un factor

        # Datos para la gráfica de temperatura
        if times_temp and values_temp:
            num_points_temp = int(len(times_temp) * zoom_factor)
            times_temp_zoomed = times_temp[-num_points_temp:]
            values_temp_zoomed = values_temp[-num_points_temp:]
            # Obtener color promedio
            fill_color_temp = get_average_color(values_temp_zoomed, min(values_temp_zoomed), max(values_temp_zoomed))

            data_temp = go.Scatter(
                x=times_temp_zoomed,
                y=values_temp_zoomed,
                mode='lines',
                fill='tozeroy',
                line=dict(color='rgba(0,0,0,0)'),  # Línea invisible
                fillcolor=fill_color_temp,
                hoverinfo='x+y',
                name=f"Temperatura"
            )
            data_temp_list.append(data_temp)
        else:
            data_temp_list = []

        # Datos para la gráfica de nivell
        if times_nivell and values_nivell:
            num_points_nivell = int(len(times_nivell) * zoom_factor)
            times_nivell_zoomed = times_nivell[-num_points_nivell:]
            values_nivell_zoomed = values_nivell[-num_points_nivell:]
            # Obtener color promedio
            fill_color_nivell = get_average_color(values_nivell_zoomed, min(values_nivell_zoomed), max(values_nivell_zoomed))

            data_nivell = go.Scatter(
                x=times_nivell_zoomed,
                y=values_nivell_zoomed,
                mode='lines',
                fill='tozeroy',
                line=dict(color='rgba(0,0,0,0)'),  # Línea invisible
                fillcolor=fill_color_nivell,
                hoverinfo='x+y',
                name=f"Nivell"
            )
            data_nivell_list.append(data_nivell)
        else:
            data_nivell_list = []

        # Crear el layout para ambas gráficas
        layout_temp = go.Layout(
            xaxis=dict(title='Tiempo'),
            yaxis=dict(title='Temperatura (°C)'),
            title=f'Temperatura en Tiempo Real - {device_id}',
            xaxis_rangeslider_visible=True,
            plot_bgcolor='#1e1e1e',  # Fondo del gráfico
            paper_bgcolor='#1e1e1e',  # Fondo del papel
            font=dict(color='#f0f0f0')  # Color de las etiquetas
        )

        layout_nivell = go.Layout(
            xaxis=dict(title='Tiempo'),
            yaxis=dict(title='Nivell'),
            title=f'Nivell en Tiempo Real - {device_id}',
            xaxis_rangeslider_visible=True,
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font=dict(color='#f0f0f0')
        )

        # Crear las figuras
        device_graphs = [html.Hr(), html.H4(f"Dispositivo: {device_id}", style={'color': '#d4af37'})]

        if data_temp_list:
            figure_temp = {'data': data_temp_list, 'layout': layout_temp}
            device_graphs.append(dcc.Graph(figure=figure_temp))
        else:
            device_graphs.append(html.Div(f"No hay datos de temperatura para el dispositivo {device_id}"))

        if data_nivell_list:
            figure_nivell = {'data': data_nivell_list, 'layout': layout_nivell}
            device_graphs.append(dcc.Graph(figure=figure_nivell))
        else:
            device_graphs.append(html.Div(f"No hay datos de nivell para el dispositivo {device_id}"))

        # Añadir las gráficas del dispositivo a la lista principal
        graphs.extend(device_graphs)

    return graphs, {'display': 'block'}, {'display': 'block'}

# Callback para descargar los datos
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('download-button', 'n_clicks'),
    State('device-checklist', 'value'),
    State('time-range-dropdown', 'value'),
    prevent_initial_call=True)
def download_data(n_clicks, selected_device_ids, selected_time_range):
    dfs = []
    for device_id in selected_device_ids:
        times_temp, values_temp = get_data(device_id, 'temperature', time_range=selected_time_range)
        times_nivell, values_nivell = get_data(device_id, 'nivell', time_range=selected_time_range)

        if times_temp and values_temp:
            df_temp = pd.DataFrame({'Tiempo': times_temp, 'Temperatura': values_temp, 'Device_ID': device_id})
        else:
            df_temp = pd.DataFrame()

        if times_nivell and values_nivell:
            df_nivell = pd.DataFrame({'Tiempo': times_nivell, 'Nivell': values_nivell, 'Device_ID': device_id})
        else:
            df_nivell = pd.DataFrame()

        # Unir los DataFrames en base al tiempo y Device_ID
        if not df_temp.empty and not df_nivell.empty:
            df = pd.merge(df_temp, df_nivell, on=['Tiempo', 'Device_ID'], how='outer').sort_values('Tiempo')
        elif not df_temp.empty:
            df = df_temp
        elif not df_nivell.empty:
            df = df_nivell
        else:
            df = pd.DataFrame()

        if not df.empty:
            dfs.append(df)

    if dfs:
        df_all = pd.concat(dfs)
        filename = f"datos_{selected_time_range}.csv"
        return dcc.send_data_frame(df_all.to_csv, filename, index=False)
    else:
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
