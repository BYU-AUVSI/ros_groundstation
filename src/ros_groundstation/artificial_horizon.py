import sys, math, rospy, random
from PyQt5 import QtCore, QtGui, QtWidgets
from std_msgs.msg import Float32
from map_subscribers import StateSub, GPSDataSub, BatterySub, ConComSub, ConInSub


class ArtificialHorizon(QtWidgets.QWidget):
    """
    Artificial horizon graphical element.

    Attributes
    ----------
    height : int
        Default window height of the Qt Gui
    width : int
        Default window width of the Qt Gui
    roll : float
        Aircraft roll in degrees
    pitch : float
        Aircraft pitch in degrees
    speed : float
        Aircraft speed KIAS
    altitude : float
        Aircraft altitude in feet MSL
    heading : float
        Aircraft heading in degrees.
    numSat : int
        Number of satellites (GPS)
    pitchInterval : float
        The percent of height used to display 1 degree
    """

    def __init__(self):
        super(ArtificialHorizon, self).__init__()
        self.initUI()

    def initUI(self):
        """
        Initialize UI attributes of the Artificial Horizon widget. 
        """
        self.height = 600
        self.width = 600

        self.roll = 0  # degrees
        self.pitch = 0  # degrees
        self.speed = 0  # KIAS
        self.altitude = 0  # ft MSL
        self.heading = 0  # degrees
        self.numSat = 0  # Number of Satellites (GPS)

        self.pitchInterval = 0.013  # % of height used to display 1 degree

        self.setGeometry(300, 300, self.width, self.height)
        self.setWindowTitle('Artificial Horizon')
        self.show()

    def resizeEvent(self, newSize):
        """
        Window resize event callback.

        Stores the new window size as attributes of the class.

        Parameters
        ----------
        newSize : QResizeEvent
            The QResizeEvent object generated by the Qt GUI.
        """
        self.width = newSize.size().width()
        self.height = newSize.size().height()

    def paintEvent(self, event):
        """
        Paint event callback.

        Creates a QPainter object and draws the artificial horizon.
        """
        painter = QtGui.QPainter()
        painter.begin(self)
        self.drawArtificialHorizon(event, painter)
        painter.end()

    def drawArtificialHorizon(self, event, painter):
        """
        Draws the artificial horizon.

        This function extracts all relevant values from its ros subscribers
        and uses them to compute all drawn values. It then calls each individual
        artist (e.g. drawSky, drawGround, etc.).
        """
        # extract relevant values here from subscribers
        self.roll = int(math.floor(StateSub.phi * (180.0 / math.pi)))
        self.pitch = int(math.floor(StateSub.theta * (180.0 / math.pi)))
        self.speed = int(math.floor(StateSub.Va))
        self.altitude = int(math.floor(StateSub.alt))
        self.heading = int(math.floor(StateSub.chi * (180.0 / math.pi))) % 360
        self.numSat = GPSDataSub.numSat

        self.drawSky(event, painter)

        painter.translate(self.width / 2, self.height / 2)
        painter.rotate(-self.roll)
        painter.translate(-self.width / 2, -self.height / 2)
        painter.translate(0, self.height * (self.pitch * self.pitchInterval))

        self.drawGround(event, painter)
        self.drawPitchIndicator(event, painter)

        painter.translate(0, self.height * (-1 * self.pitch * self.pitchInterval))

        self.drawTurnIndicator(event, painter)

        painter.translate(self.width / 2, self.height / 2)

        painter.rotate(self.roll)
        painter.translate(-self.width / 2, -self.height / 2)

        self.drawAircraftSymbol(event, painter)
        self.drawAirspeedIndicator(event, painter)
        self.drawAltitudeIndicator(event, painter)
        self.drawHeadingIndicator(event, painter)
        self.drawNumSatellites(event, painter)
        self.drawOutputIndicator(event, painter)
        self.drawBatteryMonitor(event, painter)
        # self.drawWaypointAccuracy(event, painter)

    def drawNumSatellites(self, event, painter):
        """
        Draws the "number of satellites" display.
        """
        p1 = QtCore.QPoint(0, 0)
        p2 = QtCore.QPoint(self.width * (0.25), self.height * 0.1)
        rect = QtCore.QRectF(p1, p2)
        if self.numSat < 4:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.red), 2, QtCore.Qt.SolidLine))
        else:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.green), 2, QtCore.Qt.SolidLine))
        painter.drawText(rect, QtCore.Qt.AlignCenter, "GPS: " + str(self.numSat) + " satellites")

    # def drawWaypointAccuracy(self, event, painter):
    #    p1 = QtCore.QPoint(self.width*(0.65),0)
    #    p2 = QtCore.QPoint(self.width,self.height*0.1)
    #    rect = QtCore.QRectF(p1,p2)
    #    painter.drawText(rect,QtCore.Qt.AlignCenter,"Wp Accuracy: " + "%.2f" % self.latestWpAccuracy + " m")

    def drawSky(self, event, painter):
        """
        Draws the sky.
        """
        brush = QtGui.QBrush(QtGui.QColor(38, 89, 242), QtCore.Qt.SolidPattern)
        painter.fillRect(QtCore.QRectF(0, 0, self.width, self.height), brush)

    def drawGround(self, event, painter):
        """
        Draws the ground.
        """
        brush = QtGui.QBrush(QtGui.QColor(84, 54, 10), QtCore.Qt.SolidPattern)
        painter.fillRect(
            QtCore.QRectF(-300, self.height / 2, self.width + 600, self.height * (0.5 + self.pitchInterval * 180)),
            brush)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.white), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.drawLine(-300, self.height / 2, self.width + 600, self.height / 2)

    def drawHeadingIndicator(self, event, painter):
        """
        Draws the heading indicator.
        """
        boxWidth = self.width * 1.0
        boxHeight = self.height * 0.1
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 200))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.yellow), 2, QtCore.Qt.SolidLine))
        painter.fillRect(QtCore.QRectF((self.width - boxWidth) / 2, self.height - boxHeight, boxWidth, boxHeight),
                         brush)

        directions = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S", 215: "SW", 270: "W", 315: "NW"}
        scale = 0.01
        for i in range(self.heading - 49, self.heading + 49):
            if i % 10 == 0:
                x = self.width * 0.5 - ((self.heading - i) * scale * self.width)
                y = self.height - boxHeight
                if i < 0:
                    i += 360
                i = i % 360
                text = str(i)
                if i in directions:
                    text = directions[i]
                painter.drawLine(x, y, x, y + 5)
                painter.drawText(QtCore.QPoint(x + 7 - 8 * len(text), y + 22), text)

        painter.setBrush(QtCore.Qt.black)
        p1 = QtCore.QPoint(self.width * (0.46), self.height)
        p2 = QtCore.QPoint(self.width * (0.46), self.height - boxHeight * 0.9)
        p3 = QtCore.QPoint(self.width * (0.50), self.height - boxHeight)
        p4 = QtCore.QPoint(self.width * (0.54), self.height - boxHeight * 0.9)
        p5 = QtCore.QPoint(self.width * (0.54), self.height)
        poly = QtGui.QPolygon([p1, p2, p3, p4, p5])
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.drawPolygon(poly)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(255, 255, 0)), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        rect = QtCore.QRectF(p1, p4)
        painter.drawText(rect, QtCore.Qt.AlignCenter, str(self.heading) + u'\N{DEGREE SIGN}')

    def drawAirspeedIndicator(self, event, painter):
        """
        Draws the airspeed indicator.
        """
        boxWidth = self.width * 0.13
        boxHeight = self.height * 0.6
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 200))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.yellow), 2, QtCore.Qt.SolidLine))
        painter.fillRect(QtCore.QRectF(0, (self.height - boxHeight) / 2, boxWidth, boxHeight), brush)

        scale = 0.01
        for i in range(self.speed - 29, self.speed + 29):
            if i % 10 == 0 and i >= 0:
                x = boxWidth
                y = self.height * 0.5 + ((self.speed - i) * scale * self.height)
                text = str(i)
                painter.drawLine(x - 5, y, x, y)
                painter.drawText(QtCore.QPoint(x - 10 - 8 * len(text), y + 5), text)
        if ConComSub.enabled:
            va_c = ConComSub.Va_c
            va_c_y = self.height * .5 + ((self.speed - va_c) * scale * self.height)
            if (self.height - boxHeight) / 2 <= va_c_y <= (self.height + boxHeight) / 2:
                triangle_h_dim = self.width * .02
                triangle_v_dim = self.height * .01
                triangle_right = boxWidth + triangle_h_dim
                triangle = QtGui.QPolygonF()
                triangle.append(QtCore.QPointF(boxWidth, va_c_y))
                triangle.append(QtCore.QPointF(triangle_right, triangle_v_dim + va_c_y))
                triangle.append(QtCore.QPointF(triangle_right, -triangle_v_dim + va_c_y))
                painter.drawConvexPolygon(triangle)
        painter.setBrush(QtCore.Qt.black)
        p1 = QtCore.QPoint(0, self.height * (0.46))
        p2 = QtCore.QPoint(boxWidth * 0.9, self.height * (0.46))
        p3 = QtCore.QPoint(boxWidth, self.height * (0.5))
        p4 = QtCore.QPoint(boxWidth * 0.9, self.height * (0.54))
        p5 = QtCore.QPoint(0, self.height * (0.54))
        poly = QtGui.QPolygon([p1, p2, p3, p4, p5])
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.drawPolygon(poly)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(255, 255, 0)), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        rect = QtCore.QRectF(p1, p4)
        painter.drawText(rect, QtCore.Qt.AlignCenter, str(self.speed) + " m/s")
        painter.drawText(QtCore.QPoint(5, (self.height - boxHeight) / 2 - 5), "Airspeed (m/s IAS)")
        # painter.drawText(rect,QtCore.Qt.AlignCenter,str(self.speed) + " m/s") # $$$$
        # painter.drawText(QtCore.QPoint(5,(self.height-boxHeight)/2-5),"Airspeed") # $$$$

    def drawAltitudeIndicator(self, event, painter):
        """
        Draws the altitude indicator.
        """
        boxWidth = self.width * 0.13
        boxHeight = self.height * 0.6
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 200))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.yellow), 2, QtCore.Qt.SolidLine))
        painter.fillRect(QtCore.QRectF(self.width - boxWidth, (self.height - boxHeight) / 2, boxWidth, boxHeight),
                         brush)

        scale = 0.01
        for i in range(self.altitude - 29, self.altitude + 29):
            if i % 10 == 0:
                x = self.width - boxWidth
                y = self.height * 0.5 + ((self.altitude - i) * scale * self.height)
                text = str(i)
                painter.drawLine(x, y, x + 5, y)
                painter.drawText(QtCore.QPoint(x + 10, y + 5), text)

        painter.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
        if ConComSub.enabled:
            alt_c = ConComSub.h_c
            alt_c_y = self.height * .5 + ((self.altitude - alt_c) * scale * self.height)
            if (self.height - boxHeight) / 2 <= alt_c_y <= (self.height + boxHeight) / 2:
                triangle_h_dim = self.width * .02
                triangle_v_dim = self.height * .01
                triangle_left = self.width - boxWidth - triangle_h_dim
                triangle = QtGui.QPolygonF()
                triangle.append(QtCore.QPointF(self.width - boxWidth, alt_c_y))
                triangle.append(QtCore.QPointF(triangle_left, triangle_v_dim + alt_c_y))
                triangle.append(QtCore.QPointF(triangle_left, -triangle_v_dim + alt_c_y))
                painter.drawConvexPolygon(triangle)
        painter.setBrush(QtCore.Qt.black)
        p1 = QtCore.QPoint(self.width, self.height * (0.46))
        p2 = QtCore.QPoint(self.width - boxWidth * 0.9, self.height * (0.46))
        p3 = QtCore.QPoint(self.width - boxWidth, self.height * (0.5))
        p4 = QtCore.QPoint(self.width - boxWidth * 0.9, self.height * (0.54))
        p5 = QtCore.QPoint(self.width, self.height * (0.54))
        poly = QtGui.QPolygon([p1, p2, p3, p4, p5])
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)), 2, QtCore.Qt.SolidLine))
        painter.drawPolygon(poly)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(255, 255, 0)), 2, QtCore.Qt.SolidLine))
        text = str(self.altitude) + " m"
        rect = QtCore.QRectF(p1, p4)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)
        painter.drawText(QtCore.QPoint(self.width - boxWidth + 5, (self.height - boxHeight) / 2 - 5), "Altitude")

    def drawTurnIndicator(self, event, painter):
        """
        Draws the turn indicator.
        """
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.white), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        radius = self.width * (0.3)
        yOffset = self.height * (0.10)
        painter.drawArc(
            QtCore.QRectF(self.width * (0.5) - radius, yOffset, 2 * radius, 2 * radius),
            16 * 30, 16 * 120)

        height = self.height * 0.02
        x = self.width / 2
        y = yOffset
        x2 = x
        y2 = y - height
        x3 = x
        y3 = y2 - 5
        xCenter = self.width / 2
        yCenter = radius + yOffset

        angles = [-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60]
        for angle in angles:
            painter.translate(xCenter, yCenter)
            painter.rotate(angle)
            painter.translate(-xCenter, -yCenter)

            painter.drawLine(x, y, x2, y2)
            text = str(angle)
            painter.drawText(QtCore.QPoint(x3 - 4 * len(text), y3), text)

            painter.translate(xCenter, yCenter)
            painter.rotate(-angle)
            painter.translate(-xCenter, -yCenter)

        # Draw the arrow
        height = self.height * 0.025
        poly = QtGui.QPolygon([
            QtCore.QPoint(x, y),
            QtCore.QPoint(x - height / 2, y + height),
            QtCore.QPoint(x + height / 2, y + height), ])

        painter.translate(xCenter, yCenter)
        painter.rotate(self.roll)
        painter.translate(-xCenter, -yCenter)

        painter.drawPolygon(poly)

        painter.translate(xCenter, yCenter)
        painter.rotate(-self.roll)
        painter.translate(-xCenter, -yCenter)

    def drawAircraftSymbol(self, event, painter):
        """
        Draws the aircraft symbol.
        """
        brightYellow = QtGui.QColor(255, 255, 0)
        widthFraction = 0.10
        heightFraction = 0.05
        painter.setPen(QtGui.QPen(QtGui.QBrush(brightYellow), 5, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
        painter.setBrush(brightYellow)
        poly = QtGui.QPolygon([
            QtCore.QPoint(self.width * 0.5, self.height * 0.5),
            QtCore.QPoint(self.width * (0.5 + widthFraction / 2.0), self.height * (0.5 + heightFraction)),
            QtCore.QPoint(self.width * 0.5, self.height * (0.5 + heightFraction / 2.0)),
            QtCore.QPoint(self.width * (0.5 - widthFraction / 2.0), self.height * (0.5 + heightFraction))
        ])
        painter.drawPolygon(poly)
        space = 0.25
        length = 0.1
        painter.drawLine(self.width * space, self.height / 2, self.width * (space + length), self.height / 2)
        painter.drawLine(self.width * (1 - space - length), self.height / 2, self.width * (1 - space), self.height / 2)

    def drawPitchIndicator(self, event, painter):
        """
        Draws the pitch indicator.
        """
        minHeight = 0.15 - self.pitch * self.pitchInterval
        maxHeight = 0.85 - self.pitch * self.pitchInterval
        for i in range(-9, 9):
            text = str(10 * abs(i))
            height = 0.5 - self.pitchInterval * 10 * i
            if minHeight < height < maxHeight:
                painter.drawLine(
                    self.width * (0.4), self.height * (height),
                    self.width * (0.6), self.height * (height))
                painter.drawText(QtCore.QPoint(self.width * (0.6) + 5, self.height * (height) + 5), text)
                painter.drawText(QtCore.QPoint(self.width * (0.4) - 22, self.height * (height) + 5), text)

            height = height - self.pitchInterval * 5
            if minHeight < height < maxHeight:
                painter.drawLine(
                    self.width * (0.45), self.height * (height),
                    self.width * (0.55), self.height * (height))

        if ConInSub.enabled:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.yellow), 4, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))
            pitch_command = math.degrees(ConInSub.theta_c)
            height = 0.5 - self.pitchInterval * pitch_command
            if minHeight < height < maxHeight:
                painter.drawLine(
                    self.width * (0.4), self.height * (height),
                    self.width * (0.6), self.height * (height))
                painter.drawText(QtCore.QPoint(self.width * (0.6) + 5, self.height * (height) + 5), "<")
                painter.drawText(QtCore.QPoint(self.width * (0.4) - 22, self.height * (height) + 5), ">")
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.white), 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap))

    def drawOutputIndicator(self, event, painter):
        """
        Draws the altitude indicator.
        """
        return
        boxWidth = self.width * 0.13
        boxHeight = self.height * 0.6
        brush = QtGui.QBrush(QtGui.QColor(100, 100, 100, 200))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.yellow), 2, QtCore.Qt.SolidLine))
        painter.fillRect(QtCore.QRectF(self.width - boxWidth, (self.height - boxHeight) / 2, boxWidth, boxHeight),
                         brush)

        scale = 0.01
        for i in range(self.altitude - 29, self.altitude + 29):
            if i % 10 == 0:
                x = self.width - boxWidth
                y = self.height * 0.5 + ((self.altitude - i) * scale * self.height)
                text = str(i)
                painter.drawLine(x, y, x + 5, y)
                painter.drawText(QtCore.QPoint(x + 10, y + 5), text)

        painter.setBrush(QtCore.Qt.black)
        p1 = QtCore.QPoint(self.width, self.height * (0.46))
        p2 = QtCore.QPoint(self.width - boxWidth * 0.9, self.height * (0.46))
        p3 = QtCore.QPoint(self.width - boxWidth, self.height * (0.5))
        p4 = QtCore.QPoint(self.width - boxWidth * 0.9, self.height * (0.54))
        p5 = QtCore.QPoint(self.width, self.height * (0.54))
        poly = QtGui.QPolygon([p1, p2, p3, p4, p5])
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)), 2, QtCore.Qt.SolidLine))
        painter.drawPolygon(poly)
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(255, 255, 0)), 2, QtCore.Qt.SolidLine))
        text = str(self.altitude) + " ft"
        rect = QtCore.QRectF(p1, p4)
        painter.drawText(rect, QtCore.Qt.AlignCenter, text)
        painter.drawText(QtCore.QPoint(self.width - boxWidth + 5, (self.height - boxHeight) / 2 - 5), "Altitude")

    def drawBatteryMonitor(self, event, painter):
        if BatterySub.enabled:
            painter.setBrush(QtCore.Qt.red)
            battery_width = self.width * .13
            battery_height = .05 * self.height
            battery_rect = QtCore.QRectF(0, .8 * self.height, battery_width, battery_height)
            fill_rect = QtCore.QRectF(0, .8 * self.height, int(battery_width * BatterySub.voltage_percent / 100),
                                      battery_height)
            fill_brush = QtGui.QBrush(QtCore.Qt.green, QtCore.Qt.SolidPattern)
            battery_brush = QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern)
            painter.fillRect(battery_rect, battery_brush)
            painter.fillRect(fill_rect, fill_brush)
            painter.setPen(QtCore.Qt.black)
            painter.drawText(battery_rect, "{0:.1f}V".format(BatterySub.voltage),
                             QtGui.QTextOption(QtCore.Qt.AlignCenter))


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ah = ArtificialHorizon()
    sys.exit(app.exec_())
