from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import sys

import components.manager as manager


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self):
        self.fig, self.axes = plt.subplots(2, 4)
        super(MplCanvas, self).__init__()


def comparator_buffered_request(req_1, req_2=None):
    if req_2 is None:
        req_2 = req_1
    if int(req_1[1]) < int(req_2[1]):
        return -1
    elif int(req_1[1]) > int(req_2[1]):
        return 1
    else:
        return 0


class Ui_MainWindow(object):

    def confirm_func(self):
        self.n_s = int(self.lineEditNumberSources.text())
        self.n_b = int(self.lineEditNumberBuffers.text())
        self.n_d = int(self.lineEditNumberDevices.text())
        self.number_requests = int(self.lineEditNumberRequests.text())
        self.alpha = float(self.lineEditAlpha.text())
        self.beta = float(self.lineEditBeta.text())
        self.lambda_param = float(self.lineEditLambda.text())

    def automatic_mode_clicked(self):
        sc = MplCanvas()

        amount_generated_requests,\
        probability_declining,\
        average_system_time,\
        average_waiting_time,\
        average_processing_time,\
        waiting_dispersion,\
        processing_dispersion,\
        devices_coefficients,\
        devices_numbers = manager.application(self.n_s,
                                              self.n_b,
                                              self.n_d,
                                              self.number_requests,
                                              self.alpha,
                                              self.beta,
                                              self.lambda_param)

        sc.axes[0, 0].plot(devices_numbers, amount_generated_requests)
        sc.axes[0, 0].set_title("Requests per source")
        sc.axes[0, 1].plot(devices_numbers, probability_declining)
        sc.axes[0, 1].set_title("Declining probability")
        sc.axes[0, 2].plot(devices_numbers, average_system_time)
        sc.axes[0, 2].set_title("Average time in system")
        sc.axes[0, 3].plot(devices_numbers, average_waiting_time)
        sc.axes[0, 3].set_title("Average waiting time")
        sc.axes[1, 0].plot(devices_numbers, average_processing_time)
        sc.axes[1, 0].set_title("Average processing time")
        sc.axes[1, 1].plot(devices_numbers, waiting_dispersion)
        sc.axes[1, 1].set_title("Waiting dispersion")
        sc.axes[1, 2].plot(devices_numbers, processing_dispersion)
        sc.axes[1, 2].set_title("Processing dispersion")
        sc.axes[1, 3].plot(devices_numbers, devices_coefficients)
        sc.axes[1, 3].set_title("Using coefficient")

        sc.fig.set_size_inches(12, 10)
        plt.show()

    def step_mode_start_clicked(self):
        self.editLineActiveSources.setText(str(self.n_s))
        self.editLineActiveDevices.setText(str(self.n_d))
        self.lineEdit_10.setText(str(self.n_b))
        self.is_start_clicked = True
        self.is_clicked = False
        self.cleanup()
        self.generated_requests_simulation = 0
        self.system_simulation_time, self.system_device_pointer, self.system_buffer_pointer = manager.step_init(self.n_s,
                          self.n_b,
                          self.n_d,
                          self.alpha,
                          self.beta,
                          self.lambda_param)

    def cleanup(self):
        self.lineEditSourceRequestNumber_1.setText('')
        self.lineEditSourceRequestNumber_2.setText('')
        self.lineEditSourceRequestNumber_3.setText('')
        self.lineEditSourceRequestNumber_4.setText('')
        self.lineEditSourceRequestNumber_5.setText('')
        self.lineEditSourceRequestNumber_6.setText('')
        self.lineEditSourceRequestNumber_7.setText('')

        self.lineEditDeviceRequest_1.setText('')
        self.lineEditDeviceRequest_2.setText('')
        self.lineEditDeviceRequest_3.setText('')
        self.lineEditDeviceRequest_4.setText('')
        self.lineEditDeviceRequest_5.setText('')
        self.lineEditDeviceRequest_6.setText('')
        self.lineEditDeviceRequest_7.setText('')

        self.lineEditlDeviceDispatcherRequestNumber.setText('')
        self.lineEditBuffDispatcherRequestNumber.setText('')
        self.lineEdit_11.setText('')

    def make_step_clicked(self):
        if self.is_start_clicked:

            current_step_time = self.system_simulation_time

            self.is_start_clicked, self.system_simulation_time,\
            self.generated_requests_simulation, self.system_device_pointer, self.system_buffer_pointer = manager.step_application(
                self.number_requests, self.system_simulation_time, self.generated_requests_simulation,
                self.system_device_pointer, self.system_buffer_pointer)
            self.is_start_clicked = not self.is_start_clicked
            self.SystemTimeLine.setText(str(current_step_time))

            self.cleanup()
            list_str = []
            is_refused = False
            for key, value in manager.dict.items():
                if current_step_time == float(key):
                    exec_str = "self.lineEditSourceRequestNumber_{}.setText(value[0])".format(int(value[0][:1]))
                    exec(exec_str)
                    self.lineEditBuffDispatcherRequestNumber.setText(value[0])
                if value[1] == 'buf':
                    list_str.append((value[0], value[2]))

                elif value[1].startswith('dev'):
                    temp = value[2]
                    exec_str = "self.lineEditDeviceRequest_{}.setText(value[0])".format(int(temp) + 1)
                    exec(exec_str)
                    if current_step_time == float(key) or value[1][-1] == 's':
                        value[1] = 'dev'
                        self.lineEditlDeviceDispatcherRequestNumber.setText(value[0])
                elif value[1] == 'refuse':
                    self.lineEdit_11.setText(value[0])
                    is_refused = True

            if is_refused:
                del manager.dict[str(-1.0)]

            list_str.sort(key=comparator_buffered_request)
            buffers_str = ''
            for el in list_str:
                buffers_str += (el[0] + '\n')
            self.textEdit.setText(buffers_str)
            self.is_clicked = True

    def is_step_clicked(self):
        return self.is_clicked

    def setupStartUi(self, MainWindow):
        self.n_s = 1
        self.n_b = 1
        self.n_d = 1
        self.number_requests = 0
        self.alpha = 0
        self.beta = 0
        self.lambda_param = 0
        self.is_clicked = False


        ''' Creating main window '''
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1085, 828)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.Russian, QtCore.QLocale.Russia))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")


        ''' Creating tab widget '''
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(10, 0, 1061, 781))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setObjectName("tabWidget")


        ''' Creating first tab'''
        self.Input_parameters = QtWidgets.QWidget()
        self.Input_parameters.setObjectName("Input_parameters")
        self.lineEditNumberSources = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditNumberSources.setGeometry(QtCore.QRect(350, 60, 150, 30))
        self.lineEditNumberSources.setObjectName("lineEditNumberSources")
        self.lineEditNumberBuffers = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditNumberBuffers.setGeometry(QtCore.QRect(350, 120, 150, 30))
        self.lineEditNumberBuffers.setObjectName("lineEditNumberBuffers")
        self.lineEditNumberDevices = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditNumberDevices.setGeometry(QtCore.QRect(350, 180, 150, 30))
        self.lineEditNumberDevices.setObjectName("lineEditNumberDevices")
        self.lineEditNumberRequests = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditNumberRequests.setGeometry(QtCore.QRect(350, 240, 150, 30))
        self.lineEditNumberRequests.setObjectName("lineEditNumberRequests")
        self.lineEditAlpha = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditAlpha.setGeometry(QtCore.QRect(350, 300, 150, 30))
        self.lineEditAlpha.setObjectName("lineEditAlpha")
        self.lineEditBeta = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditBeta.setGeometry(QtCore.QRect(350, 360, 150, 30))
        self.lineEditBeta.setObjectName("lineEditBeta")
        self.lineEditLambda = QtWidgets.QLineEdit(self.Input_parameters)
        self.lineEditLambda.setGeometry(QtCore.QRect(350, 420, 150, 30))
        self.lineEditLambda.setObjectName("lineEditLambda")

        self.LabelSources = QtWidgets.QLabel(self.Input_parameters)
        self.LabelSources.setGeometry(QtCore.QRect(150, 60, 150, 30))
        self.LabelSources.setObjectName("LabelSources")
        self.LabelBuffers = QtWidgets.QLabel(self.Input_parameters)
        self.LabelBuffers.setGeometry(QtCore.QRect(150, 120, 150, 30))
        self.LabelBuffers.setObjectName("LabelBuffers")
        self.LabelDevices = QtWidgets.QLabel(self.Input_parameters)
        self.LabelDevices.setGeometry(QtCore.QRect(150, 180, 150, 30))
        self.LabelDevices.setObjectName("LabelDevices")
        self.LabelRequests = QtWidgets.QLabel(self.Input_parameters)
        self.LabelRequests.setGeometry(QtCore.QRect(150, 240, 150, 30))
        self.LabelRequests.setObjectName("LabelRequests")
        self.LabelAlpha = QtWidgets.QLabel(self.Input_parameters)
        self.LabelAlpha.setGeometry(QtCore.QRect(150, 300, 150, 30))
        self.LabelAlpha.setObjectName("LabelAlpha")
        self.LabelBeta = QtWidgets.QLabel(self.Input_parameters)
        self.LabelBeta.setGeometry(QtCore.QRect(150, 360, 150, 30))
        self.LabelBeta.setObjectName("LabelBeta")
        self.LabelLambda = QtWidgets.QLabel(self.Input_parameters)
        self.LabelLambda.setGeometry(QtCore.QRect(150, 420, 150, 30))
        self.LabelLambda.setObjectName("LabelLambda")
        self.ButtonConfirm = QtWidgets.QPushButton(self.Input_parameters)
        self.ButtonConfirm.setGeometry(QtCore.QRect(150, 480, 75, 23))
        self.ButtonConfirm.setObjectName("ButtonConfirm")
        self.ButtonConfirm.clicked.connect(self.confirm_func)
        self.tabWidget.addTab(self.Input_parameters, "")


        ''' Creating second tab '''
        self.Automatic_mode = QtWidgets.QWidget()
        self.Automatic_mode.setObjectName("Automatic_mode")
        self.ButtonAutomaticMode = QtWidgets.QPushButton(self.Automatic_mode)
        self.ButtonAutomaticMode.setGeometry(QtCore.QRect(440, 300, 200, 50))
        self.ButtonAutomaticMode.setObjectName("ButtonAutomaticMode")
        self.ButtonAutomaticMode.clicked.connect(self.automatic_mode_clicked)
        self.tabWidget.addTab(self.Automatic_mode, "")


        ''' Creating third tab '''
        self.Step_mode = QtWidgets.QWidget()
        self.Step_mode.setObjectName("Step_mode")
        self.ButtonStartStepMode = QtWidgets.QPushButton(self.Step_mode)
        self.ButtonStartStepMode.setGeometry(QtCore.QRect(50, 690, 150, 30))
        self.ButtonStartStepMode.setObjectName("ButtonStartStepMode")
        self.ButtonStartStepMode.clicked.connect(self.step_mode_start_clicked)
        self.ButtonMakeStep = QtWidgets.QPushButton(self.Step_mode)
        self.ButtonMakeStep.setGeometry(QtCore.QRect(220, 690, 150, 30))
        self.ButtonMakeStep.setObjectName("ButtonMakeStep")
        self.ButtonMakeStep.clicked.connect(self.make_step_clicked)

        self.first_source_x = 40
        self.first_source_y = 30
        self.source_width = 120
        self.source_height = 80

        ''' Creating first source '''
        self.Source_1 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_1.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (1 - 1), self.source_width, self.source_height))
        self.Source_1.setObjectName("Source_{}".format(1))
        self.labelNumberGeneratedRequest_1 = QtWidgets.QLabel(self.Source_1)
        self.labelNumberGeneratedRequest_1.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_1.setObjectName("labelNumberGeneratedRequest_{}".format(1))
        self.labelNumberGeneratedRequest_1.setText(("Request number"))
        self.lineEditSourceRequestNumber_1 = QtWidgets.QLineEdit(self.Source_1)
        self.lineEditSourceRequestNumber_1.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_1.setTitle("Source {}".format(1))
        self.lineEditSourceRequestNumber_1.setObjectName("lineEditSourceRequestNumber_{}".format(1))

        self.Source_2 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_2.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (2 - 1), self.source_width, self.source_height))
        self.Source_2.setObjectName("Source_{}".format(2))
        self.labelNumberGeneratedRequest_2 = QtWidgets.QLabel(self.Source_2)
        self.labelNumberGeneratedRequest_2.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_2.setObjectName("labelNumberGeneratedRequest_{}".format(2))
        self.labelNumberGeneratedRequest_2.setText(("Request number"))
        self.lineEditSourceRequestNumber_2 = QtWidgets.QLineEdit(self.Source_2)
        self.lineEditSourceRequestNumber_2.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_2.setTitle("Source {}".format(2))
        self.lineEditSourceRequestNumber_2.setObjectName("lineEditSourceRequestNumber_{}".format(2))

        self.Source_3 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_3.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (3 - 1), self.source_width, self.source_height))
        self.Source_3.setObjectName("Source_{}".format(3))
        self.labelNumberGeneratedRequest_3 = QtWidgets.QLabel(self.Source_3)
        self.labelNumberGeneratedRequest_3.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_3.setObjectName("labelNumberGeneratedRequest_{}".format(3))
        self.labelNumberGeneratedRequest_3.setText(("Request number"))
        self.lineEditSourceRequestNumber_3 = QtWidgets.QLineEdit(self.Source_3)
        self.lineEditSourceRequestNumber_3.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_3.setTitle("Source {}".format(3))
        self.lineEditSourceRequestNumber_3.setObjectName("lineEditSourceRequestNumber_{}".format(3))

        self.Source_4 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_4.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (4 - 1), self.source_width, self.source_height))
        self.Source_4.setObjectName("Source_{}".format(4))
        self.labelNumberGeneratedRequest_4 = QtWidgets.QLabel(self.Source_4)
        self.labelNumberGeneratedRequest_4.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_4.setObjectName("labelNumberGeneratedRequest_{}".format(4))
        self.labelNumberGeneratedRequest_4.setText(("Request number"))
        self.lineEditSourceRequestNumber_4 = QtWidgets.QLineEdit(self.Source_4)
        self.lineEditSourceRequestNumber_4.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_4.setTitle("Source {}".format(4))
        self.lineEditSourceRequestNumber_4.setObjectName("lineEditSourceRequestNumber_{}".format(4))

        self.Source_5 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_5.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (5 - 1), self.source_width, self.source_height))
        self.Source_5.setObjectName("Source_{}".format(5))
        self.labelNumberGeneratedRequest_5 = QtWidgets.QLabel(self.Source_5)
        self.labelNumberGeneratedRequest_5.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_5.setObjectName("labelNumberGeneratedRequest_{}".format(5))
        self.labelNumberGeneratedRequest_5.setText(("Request number"))
        self.lineEditSourceRequestNumber_5 = QtWidgets.QLineEdit(self.Source_5)
        self.lineEditSourceRequestNumber_5.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_5.setTitle("Source {}".format(5))
        self.lineEditSourceRequestNumber_5.setObjectName("lineEditSourceRequestNumber_{}".format(5))

        self.Source_6 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_6.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (6 - 1), self.source_width, self.source_height))
        self.Source_6.setObjectName("Source_{}".format(6))
        self.labelNumberGeneratedRequest_6 = QtWidgets.QLabel(self.Source_6)
        self.labelNumberGeneratedRequest_6.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_6.setObjectName("labelNumberGeneratedRequest_{}".format(6))
        self.labelNumberGeneratedRequest_6.setText(("Request number"))
        self.lineEditSourceRequestNumber_6 = QtWidgets.QLineEdit(self.Source_6)
        self.lineEditSourceRequestNumber_6.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_6.setTitle("Source {}".format(6))
        self.lineEditSourceRequestNumber_6.setObjectName("lineEditSourceRequestNumber_{}".format(6))

        self.Source_7 = QtWidgets.QGroupBox(self.Step_mode)
        self.Source_7.setGeometry(QtCore.QRect(self.first_source_x, self.first_source_y\
                                        + 90 * (7 - 1), self.source_width, self.source_height))
        self.Source_7.setObjectName("Source_{}".format(7))
        self.labelNumberGeneratedRequest_7 = QtWidgets.QLabel(self.Source_7)
        self.labelNumberGeneratedRequest_7.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelNumberGeneratedRequest_7.setObjectName("labelNumberGeneratedRequest_{}".format(7))
        self.labelNumberGeneratedRequest_7.setText(("Request number"))
        self.lineEditSourceRequestNumber_7 = QtWidgets.QLineEdit(self.Source_7)
        self.lineEditSourceRequestNumber_7.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.Source_7.setTitle("Source {}".format(7))
        self.lineEditSourceRequestNumber_7.setObjectName("lineEditSourceRequestNumber_{}".format(7))

        self.labelActiveSources = QtWidgets.QLabel(self.Step_mode)
        self.labelActiveSources.setGeometry(QtCore.QRect(self.first_source_x + self.source_width + 20, self.first_source_y, 80, 13))
        self.labelActiveSources.setObjectName("labelActiveSources")
        self.labelActiveSources.setText("Active sources")
        self.editLineActiveSources = QtWidgets.QLineEdit(self.Step_mode)
        self.editLineActiveSources.setGeometry(QtCore.QRect(self.first_source_x + self.source_width + 20, self.first_source_y + 23, 80, 15))
        self.editLineActiveSources.setObjectName("editLineActiveSources")
        self.editLineActiveSources.setText("0")


        ''' Buffer dispathcer '''
        self.BufferSetDispatcher = QtWidgets.QGroupBox(self.Step_mode)
        self.BufferSetDispatcher.setGeometry(QtCore.QRect(220, 120, 120, 80))
        self.BufferSetDispatcher.setObjectName("BufferSetDispatcher")
        self.labelBuffDispatcherRequestNumber = QtWidgets.QLabel(self.BufferSetDispatcher)
        self.labelBuffDispatcherRequestNumber.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelBuffDispatcherRequestNumber.setObjectName("labelBuffDispatcherRequestNumber")
        self.lineEditBuffDispatcherRequestNumber = QtWidgets.QLineEdit(self.BufferSetDispatcher)
        self.lineEditBuffDispatcherRequestNumber.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditBuffDispatcherRequestNumber.setObjectName("lineEditBuffDispatcherRequestNumber")


        ''' System time widget '''
        self.SystemTimeLine = QtWidgets.QLineEdit(self.Step_mode)
        self.SystemTimeLine.setGeometry(QtCore.QRect(400, 690, 150, 15))
        self.SystemTimeLine.setObjectName("SystemTimeLine")
        self.SystemTimeLine.setText("0.0")
        self.labelSystemTimeLine = QtWidgets.QLabel(self.Step_mode)
        self.labelSystemTimeLine.setGeometry(QtCore.QRect(400, 667, 80, 13))
        self.labelSystemTimeLine.setObjectName("labelSystemTimeLine")
        self.labelSystemTimeLine.setText("System time")


        ''' Device dispatcher '''
        self.DeviceSetDispatcher = QtWidgets.QGroupBox(self.Step_mode)
        self.DeviceSetDispatcher.setGeometry(QtCore.QRect(630, 120, 120, 80))
        self.DeviceSetDispatcher.setObjectName("DeviceSetDispatcher")
        self.labelDeviceDispatcherRequestNumber = QtWidgets.QLabel(self.DeviceSetDispatcher)
        self.labelDeviceDispatcherRequestNumber.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceDispatcherRequestNumber.setObjectName("labelDeviceDispatcherRequestNumber")
        self.lineEditlDeviceDispatcherRequestNumber = QtWidgets.QLineEdit(self.DeviceSetDispatcher)
        self.lineEditlDeviceDispatcherRequestNumber.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditlDeviceDispatcherRequestNumber.setObjectName("lineEditlDeviceDispatcherRequestNumber")


        ''' Creating first device '''
        self.first_device_x = 810
        self.first_device_y = 30
        self.device_width = 120
        self.device_height = 80
        self.Device_1 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_1.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (1 - 1), self.device_width, self.device_height))
        self.Device_1.setObjectName("Device_1")
        self.labelDeviceRequest_1 = QtWidgets.QLabel(self.Device_1)
        self.labelDeviceRequest_1.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_1.setObjectName("labelDeviceRequest_1")
        self.labelDeviceRequest_1.setText("Request number")
        self.lineEditDeviceRequest_1 = QtWidgets.QLineEdit(self.Device_1)
        self.lineEditDeviceRequest_1.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_1.setObjectName("lineEditDeviceRequest_1")
        self.Device_1.setTitle("Device 1")

        self.Device_2 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_2.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (2 - 1), self.device_width, self.device_height))
        self.Device_2.setObjectName("Device_2")
        self.labelDeviceRequest_2 = QtWidgets.QLabel(self.Device_2)
        self.labelDeviceRequest_2.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_2.setObjectName("labelDeviceRequest_2")
        self.labelDeviceRequest_2.setText("Request number")
        self.lineEditDeviceRequest_2 = QtWidgets.QLineEdit(self.Device_2)
        self.lineEditDeviceRequest_2.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_2.setObjectName("lineEditDeviceRequest_2")
        self.Device_2.setTitle("Device 2")

        self.Device_3 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_3.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (3 - 1), self.device_width, self.device_height))
        self.Device_3.setObjectName("Device_3")
        self.labelDeviceRequest_3 = QtWidgets.QLabel(self.Device_3)
        self.labelDeviceRequest_3.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_3.setObjectName("labelDeviceRequest_3")
        self.labelDeviceRequest_3.setText("Request number")
        self.lineEditDeviceRequest_3 = QtWidgets.QLineEdit(self.Device_3)
        self.lineEditDeviceRequest_3.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_3.setObjectName("lineEditDeviceRequest_3")
        self.Device_3.setTitle("Device 3")

        self.Device_4 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_4.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (4 - 1), self.device_width, self.device_height))
        self.Device_4.setObjectName("Device_4")
        self.labelDeviceRequest_4 = QtWidgets.QLabel(self.Device_4)
        self.labelDeviceRequest_4.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_4.setObjectName("labelDeviceRequest_4")
        self.labelDeviceRequest_4.setText("Request number")
        self.lineEditDeviceRequest_4 = QtWidgets.QLineEdit(self.Device_4)
        self.lineEditDeviceRequest_4.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_4.setObjectName("lineEditDeviceRequest_4")
        self.Device_4.setTitle("Device 4")

        self.Device_5 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_5.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (5 - 1), self.device_width, self.device_height))
        self.Device_5.setObjectName("Device_5")
        self.labelDeviceRequest_5 = QtWidgets.QLabel(self.Device_5)
        self.labelDeviceRequest_5.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_5.setObjectName("labelDeviceRequest_5")
        self.labelDeviceRequest_5.setText("Request number")
        self.lineEditDeviceRequest_5 = QtWidgets.QLineEdit(self.Device_5)
        self.lineEditDeviceRequest_5.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_5.setObjectName("lineEditDeviceRequest_5")
        self.Device_5.setTitle("Device 5")

        self.Device_6 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_6.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (6 - 1), self.device_width, self.device_height))
        self.Device_6.setObjectName("Device_6")
        self.labelDeviceRequest_6 = QtWidgets.QLabel(self.Device_6)
        self.labelDeviceRequest_6.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_6.setObjectName("labelDeviceRequest_6")
        self.labelDeviceRequest_6.setText("Request number")
        self.lineEditDeviceRequest_6 = QtWidgets.QLineEdit(self.Device_6)
        self.lineEditDeviceRequest_6.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_6.setObjectName("lineEditDeviceRequest_6")
        self.Device_6.setTitle("Device 6")

        self.Device_7 = QtWidgets.QGroupBox(self.Step_mode)
        self.Device_7.setGeometry(QtCore.QRect(self.first_device_x, self.first_device_y + 90 * (7 - 1), self.device_width, self.device_height))
        self.Device_7.setObjectName("Device_7")
        self.labelDeviceRequest_7 = QtWidgets.QLabel(self.Device_7)
        self.labelDeviceRequest_7.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelDeviceRequest_7.setObjectName("labelDeviceRequest_7")
        self.labelDeviceRequest_7.setText("Request number")
        self.lineEditDeviceRequest_7 = QtWidgets.QLineEdit(self.Device_7)
        self.lineEditDeviceRequest_7.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEditDeviceRequest_7.setObjectName("lineEditDeviceRequest_7")
        self.Device_7.setTitle("Device 7")

        self.labelActiveDevices = QtWidgets.QLabel(self.Step_mode)
        self.labelActiveDevices.setGeometry(QtCore.QRect(self.first_device_x - 90, self.first_device_y, 80, 13))
        self.labelActiveDevices.setObjectName("labelActiveSources")
        self.labelActiveDevices.setText("Active devices")
        self.editLineActiveDevices = QtWidgets.QLineEdit(self.Step_mode)
        self.editLineActiveDevices.setGeometry(QtCore.QRect(self.first_device_x - 90, self.first_device_y + 23, 80, 15))
        self.editLineActiveDevices.setObjectName("editLineActiveSources")
        self.editLineActiveDevices.setText("0")


        self.Buffers = QtWidgets.QGroupBox(self.Step_mode)
        self.Buffers.setGeometry(QtCore.QRect(390, 30, 170, 491))
        self.Buffers.setObjectName("Buffers")
        self.labelBuffersNumbers = QtWidgets.QLabel(self.Buffers)
        self.labelBuffersNumbers.setGeometry(QtCore.QRect(20, 20, 80, 17))
        self.labelBuffersNumbers.setObjectName("labelBuffersNumbers")
        self.lineEdit_10 = QtWidgets.QLineEdit(self.Buffers)
        self.lineEdit_10.setGeometry(QtCore.QRect(110, 20, 41, 20))
        self.lineEdit_10.setObjectName("lineEdit_10")
        self.textEdit = QtWidgets.QTextEdit(self.Buffers)
        self.textEdit.setGeometry(QtCore.QRect(20, 50, 131, 421))
        self.textEdit.setObjectName("textEdit")
        self.RefuseBoxRefuseRequestNumber = QtWidgets.QGroupBox(self.Step_mode)
        self.RefuseBoxRefuseRequestNumber.setGeometry(QtCore.QRect(220, 300, 120, 80))
        self.RefuseBoxRefuseRequestNumber.setObjectName("RefuseBoxRefuseRequestNumber")
        self.labelRefuseRequestNumber = QtWidgets.QLabel(self.RefuseBoxRefuseRequestNumber)
        self.labelRefuseRequestNumber.setGeometry(QtCore.QRect(20, 20, 80, 13))
        self.labelRefuseRequestNumber.setObjectName("labelRefuseRequestNumber")
        self.lineEdit_11 = QtWidgets.QLineEdit(self.RefuseBoxRefuseRequestNumber)
        self.lineEdit_11.setGeometry(QtCore.QRect(20, 50, 80, 13))
        self.lineEdit_11.setObjectName("lineEdit_11")
        self.line = QtWidgets.QFrame(self.Step_mode)
        self.line.setGeometry(QtCore.QRect(280, 220, 3, 61))
        self.line.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.Step_mode)
        self.line_2.setGeometry(QtCore.QRect(350, 160, 31, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.Step_mode)
        self.line_3.setGeometry(QtCore.QRect(580, 160, 31, 16))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.line_4 = QtWidgets.QFrame(self.Step_mode)
        self.line_4.setGeometry(QtCore.QRect(760, 160, 31, 16))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.Step_mode)
        self.line_5.setGeometry(QtCore.QRect(170, 160, 31, 16))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.tabWidget.addTab(self.Step_mode, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1085, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SMO"))
        self.LabelSources.setText(_translate("MainWindow", "Number of sources"))
        self.LabelBuffers.setText(_translate("MainWindow", "Number of buffers"))
        self.LabelDevices.setText(_translate("MainWindow", "Number of devices"))
        self.LabelRequests.setText(_translate("MainWindow", "Number of requests"))
        self.LabelAlpha.setText(_translate("MainWindow", "Alpha"))
        self.LabelBeta.setText(_translate("MainWindow", "Beta"))
        self.LabelLambda.setText(_translate("MainWindow", "Lambda"))
        self.ButtonConfirm.setText(_translate("MainWindow", "Confirm"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Input_parameters), _translate("MainWindow", "Input parameters"))
        self.ButtonAutomaticMode.setText(_translate("MainWindow", "Run automatic mode"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Automatic_mode), _translate("MainWindow", "Automatic mode"))
        self.ButtonStartStepMode.setText(_translate("MainWindow", "Start step mode"))
        self.ButtonMakeStep.setText(_translate("MainWindow", "Make step"))

        self.BufferSetDispatcher.setTitle(_translate("MainWindow", "Buffer set dispatcher"))
        self.labelBuffDispatcherRequestNumber.setText(_translate("MainWindow", "Request number"))
        self.DeviceSetDispatcher.setTitle(_translate("MainWindow", "Device set dispatcher"))
        self.labelDeviceDispatcherRequestNumber.setText(_translate("MainWindow", "Request number"))

        self.Buffers.setTitle(_translate("MainWindow", "GroupBox"))
        self.labelBuffersNumbers.setText(_translate("MainWindow", "Active buffers"))
        self.RefuseBoxRefuseRequestNumber.setTitle(_translate("MainWindow", "Refuse"))
        self.labelRefuseRequestNumber.setText(_translate("MainWindow", "Request number"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Step_mode), _translate("MainWindow", "Step mode"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupStartUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
