The function _compute_desired_force_and_euler takes in the following parameters:

control_timestep: Time step for control.
cur_pos: Current position of the system.
cur_quat: Current orientation quaternion of the system.
cur_vel: Current velocity of the system.
target_pos: Reference position for tracking.
target_rpy: Reference roll, pitch, and yaw angles for tracking.
target_vel: Reference velocity for tracking.
target_acc: Reference acceleration for tracking.

The function computes the desired thrust and Euler angles based on the provided inputs and returns them along with the position error.

In order to achieve the desired performance, change the variables kp and kv defined in the function.

Compute the thrust using the mass and the calculated accelaration

Post which, compute the desired attitute control using the rotational matrix and convert it into euler angles.
