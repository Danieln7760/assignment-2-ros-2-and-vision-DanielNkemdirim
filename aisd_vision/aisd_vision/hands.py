
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import mediapipe as mp

from aisd_msgs.msg import Hand

mp_hands = mp.solutions.hands


class Hands(Node):

    def __init__(self):
        super().__init__('hands')

        # Subscribe to webcam images.
        self.subscription = self.create_subscription(
            Image, 'video_frames',
            self.listener_callback, 10
        )

        # Convert ROS images to OpenCV format.
        self.br = CvBridge()

        # Publish finger positions to cmd_hand.
        self.hand_publisher = self.create_publisher(
            Hand, 'cmd_hand', 10
        )

        # Initialize MediaPipe hand detection.
        self.detector = mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def listener_callback(self, msg):

        # Convert the ROS image to OpenCV.
        image = self.br.imgmsg_to_cv2(
            msg, desired_encoding='bgr8'
        )

        # Landmark numbers for the fingertips.
        PINKY_FINGER_TIP = 20
        INDEX_FINGER_TIP = 8

        # MediaPipe requires RGB images.
        image = cv2.cvtColor(
            image, cv2.COLOR_BGR2RGB
        )

        image.flags.writeable = False

        # Process the image to detect hands.
        results = self.detector.process(image)

        if results.multi_hand_landmarks:

            # Use the first detected hand.
            landmarks = results.multi_hand_landmarks[0].landmark

            # Create a custom Hand message.
            hand_msg = Hand()

            # Extract normalized X coordinates.
            hand_msg.xpinky = landmarks[PINKY_FINGER_TIP].x
            hand_msg.xindex = landmarks[INDEX_FINGER_TIP].x

            # Publish when a subscriber is connected.
            if self.hand_publisher.get_subscription_count() > 0:
                self.hand_publisher.publish(hand_msg)
            else:
                self.get_logger().info(
                    'waiting for subscriber'
                )

    def destroy_node(self):
        self.detector.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = Hands()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
