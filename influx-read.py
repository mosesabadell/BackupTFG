import sys
import time
from influxdb_client import InfluxDBClient
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from datetime import datetime

# Configuración de la conexión
url = "http://localhost:8086"
token = "amate-dadesaltaveu-auth-token"  # Reemplaza con tu token
org = "amate"
bucket = "dadesaltaveu"

# Crear el cliente para InfluxDB
client = InfluxDBClient(url=url, token=token, org=org)

# Crear una instancia para consultar
query_api = client.query_api()

# Inicializar listas para almacenar los datos
xdata = []
ydata = []

# Función para obtener el último dato de temperatura
def get_last_temperature():
    query = f'''
    from(bucket: "{bucket}")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "Temperature")
    |> filter(fn: (r) => r._field == "temperature")
    |> sort(columns: ["_time"], desc: true)
    |> limit(n:1)
    '''
    tables = query_api.query(query)
    for table in tables:
        for record in table.records:
            return record.get_time().timestamp(), record.get_value()
    return None, None

# Configurar la aplicación PyQt
app = QtWidgets.QApplication(sys.argv)

# Crear la ventana principal
main_window = QtWidgets.QWidget()
main_window.setWindowTitle("Temperatura en tiempo real")

# Crear un layout vertical
layout = QtWidgets.QVBoxLayout()
main_window.setLayout(layout)

# Crear la gráfica
plot_widget = pg.PlotWidget(title="Temperatura")
plot_widget.setLabel('left', 'Temperatura (°C)')
plot_widget.setLabel('bottom', 'Tiempo')
curve = plot_widget.plot(pen='y')  # Línea amarilla

# Establecer el rango fijo del eje Y entre 10 y 20 grados
plot_widget.setYRange(10, 20)

# Desactivar el autoajuste del eje Y y activar solo el del eje X
plot_widget.enableAutoRange(axis='x', enable=True)
plot_widget.enableAutoRange(axis='y', enable=False)

# Crear un QLabel para mostrar la hora actual
time_label = QtWidgets.QLabel()
time_label.setAlignment(QtCore.Qt.AlignCenter)
time_label.setStyleSheet("font-size: 16px;")

# Añadir widgets al layout
layout.addWidget(plot_widget)
layout.addWidget(time_label)

# Mostrar la ventana principal
main_window.show()

# Función para actualizar la gráfica y la hora
def update():
    time_point, temp = get_last_temperature()
    if time_point and temp:
        xdata.append(time_point)
        ydata.append(temp)
        # Mantener solo los últimos 100 puntos
        xdata_plot = xdata[-100:]
        ydata_plot = ydata[-100:]
        # Actualizar la gráfica
        curve.setData(xdata_plot, ydata_plot)
        # Formatear el eje x para mostrar tiempo legible
        x_axis = plot_widget.getAxis('bottom')
        x_axis.setTickSpacing(major=60, minor=10)
        x_axis.setLabel('Tiempo', units=None)
        x_ticks = [(t, datetime.fromtimestamp(t).strftime("%H:%M:%S")) for t in xdata_plot]
        x_axis.setTicks([x_ticks])
        # Solo permitir autoajuste en el eje X
        plot_widget.enableAutoRange(axis='x', enable=True)
    else:
        print("No se encontraron datos.")

    # Actualizar la hora actual en el QLabel
    current_time = datetime.now().strftime("%H:%M:%S")
    time_label.setText(f"Hora actual: {current_time}")

# Configurar el temporizador para actualizar cada segundo
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)  # Actualiza cada 1000 ms (1 segundo)

# Ejecutar la aplicación
if __name__ == '__main__':
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Cerrando la aplicación.")
    finally:
        # Cerrar el cliente al terminar
        client.close()
