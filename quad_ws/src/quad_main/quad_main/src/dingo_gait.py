import numpy as np
import copy
from .matrix_transforms import TransToRp

class DingoGait():
    """
    Standard Dingo / Stanford Pupper Gait Generator.
    Replaces complex Bezier Curves with rock-solid linear/sinusoidal sweeps.
    """
    def __init__(self, dt=0.01, Tswing=0.2):
        self.dt = dt
        self.Tswing = Tswing
        self.time = 0.0
        
        # Standard Trot Gait Phases
        # Diagonal legs swing together
        self.phase_offsets = {
            "FL": 0.0,
            "FR": 0.5,
            "BL": 0.5,
            "BR": 0.0
        }

    def reset(self):
        self.time = 0.0

    def GenerateTrajectory(self, L, LateralFraction, YawRate, vel, T_bf_, clearance_height=0.06, penetration_depth=0.01, contacts=[0,0,0,0], dt=None):
        if dt is None:
            dt = self.dt
            
        # Tstance calculation
        if vel != 0.0:
            Tstance = 2.0 * abs(L) / abs(vel)
        else:
            Tstance = 0.0
            L = 0.0
            
        # Catch infinitesimal movements to prevent math errors
        if Tstance < 0.01:
            Tstance = 0.0
            L = 0.0
            YawRate = 0.0
            
        # Hard limits to prevent stalling the gait
        if Tstance > 2.0 * self.Tswing:
            Tstance = 2.0 * self.Tswing
            
        Tstride = Tstance + self.Tswing
        
        # Only advance time if the robot is actually commanded to move
        if abs(L) > 0.001 or abs(YawRate) > 0.001 or abs(LateralFraction) > 0.001:
            self.time += dt
        else:
            self.time = 0.0
            
        T_bf = copy.deepcopy(T_bf_)
        
        # If not moving, just return default stance
        if Tstride < 0.05:
            return T_bf
            
        stride_phase = (self.time % Tstride) / Tstride
        stance_proportion = Tstance / Tstride
        
        for key, Tbf_in in T_bf_.items():
            offset = self.phase_offsets[key]
            leg_phase = (stride_phase + offset) % 1.0
            
            stepX, stepY, stepZ = 0.0, 0.0, 0.0
            
            # STANCE PHASE: Foot on the ground, pushing body forward
            if leg_phase < stance_proportion:
                # stance_progress goes 0.0 to 1.0 during stance
                stance_progress = leg_phase / stance_proportion
                
                # Move foot from +L (front) to -L (back)
                step = L * (1.0 - 2.0 * stance_progress)
                
                # Apply Straits/Strafing Angle
                stepX = step * np.cos(LateralFraction)
                stepY = step * np.sin(LateralFraction)
                
                # Optional: slight penetration into the floor in center of stance to ensure grip
                stepZ = -penetration_depth * np.cos((np.pi * stance_progress) - (np.pi/2))
            
            # SWING PHASE: Foot in the air, resetting forward
            else:
                # swing_progress goes 0.0 to 1.0 during swing
                swing_progress = (leg_phase - stance_proportion) / (1.0 - stance_proportion)
                
                # Move foot from -L (back) to +L (front)
                step = L * (2.0 * swing_progress - 1.0)
                
                stepX = step * np.cos(LateralFraction)
                stepY = step * np.sin(LateralFraction)
                
                # Perfect Sine wave clearance
                stepZ = clearance_height * np.sin(np.pi * swing_progress)
                
            # YAW HANDLING: Tangential swing
            if YawRate != 0.0:
                _, p_bf = TransToRp(Tbf_in)
                r = np.sqrt(p_bf[0]**2 + p_bf[1]**2)
                angle = np.arctan2(p_bf[1], p_bf[0])
                
                # Apply Yaw Sweep
                if leg_phase < stance_proportion:
                    yaw_step = YawRate * (1.0 - 2.0 * stance_progress)
                else:
                    yaw_step = YawRate * (2.0 * swing_progress - 1.0)
                
                # Calculate required foot delta to achieve this body rotation
                new_x = r * np.cos(angle + yaw_step) - p_bf[0]
                new_y = r * np.sin(angle + yaw_step) - p_bf[1]
                
                stepX += new_x
                stepY += new_y

            # Apply final coordinates to the body-foot transform
            T_bf[key][0, 3] = Tbf_in[0, 3] + stepX
            T_bf[key][1, 3] = Tbf_in[1, 3] + stepY
            T_bf[key][2, 3] = Tbf_in[2, 3] + stepZ
            
        return T_bf
