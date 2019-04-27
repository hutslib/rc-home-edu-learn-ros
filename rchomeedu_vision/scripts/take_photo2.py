#!/usr/bin/env python

'''
Copyright (c) 2016, Nadya Ampilogova
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


from __future__ import print_function
import sys
import rospy
import cv2
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import time
import argparse


# select topic of type sensor_msgs/Image
def autoImageTopic():
    topics = rospy.get_published_topics()
    for t in topics:
        if t[1]=='sensor_msgs/Image':
            return t[0]
    return None


class TakePhoto:

    def __init__(self, img_topic=None, takephoto_topic=None):

        self.bridge = CvBridge()
        self.image_received = False

        if img_topic is None:
            img_topic = autoImageTopic()

        if img_topic is None:
            rospy.logerr("Cannot find any image topic!!! Aborting.")
            sys.exit(0)

        rospy.loginfo("Image topic: %s" %img_topic)
        self.image_sub = rospy.Subscriber(img_topic, Image, self.image_cb)

        # Allow up to one second to connection
        rospy.sleep(1)

        if takephoto_topic!=None:
            rospy.loginfo("TakePhoto topic: %s" %takephoto_topic)
            rospy.Subscriber(takephoto_topic, String, self.take_photo_cb)

    def image_cb(self, data):

        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    def take_picture(self, img_title, usetimestamp=False):
        if self.image_received:
            # Set filename
            img_file = img_title
            if usetimestamp:
                timestr = time.strftime("%Y%m%d-%H%M%S-")
                img_file = timestr + img_title
            # Save an image
            cv2.imwrite(img_file, self.image)
            rospy.loginfo("Saved image " + img_file)
            return True
        else:
            rospy.loginfo("No images received")
            return False

    def take_photo_cb(self, msg):
        #print msg.data
        if msg.data == "take photo":
            # Take a photo
            self.take_picture('photo.jpg', usetimestamp=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-image_topic", type=str, default=None,
                        help="Image topic (default: auto detect)")
    parser.add_argument("-takephoto_topic", type=str, default='/take_photo',
                        help="Topic name for takephoto subscriber (default: /take_photo)")
    parser.add_argument("-savefile", type=str, default=None,
                        help="Output base filename (default: None)")


    args = parser.parse_args()
    img_topic = args.image_topic
    img_title = args.savefile
    takephoto_topic = args.takephoto_topic

    # Initialize
    rospy.init_node('take_photo', anonymous=False)
    camera = TakePhoto(img_topic, takephoto_topic)

    # Set output file
    if (img_title is not None):

        # Take and save the photo
        camera.take_picture(img_title)

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)

    else:
        rospy.spin()
