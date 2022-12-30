import smbus
import RPi.GPIO as GPIO
import math
import time
from time import sleep

#Setup GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Pines ESC
GPIO.setup(4,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)

pwm1 = GPIO.PWM(4,50)
pwm2 = GPIO.PWM(5,50)

pwm1.start(5)
pwm2.start(5)
sleep(10)

PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT = 0x3B
ACCEL_YOUT = 0x3D
ACCEL_ZOUT = 0x3F
GYRO_XOUT  = 0x43
GYRO_YOUT  = 0x45
GYRO_ZOUT  = 0x47

bus = smbus.SMBus(1) 
Device_Address = 0x68

def setDuty():
    Duty(0)

def _map(x, in_min, in_max, out_min, out_max):
    return ((x-in_min)*(out_max-out_min)/(in_max-in_min) + out_min)
    
def MPU_Init():
    
    #write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    #Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    #Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    #Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    #Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    #Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value

A_ref = 0
Vel_i = 1000

pid_p = 0
pid_i = 0
pid_d = 0

kp = 3.5
ki = 0.005
kd = 2.05

error_prev = 0
t_prev = int(time.time_ns())/1000000000

MPU_Init()

while True:
    #Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT)
    acc_y = read_raw_data(ACCEL_YOUT)
    acc_z = read_raw_data(ACCEL_ZOUT)

    #Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT)
    gyro_y = read_raw_data(GYRO_YOUT)
    gyro_z = read_raw_data(GYRO_ZOUT)

    Ax = acc_x/16384.0
    Ay = acc_y/16384.0 
    Az = acc_z/16384.0

    Gx = gyro_x/131.0
    Gy = gyro_y/131.0
    Gz = gyro_z/131.0
    
    A_ac = round(math.atan(Ay/Az)*180/math.pi)
    error = A_ac - A_ref
    t = int(time.time_ns())/1000000000
    
    
    pid_p = kp*error
    
    if (-3 < error < 3):
        pid_i = pid_i+(ki*error)
    else:
        pid_i = 0
    
    pid_d = kd*((error-error_prev)/(t-t_prev))
    
    PID = pid_p + pid_i + pid_d
    
    
    if (PID < -1000):
        PID = -1000
    
    if (PID > 1000):
        PID = 1000
    
    Vel_M1 = Vel_i + PID
    Vel_M2 = Vel_i - PID
    
    if (Vel_M1 < 1000):
        Vel_M1 = 1000
    
    if (Vel_M1 > 2000):
        Vel_M1 = 2000
    
    if (Vel_M2 < 1000):
        Vel_M2 = 1000
    
    if (Vel_M2 > 2000):
        Vel_M2 = 2000
    
    M1 = _map(Vel_M1, 1000, 2000, 5, 10)
    M2 = _map(Vel_M2, 1000, 2000, 5, 10)
    
    GPIO.output(4,True)
    pwm1.ChangeDutyCycle(M1)
    GPIO.output(5,False)
    
    GPIO.output(5,True)
    pwm2.ChangeDutyCycle(M2)
    GPIO.output(5,False)
    
    Angulo = _map(A_ac, -90, 90, 0, 180)
    
    
    print("Angulo A = %.2f" %A_ac, "Error = %.2f" %error, "PID_p = %.4f" %pid_p, "PID_i = %.4f" %pid_i, "PID_d = %.4f" %pid_d)
    print("PID = %.4f" %PID, "Vel. M1 = %.4f" %Vel_M1, "Vel. M2 = %.4f" %Vel_M2, "Ciclo M1 = %.4f" %M1, "Ciclo M2 = %.4f" %M2)
    
    error_prev = error
    t_prev = int(time.time_ns())/1000000000
    sleep(0.1)