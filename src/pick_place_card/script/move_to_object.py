#!/usr/bin/env python
import rospy
import time
import motion
import numpy as np
import almath
import sys
from naoqi import ALProxy
from std_srvs.srv import Empty  # Import the appropriate service message type
import cv2
import tf
# from pick_place_card.srv import Pose2D
import tf2_ros
from pick_place_card.srv import CartesianPositionOrientation

from cv_bridge import CvBridge # Package to convert between ROS and OpenCV Images
from geometry_msgs.msg import TransformStamped # Handles TransformStamped message
from geometry_msgs.msg import Pose2D
from sensor_msgs.msg import Image # Image is the message type
from tf2_ros import TransformBroadcaster
import math
#motionProxy =0;

def call_enable_body_stiffness_service():
    rospy.wait_for_service('/body_stiffness/enable')  # Replace with the actual service name
    try:
        # Create a proxy to call the service
        enable_body_stiffness_proxy = rospy.ServiceProxy('/body_stiffness/enable', Empty)
        
        # Call the service with an empty request
        response = enable_body_stiffness_proxy()
        
        # Process the response (empty for this service)
        print("Enabled")
    except rospy.ServiceException as e:
        print("Service cansform.transform.translation.x = tvec[0][0]ll failed:", str(e))

def call_disable_body_stiffness_service():
    rospy.wait_for_service('/body_stiffness/disable')  # Replace with the actual service name
    try:
        # Create a proxy to call the service
        disable_body_stiffness_proxy = rospy.ServiceProxy('/body_stiffness/disable', Empty)
        
        # Call the service with an empty request
        response = disable_body_stiffness_proxy()
        
        # Process the response (empty for this service)
        print("Disabled")
    except rospy.ServiceException as e:
        print("Service call failed:", str(e))
        
class MovetoTarget(object):

    def __init__(self, robotIP = "10.152.246.180", PORT = 9559):

        self.motionProxy = ALProxy("ALMotion", robotIP, PORT)
        self.postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
        call_enable_body_stiffness_service()
        self.pub = rospy.Publisher('/cmd_pose', Pose2D, queue_size=10)
        
        self.move_joints_server()

    def get_LArm_positions(self, req):
            try:
             #LArm Rest Position Cartesian_Position_Orientation: [0.020364301279187202, 0.12601032853126526, -0.11523474752902985, -0.6465103626251221, 1.423244833946228, 0.6563076972961426]
             #Bottom Part Cartesian_Position_Orientation: [0.15335305035114288, 0.06843108683824539, -0.01828966662287712, -1.910516619682312, 0.23121587932109833, -0.029442522674798965]
             #Upper Part Cartesian_Position_Orientation: [0.19423720240592957, 0.11404170095920563, 0.02963467501103878, -1.4287537336349487, 0.0009230562718585134, 0.13425925374031067]
                

            # UP Cartesian_Position_Orientation: [0.20340755581855774, 0.15785562992095947, 0.07319368422031403, -1.6913267374038696, -0.09684331715106964, 0.355697363615036]
            # DOWN [0.1751420795917511, 0.1285971701145172, 0.0202433243393898, -2.150057554244995, 0.01597822830080986, 0.21731269359588623]
            # MID Cartesian_Position_Orientation: [0.121991366147995, 0.11651371419429779, 0.007444058544933796, -2.1198246479034424, -0.05146960914134979, 0.1333589255809784]
                JointName = req.JointName
                space = motion.FRAME_TORSO   # Task space {FRAME_TORSO = 0, FRAME_WORLD = 1, FRAME_ROBOT = 2}.
                useSensorValues = True  #If true, the sensor values will be used to determine the position.
                Position6D = self.motionProxy.getPosition(JointName, space, useSensorValues)
                return (Position6D,)
            except Exception as e:
                print(e)
                print("Move joints failed")
                return False
            
    def LArm_init(self):
        try: 
            
            #Position6DLeft = [0.121991366147995, 0.11651371419429779, 0.007444058544933796, -2.1198246479034424, -0.05146960914134979, 0.1333589255809784]
            Position6DLeft = [0.11926589906215668, 0.08077982068061829, -0.04658479616045952, -0.16600564122200012, 0.2785385251045227, 0.02825542539358139]
            JointName = "LArm"
            space = motion.FRAME_TORSO
            MaximumVelocity = 0.9
            self.motionProxy.setPosition(JointName, space, Position6DLeft, MaximumVelocity, 63)
            print('Move to the mid position')

        
        except Exception as e:
                print(e)
                print("Move joints failed")
                return False
        
    
    def RArm_init(self):
        try: 
            
            #Position6DLeft = [0.121991366147995, 0.11651371419429779, 0.007444058544933796, -2.1198246479034424, -0.05146960914134979, 0.1333589255809784]
            Position6DRight =  [0.13970205187797546, -0.10936237871646881, 0.008094454184174538, 1.9241509437561035, -0.05772218480706215, -0.16212432086467743]
            JointName = "RArm"
            space = motion.FRAME_TORSO
            MaximumVelocity = 0.9
            self.motionProxy.setPosition(JointName, space, Position6DRight, MaximumVelocity, 63)
            print('Move to the mid position')

        
        except Exception as e:
                print(e)
                print("Move joints failed")
                return False
        
            

    def move_LArm(self):
        try:

            JointName = "LArm"
            space = motion.FRAME_TORSO
            MaximumVelocity = 0.4
            # Position6DLeft_Down =  [0.1751420795917511, 0.1285971701145172, 0.0202433243393898, -2.150057554244995, 0.01597822830080986, 0.21731269359588623]
            # self.motionProxy.setPosition(JointName, space, Position6DLeft_Down, MaximumVelocity, 63)
            # print('Move Down Row')
            # rospy.sleep(2)
            # Position6DLeft_MoveBack = [0.121991366147995, 0.11651371419429779, 0.007444058544933796, -2.1198246479034424, -0.05146960914134979, 0.1333589255809784]
            # self.motionProxy.setPosition(JointName, space, Position6DLeft_MoveBack, MaximumVelocity, 63)
            # print('Move Back with Card')
            # Position6DLeft_Up = [0.20340755581855774, 0.15785562992095947, 0.07319368422031403, -1.6913267374038696, -0.09684331715106964, 0.355697363615036]
            # self.motionProxy.setPosition(JointName, space, Position6DLeft_Up, MaximumVelocity, 63)
            # print('Move Upper Row')
            Position6D_Up = [0.18167956173419952, 0.10307253897190094, -0.01296320278197527, -0.2035345882177353, 0.22035706043243408, 0.09165364503860474]
            self.motionProxy.setPosition(JointName, space, Position6D_Up, MaximumVelocity, 63)
            print('Choose Up Middle')



        except Exception as e:
                print(e)
                print("Move joints failed")
                return False
        
    def move_RArm_withHead(self):
        try:

            JointName = "RArm"
            #JointNameT = "LArm"
            space = motion.FRAME_TORSO
            MaximumVelocity = 0.4
            # Position6DLeft_Down =  [0.1751420795917511, 0.1285971701145172, 0.0202433243393898, -2.150057554244995, 0.01597822830080986, 0.21731269359588623]
            # self.motionProxy.setPosition(JointName, space, Position6DLeft_Down, MaximumVelocity, 63)
            # print('Move Down Row')
            # rospy.sleep(2)
            # Position6DLeft_MoveBack = [0.121991366147995, 0.11651371419429779, 0.007444058544933796, -2.1198246479034424, -0.05146960914134979, 0.1333589255809784]
            # self.motionProxy.setPosition(JointName, space, Position6DLeft_MoveBack, MaximumVelocity, 63)
            # print('Move Back with Card')
            # Position6DLeft_Up = [0.20340755581855774, 0.15785562992095947, 0.07319368422031403, -1.6913267374038696, -0.09684331715106964, 0.355697363615036]
            # self.motionProxy.setPosition(JointName, space, Position6DLeft_Up, MaximumVelocity, 63)
            # print('Move Upper Row')
            # Position6D_RightArm = [0.05069751664996147, 0.12137755006551743, -0.10618214309215546, -1.0323925018310547, 1.1300336122512817, 0.03199877589941025]
            # self.motionProxy.setPosition(JointNameT, space, Position6D_RightArm, MaximumVelocity, 63)
            # print('Move Hand Up')
            rospy.sleep(2)
            pose_msg = Pose2D()
            pose_msg.x = 0.025
            pose_msg.y = 0.002
            pose_msg.theta = 0.0
            leftArmEnable  = True
            rightArmEnable = False
            self.motionProxy.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
            #self.pub.publish(pose_msg)
            print('tried to walk')
            rospy.sleep(2)
            Position6D_MoveUp = [0.13642016053199768, -0.20635484158992767, 0.10498404502868652, 0.6817927360534668, -0.27265381813049316, -0.12625375390052795]
            self.motionProxy.setPosition(JointName, space, Position6D_MoveUp, MaximumVelocity, 63)
            print('Move Hand Up')
            rospy.sleep(2)
            Position6D_MoveUp2 =[0.2021799087524414, -0.13816867768764496, 0.17279157042503357, 2.1393582820892334, -0.3292554020881653, -0.17120546102523804]
            self.motionProxy.setPosition(JointName, space, Position6D_MoveUp2, MaximumVelocity, 63)
            print('Move Hand Up 2')
            rospy.sleep(2)
            Position6D_GrabCard = [0.18671053647994995, -0.12029566615819931, 0.02682342939078808, 1.8209658861160278, 0.014070006087422371, -0.11497621238231659]
            self.motionProxy.setPosition(JointName, space, Position6D_GrabCard, MaximumVelocity, 63)
            print('Grab Card')
            rospy.sleep(2)
            self.motionProxy.setPosition(JointName, space, Position6D_MoveUp2, MaximumVelocity, 63)
            print('Move Hand Up')
            rospy.sleep(2)
            Position6D_Look = [0.14135761559009552, -0.10562633723020554, 0.15602819621562958, -2.2834408283233643, -1.018161416053772, -0.3273433744907379]
            self.motionProxy.setPosition(JointName, space, Position6D_Look, MaximumVelocity, 63)
            print('Look at the card')
            rospy.sleep(2)
            JointNameH = 'Head'
            Position6D_Head = [0.0, 0.0, 0.1264999955892563, 0.0, -0.5492139458656311, -0.46331000328063965]
            self.motionProxy.setPosition(JointNameH, space, Position6D_Head, MaximumVelocity, 63)
            print('Head Rotation')
            rospy.sleep(2)




        except Exception as e:
            print(e)
            print("Move joints failed")
            return False


    def move_RArm_withLeftArm(self):
            try:

                JointName = "RArm"
                JointNameT = "LArm"
                space = motion.FRAME_TORSO
                MaximumVelocity = 0.4
                # Position6DLeft_Down =  [0.1751420795917511, 0.1285971701145172, 0.0202433243393898, -2.150057554244995, 0.01597822830080986, 0.21731269359588623]
                # self.motionProxy.setPosition(JointName, space, Position6DLeft_Down, MaximumVelocity, 63)
                # print('Move Down Row')
                # rospy.sleep(2)
                # Position6DLeft_MoveBack = [0.121991366147995, 0.11651371419429779, 0.007444058544933796, -2.1198246479034424, -0.05146960914134979, 0.1333589255809784]
                # self.motionProxy.setPosition(JointName, space, Position6DLeft_MoveBack, MaximumVelocity, 63)
                # print('Move Back with Card')
                # Position6DLeft_Up = [0.20340755581855774, 0.15785562992095947, 0.07319368422031403, -1.6913267374038696, -0.09684331715106964, 0.355697363615036]
                # self.motionProxy.setPosition(JointName, space, Position6DLeft_Up, MaximumVelocity, 63)
                # print('Move Upper Row')
                Position6D_RightArm = [0.05069751664996147, 0.12137755006551743, -0.10618214309215546, -1.0323925018310547, 1.1300336122512817, 0.03199877589941025]
                self.motionProxy.setPosition(JointNameT, space, Position6D_RightArm, MaximumVelocity, 63)
                print('Move Hand Up')
                rospy.sleep(2)
                pose_msg = Pose2D()
                pose_msg.x = 0.025
                pose_msg.y = 0.002
                pose_msg.theta = 0.0
                leftArmEnable  = True
                rightArmEnable = False
                self.motionProxy.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
                #self.pub.publish(pose_msg)
                print('tried to walk')
                rospy.sleep(2)
                Position6D_MoveUp = [0.13642016053199768, -0.20635484158992767, 0.10498404502868652, 0.6817927360534668, -0.27265381813049316, -0.12625375390052795]
                self.motionProxy.setPosition(JointName, space, Position6D_MoveUp, MaximumVelocity, 63)
                print('Move Hand Up')
                rospy.sleep(2)
                Position6D_MoveUp2 =[0.2021799087524414, -0.13816867768764496, 0.17279157042503357, 2.1393582820892334, -0.3292554020881653, -0.17120546102523804]
                self.motionProxy.setPosition(JointName, space, Position6D_MoveUp2, MaximumVelocity, 63)
                print('Move Hand Up 2')
                rospy.sleep(2)
                Position6D_GrabCard = [0.18671053647994995, -0.12029566615819931, 0.02682342939078808, 1.8209658861160278, 0.014070006087422371, -0.11497621238231659]
                self.motionProxy.setPosition(JointName, space, Position6D_GrabCard, MaximumVelocity, 63)
                print('Grab Card')
                rospy.sleep(2)
                self.motionProxy.setPosition(JointName, space, Position6D_MoveUp2, MaximumVelocity, 63)
                print('Move Hand Up')
                rospy.sleep(2)
                Position6D_PoseCard =  [0.18736161291599274, -0.021594852209091187, 0.050105225294828415, 1.897408127784729, -0.007399186957627535, 0.43245595693588257]
                self.motionProxy.setPosition(JointName, space, Position6D_PoseCard, MaximumVelocity, 63)
                print('Intermediate Pose Card')
                rospy.sleep(2)
                Position6D_PoseCard2 = [0.15297944843769073, -0.030844084918498993, -0.026381902396678925, 2.0064480304718018, 0.4038686752319336, 0.4108651876449585]
                self.motionProxy.setPosition(JointName, space, Position6D_PoseCard2, MaximumVelocity, 63)
                print('Pose Card')
                rospy.sleep(5)
                Position6D_EndMovement = [0.08185836672782898, -0.04597493261098862, -0.0026721833273768425, 1.7218643426895142, 0.1917998343706131, 1.0842033624649048]
                self.motionProxy.setPosition(JointName, space, Position6D_EndMovement, MaximumVelocity, 63)
                print('Pose Card')



            except Exception as e:
                    print(e)
                    print("Move joints failed")
                    return False

            
    def move_to_Object(self):
        try:
            
            #Middle Low Picked 
            pose_msg = Pose2D()
            pose_msg.x = 0.13
            pose_msg.y = 0
            pose_msg.theta = 0.0
            leftArmEnable  = False
            rightArmEnable = False
            self.motionProxy.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
            self.pub.publish(pose_msg)
            print('tried to walk')


            #Left Low Picked
            # pose_msg = Pose2D()
            # pose_msg.x = 0.12
            # pose_msg.y = 0.05
            # pose_msg.theta = 0.0
            # self.postureProxy.goToPosture("StandInit", 0.5)
            # rospy.sleep(2)
            # self.pub.publish(pose_msg)
            # print('tried to walk')
            

            return True

        except Exception as e:
            print(e)
            print("Move to Target failed")
            return False
        
    def move_back(self):
        try:
            
            #Middle Low Picked 
            pose_msg = Pose2D()
            pose_msg.x = 0.14
            pose_msg.y = 0
            pose_msg.theta = 0.0
            self.pub.publish(pose_msg)
            rospy.sleep(2)
            self.postureProxy.goToPosture("StandZero", 1)

            
            print('tried to walk')


            #Left Low Picked
            # pose_msg = Pose2D()
            # pose_msg.x = 0.12
            # pose_msg.y = 0.05
            # pose_msg.theta = 0.0
            # self.postureProxy.goToPosture("StandInit", 0.5)
            # rospy.sleep(2)
            # self.pub.publish(pose_msg)
            # print('tried to walk')
            

            return True

        except Exception as e:
            print(e)
            print("Move to Target failed")
            return False
        
        
    def throw_card(self):
        try:
            
            #Middle Low Picked 
            pose_msg = Pose2D()
            pose_msg.x = -0.01
            pose_msg.y = -0.12
            pose_msg.theta = 0.0
            leftArmEnable  = False
            rightArmEnable = True
            self.motionProxy.setMoveArmsEnabled(leftArmEnable, rightArmEnable)
            self.pub.publish(pose_msg)
            print('tried to walk')
            rospy.sleep(2)
            # self.postureProxy.goToPosture("StandInit", 1)
  




            #Left Low Picked
            # pose_msg = Pose2D()
            # pose_msg.x = 0.12
            # pose_msg.y = 0.05
            # pose_msg.theta = 0.0
            # self.postureProxy.goToPosture("StandInit", 0.5)
            # rospy.sleep(2)
            # self.pub.publish(pose_msg)
            # print('tried to walk')
            

            return True

        except Exception as e:
            print(e)
            print("Move to Target failed")
            return False
        
    def put_card(self):
        try:
            JointName = "LArm"
            space = motion.FRAME_TORSO
            MaximumVelocity = 0.6
            Position6DLeft_PutCard = [0.1629522293806076, 0.17891249060630798, 0.08092391490936279, -0.014790819957852364, -0.06110773980617523, -0.10336251556873322]
            self.motionProxy.setPosition(JointName, space, Position6DLeft_PutCard, MaximumVelocity, 63)
            rospy.sleep(2)
            Position6DLeft_PutCard =[0.20895427465438843, 0.05273515731096268, 0.05187284201383591, -0.52846360206604, 0.1518012136220932, -0.261351615190506]
            self.motionProxy.setPosition(JointName, space, Position6DLeft_PutCard, MaximumVelocity, 63)
            print('Movement 2')


            return True

        except Exception as e:
            print(e) 
            print("Move to Target failed")
            return False   
        

    def Left_Hand_Movement(self):
        # pick a card on shelf with left tool
        try:
            self.LArm_init()
            rospy.sleep(2)
            #self.move_to_Object()
            # rospy.sleep(2)
            self.move_LArm()
            rospy.sleep(2)
            self.LArm_init()
            rospy.sleep(2)
            self.throw_card()
            rospy.sleep(2)
            self.move_LArm()
            rospy.sleep(2)
            self.LArm_init()
            rospy.sleep(2)

        except Exception as e:
            print(e) 
            print("Left Hand Movement Fail")
            return False   
        
    
    def Right_Hand_MovementHead(self):
        # pick card from the deck, then look at it.
        try:
            self.RArm_init()
            rospy.sleep(2)
            self.move_RArm_withHead()
            rospy.sleep(2)
            self.RArm_init()

        
        except Exception as e:
            print(e) 
            print("Left Hand Movement Fail")
            return False   
        
    def Right_Hand_MovementLeft(self):
        # pick card from the deck and put it on the table.
        try:
            self.RArm_init()
            rospy.sleep(2)
            self.move_RArm_withLeftArm()
            rospy.sleep(2)
            self.RArm_init()

        
        except Exception as e:
            print(e) 
            print("Left Hand Movement Fail")
            return False   



    def move_joints_server(self):
        rospy.init_node('move_joints_server')
        service3 = rospy.Service('get_LArm_positions', CartesianPositionOrientation, self.get_LArm_positions)
        # service1 = rospy.Service('FeetMovement', Pose2D, self.move_to_Object)
        print("Ready to move joints.")
        self.postureProxy.goToPosture("StandInit", 0.5)
        rospy.sleep(2)

        mode = raw_input("choose right or left movement, r/l/c \n")
        print(mode)
        if mode == 'l':
            self.Left_Hand_Movement()
        elif mode =='r':
            self.Right_Hand_MovementHead()
        elif mode =='c':
            self.Right_Hand_MovementLeft()
        else:
            print('Error')
        rospy.spin()
    
# 	('Rotated Matrix:', array([[  6.12323400e-17,   0.00000000e+00,   1.00000000e+00],
#    [  1.00000000e+00,   6.12323400e-17,  -6.12323400e-17],
#    [ -6.12323400e-17,   1.00000000e+00,   3.74939946e-33]]))

if __name__ == '__main__':
    # motionProxy = ALProxy("ALMotion", robotIP, PORT)
    # rospy.init_node('move_joints_server')
    # rospy.spin()
    # robotIP=str(sys.argv[1])
    # PORT=int(sys.argv[2])
    # print sys.argv[2]
 
    jc = MovetoTarget()