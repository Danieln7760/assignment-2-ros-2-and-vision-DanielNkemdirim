
import rclpy
from rclpy.node import Node
from aisd_msgs.msg import Hand
from geometry_msgs.msg import Twist


class Move(Node):

    def __init__(self):
        super().__init__('move')

        # Subscribe to the hand position messages.
        self.subscription = self.create_subscription(
            Hand,
            'cmd_hand',
            self.listener_callback,
            10
        )

        # Publish robot velocity commands.
        self.vel_publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

    def listener_callback(self, msg):

        # Initialize angular and linear velocity.
        angle = 0.0
        linear = 0.0

        # Turn right when the index finger is
        # positioned to the right of the image.
        if msg.xindex > 0.55:
            self.get_logger().info('right')
            angle = -0.1

        # Turn left when the index finger is
        # positioned to the left of the image.
        elif msg.xindex < 0.45:
            self.get_logger().info('left')
            angle = 0.1

        # Do not rotate when the finger is centered.
        else:
            angle = 0.0

        # Move forward when the index finger's
        # X coordinate is greater than the pinky's.
        if msg.xindex > msg.xpinky:
            self.get_logger().info('come')
            linear = 0.5

        # Otherwise, stop forward movement.
        else:
            self.get_logger().info('stay')
            linear = 0.0

        # Create a Twist message.
        twist = Twist()

        # Set forward velocity.
        twist.linear.x = linear

        # Set rotational velocity.
        twist.angular.z = angle

        # Publish only when a subscriber is connected.
        if self.vel_publisher.get_subscription_count() > 0:
            self.vel_publisher.publish(twist)
        else:
            self.get_logger().info(
                'waiting for subscriber'
            )


def main(args=None):
    rclpy.init(args=args)

    node = Move()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
