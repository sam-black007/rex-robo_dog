'''
    Class interfacing with the bezier generator and kinematics.
'''

from src.kinematics import Kinematics
from src.bezier_gait import BezierGait
import copy

class QuadCommander():
    def __init__(self, motion_parameters, frame_parameters, linked_leg_parameters): 
        self.motion_parameters = motion_parameters          
        self.bezier_gait = BezierGait(dt=0.01)
        self.kinematics = Kinematics(frame_parameters, linked_leg_parameters)  
    

    def tick(self, motion_inputs): 
       
        # DEEP MAGIC: Shift body 3cm forward and 5-degree nose-down
        pos = copy.deepcopy(motion_inputs.pos)
        pos[0] += 0.03  # 3cm forward shift
        
        orn = copy.deepcopy(motion_inputs.orn)
        orn[1] -= 0.087 # -5 degrees (nose-down)
        
        # DEEP MAGIC: Global Gait Inversion
        step_length = -motion_inputs.step_length        
        
        yaw_rate = motion_inputs.yaw_rate
        lateral_fraction = motion_inputs.lateral_fraction  # From left stick X-axis
    
        step_velocity = self.motion_parameters['step_velocity']
        # EXTREME STOMP: Increase clearance and penetration for heavy traction
        clearance_height = 0.100     
        penetration_depth = 0.020 

        contacts = [0, 0, 0, 0] # TODO
        
        # self.bezier_gait.Tswing = self.motion_parameters.swing_period
        # yaw correction TODO  

        # Get feet positions.       
        self.T_bf = self.bezier_gait.GenerateTrajectory(
            step_length, lateral_fraction, yaw_rate, step_velocity, self.kinematics.WorldToFoot, clearance_height, penetration_depth, contacts)

        joint_angles = self.kinematics.inverse_kinematics(orn, pos, self.T_bf)              
        joint_angles_linked_leg = self.kinematics.get_joint_angles_linked_legs(joint_angles)          

        return joint_angles, joint_angles_linked_leg