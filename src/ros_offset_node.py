#!/usr/bin/env python3
"""ROS node wrapping OffsetCalculator and serial communication."""

import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge

from offset_serial import OffsetCalculator, send_offset

class OffsetNode:
    def __init__(self):
        model_path = rospy.get_param('~model_path')
        port = rospy.get_param('~serial_port')
        self.calculator = OffsetCalculator(model_path)
        self.port = port
        self.bridge = CvBridge()
        self.pub = rospy.Publisher('offset', Float32MultiArray, queue_size=1)
        rospy.Subscriber('image', Image, self.image_cb, queue_size=1)

    def image_cb(self, msg: Image):
        cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        offset = self.calculator.compute(cv_image)
        send_offset(self.port, offset)
        out = Float32MultiArray(data=[offset.dx, offset.dy])
        self.pub.publish(out)


def main():
    rospy.init_node('offset_node')
    OffsetNode()
    rospy.spin()


if __name__ == '__main__':
    main()
