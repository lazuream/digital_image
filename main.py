import sys
import numpy as np
import cv2
from PyQt5.QtCore import Qt, QCoreApplication, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QDesktopWidget, \
    QFileDialog, QLabel, QInputDialog, QMessageBox, QGraphicsBlurEffect, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QPainter, QTransform, QColor, qGray, QImage, qRgb, qRgba
from page1 import Ui_MainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 设置窗口无边框及透明背景
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # # 创建并配置模糊效果
        # blur_effect = QGraphicsBlurEffect()
        # blur_effect.setBlurRadius(8)  # 设置模糊半径
        #
        # # 应用模糊效果到 frame_2
        # self.ui.frame_2.setGraphicsEffect(blur_effect)

        # 窗口居中显示
        self.center()

        # 定义退出按钮
        self.ui.pushButton_exit.clicked.connect(self.close)

        # 定义一个字典来跟踪每个容器的状态
        self.container_states = {
            self.ui.transformationContainer_1: False,
            self.ui.transformationContainer_2: False,
            self.ui.transformationContainer_3: False,
            self.ui.transformationContainer_4: False,
        }

        # 初始化所有 transformationContainer 的可见状态，默认隐藏，并存储状态
        self.container_states = {}
        self.init_container(self.ui.transformationContainer_1, ['Translate', 'Rotate', 'Scale', 'Mirror'])
        self.init_container(self.ui.transformationContainer_2, ['Gray Scale', 'Histogram Equalization'])
        self.init_container(self.ui.transformationContainer_3, ['Mean Filter', 'Median Filter', 'Low Pass Filter'])
        self.init_container(self.ui.transformationContainer_4, ['Edge Detection', 'Thresholding', 'Region Segmentation'])
        self.init_container(self.ui.transformationContainer_5, ['Grayscale', 'binarization', 'Gaussian blur', 'edge detection'])

        # 连接按钮点击事件到槽函数
        self.ui.pushButton_Geometric.clicked.connect(lambda: self.toggle_container(self.ui.transformationContainer_1))
        self.ui.pushButton_Contrast.clicked.connect(lambda: self.toggle_container(self.ui.transformationContainer_2))
        self.ui.pushButton_Smooth.clicked.connect(lambda: self.toggle_container(self.ui.transformationContainer_3))
        self.ui.pushButton_Partition.clicked.connect(lambda: self.toggle_container(self.ui.transformationContainer_4))
        self.ui.pushButton_Preprocessing.clicked.connect(lambda: self.toggle_container(self.ui.transformationContainer_5))

        # 添加图片按钮连接到槽函数
        self.ui.pushButton_add.clicked.connect(self.load_image)

        # 保存图片按钮连接到槽函数
        self.ui.pushButton_save.clicked.connect(self.save_image)

        # 创建一个 QLabel 用于显示加载图片，并将其添加到 frame_initialimage
        self.image_label = QLabel(self.ui.frame_initialimage)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: transparent;")

        # 创建一个 QLabel 用于显示结果图片，并将其添加到 frame_retimage
        self.result_label = QLabel(self.ui.scrollAreaWidgetContents_retimage)
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("background-color: transparent;")
        self.center_image_in_frame_ret()

    def init_container(self, container, buttons):
        """初始化一个 transformationContainer 及其按钮"""
        container.setVisible(False)  # 默认隐藏
        self.container_states[container] = False  # 添加状态跟踪

        if container.layout() is None:
            layout = QVBoxLayout(container)
        else:
            layout = container.layout()

        for btnText in buttons:
            button = QPushButton(btnText, container)
            button.clicked.connect(lambda checked, text=btnText: self.onTransformationButtonClick(text))
            button.setStyleSheet("""
                        QPushButton {
                            border: 2px solid black;
                            border-radius: 10px; /* 圆角半径 */
                            padding: 6px; /* 按钮内边距 */
                            background-color: white;
                            min-width: 80px;
                        }
                        QPushButton:hover {
                            background-color: lightgray;
                        }
                        QPushButton:pressed {
                            background-color: gray;
                            padding-top: 8px;
                            padding-left: 8px;
                            padding-bottom: 4px;
                            padding-right: 4px;
                        }
                    """)
            layout.addWidget(button)

    def toggle_container(self, container):
        """切换指定 container 的可见性"""
        try:
            # 关闭所有已开启的容器
            for c, state in list(self.container_states.items()):
                if state and c != container:
                    print(f"Hiding container {c.objectName()}.")
                    c.setVisible(False)
                    self.container_states[c] = False

            # 切换当前容器的可见性
            is_visible = self.container_states.get(container, False)

            if not is_visible:
                print(f"Showing container {container.objectName()}.")
                container.setVisible(True)
            else:
                print(f"Hiding container {container.objectName()}.")
                container.setVisible(False)

            self.container_states[container] = not is_visible
        except Exception as e:
            print(f"Error in toggle_container: {e}")

    def onTransformationButtonClick(self, text):
        print(f'Transformation button clicked: {text}')

    def load_image(self):
        """打开文件对话框选择图片并显示在 frame_initialimage 中"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options)
        if file_name:
            pixmap = QPixmap(file_name)
            if not pixmap.isNull():
                # 设置最大尺寸
                max_size = 400  # 最大宽度或高度为400像素
                scaled_pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                self.center_image_in_frame()
            else:
                print("Failed to load image.")

    def save_image(self):
        """打开文件对话框选择保存位置并保存 transformed_pixmap 中的图片"""
        # 确保有图片可以保存
        if not self.transformed_pixmap or self.transformed_pixmap.isNull():
            print("No transformed image to save.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "保存图片", "",
                                                   "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)",
                                                   options=options)

        if file_name:
            pixmap = self.transformed_pixmap
            # 如果用户没有提供扩展名，则根据选择的文件类型添加默认扩展名
            if not file_name.lower().endswith(('.png', '.xpm', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_name += '.png'  # 默认为PNG格式

            success = pixmap.save(file_name)

            if success:
                print(f"Transformed image successfully saved to {file_name}")
            else:
                print("Failed to save image.")

    def center_image_in_frame(self):
        pixmap = self.image_label.pixmap()
        if pixmap:
            size = self.ui.frame_initialimage.size()
            label_size = pixmap.size()
            x = (size.width() - label_size.width()) / 2
            y = (size.height() - label_size.height()) / 2
            self.image_label.move(x, y)

    def center_image_in_frame(self):
        """使图片在 frame_initialimage 内居中显示"""
        frame_rect = self.ui.frame_initialimage.geometry()
        pixmap_size = self.image_label.pixmap().size()

        x_offset = (frame_rect.width() - pixmap_size.width()) // 2
        y_offset = (frame_rect.height() - pixmap_size.height()) // 2

        # 确保偏移量不为负数（即图片比 frame 小）
        x_offset = max(0, x_offset)
        y_offset = max(0, y_offset)

        # 设置 QLabel 的几何位置
        self.image_label.setGeometry(x_offset, y_offset, pixmap_size.width(), pixmap_size.height())

    def center_image_in_frame_ret(self):
        """使结果图片在 frame_retimage 内居中显示"""
        frame_rect = self.ui.frame_retimage.geometry()
        if self.result_label.pixmap():
            pixmap_size = self.result_label.pixmap().size()
        else:
            pixmap_size = QSize(0, 0)

        x_offset = (frame_rect.width() - pixmap_size.width()) // 2
        y_offset = (frame_rect.height() - pixmap_size.height()) // 2

        # 确保偏移量不为负数（即图片比 frame 小）
        x_offset = max(0, x_offset)
        y_offset = max(0, y_offset)

        # 设置 QLabel 的几何位置
        self.result_label.setGeometry(x_offset, y_offset, pixmap_size.width(), pixmap_size.height())

    def onTransformationButtonClick(self, text):
        """根据按钮文本执行相应的图像变换操作"""
        print("onTransformationButtonClick called!")  # 确认方法被调用
        print(f'Transformation button clicked: {text}')
        pixmap = self.image_label.pixmap()
        if not pixmap or pixmap.isNull():
            print("No image loaded to transform.")
            return

        transformed_pixmap = None
        transformation_result_message = ""  # 初始化变换结果消息

        if text == 'Translate':
            transformed_pixmap = self.translate_image(pixmap)
            transformation_result_message = "平移后结果图片"
        elif text == 'Rotate':
            transformed_pixmap = self.rotate_image(pixmap)
            transformation_result_message = "旋转后结果图片"
        elif text == 'Scale':
            transformed_pixmap = self.scale_image(pixmap)
            transformation_result_message = "缩放后结果图片"
        elif text == 'Mirror':
            transformed_pixmap = self.mirror_image(pixmap)
            transformation_result_message = "镜像后结果图片"
        elif text == 'Gray Scale':
            transformed_pixmap = self.grayscale_image(pixmap)
            transformation_result_message = "灰度化后结果图片"
        elif text == 'Histogram Equalization':
            transformed_pixmap = self.histogram_equalization(pixmap)
            transformation_result_message = "直方图均衡化后结果图片"
        elif text == 'Mean Filter':
            transformed_pixmap = self.mean_filter(pixmap)
            transformation_result_message = "均值滤波后结果图片"
        elif text == 'Median Filter':
            transformed_pixmap = self.median_filter(pixmap)
            transformation_result_message = "中值滤波后结果图片"
        elif text == 'Low Pass Filter':
            transformed_pixmap = self.low_pass_filter(pixmap)
            transformation_result_message = "低通滤波后结果图片"
        elif text == 'Edge Detection':
            transformed_pixmap = self.edge_detection(pixmap)
            transformation_result_message = "边缘检测后结果图片"
        elif text == 'Thresholding':
            transformed_pixmap = self.thresholding(pixmap)
            transformation_result_message = "阈值处理后结果图片"
        elif text == 'Region Segmentation':
            transformed_pixmap = self.region_segmentation(pixmap)
            transformation_result_message = "区域分割后结果图片"
        elif text == 'Grayscale':
            transformed_pixmap = self.grayscale(pixmap)
            transformation_result_message = "灰度化结果图片"
        elif text == 'binarization':
            transformed_pixmap = self.binarization(pixmap)
            transformation_result_message = "二值化结果图片"
        elif text == 'Gaussian blur':
            transformed_pixmap = self.gaussian_blur(pixmap)
            transformation_result_message = "高斯模糊结果图片"
        elif text == 'edge detection':
            transformed_pixmap = self.edge_detection(pixmap)
            transformation_result_message = "边缘检测结果图片"
        if transformed_pixmap:
            self.show_transformed_image(transformed_pixmap)
            self.transformed_pixmap = transformed_pixmap  # 更新变换后的图像

        # 更新 textEdit_2 组件的文本
        try:
            print(f"new text:{transformation_result_message}")
            # 使用 HTML 格式化文本以实现居中
            centered_text = f"<div align='center' style='font-size:18px; font-weight:bold;'>{transformation_result_message}</div>"
            self.ui.textEdit_2.setHtml(centered_text)

        except Exception as e:
            print(f"An error occurred while updating textEdit_2: {e}")

    def translate_image(self, pixmap):
        """实现 Translate 操作"""

        # 弹出对话框获取用户输入的 dx 和 dy 值
        def get_user_input(prompt, default_value):
            value, ok = QInputDialog.getInt(
                self,
                "输入偏移量",
                prompt,
                default_value,
                -10000,  # 最小值
                10000,  # 最大值
                1  # 步长
            )
            return value if ok else None

        dx = get_user_input("水平偏移量 (X):", 50) or 0
        dy = get_user_input("垂直偏移量 (Y):", 50) or 0

        # 如果用户取消了任意一个输入对话框，则直接返回原始pixmap
        if dx is None or dy is None:
            return pixmap

        # 创建一个新的透明背景的 QPixmap，尺寸与原始pixmap相同
        translated_pixmap = QPixmap(pixmap.size())
        translated_pixmap.fill(Qt.transparent)

        painter = QPainter(translated_pixmap)
        try:
            # 计算新位置，允许图像超出 QLabel 边界
            painter.drawPixmap(dx, dy, pixmap)
        finally:
            painter.end()

        self.show_transformed_image_2(translated_pixmap, 1)

    def rotate_image(self, pixmap):
        """实现 Rotate 操作"""
        try:
            # 设置默认旋转角度
            default_angle = 45

            # 弹出输入对话框让用户输入旋转角度
            angle, ok = QInputDialog.getDouble(
                self,
                '设置旋转角度',
                '请输入旋转角度 (度):',
                value=default_angle,
                min=-360,
                max=360,
                decimals=1
            )
            if not ok:
                return None

            transform = QTransform().rotate(angle)

            # 应用旋转并保持纵横比
            rotated_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

            return rotated_pixmap

        except Exception as e:
            print(f"Error during rotation: {e}")
            return None

    def scale_image(self, pixmap):
        """实现 Scale 操作"""
        # 弹出对话框获取用户输入的 scale_factor 值
        def get_user_input(prompt, default_value):
            try:
                value, ok = QInputDialog.getDouble(
                    self,
                    "输入缩放比例",
                    prompt,
                    default_value,
                    0.1,  # 最小值
                    10.0,  # 最大值
                    2  # 小数位数
                )
                return value if ok else None
            except Exception as e:
                print(f"Error in get_user_input: {e}")
                return None

        scale_factor = get_user_input("缩放比例:", 1.0) or 1.0

        # 如果用户取消了输入对话框，则直接返回原始pixmap
        if scale_factor is None:
            print("User canceled input dialog.")
            return

        try:
            # 创建一个新的透明背景的 QPixmap，尺寸与原始pixmap按比例调整
            scaled_width = int(pixmap.width() * scale_factor)
            scaled_height = int(pixmap.height() * scale_factor)
            scaled_pixmap = QPixmap(scaled_width, scaled_height)
            scaled_pixmap.fill(Qt.transparent)

            painter = QPainter(scaled_pixmap)
            try:
                # 绘制缩放后的图像
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
                painter.drawPixmap(0, 0, scaled_width, scaled_height, pixmap)
            finally:
                painter.end()

            self.show_transformed_image_2(scaled_pixmap,scale_factor)
        except Exception as e:
            print(f"Error scaling image: {e}")

    def mirror_image(self, pixmap):
        """实现 Mirror 操作"""

        def get_user_choice():
            choices = ["Horizontal", "Vertical", "Both"]

            # 创建自定义按钮
            horizontal_button = QMessageBox.StandardButton.Yes
            vertical_button = QMessageBox.StandardButton.No
            both_button = QMessageBox.StandardButton.Abort

            # 设置按钮文本
            msg_box = QMessageBox()
            msg_box.setWindowTitle("选择翻转方式")
            msg_box.setText("请选择翻转方式:")
            msg_box.addButton(horizontal_button)
            msg_box.addButton(vertical_button)
            msg_box.addButton(both_button)
            msg_box.button(horizontal_button).setText(choices[0])
            msg_box.button(vertical_button).setText(choices[1])
            msg_box.button(both_button).setText(choices[2])

            # 显示对话框并获取用户选择
            choice = msg_box.exec_()

            if choice == horizontal_button:
                return "horizontal"
            elif choice == vertical_button:
                return "vertical"
            elif choice == both_button:
                return "both"
            else:
                return None

        choice = get_user_choice()
        if choice is None:
            return None

        mirrored_pixmap = pixmap

        if choice == "horizontal":
            mirrored_pixmap = pixmap.transformed(QTransform().scale(-1, 1))
        elif choice == "vertical":
            mirrored_pixmap = pixmap.transformed(QTransform().scale(1, -1))
        elif choice == "both":
            mirrored_pixmap = pixmap.transformed(QTransform().scale(-1, -1))

        return mirrored_pixmap

    def grayscale_image(self, pixmap):
        """实现 Gray Scale 操作"""
        image = pixmap.toImage()  # 将 QPixmap 转换为 QImage

        # 创建一个新的灰度图像
        gray_image = QImage(image.size(), QImage.Format_Grayscale8)

        for x in range(image.width()):
            for y in range(image.height()):
                color = QColor(image.pixel(x, y))
                gray = qGray(color.rgb())  # 计算灰度值
                gray_image.setPixel(x, y, qRgb(gray, gray, gray))

        return QPixmap.fromImage(gray_image)  # 返回转换后的 QPixmap

    def histogram_equalization(self, pixmap):
        """实现 Histogram Equalization 操作"""
        image = pixmap.toImage().convertToFormat(QImage.Format_RGB32)  # 确保图像格式是 RGB32
        width, height = image.width(), image.height()

        # 创建一个直方图数组，长度为256（每个亮度级别）
        hist = [0] * 256

        # 计算原始图像的直方图
        for x in range(width):
            for y in range(height):
                gray = qGray(image.pixel(x, y))
                hist[gray] += 1

        # 计算累积分布函数 (CDF)
        cdf = [sum(hist[:i + 1]) for i in range(len(hist))]
        cdf_min = min(i for i in cdf if i > 0)

        # 创建查找表 (LUT) 进行直方图均衡化
        lut = [round((cdf[i] - cdf_min) * 255 / (width * height - cdf_min)) for i in range(256)]

        # 应用 LUT 到图像
        for x in range(width):
            for y in range(height):
                gray = qGray(image.pixel(x, y))
                new_gray = lut[gray]
                image.setPixel(x, y, qRgb(new_gray, new_gray, new_gray))

        return QPixmap.fromImage(image)

    def mean_filter(self, pixmap):
        """实现 Mean Filter 操作"""
        # 弹出输入对话框让用户输入滤波器大小
        default_threshold = 3

        while True:
            kernel_size, ok1 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入滤波器大小 (大于3的奇数):',
                value=default_threshold,
                min=3,
                max=15
            )
            if not ok1:
                return None

            if kernel_size >= 3 and kernel_size % 2 == 1:
                break
            else:
                QMessageBox.warning(self, "无效输入", "滤波器大小必须是大于3的奇数，请重新输入。")

        image = pixmap.toImage()
        width, height = image.width(), image.height()

        # 创建一个新的图像用于存储结果
        filtered_image = QImage(width, height, QImage.Format_RGB32)

        half_kernel = kernel_size // 2

        for x in range(width):
            for y in range(height):
                sum_r, sum_g, sum_b = 0, 0, 0
                count = 0
                for i in range(-half_kernel, half_kernel + 1):
                    for j in range(-half_kernel, half_kernel + 1):
                        px_x = min(max(x + i, 0), width - 1)
                        px_y = min(max(y + j, 0), height - 1)
                        color = QColor(image.pixel(px_x, px_y))
                        sum_r += color.red()
                        sum_g += color.green()
                        sum_b += color.blue()
                        count += 1

                avg_color = QColor(sum_r // count, sum_g // count, sum_b // count)
                filtered_image.setPixel(x, y, avg_color.rgb())

        return QPixmap.fromImage(filtered_image)

    def median_filter(self, pixmap):
        """实现 Median Filter 操作"""
        # 弹出输入对话框让用户输入滤波器大小
        default_threshold = 3

        while True:
            kernel_size, ok1 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入滤波器大小 (大于3的奇数):',
                value=default_threshold,
                min=3,
                max=15
            )
            if not ok1:
                return None

            if kernel_size >= 3 and kernel_size % 2 == 1:
                break
            else:
                QMessageBox.warning(self, "无效输入", "滤波器大小必须是大于3的奇数，请重新输入。")

        image = pixmap.toImage()
        width, height = image.width(), image.height()

        filtered_image = QImage(width, height, QImage.Format_RGB32)

        half_kernel = kernel_size // 2

        for x in range(width):
            for y in range(height):
                pixels = []
                for i in range(-half_kernel, half_kernel + 1):
                    for j in range(-half_kernel, half_kernel + 1):
                        px_x, px_y = min(max(x + i, 0), width - 1), min(max(y + j, 0), height - 1)
                        color = QColor(image.pixel(px_x, px_y))
                        pixels.append((color.red(), color.green(), color.blue()))

                pixels.sort()  # 对所有通道一起排序可能不是最佳做法，但这里简化处理
                median_pixel = pixels[len(pixels) // 2]
                median_color = QColor(*median_pixel)

                filtered_image.setPixel(x, y, median_color.rgb())

        return QPixmap.fromImage(filtered_image)

    def low_pass_filter(self, pixmap):
        # 弹出对话框获取用户输入的 sigma 值
        def get_user_input(prompt, default_value):
            try:
                value, ok = QInputDialog.getDouble(
                    self,
                    "输入sigma",
                    prompt,
                    default_value,
                    0.1,  # 最小值
                    100.0,  # 最大值
                    2  # 小数位数
                )
                return value if ok else None
            except Exception as e:
                print(f"Error in get_user_input: {e}")
                return None

        sigma = get_user_input("sigma:", 1.0) or 1.0

        # 如果用户取消了输入对话框，则直接返回原始pixmap
        if sigma is None:
            print("User canceled input dialog.")
            return
        # 将 QPixmap 转换为 QImage
        image = pixmap.toImage()

        # 获取图像的高度和宽度
        width, height = image.width(), image.height()

        # 创建一个字节数组来存储图像数据
        bytes_per_line = image.bytesPerLine()
        qformat = QImage.Format_RGB32

        # 将 QImage 转换为 OpenCV 格式的图像
        if qformat == QImage.Format_RGB32:
            converted_image = image.convertToFormat(QImage.Format_RGBA8888)
            ptr = converted_image.bits()
            ptr.setsize(converted_image.byteCount())
            arr = np.array(ptr).reshape(height, width, 4)  # Shape (height, width, channels)
            bgr_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        else:
            raise ValueError("Unsupported format")

        # 将 BGR 图像转换为灰度图像
        gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

        # 获取图像的高度和宽度
        rows, cols = gray_image.shape
        crow, ccol = rows // 2, cols // 2

        # 创建高斯滤波器
        x, y = np.meshgrid(np.arange(cols) - ccol, np.arange(rows) - crow)
        d = np.sqrt(x ** 2 + y ** 2)
        gaussian_filter = np.exp(-(d ** 2 / (2 * sigma ** 2)))

        # 将图像转换到频域
        f_transform = np.fft.fft2(gray_image)
        f_shifted = np.fft.fftshift(f_transform)

        # 应用高斯滤波器
        f_filtered = f_shifted * gaussian_filter

        # 将图像转换回空间域
        f_ishifted = np.fft.ifftshift(f_filtered)
        img_back = np.fft.ifft2(f_ishifted)
        img_back = np.abs(img_back)

        # 转换数据类型以便显示
        img_back = cv2.normalize(img_back, None, 0, 255, cv2.NORM_MINMAX).astype('uint8')

        # 将 OpenCV 格式的图像转换回 QImage
        qimage = QImage(img_back.data, width, height, width, QImage.Format_Grayscale8)

        # 将 QImage 转换回 QPixmap
        filtered_pixmap = QPixmap.fromImage(qimage)

        return filtered_pixmap

    def edge_detection(self, pixmap):
        """实现边缘法的图像分割"""
        try:
            # 设置默认阈值
            default_lower_threshold = 50
            default_upper_threshold = 150

            # 弹出输入对话框让用户输入阈值下限和上限
            lower_threshold, ok1 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入低阈值 (0-255):',
                value=default_lower_threshold,
                min=0,
                max=255
            )
            if not ok1:
                return None

            upper_threshold, ok2 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入高阈值 (0-255):',
                value=default_upper_threshold,
                min=0,
                max=255)
            if not ok2 or lower_threshold >= upper_threshold:
                QMessageBox.warning(self, "无效的阈值范围", "请确保低阈值小于高阈值。")
                return None

            # 将QPixmap转换为OpenCV格式
            image = pixmap.toImage()
            s = image.bits().asstring(image.width() * image.height() * 4)
            arr = np.frombuffer(s, dtype=np.uint8).reshape((image.height(), image.width(), 4))
            bgr_image = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

            # 转换为灰度图
            gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

            # 使用Canny算子进行边缘检测
            edges = cv2.Canny(gray_image, lower_threshold, upper_threshold)

            # 创建一个新的图像用于存储结果，保持RGB32格式以便显示彩色前景
            height, width = edges.shape
            bytes_per_line = width
            segmented_image = QImage(edges.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

            # 将边缘检测结果转换回QPixmap
            result_pixmap = QPixmap.fromImage(segmented_image)

            return result_pixmap

        except Exception as e:
            print(f"Error during edge detection: {e}")
            return None

    def thresholding(self, pixmap):
        try:
            # 设置默认阈值
            default_threshold=128

            # 弹出输入对话框让用户输入阈值下限和上限
            lower_threshold, ok1 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入低阈值 (0-255):',
                value=default_threshold,
                min=0,
                max=255
            )
            if not ok1:
                return None

            upper_threshold, ok2 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入阈值上限 (0-255):',
                value=255,
                min=0,
                max=255
            )
            if not ok2 or lower_threshold >= upper_threshold:
                QMessageBox.warning(self, "无效的阈值范围", "请确保阈值下限小于上限。")
                return None

            image = pixmap.toImage().convertToFormat(QImage.Format_Grayscale8)  # 转换为灰度图
            width, height = image.width(), image.height()

            # 创建一个新的图像用于存储结果，保持灰度格式
            binary_image = QImage(width, height, QImage.Format_Grayscale8)

            for x in range(width):
                for y in range(height):
                    gray = QColor(image.pixel(x, y)).red()
                    if lower_threshold <= gray <= upper_threshold:
                        binary_image.setPixel(x, y, qRgba(255, 255, 255, 255))  # 白色
                    else:
                        binary_image.setPixel(x, y, qRgba(0, 0, 0, 255))  # 黑色

            return QPixmap.fromImage(binary_image)

        except Exception as e:
            print(f"Error during edge detection: {e}")
            return None

    def region_segmentation(self, pixmap):
        """实现区域法的图像分割"""
        try:
            # 弹出输入对话框让用户输入阈值下限和上限
            lower_threshold, ok1 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入阈值下限 (0-255):',
                value=0,
                min=0,
                max=255
            )
            if not ok1:
                return None

            upper_threshold, ok2 = QInputDialog.getInt(
                self,
                '设置阈值',
                '请输入阈值上限 (0-255):',
                value=255,
                min=0,
                max=255
            )
            if not ok2 or lower_threshold >= upper_threshold:
                QMessageBox.warning(self, "无效的阈值范围", "请确保阈值下限小于上限。")
                return None

            # 转换为灰度图
            image = pixmap.toImage().convertToFormat(QImage.Format_Grayscale8)
            width, height = image.width(), image.height()

            if width == 0 or height == 0:
                raise ValueError("Input image has invalid dimensions.")

            # 创建一个新的图像用于存储结果，保持RGB32格式以便显示彩色前景
            segmented_image = QImage(width, height, QImage.Format_RGB32)

            for y in range(height):
                for x in range(width):
                    gray = QColor(image.pixel(x, y)).red()

                    if lower_threshold <= gray <= upper_threshold:
                        # 前景设为原图的颜色
                        original_color = QColor(pixmap.toImage().pixel(x, y))
                        segmented_image.setPixel(x, y, qRgb(original_color.red(), original_color.green(),
                                                            original_color.blue()))
                    else:
                        # 背景设为白色
                        segmented_image.setPixel(x, y, qRgb(255, 255, 255))

            return QPixmap.fromImage(segmented_image)

        except Exception as e:
            print(f"Error during region segmentation: {e}")
            return None

    def show_transformed_image(self, pixmap):
        """显示转换后的图片"""
        # 清除之前的结果图片
        self.result_label.clear()
        # 设置最大尺寸
        max_size = 400  # 最大宽度或高度为400像素
        scaled_pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.result_label.setPixmap(scaled_pixmap)
        self.center_image_in_frame_ret()

    def show_transformed_image_2(self, pixmap,multiple):
        """显示转换后的图片"""
        # 清除之前的结果图片
        self.result_label.clear()
        scaled_pixmap = pixmap.scaled(400*multiple, 400*multiple, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.result_label.setPixmap(scaled_pixmap)
        self.center_image_in_frame_ret()

    def center(self):
        """使窗口居中显示"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def grayscale(self, pixmap):
        """灰度化操作"""
        try:
            # 将 QPixmap 转换为 QImage
            image = pixmap.toImage()
            width, height = image.width(), image.height()

            # 创建灰度图像
            gray_image = QImage(width, height, QImage.Format_Grayscale8)

            for x in range(width):
                for y in range(height):
                    color = QColor(image.pixel(x, y))
                    # 使用加权法计算灰度值 (人眼对不同颜色的敏感度不同)
                    gray = int(0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
                    gray_image.setPixel(x, y, qRgb(gray, gray, gray))

            return QPixmap.fromImage(gray_image)

        except Exception as e:
            print(f"Error during grayscale: {e}")
            return None

    def binarization(self, pixmap):
        """二值化操作"""
        try:
            # 弹出对话框获取用户输入的阈值
            default_threshold = 128
            threshold, ok = QInputDialog.getInt(
                self,
                '设置二值化阈值',
                '请输入阈值 (0-255):',
                value=default_threshold,
                min=0,
                max=255
            )
            if not ok:
                return None

            # 首先将图像转换为灰度
            gray_pixmap = self.grayscale(pixmap)
            if gray_pixmap is None:
                return None

            # 将灰度 QPixmap 转换为 QImage
            image = gray_pixmap.toImage()
            width, height = image.width(), image.height()

            # 创建二值图像
            binary_image = QImage(width, height, QImage.Format_Mono)

            for x in range(width):
                for y in range(height):
                    gray = qGray(image.pixel(x, y))
                    # 根据阈值进行二值化
                    if gray >= threshold:
                        binary_image.setPixel(x, y, 1)  # 白色
                    else:
                        binary_image.setPixel(x, y, 0)  # 黑色

            return QPixmap.fromImage(binary_image)

        except Exception as e:
            print(f"Error during binarization: {e}")
            return None

    def gaussian_blur(self, pixmap):
        """高斯模糊操作"""
        try:
            # 弹出对话框获取用户输入的高斯核大小
            kernel_size, ok1 = QInputDialog.getInt(
                self,
                '设置高斯核大小',
                '请输入高斯核大小 (大于0的奇数):',
                value=5,
                min=1,
                max=31
            )
            if not ok1:
                return None

            # 确保核大小为奇数
            if kernel_size % 2 == 0:
                QMessageBox.warning(self, "警告", "高斯核大小必须是奇数，已自动加1")
                kernel_size += 1

            # 弹出对话框获取用户输入的sigma值
            sigma, ok2 = QInputDialog.getDouble(
                self,
                '设置sigma值',
                '请输入sigma值 (标准差):',
                value=1.0,
                min=0.1,
                max=10.0,
                decimals=1
            )
            if not ok2:
                return None

            # 将 QPixmap 转换为 QImage
            image = pixmap.toImage()
            width, height = image.width(), image.height()

            # 将 QImage 转换为 OpenCV 格式
            # 首先转换为 RGB888 格式
            if image.format() != QImage.Format_RGB888:
                image = image.convertToFormat(QImage.Format_RGB888)

            # 获取图像数据
            ptr = image.bits()
            ptr.setsize(image.byteCount())

            # 转换为 numpy 数组
            arr = np.array(ptr).reshape(height, width, 3)

            # OpenCV 使用 BGR 格式，需要转换
            bgr_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

            # 应用高斯模糊
            blurred_image = cv2.GaussianBlur(bgr_image, (kernel_size, kernel_size), sigma)

            # 将 OpenCV 格式转换回 RGB
            rgb_image = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2RGB)

            # 创建新的 QImage
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width

            # 创建 QImage
            qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)

            return QPixmap.fromImage(qimage)

        except Exception as e:
            print(f"Error during Gaussian blur: {e}")
            # 如果 OpenCV 方法失败，使用 QPainter 实现简单的高斯模糊效果
            try:
                return self.simple_gaussian_blur(pixmap, kernel_size)
            except:
                return None

    def simple_gaussian_blur(self, pixmap, kernel_size):
        """简单的高斯模糊实现（使用多次平均滤波模拟）"""
        # 创建临时 pixmap
        temp_pixmap = pixmap.copy()

        # 应用多次平均滤波来模拟高斯模糊
        for _ in range(3):  # 迭代次数越多，效果越接近高斯模糊
            # 创建临时图像
            temp_image = temp_pixmap.toImage()
            width, height = temp_image.width(), temp_image.height()

            blurred_image = QImage(width, height, QImage.Format_ARGB32)

            half_kernel = kernel_size // 2

            # 应用简单的均值滤波（作为高斯模糊的近似）
            for x in range(width):
                for y in range(height):
                    sum_r, sum_g, sum_b, sum_a = 0, 0, 0, 0
                    count = 0

                    for i in range(-half_kernel, half_kernel + 1):
                        for j in range(-half_kernel, half_kernel + 1):
                            px_x = min(max(x + i, 0), width - 1)
                            px_y = min(max(y + j, 0), height - 1)

                            color = QColor(temp_image.pixel(px_x, px_y))
                            sum_r += color.red()
                            sum_g += color.green()
                            sum_b += color.blue()
                            sum_a += color.alpha()
                            count += 1

                    avg_color = QColor(
                        sum_r // count,
                        sum_g // count,
                        sum_b // count,
                        sum_a // count
                    )
                    blurred_image.setPixel(x, y, avg_color.rgba())

            temp_pixmap = QPixmap.fromImage(blurred_image)

        return temp_pixmap


if __name__ == '__main__':
    # 启用高DPI缩放
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()  # 确保调用了 show() 方法使窗口可见

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An error occurred: {e}")