import os
import math
import time
import numpy as np
import pybullet as p
import matplotlib.pyplot as plt

from scipy.spatial.transform import Rotation
from enum import Enum
from functools import wraps
import csv

class GeoController():
    """Geometric control class for Crazyflies.

    """

    def __init__(self,
                 g: float = 9.8,
                 m: float = 0.036,
                 kf: float = 3.16e-10,
                 km: float = 7.94e-12,
                 pwm2rpm_scale: float = 0.2685,
                 pwm2rpm_const: float = 4070.3,
                 min_pwm: float = 20000,
                 max_pwm: float = 65535
                 ):
        """Common control classes __init__ method.

        Args:
            g (float, optional): The gravitational acceleration in m/s^2.
            m (float, optional): Mass of the quadrotor in kg.
            kf (float, optional): thrust coefficient.
            km (float, optional): torque coefficient.
            pwm2rpm_scale (float, optional): PWM-to-RPM scale factor.
            pwm2rpm_const (float, optional): PWM-to-RPM constant factor.
            min_pwm (float, optional): minimum PWM.
            max_pwm (float, optional): maximum PWM.

        """
        self.grav = g
        self.mass = m
        self.GRAVITY = g * m # The gravitational force (M*g) acting on each drone.
        self.KF = kf
        self.KM = km
        self.PWM2RPM_SCALE = pwm2rpm_scale
        self.PWM2RPM_CONST = pwm2rpm_const
        self.MIN_PWM = min_pwm
        self.MAX_PWM = max_pwm
        self.MIXER_MATRIX = np.array([[.5, -.5, 1], [.5, .5, -1], [-.5, .5, 1], [-.5, -.5, -1]])
        self.reset()

        self.file1 = open('AcPos.csv', mode='w', newline='')
        self.writer1 = csv.writer(self.file1)
        self.writer1.writerow(["Errx", "ErrY",  "ErrZ", "ErrYaw", "DesPosX","DesPosY","DesPosZ","DesYaw", "AcPosX","AcPosY","AcPosZ","AcYaw"])

    def reset(self):
        """Resets the control classes.

        The previous step's and integral errors for both position and attitude are set to zero.

        """
        self.control_counter = 0  # Store the last roll, pitch, and yaw.
        self.last_rpy = np.zeros(3)  # Initialized PID control variables.
        self.last_pos_e = np.zeros(3)
        self.integral_pos_e = np.zeros(3)
        self.last_rpy_e = np.zeros(3)
        self.integral_rpy_e = np.zeros(3)
    
    def plot_error_graph(self, Actualp, Desiredp, DesiredYaw, AcrualYaw):
        """
        Update csv file with the values collected at each iteration
        """
        self.writer1.writerow([
            Actualp[0] - Desiredp[0],
            Actualp[1] - Desiredp[1],
            Actualp[2] - Desiredp[2],
            AcrualYaw - DesiredYaw,
            Desiredp[0],
            Desiredp[1],
            Desiredp[2],
            DesiredYaw,
            Actualp[0],
            Actualp[1],
            Actualp[2],
            AcrualYaw])






    def compute_control(self,
                        control_timestep,
                        cur_pos,
                        cur_quat,
                        cur_vel,
                        cur_ang_vel,
                        target_pos,
                        target_rpy=np.zeros(3),
                        target_vel=np.zeros(3),
                        target_acc=np.zeros(3),
                        target_rpy_rates=np.zeros(3)
                        ):
        """Compute the rotor speed using the geometric controller
            Args:
                control_timestep (float): The time step at which control is computed.
                cur_pos (ndarray): (3,1)-shaped array of floats containing the current position.
                cur_quat (ndarray): (4,1)-shaped array of floats containing the current orientation as a quaternion.
                cur_vel (ndarray): (3,1)-shaped array of floats containing the current velocity.
                cur_ang_vel (ndarray): (3,1)-shaped array of floats containing the current angular velocity.
                target_pos (ndarray): (3,1)-shaped array of floats containing the desired position.
                target_rpy (ndarray): (3,1)-shaped array of floats containing the desired yaw angle
                target_vel (ndarray): (3,1)-shaped array of floats containing the desired velocity.
                target_acc (ndarray): (3,1)-shaped array of floats containing the desired acceleration.
                target_rpy_rates (ndarray): (3,1)-shaped array of floats containing the desired bodyrate.
        """

        self.control_counter += 1

        desired_thrust, desire_rpy, pos_e = self._compute_desired_force_and_euler(control_timestep,
                                                                           cur_pos,
                                                                           cur_quat,
                                                                           cur_vel,
                                                                           target_pos,
                                                                           target_rpy,
                                                                           target_vel,
                                                                           target_acc
                                                                           )



        rpm = self._compute_rpms(control_timestep,
                                 desired_thrust,
                                 cur_quat,
                                 desire_rpy,
                                 target_rpy_rates
                                 )
        cur_rpy = p.getEulerFromQuaternion(cur_quat)
        return rpm, pos_e, desire_rpy[2] - cur_rpy[2]

    def _compute_desired_force_and_euler(self,
                                 control_timestep,
                                 cur_pos,
                                 cur_quat,
                                 cur_vel,
                                 target_pos, # reference position
                                 target_rpy, # the last entry contains the reference heading
                                 target_vel, # reference velocity
                                 target_acc  # reference acceleration
                                 ): 
        

        #---------Lab2: Design a geomtric controller--------#

        reference_yaw = target_rpy[2]

        # tracking errors
        pos_e = target_pos - cur_pos
        vel_e = target_vel - cur_vel
        
        # You should compute a proper desired_thrust and desired_euler
        # such that the circle trajectory can be tracked

        # declare variables for thrust and euler
        desired_thrust = 0
        desired_euler = np.zeros(3)

        # gain values for position and velocity
        kp = 5.3          ##tuning
        kv = 5.3              ##tuning
        #---------Tip 1: Compute the desired acceration command--------#

        # defining kpos and kvel using the constant declared above
        Kpos  = np.array([[kp,0,0],[0,kp,0],[0,0,kp]])
        Kvel  = np.array([[kv,0,0],[0,kv,0],[0,0,kv]])

        # calculating a_fb
        afb = np.dot(Kpos, pos_e.reshape(3,1)) + np.dot(Kvel ,vel_e.reshape(3,1))

        # defining gravity
        gr= np.array([0,0,self.grav])

        # calculating a_des
        ades = afb + target_acc.reshape(3,1) + gr.reshape(3,1)
        #---------Tip 2: Compute the desired thrust command--------#
        
        desired_thrust = self.mass * np.linalg.norm(ades)
        #---------Tip 3: Compute the desired attitude command--------#

        # calculating xB,yB,zB and stacking them to create a rotational matrix.
        # Further using it to computing euler angles
        # using inbuilt function function
        yc = np.array([-1 * math.sin(reference_yaw), math.cos(reference_yaw), 0])
        zBdes = ades/np.linalg.norm(ades)
        xBDesNum = np.cross(yc.reshape(1,3), zBdes.reshape(1,3))
        xBdes = xBDesNum/np.linalg.norm(xBDesNum)
        yBdes = np.cross(zBdes.reshape(1,3), xBdes.reshape(1,3))
        Rdes = np.vstack((xBdes,yBdes,zBdes.reshape(1,3))).T

        desired_euler = (Rotation.from_matrix(Rdes)).as_euler('xyz',degrees= False)

        # using current quaternion to calculate current yaw
        cur_rpy = p.getEulerFromQuaternion(cur_quat)
        # log this data into a csv to plot graph from
        self.plot_error_graph(cur_pos, target_pos,reference_yaw, cur_rpy[2])

        return desired_thrust, desired_euler, pos_e


    def _compute_rpms(self,
                      control_timestep,
                      thrust,
                      cur_quat,
                      target_euler,
                      target_rpy_rates
                      ):
        """DSL's CF2.x PID attitude control.

        Args:
            control_timestep (float): The time step at which control is computed.
            thrust (float): The target thrust along the drone z-axis.
            cur_quat (ndarray): (4,1)-shaped array of floats containing the current orientation as a quaternion.
            target_euler (ndarray): (3,1)-shaped array of floats containing the computed target Euler angles.
            target_rpy_rates (ndarray): (3,1)-shaped array of floats containing the desired roll, pitch, and yaw rates.

        Returns:
            ndarray: (4,1)-shaped array of integers containing the RPMs to apply to each of the 4 motors.

        """

        thrust = (math.sqrt(thrust / (4*self.KF)) - self.PWM2RPM_CONST) / self.PWM2RPM_SCALE

        self.P_COEFF_TOR = np.array([70000., 70000., 60000.])
        self.I_COEFF_TOR = np.array([.0, .0, 500.])
        self.D_COEFF_TOR = np.array([20000., 20000., 12000.])

        cur_rotation = np.array(p.getMatrixFromQuaternion(cur_quat)).reshape(3, 3)
        cur_rpy = np.array(p.getEulerFromQuaternion(cur_quat))
        target_quat = (Rotation.from_euler('xyz', target_euler, degrees=False)).as_quat()
        w, x, y, z = target_quat
        target_rotation = (Rotation.from_quat([w, x, y, z])).as_matrix()
        rot_matrix_e = np.dot((target_rotation.transpose()), cur_rotation) - np.dot(cur_rotation.transpose(), target_rotation)
        rot_e = np.array([rot_matrix_e[2, 1], rot_matrix_e[0, 2], rot_matrix_e[1, 0]])
        rpy_rates_e = target_rpy_rates - (cur_rpy - self.last_rpy)/control_timestep
        self.last_rpy = cur_rpy
        self.integral_rpy_e = self.integral_rpy_e - rot_e*control_timestep
        self.integral_rpy_e = np.clip(self.integral_rpy_e, -1500., 1500.)
        self.integral_rpy_e[0:2] = np.clip(self.integral_rpy_e[0:2], -1., 1.)
        # PID target torques.
        target_torques = - np.multiply(self.P_COEFF_TOR, rot_e) \
                         + np.multiply(self.D_COEFF_TOR, rpy_rates_e) \
                         + np.multiply(self.I_COEFF_TOR, self.integral_rpy_e)
        target_torques = np.clip(target_torques, -3200, 3200)
        pwm = thrust + np.dot(self.MIXER_MATRIX, target_torques)
        pwm = np.clip(pwm, self.MIN_PWM, self.MAX_PWM)
        return self.PWM2RPM_SCALE * pwm + self.PWM2RPM_CONST