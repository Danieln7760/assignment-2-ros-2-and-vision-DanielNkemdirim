
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class ImagePublisher(Node):

    def __init__(self):
        super().__init__('image_publisher')

        # Publish camera images to the video_frames topic
        self.publisher_ = self.create_publisher(
            Image, 'video_frames', 10
        )

        # Publish a frame every 0.1 seconds
        self.timer = self.create_timer(
            0.1, self.timer_callback
        )

        # Open the default webcam
        self.cap = cv2.VideoCapture(0)

        # Convert OpenCV images into ROS Image messages
        self.br = CvBridge()

        if not self.cap.isOpened():
            self.get_logger().error('Cannot open webcam')

    def timer_callback(self):

        # Capture a frame from the webcam
        ret, frame = self.cap.read()

        # Publish the frame if capture succeeded
        if ret:
            self.publisher_.publish(
                self.br.cv2_to_imgmsg(frame)
            )


def main(args=None):
    rclpy.init(args=args)

    image_publisher = ImagePublisher()

    try:
        rclpy.spin(image_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        image_publisher.cap.release()
        image_publisher.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
