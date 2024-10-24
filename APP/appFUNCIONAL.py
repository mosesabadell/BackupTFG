import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
from influxdb_client import InfluxDBClient
import dash_bootstrap_components as dbc
import pandas as pd
import datetime

# Configuración de la conexión a InfluxDB
url = "http://192.168.1.7:8086"  # Dirección IP de tu Synology NAS
token = "amate-dadesaltaveu-auth-token"  # Reemplaza con tu token si es diferente
org = "amate"  # Reemplaza con tu organización si es diferente
bucket = "dadesaltaveu"  # Reemplaza con tu bucket si es diferente

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
                interval=2 * 1000,  # Actualizar cada 2 segundos para una visualización más fluida
                n_intervals=0
            )
        ], width=8),
        
        # Columna derecha: Descargar datos
        dbc.Col([
            html.H4("Descargar Datos", style={'color': '#d4af37'}),
            html.Label('Opciones de Descarga:'),
            html.Button('Descargar CSV', id='download-button', className='btn btn-primary'),
            dcc.Download(id='download-dataframe-csv'),
        ], width=2, style={'padding': '20px', 'background-color': '#1e1e1e'})
    ])
])

# Función para obtener el color basado en el valor promedio
def get_average_color(values, min_value, max_value):
    if not values:
        return 'green'
    avg_value = sum(values) / len(values)
    normalized = (avg_value - min_value) / (max_value - min_value) if max_value > min_value else 0
    r = int(normalized * (255 - 0) + 0)
    g = int(normalized * (165 - 255) + 255)
    b = 0
    return f'rgba({r},{g},{b},0.6)'  # Añadir transparencia

# Función para obtener datos de InfluxDB
def get_data(device_id, measurement, field, time_range='10m'):
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -{time_range})
    |> filter(fn: (r) => r["device_id"] == "{device_id}")
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")
    |> filter(fn: (r) => r["_field"] == "{field}")
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
    if not selected_device_ids:
        return [], {'display': 'none'}, {'display': 'none'}

    graphs = []

    for device_id in selected_device_ids:
        data_temp_list = []
        data_level_in_list = []
        data_level_out_list = []

        # Obtener datos de temperatura
        times_temp, values_temp = get_data(device_id, "Speaker", "temperature", time_range=selected_time_range)
        # Obtener datos de nivel de entrada
        times_level_in, values_level_in = get_data(device_id, "Speaker", "level_in", time_range=selected_time_range)
        # Obtener datos de nivel de salida
        times_level_out, values_level_out = get_data(device_id, "Speaker", "level_out", time_range=selected_time_range)

        zoom_factor = zoom_value / 100  # Convertir el valor de zoom a un factor

        if times_temp and values_temp:
            num_points_temp = int(len(times_temp) * zoom_factor)
            times_temp_zoomed = times_temp[-num_points_temp:]
            values_temp_zoomed = values_temp[-num_points_temp:]
            fill_color_temp = get_average_color(values_temp_zoomed, min(values_temp_zoomed), max(values_temp_zoomed))

            data_temp = go.Scatter(
                x=times_temp_zoomed,
                y=values_temp_zoomed,
                mode='lines+markers',  # Añadir marcadores para mejorar la fluidez visual
                line_shape='spline',  # Usar líneas suaves
                fill='tozeroy',
                line=dict(color='rgba(0,0,0,0)'),  # Línea invisible
                fillcolor=fill_color_temp,
                hoverinfo='x+y',
                name=f"Temperatura"
            )
            data_temp_list.append(data_temp)

        if times_level_in and values_level_in:
            num_points_level_in = int(len(times_level_in) * zoom_factor)
            times_level_in_zoomed = times_level_in[-num_points_level_in:]
            values_level_in_zoomed = values_level_in[-num_points_level_in:]
            fill_color_level_in = get_average_color(values_level_in_zoomed, min(values_level_in_zoomed), max(values_level_in_zoomed))

            data_level_in = go.Scatter(
                x=times_level_in_zoomed,
                y=values_level_in_zoomed,
                mode='lines+markers',  # Añadir marcadores
                line_shape='spline',  # Líneas suaves
                fill='tozeroy',
                line=dict(color='rgba(0,0,0,0)'),
                fillcolor=fill_color_level_in,
                hoverinfo='x+y',
                name=f"Nivel de Entrada"
            )
            data_level_in_list.append(data_level_in)

        if times_level_out and values_level_out:
            num_points_level_out = int(len(times_level_out) * zoom_factor)
            times_level_out_zoomed = times_level_out[-num_points_level_out:]
            values_level_out_zoomed = values_level_out[-num_points_level_out:]
            fill_color_level_out = get_average_color(values_level_out_zoomed, min(values_level_out_zoomed), max(values_level_out_zoomed))

            data_level_out = go.Scatter(
                x=times_level_out_zoomed,
                y=values_level_out_zoomed,
                mode='lines+markers',  # Añadir marcadores
                line_shape='spline',  # Líneas suaves
                fill='tozeroy',
                line=dict(color='rgba(0,0,0,0)'),
                fillcolor=fill_color_level_out,
                hoverinfo='x+y',
                name=f"Nivel de Salida"
            )
            data_level_out_list.append(data_level_out)

        layout_common = go.Layout(
            xaxis=dict(title='Tiempo'),
            xaxis_rangeslider_visible=True,
            uirevision='constant',  # Mantener el estado del gráfico entre actualizaciones
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font=dict(color='#f0f0f0')
        )

        device_graphs = [html.Hr(), html.H4(f"Dispositivo: {device_id}", style={'color': '#d4af37'})]

        if data_temp_list:
            layout_temp = layout_common.update(yaxis=dict(title='Temperatura (°C)'), title=f'Temperatura en Tiempo Real - {device_id}')
            figure_temp = {'data': data_temp_list, 'layout': layout_temp}
            device_graphs.append(dcc.Graph(figure=figure_temp))

        if data_level_in_list:
            layout_level_in = layout_common.update(yaxis=dict(title='Nivel de Entrada'), title=f'Nivel de Entrada en Tiempo Real - {device_id}')
            figure_level_in = {'data': data_level_in_list, 'layout': layout_level_in}
            device_graphs.append(dcc.Graph(figure=figure_level_in))

        if data_level_out_list:
            layout_level_out = layout_common.update(yaxis=dict(title='Nivel de Salida'), title=f'Nivel de Salida en Tiempo Real - {device_id}')
            figure_level_out = {'data': data_level_out_list, 'layout': layout_level_out}
            device_graphs.append(dcc.Graph(figure=figure_level_out))

        graphs.extend(device_graphs)

    return graphs, {'display': 'block'}, {'display': 'block'}

if __name__ == '__main__':
    app.run_server(debug=True)
