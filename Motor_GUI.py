
import customtkinter
import platform
import os
import logging
from tkinter.messagebox import showinfo
from math import pi
import time
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import serial as sr
import tkinter as tk

# Configure debug format
logging.basicConfig(level = logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s',
    datefmt='%H:%M:%S'
)
#logging.disable(logging.DEBUG)


# Finds out where the program and images are stored
my_os = platform.system()
if my_os == "Windows":
    Image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    logging.debug("Os is Windows")
else:
    Image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    logging.debug("Os is Linux")
    
logging.debug(Image_path)

#Default serial params
s = sr.Serial()
_baudrate = 256000
_port = 'COM3'
#s.open()

text_size = 14

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

color_mode = "light"

port_open = 0
global_position = 0
global_speed = 0
global_current = 0
values_show_tick = 0


# Serial handler thread
def Serial_handler():
      None
      
# Avg 25 FPS = 0.04s
# We have 100 samples * 0.04s = 4s, x scale goes from 0 to 4 seconds
x_len = 100
x = np.linspace(0, 4, 100)
ys1 = [0] * x_len
ys2 = [0] * x_len
ys3 = [0] * x_len

def animate_sine_wave(i, line1, x):
    global frame_count
    global global_position
    frame_count += 1
    global ys1
    #line1.set_ydata(np.sin(x + i/10))
    ys1.append(global_position)
    ys1 = ys1[-x_len:]
    line1.set_ydata(ys1)
    return line1,

def animate_square_wave(i, line2, x):
    global global_speed
    global ys2
    ys2.append(global_speed)
    ys2 = ys2[-x_len:]
    line2.set_ydata(ys2)
    #line2.set_ydata(np.sign(np.sin(2 * np.pi * (x + i/10))))
    return line2,

def animate_sawtooth_wave(i, line3, x):
    global global_current
    global ys3
    ys3.append(global_current)
    ys3 = ys3[-x_len:]
    line3.set_ydata(ys3)
    #line3.set_ydata(2 * (x + i/10 - np.floor(x + i/10)) - 1)
    return line3,

# GUI
def GUI(var):

    global start_time, frame_count
    global x

    start_time = time.time()
    
    frame_count = 0
    app = customtkinter.CTk()

        # configure window
    app.title("Spectral motor GUI.py")
    app.geometry(f"{1600}x{1200}")
    app.attributes('-topmost',False)

    # Add app icon
    #logo = (os.path.join(Image_path, "logo.ico"))
    #app.iconbitmap(logo)

    # configure grid layout (4x5) weight 0 means it is fixed, 1 it is scaling
    app.grid_columnconfigure((1,2), weight=1)
    app.grid_columnconfigure((0), weight=1)
    app.grid_rowconfigure((0), weight=0)
    app.grid_rowconfigure((1), weight=0)
    app.grid_rowconfigure((2), weight=1)
    app.grid_rowconfigure((3), weight=0) 
    app.grid_rowconfigure((4), weight=0) 

    fig = plt.figure(figsize=(45, 15))  # Adjust the figsize to fit three plots vertically

    ax1 = fig.add_subplot(311)  # Adjust the subplot indices
    y_range = [-16000, 16000] # What range to show on Y axis
    ax1.set_ylim(y_range)
    #x = np.linspace(0, 2*np.pi, 100)
    #x = np.linspace(0, 5000, 5000)
    line1, = ax1.plot(x, np.sin(x))
    ax1.set_title("Position [ticks]")
    ax1.grid(True)


    y_range2 = [-10000, 10000] # What range to show on Y axis
    ax2 = fig.add_subplot(312)  # Adjust the subplot indices
    ax2.set_ylim(y_range2)
    line2, = ax2.plot(x, np.sign(np.sin(2 * np.pi * x)))
    ax2.set_title("Speed [ticks/s]")
    ax2.grid(True)


    y_range3 = [-2000, 2000] # What range to show on Y axis
    ax3 = fig.add_subplot(313)  # Adjust the subplot indices
    ax3.set_ylim(y_range3)
    line3, = ax3.plot(x, 2 * (x - np.floor(x)) - 1)
    ax3.set_title("Current [mA]")
    ax3.grid(True)

 
    def Top_frame():

        Top_frame = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
        Top_frame.grid(row=0, column=0, columnspan=4, padx=(5,5), pady=(5,5),sticky="new")
        Top_frame.grid_columnconfigure(0, weight=0)
        Top_frame.grid_rowconfigure(0, weight=0)

        uart_label = customtkinter.CTkLabel( Top_frame, text="UART baud: ", anchor="e")
        uart_label.grid(row=0, column=0, padx=(5, 0))

        app.uart_baud_entry = customtkinter.CTkEntry( Top_frame, width= 100)
        app.uart_baud_entry.grid(row=0, column=1, padx=(5, 0),pady=(3,3))

        uart_com = customtkinter.CTkLabel( Top_frame, text="UART COM: ", anchor="e")
        uart_com.grid(row=0, column=2, padx=(5, 0))

        app.uart_com_entry = customtkinter.CTkEntry( Top_frame, width= 100)
        app.uart_com_entry.grid(row=0, column=3, padx=(5, 0),pady=(3,3))

        UART_connect = customtkinter.CTkButton( Top_frame,text="Connect UART", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Connect_serial)
        UART_connect.grid(row=0, column=4, padx=20,pady = (5,5),sticky="news")

        app.uart_status = customtkinter.CTkLabel( Top_frame, text="Not connected ", anchor="e", text_color="red")
        app.uart_status.grid(row=0, column=5, padx=(5, 0))

        app.uart_baud_entry.insert(0,"256000")
        app.uart_com_entry.insert(0,"COM3")

        CAN_label = customtkinter.CTkLabel( Top_frame, text="CAN baud: ", anchor="e")
        CAN_label.grid(row=1, column=0, padx=(5, 0))

        CAN_baud_entry = customtkinter.CTkEntry( Top_frame, width= 100)
        CAN_baud_entry.grid(row=1, column=1, padx=(5, 0),pady=(3,3))

        CAN_com = customtkinter.CTkLabel( Top_frame, text="CAN COM: ", anchor="e")
        CAN_com.grid(row=1, column=2, padx=(5, 0))

        CAN_com_entry = customtkinter.CTkEntry( Top_frame, width= 100)
        CAN_com_entry.grid(row=1, column=3, padx=(5, 0),pady=(3,3))

        CAN_id = customtkinter.CTkLabel( Top_frame, text="CAN node ID: ", anchor="e")
        CAN_id.grid(row=1, column=5, padx=(5, 0))

        CAN_id_entry = customtkinter.CTkEntry( Top_frame, width= 100)
        CAN_id_entry.grid(row=1, column=6, padx=(5, 0),pady=(3,3))

        CAN_connect = customtkinter.CTkButton( Top_frame,text="Connect CAN", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
        CAN_connect.grid(row=1, column=4, padx=20,pady = (5,5),sticky="news")

        app.CAN_status = customtkinter.CTkLabel( Top_frame, text="Not connected ", anchor="e", text_color="red")
        app.CAN_status.grid(row=1, column=7, padx=(5, 0))

        #Control_button = customtkinter.CTkButton( Top_frame,text="Control", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command = test)
        #Control_button.grid(row=0, column=0, padx=20,pady = (5,5),sticky="news")

        #Config_button = customtkinter.CTkButton( Top_frame,text="Configure", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
        #Config_button.grid(row=0, column=1, padx=20,pady = (5,5),sticky="news")

        #Setup_button = customtkinter.CTkButton( Top_frame,text="Setup", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
        #Setup_button.grid(row=0, column=2, padx=20,pady = (5,5),sticky="news")


    def Commands_frame1():
            
            Commands_frame1 = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Commands_frame1.grid(row=1, column=0, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
            Commands_frame1.grid_columnconfigure(0, weight=0)
            Commands_frame1.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Commands_frame1, text="Trajectory commands", anchor="e",font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))


    def Commands_frame2():
            
            Commands_frame2 = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Commands_frame2.grid(row=1, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
            Commands_frame2.grid_columnconfigure(0, weight=0)
            Commands_frame2.grid_rowconfigure(0, weight=0)

            Calibrate = customtkinter.CTkButton( Commands_frame2,text="Calibrate", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Calibrate_command)
            Calibrate.grid(row=0, column=0, padx=20,pady = (5,5),sticky="news")

            Idle = customtkinter.CTkButton( Commands_frame2,text="Idle", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Idle_command)
            Idle.grid(row=1, column=0, padx=20,pady = (5,5),sticky="news")

            Clear_error = customtkinter.CTkButton( Commands_frame2,text="Clear error", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Clear_error_command)
            Clear_error.grid(row=2, column=0, padx=20,pady = (5,5),sticky="news")

            Reset_button = customtkinter.CTkButton( Commands_frame2,text="Reset_mcu", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Reset_command)
            Reset_button.grid(row=3, column=0, padx=20,pady = (5,5),sticky="news")

            Pull_config = customtkinter.CTkButton( Commands_frame2,text="Pull config", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Pull_config_command)
            Pull_config.grid(row=0, column=1, padx=20,pady = (5,5),sticky="news")

            Save_config = customtkinter.CTkButton( Commands_frame2,text="Save config", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Save_config_command)
            Save_config.grid(row=1, column=1, padx=20,pady = (5,5),sticky="news")

            Estop_button = customtkinter.CTkButton( Commands_frame2,text="ESTOP", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Estop_command)
            Estop_button.grid(row=2, column=1, padx=20,pady = (5,5),sticky="news")

            app.Position_is = customtkinter.CTkLabel( Commands_frame2, text="Position: ", anchor="e")
            app.Position_is.grid(row=0, column=2, padx=(5, 0))

            app.Speed_is = customtkinter.CTkLabel( Commands_frame2, text="Speed: ", anchor="e")
            app.Speed_is.grid(row=1, column=2, padx=(5, 0))

            app.Current_is = customtkinter.CTkLabel( Commands_frame2, text="Current: ", anchor="e")
            app.Current_is.grid(row=2, column=2, padx=(5, 0))

            app.Position_var = customtkinter.CTkLabel( Commands_frame2, text="", anchor="e")
            app.Position_var.grid(row=0, column=3, padx=(5, 0))

            app.Speed_var = customtkinter.CTkLabel( Commands_frame2, text="", anchor="e")
            app.Speed_var.grid(row=1, column=3, padx=(5, 0))

            app.Current_var = customtkinter.CTkLabel( Commands_frame2, text="", anchor="e")
            app.Current_var.grid(row=2, column=3, padx=(5, 0))

            app.Vbus_is = customtkinter.CTkLabel( Commands_frame2, text="Vbus: ", anchor="e")
            app.Vbus_is.grid(row=3, column=2, padx=(5, 0))

            app.Vbus_var = customtkinter.CTkLabel( Commands_frame2, text="", anchor="e")
            app.Vbus_var.grid(row=3, column=3, padx=(5, 0))


    def Commands_frame3():

            Commands_frame3 = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Commands_frame3.grid(row=1, column=2, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
            Commands_frame3.grid_columnconfigure(0, weight=0)
            Commands_frame3.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Commands_frame3, text="GUI options ", anchor="e",font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))

            plot_pause = customtkinter.CTkButton( Commands_frame3,text="Pause", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Pause_plots)
            plot_pause.grid(row=0, column=1, padx=20,pady = (5,5),sticky="news")

            plot_start = customtkinter.CTkButton( Commands_frame3,text="Start", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Start_plots)
            plot_start.grid(row=0, column=2, padx=20,pady = (5,5),sticky="news")

            #autoscale = customtkinter.CTkRadioButton(master=Commands_frame3, text="Autoscale",  value=2)
            #autoscale.grid(row=1, column=0, pady=10, padx=20, sticky="we")

            lower_limit = customtkinter.CTkLabel( Commands_frame3, text="Lower limit" , anchor="e")
            lower_limit.grid(row=1, column=1, padx=(5, 5))

            upper_limit = customtkinter.CTkLabel( Commands_frame3, text="Upper limit ", anchor="e")
            upper_limit.grid(row=1, column=2, padx=(5, 0))
        
            Position_scale = customtkinter.CTkLabel( Commands_frame3, text="Position ", anchor="e")
            Position_scale.grid(row=2, column=0, padx=(5, 0))

            app.pos_lower = customtkinter.CTkEntry( Commands_frame3, width= 150)
            app.pos_lower.grid(row=2, column=1, padx=(5, 0),pady=(3,3),sticky="news")
        
            app.pos_upper = customtkinter.CTkEntry( Commands_frame3, width= 150)
            app.pos_upper.grid(row=2, column=2, padx=(5, 0),pady=(3,3),sticky="news")

            pos_set = customtkinter.CTkButton( Commands_frame3,text="Set", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command= rescale_pos)
            pos_set.grid(row=2, column=3, padx=20,pady = (5,5),sticky="news")

            Speed_scale = customtkinter.CTkLabel( Commands_frame3, text="Speed ", anchor="e")
            Speed_scale.grid(row=3, column=0, padx=(5, 0))

            app.speed_lower = customtkinter.CTkEntry( Commands_frame3, width= 150)
            app.speed_lower.grid(row=3, column=1, padx=(5, 0),pady=(3,3),sticky="news")
        
            app.speed_upper = customtkinter.CTkEntry( Commands_frame3, width= 150)
            app.speed_upper.grid(row=3, column=2, padx=(5, 0),pady=(3,3),sticky="news")

            speed_set = customtkinter.CTkButton( Commands_frame3,text="Set", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=rescale_speed)
            speed_set.grid(row=3, column=3, padx=20,pady = (5,5),sticky="news")

            Current_scale = customtkinter.CTkLabel( Commands_frame3, text="Current ", anchor="e")
            Current_scale.grid(row=4, column=0, padx=(5, 0))

            app.current_lower = customtkinter.CTkEntry( Commands_frame3, width= 150)
            app.current_lower.grid(row=4, column=1, padx=(5, 0),pady=(3,3),sticky="news")
        
            app.current_upper = customtkinter.CTkEntry( Commands_frame3, width= 150)
            app.current_upper.grid(row=4, column=2, padx=(5, 0),pady=(3,3),sticky="news")

            curret_set = customtkinter.CTkButton( Commands_frame3,text="Set", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=rescale_current)
            curret_set.grid(row=4, column=3, padx=20,pady = (5,5),sticky="news")

        
  
            
    Plots_frame = customtkinter.CTkFrame(app ,height = 100,width=150, corner_radius=0, )
    Plots_frame.grid(row=2, column=0, columnspan=4, padx=(5,5), pady=(5,5),sticky="news")
    Plots_frame.grid_columnconfigure(0, weight=1)
    Plots_frame.grid_rowconfigure(0, weight=1)
        

    canvas = FigureCanvasTkAgg(fig, master=Plots_frame)
    canvas.draw()
    #canvas.get_tk_widget().grid(row=0, column=0, padx=(5, 0))
    canvas.get_tk_widget().pack()


    def change_scaling_event(app, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def change_appearance_mode_event(app, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)


    def Modes_frame():
        Modes_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
        Modes_frame.grid(row=3, column=0, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
        Modes_frame.grid_columnconfigure(0, weight=0)
        Modes_frame.grid_rowconfigure(0, weight=0)



        Position_setpoint = customtkinter.CTkButton( Modes_frame,text="Position control mode", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_Position_frame)
        Position_setpoint.grid(row=0, column=0, padx=20,pady = (5,5),sticky="news")

        Speed_setpoint = customtkinter.CTkButton( Modes_frame,text="Speed control mode", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_Speed_frame)
        Speed_setpoint.grid(row=1, column=0, padx=20,pady = (5,5),sticky="news")

        Current_setpoint = customtkinter.CTkButton( Modes_frame,text="Current control mode", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_Current_frame)
        Current_setpoint.grid(row=2, column=0, padx=20,pady = (5,5),sticky="news")

        PD_setpoint = customtkinter.CTkButton( Modes_frame,text="PD control mode", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_PD_frame)
        PD_setpoint.grid(row=3, column=0, padx=20,pady = (5,5),sticky="news")

        Settings_setpoint = customtkinter.CTkButton( Modes_frame,text="Settings", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_settings_frame)
        Settings_setpoint.grid(row=4, column=0, padx=20,pady = (5,5),sticky="news")

        Errors_setpoint = customtkinter.CTkButton( Modes_frame,text="Active errors", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_errors_frame)
        Errors_setpoint.grid(row=5, column=0, padx=20,pady = (5,5),sticky="news")

        Motor_info_setpoint = customtkinter.CTkButton( Modes_frame,text="Motor info", width= 50, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=raise_motor_info_frame)
        Motor_info_setpoint.grid(row=5, column=0, padx=20,pady = (5,5),sticky="news")


    Pos_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    Pos_frame.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    Pos_frame.grid_columnconfigure(0, weight=0)
    Pos_frame.grid_rowconfigure(0, weight=0)

    def Position_mode():

        Position_mode = customtkinter.CTkLabel( Pos_frame, text="Position control mode", anchor="e")
        Position_mode.grid(row=0, column=0, padx=(5, 0))

        Position_setpoint = customtkinter.CTkButton( Pos_frame,text="Position setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command = Send_position_setpoint)
        Position_setpoint.grid(row=1, column=0, padx=20,pady = (5,5),sticky="news")

        app.Position_entry = customtkinter.CTkEntry( Pos_frame, width= 150)
        app.Position_entry.grid(row=1, column=1, padx=(5, 0),pady=(3,3),sticky="news")

        Kp_setpoint_pos = customtkinter.CTkButton( Pos_frame,text="Kp setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_Kp_position)
        Kp_setpoint_pos.grid(row=2, column=0, padx=20,pady = (5,5),sticky="news")

        app.Kp_setpoint_entry_pos = customtkinter.CTkEntry( Pos_frame, width= 150)
        app.Kp_setpoint_entry_pos.grid(row=2, column=1, padx=(5, 0),pady=(3,3),sticky="news")


    Speed_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    Speed_frame.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    Speed_frame.grid_columnconfigure(0, weight=0)
    Speed_frame.grid_rowconfigure(0, weight=0)

    def Speed_mode():
        
        speed_loop = customtkinter.CTkLabel( Speed_frame, text="Speed control mode ", anchor="e")
        speed_loop.grid(row=0, column=0, padx=(35, 35))

        speed_setpoint = customtkinter.CTkButton( Speed_frame,text="Speed setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_speed_setpoint)
        speed_setpoint.grid(row=1, column=0, padx=20,pady = (5,5),sticky="news")

        app.speed_entry = customtkinter.CTkEntry( Speed_frame, width= 150)
        app.speed_entry.grid(row=1, column=1, padx=(5, 0),pady=(3,3),sticky="news")

        Kp_setpoint_speed = customtkinter.CTkButton( Speed_frame,text="Kp setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_Kp_speed)
        Kp_setpoint_speed.grid(row=2, column=0, padx=20,pady = (5,5),sticky="news")

        app.Kp_setpoint_entry_speed = customtkinter.CTkEntry( Speed_frame, width= 150)
        app.Kp_setpoint_entry_speed.grid(row=2, column=1, padx=(5, 0),pady=(3,3),sticky="news")
    
        Ki_setpoint_speed = customtkinter.CTkButton( Speed_frame,text="Ki setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_Ki_speed)
        Ki_setpoint_speed.grid(row=3, column=0, padx=20,pady = (5,5),sticky="news")

        app.Ki_setpoint_entry = customtkinter.CTkEntry( Speed_frame, width= 150)
        app.Ki_setpoint_entry.grid(row=3, column=1, padx=(5, 0),pady=(3,3),sticky="news")

        Speed_limit = customtkinter.CTkButton( Speed_frame,text="Speed limits setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_vel_limit)
        Speed_limit.grid(row=4, column=0, padx=20,pady = (5,5),sticky="news")

        app.Speed_limit_entry = customtkinter.CTkEntry( Speed_frame, width= 150)
        app.Speed_limit_entry.grid(row=4, column=1, padx=(5, 0),pady=(3,3),sticky="news")

    Current_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    Current_frame.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    Current_frame.grid_columnconfigure(0, weight=0)
    Current_frame.grid_rowconfigure(0, weight=0)

    def Current_mode():

        Current_loop = customtkinter.CTkLabel( Current_frame, text="Current control mode ", anchor="e")
        Current_loop.grid(row=0, column=0, padx=(35, 35))

        Current_setpoint = customtkinter.CTkButton( Current_frame,text="Current setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_current_setpoint)
        Current_setpoint.grid(row=1, column=0, padx=20,pady = (5,5),sticky="news")

        app.Current_entry = customtkinter.CTkEntry( Current_frame, width= 150)
        app.Current_entry.grid(row=1, column=1, padx=(5, 0),pady=(3,3),sticky="news")

        Kp_setpoint_current = customtkinter.CTkButton( Current_frame,text="Kp setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_Kp_current)
        Kp_setpoint_current.grid(row=2, column=0, padx=20,pady = (5,5),sticky="news")

        app.Kp_setpoint_entry_current = customtkinter.CTkEntry( Current_frame, width= 150)
        app.Kp_setpoint_entry_current.grid(row=2, column=1, padx=(5, 0),pady=(3,3),sticky="news")
    
        Ki_setpoint_current = customtkinter.CTkButton( Current_frame,text="Ki setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_Ki_current)
        Ki_setpoint_current.grid(row=3, column=0, padx=20,pady = (5,5),sticky="news")

        app.Ki_setpoint_entry_current = customtkinter.CTkEntry( Current_frame, width= 150)
        app.Ki_setpoint_entry_current.grid(row=3, column=1, padx=(5, 0),pady=(3,3),sticky="news")

        Current_limit = customtkinter.CTkButton( Current_frame,text="Current limits setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_current_limit)
        Current_limit.grid(row=4, column=0, padx=20,pady = (5,5),sticky="news")

        app.Current_limit_entry = customtkinter.CTkEntry( Current_frame, width= 150)
        app.Current_limit_entry.grid(row=4, column=1, padx=(5, 0),pady=(3,3),sticky="news")


    PD_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    PD_frame.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    PD_frame.grid_columnconfigure(0, weight=0)
    PD_frame.grid_rowconfigure(0, weight=0)

    def PD_mode():

        PD_loop = customtkinter.CTkLabel( PD_frame, text="PD impedance control mode ", anchor="e")
        PD_loop.grid(row=0, column=0, padx=(35, 35))

        Position_setpoint_PD = customtkinter.CTkButton( PD_frame,text="Position setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_PD_pos)
        Position_setpoint_PD.grid(row=1, column=0, padx=20,pady = (5,5),sticky="news")

        app.Position_entry_PD = customtkinter.CTkEntry( PD_frame, width= 150)
        app.Position_entry_PD.grid(row=1, column=1, padx=(5, 0),pady=(3,3),sticky="news")

        KP_setpoint_PD = customtkinter.CTkButton( PD_frame,text="KP setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_KP)
        KP_setpoint_PD.grid(row=2, column=0, padx=20,pady = (5,5),sticky="news")

        app.KP_setpoint_entry_PD = customtkinter.CTkEntry( PD_frame, width= 150)
        app.KP_setpoint_entry_PD.grid(row=2, column=1, padx=(5, 0),pady=(3,3),sticky="news")
    
        KD_setpoint = customtkinter.CTkButton( PD_frame,text="KD setpoint", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_KD)
        KD_setpoint.grid(row=3, column=0, padx=20,pady = (5,5),sticky="news")

        app.KD_setpoint_entry = customtkinter.CTkEntry( PD_frame, width= 150)
        app.KD_setpoint_entry.grid(row=3, column=1, padx=(5, 0),pady=(3,3),sticky="news")


    Active_errors_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    Active_errors_frame.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    Active_errors_frame.grid_columnconfigure(0, weight=0)
    Active_errors_frame.grid_rowconfigure(0, weight=0)

    def Active_errors():
        Errors_button = customtkinter.CTkButton( Active_errors_frame,text="TEST BUTTON", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
        Errors_button.grid(row=4, column=0, padx=20,pady = (5,5),sticky="news")
         

    Settings_frame = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    Settings_frame.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    Settings_frame.grid_columnconfigure(0, weight=0)
    Settings_frame.grid_rowconfigure(0, weight=0)

    def settings_mode():
        settings_button = customtkinter.CTkButton( Settings_frame,text="TEST BUTTON", width= 50,fg_color="gray54", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
        settings_button.grid(row=4, column=0, padx=20,pady = (5,5),sticky="news")
         
         # Hearbeat
         # Watchdog
         # 

    Motor_info = customtkinter.CTkFrame(app ,height = 100,width=200, corner_radius=0, )
    Motor_info.grid(row=3, column=1, columnspan=1, padx=(5,5), pady=(5,5),sticky="news")
    Motor_info.grid_columnconfigure(0, weight=0)
    Motor_info.grid_rowconfigure(0, weight=0)

    def Motor_info_frame():

        app.Motor_resistance = customtkinter.CTkLabel( Motor_info, text="Phase resistance: ", anchor="e")
        app.Motor_resistance.grid(row=0, column=0, padx=(5, 0))

        app.Motor_inductance = customtkinter.CTkLabel( Motor_info, text="Phase inductance: ", anchor="e")
        app.Motor_inductance.grid(row=1, column=0, padx=(5, 0))

        app.Pole_pairs = customtkinter.CTkLabel( Motor_info, text="Pole pairs: ", anchor="e")
        app.Pole_pairs.grid(row=2, column=0, padx=(5, 0))

        app.Serial_number = customtkinter.CTkLabel( Motor_info, text="Serial number: ", anchor="e")
        app.Serial_number.grid(row=3, column=0, padx=(5, 0))

        app.Hardware_version = customtkinter.CTkLabel( Motor_info, text="Hardware version: ", anchor="e")
        app.Hardware_version.grid(row=4, column=0, padx=(5, 0))

        app.Batch_date = customtkinter.CTkLabel( Motor_info, text="Batch date: ", anchor="e")
        app.Batch_date.grid(row=5, column=0, padx=(5, 0))

        app.Software_version = customtkinter.CTkLabel( Motor_info, text="Software version: ", anchor="e")
        app.Software_version.grid(row=6, column=0, padx=(5, 0))



        app.Calibrated_label = customtkinter.CTkLabel( Motor_info, text="Calibrated: ", anchor="e")
        app.Calibrated_label.grid(row=0, column=1, padx=(40, 0))

        app.Error_label = customtkinter.CTkLabel( Motor_info, text="Error: ", anchor="e")
        app.Error_label.grid(row=1, column=1, padx=(40, 0))

        app.temperature_error = customtkinter.CTkLabel( Motor_info, text="Temperature error: ", anchor="e")
        app.temperature_error.grid(row=2, column=1, padx=(40, 0))

        app.Encoder_error = customtkinter.CTkLabel( Motor_info, text="Encoder error: ", anchor="e")
        app.Encoder_error.grid(row=3, column=1, padx=(40, 0))

        app.Vbus_error = customtkinter.CTkLabel( Motor_info, text="Vbus error: ", anchor="e")
        app.Vbus_error.grid(row=4, column=1, padx=(40, 0))

        app.Driver_error = customtkinter.CTkLabel( Motor_info, text="Driver error: ", anchor="e")
        app.Driver_error.grid(row=5, column=1, padx=(40, 0))

        app.Velocity_error = customtkinter.CTkLabel( Motor_info, text="Velocity error: ", anchor="e")
        app.Velocity_error.grid(row=6, column=1, padx=(40, 0))

        app.Current_error = customtkinter.CTkLabel( Motor_info, text="Current error: ", anchor="e")
        app.Current_error.grid(row=7, column=1, padx=(40, 0))

        app.Estop_error = customtkinter.CTkLabel( Motor_info, text="Estop error: ", anchor="e")
        app.Estop_error.grid(row=8, column=1, padx=(40, 0))

        app.Watchdog_error = customtkinter.CTkLabel( Motor_info, text="Watchdog error: ", anchor="e")
        app.Watchdog_error.grid(row=8, column=1, padx=(40, 0))
         
         # Hearbeat
         # Watchdog
         # 

    def Logs_frame():

        Logs_frame3 = customtkinter.CTkFrame(app ,height = 100,width=600, corner_radius=0, )
        Logs_frame3.grid(row=3, column=2, columnspan=1, padx=(5,5), pady=(5,5),sticky="new")
        Logs_frame3.grid_columnconfigure(0, weight=1)
        Logs_frame3.grid_rowconfigure(0, weight=1)

        commands_label = customtkinter.CTkLabel( Logs_frame3, text="Send command ", anchor="e")
        commands_label.grid(row=0, column=0, padx=(5, 0))
    
        app.command_entry = customtkinter.CTkEntry( Logs_frame3, width= 200)
        app.command_entry.grid(row=1, column=0, padx=(5, 0),pady=(3,3))

        Send_commands = customtkinter.CTkButton(Logs_frame3,text="Send", width= 100, font = customtkinter.CTkFont(size=15, family='TkDefaultFont'),command=Send_command)
        Send_commands.grid(row=1, column=1, padx=20,pady = (5,5),sticky="e")

        Logs_label = customtkinter.CTkLabel( Logs_frame3, text="Responses ", anchor="e")
        Logs_label.grid(row=2, column=0, padx=(5, 0))

        app.textbox_response = customtkinter.CTkTextbox(Logs_frame3,font = customtkinter.CTkFont(size=14, family='TkDefaultFont'))
        app.textbox_response.grid(row=3, column=0,columnspan=2,  padx=(20, 20), pady=(5, 20), sticky="nsew")
        #app.textbox_response.bind("<KeyRelease>", highlight_words_response)




    def Bottom_frame():
            Bottom_frame = customtkinter.CTkFrame(app ,height = 0,width=150, corner_radius=0, )
            Bottom_frame.grid(row=4, column=0, columnspan=4, padx=(5,5), pady=(5,5),sticky="new")
            Bottom_frame.grid_columnconfigure(0, weight=0)
            Bottom_frame.grid_rowconfigure(0, weight=0)

            appearance_mode_label = customtkinter.CTkLabel( Bottom_frame, text="Appearance Mode:", anchor="w")
            appearance_mode_label.grid(row=0, column=0, padx=(5, 0))
            appearance_mode_optionemenu = customtkinter.CTkOptionMenu( Bottom_frame, values= ["Light","Dark"],
                                                                    command= change_appearance_mode_event)
            appearance_mode_optionemenu.grid(row=0, column=0, padx=(5, 0))

            app.FPS_label = customtkinter.CTkLabel( Bottom_frame, text="FPS ", anchor="e")
            app.FPS_label.grid(row=0, column=1, padx=(50, 50))


    def settings_frame():
            demo1 = customtkinter.CTkButton( settings_frame,text="demo1", font = customtkinter.CTkFont(size=15, family='TkDefaultFont'))
            demo1.grid(row=0, column=0, padx=20,pady = (10,20),sticky="news")

            scaling_label = customtkinter.CTkLabel( settings_frame, text="UI Scaling:", anchor="w")
            scaling_label.grid(row=0, column=1, padx=(5, 0))

            scaling_optionemenu = customtkinter.CTkOptionMenu( settings_frame, values=["80%", "90%", "100%", "110%", "120%","150%"],
                                                            command= change_scaling_event)
            scaling_optionemenu.grid(row=0, column=2,padx=(5, 0) )

            appearance_mode_label = customtkinter.CTkLabel( settings_frame, text="Appearance Mode:", anchor="w")
            appearance_mode_label.grid(row=0, column=3, padx=(5, 0))
            appearance_mode_optionemenu = customtkinter.CTkOptionMenu( settings_frame, values= ["Light","Dark"],
                                                                    command= change_appearance_mode_event)
            appearance_mode_optionemenu.grid(row=0, column=4, padx=(5, 0))


        # This function periodically updates elements of the GUI that need to be updated
    def Stuff_To_Update():
        global port_open, global_current, global_position, global_speed,values_show_tick
        if port_open == 1:
            while (s.inWaiting() > 0):
                input_string = s.readline()
                decoded_string = input_string.decode('utf-8')  # Decode bytes to string
                cleaned_string = decoded_string.rstrip('\r\n')  # Remove '\r\n' from the end

                if(cleaned_string[0] == '$'):
                    values = cleaned_string.strip().split()
                    global_position = int(values[1])
                    global_speed = int(values[2])
                    global_current = float(values[3])
                    values_show_tick = values_show_tick + 1
                    if(values_show_tick == 10):
                        app.Position_var.configure(text = (values[1]))
                        app.Speed_var.configure(text = (values[2]))
                        app.Current_var.configure( text =(values[3]))
                        global_position = int(values[1])
                        global_speed = int(values[2])
                        global_current = float(values[3])
                        values_show_tick = 0

                elif(cleaned_string[0] == '%'):
                    values = cleaned_string.strip().split()
                    app.Kp_setpoint_entry_pos.insert(0,values[1])

                    app.Kp_setpoint_entry_speed.insert(0,values[2])
                    app.Ki_setpoint_entry.insert(0,values[3])
                    app.Speed_limit_entry.insert(0,values[4])

                    app.Kp_setpoint_entry_current.insert(0,values[5])
                    app.Ki_setpoint_entry_current.insert(0,values[6])
                    app.Current_limit_entry.insert(0,values[7])

                    app.KP_setpoint_entry_PD.insert(0,values[8])
                    app.KD_setpoint_entry.insert(0,values[9]) 

                    app.Motor_resistance.configure(text="Phase resistance: "+ values[10])
                    app.Motor_inductance.configure(text="Phase inductance: "+ values[11])
                    app.Pole_pairs.configure(text="Pole pairs: "+ values[12])
                    app.Serial_number.configure(text="Serial number: "+ values[13])
                    app.Hardware_version.configure(text="Hardware version: "+ values[14])
                    app.Batch_date.configure(text="Batch date: "+ values[15])
                    app.Software_version.configure(text="Software version: "+ values[16])


                    app.Calibrated_label.configure(text="Calibrated: "+ values[17])
                    app.Error_label.configure(text="Error: "+ values[18])
                    app.temperature_error.configure(text="Temperature error: "+ values[19])
                    app.Encoder_error.configure(text="Encoder error: "+ values[20])
                    app.Vbus_error.configure(text="Vbus error: "+ values[21])
                    app.Driver_error.configure(text="Driver error: "+ values[22])
                    app.Velocity_error.configure(text="Velocity error: "+ values[23])
                    app.Current_error.configure(text="Current error: "+ values[24])
                    app.Estop_error.configure(text="Estop error: "+ values[25])
                    app.Watchdog_error.configure(text="Watchdog error: "+ values[26])

                    app.Vbus_var.configure(text = values[27])

                else:
                    app.textbox_response.insert(tk.INSERT,cleaned_string + "\n")
                    app.textbox_response.see(tk.END)
                
                    values_show_tick = values_show_tick + 1
                    if(values_show_tick == 7):
                        values = cleaned_string.strip().split()
                        app.Position_var.configure(text = (values[1]))
                        app.Speed_var.configure(text = (values[2]))
                        app.Current_var.configure( text =(values[3]))
                        values_show_tick = 0



        app.after(10,Stuff_To_Update) 


    def change_scaling_event( new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def change_appearance_mode_event( new_appearance_mode: str):

        if(new_appearance_mode == "Dark"):
            fig.patch.set_facecolor("#2b2b2b")
            canvas.draw()
        if(new_appearance_mode == "Light"):
            fig.patch.set_facecolor("White")
            canvas.draw()
        customtkinter.set_appearance_mode(new_appearance_mode)

    def Pause_plots():
        ani.event_source.stop()
        ani2.event_source.stop()
        ani3.event_source.stop()

    def Start_plots():
        ani.event_source.start()
        ani2.event_source.start()
        ani3.event_source.start()

    def raise_Position_frame():
        Pos_frame.tkraise()

    def raise_Speed_frame():
        Speed_frame.tkraise()

    def raise_Current_frame():
        Current_frame.tkraise()

    def raise_PD_frame():
        PD_frame.tkraise()

    def raise_settings_frame():
        Settings_frame.tkraise()
    
    def raise_errors_frame():
        Active_errors_frame.tkraise()

    def raise_motor_info_frame():
        Motor_info.tkraise()

    def Idle_command():
         msg = "#Idle\n"
         s.write(msg.encode())

    def Calibrate_command():
         msg = "#Cal\n"
         s.write(msg.encode())

    def Clear_error_command():
         msg = "#Clear\n"
         s.write(msg.encode())

    def Estop_command():
         msg = "#Idle\n"
         s.write(msg.encode())

    def Pull_config_command():
                    
        app.Kp_setpoint_entry_pos.delete(0,tk.END)
        app.Kp_setpoint_entry_speed.delete(0,tk.END)
        app.Ki_setpoint_entry.delete(0,tk.END)
        app.Speed_limit_entry.delete(0,tk.END)

        app.Kp_setpoint_entry_current.delete(0,tk.END)
        app.Ki_setpoint_entry_current.delete(0,tk.END)
        app.Current_limit_entry.delete(0,tk.END)

        app.KP_setpoint_entry_PD.delete(0,tk.END)
        app.KD_setpoint_entry.delete(0,tk.END)

        msg = "#Pullconfig\n"
        s.write(msg.encode())
        

    def Save_config_command():
        msg = "#Save\n"
        s.write(msg.encode())

    def Reset_command():
        msg = "#Reset\n"
        s.write(msg.encode())

    def Connect_serial():
        global port_open
        uart_baud = app.uart_baud_entry.get()
        uart_com = app.uart_com_entry.get()
        s.baudrate = int(uart_baud)
        s.port = str(uart_com)
        s.open()
        if(s.is_open == True):
            app.uart_status.configure(text = "Connected",text_color="green")
            port_open = 1
            msg = "#Cyc 30\n"
            s.write(msg.encode())
            msg = "#Pullconfig\n"
            s.write(msg.encode())


    def Connect_CAN():
         None

    def rescale_pos():
        min_var = app.pos_lower.get()
        max_var = app.pos_upper.get()
        y_range = [int(min_var), int(max_var)] # What range to show on Y axis
        ax1.set_ylim(y_range)
        fig.canvas.resize_event()
    
    def rescale_speed():
        min_var = app.speed_lower.get()
        max_var = app.speed_upper.get()
        y_range = [int(min_var), int(max_var)] # What range to show on Y axis
        ax2.set_ylim(y_range)
        fig.canvas.resize_event()

    def rescale_current():
        min_var = app.current_lower.get()
        max_var = app.current_upper.get()
        y_range = [int(min_var), int(max_var)] # What range to show on Y axis
        ax3.set_ylim(y_range)
        fig.canvas.resize_event()

    def Send_position_setpoint():
        msg = "#P " +str(app.Position_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_Kp_position():
        msg = "#Kpp " +str(app.Kp_setpoint_entry_pos.get()) + "\n"
        s.write(msg.encode())

    def Send_speed_setpoint():
        msg = "#V " +str(app.speed_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_Kp_speed():
        msg = "#Kpv " +str(app.Kp_setpoint_entry_speed.get()) + "\n"
        s.write(msg.encode())

    def Send_Ki_speed():
        msg = "#Kiv " +str(app.Ki_setpoint_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_vel_limit():
        msg = "#Vlimit " +str(app.Speed_limit_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_current_setpoint():
        msg = "#Iq  " +str(app.Current_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_Kp_current():
        msg = "#Kpiq " +str(app.Kp_setpoint_entry_current.get()) + "\n"
        s.write(msg.encode())

    def Send_Ki_current():
        msg = "#Kiiq " +str(app.Ki_setpoint_entry_current.get()) + "\n"
        s.write(msg.encode())

    def Send_current_limit():
        msg = "#Ilim " +str(app.Current_limit_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_PD_pos():
        msg = "#PD " +str(app.Position_entry_PD.get()) + "\n"
        s.write(msg.encode())

    def Send_KP():
        msg = "#KP " +str(app.KP_setpoint_entry_PD.get()) + "\n"
        s.write(msg.encode())
    
    def Send_KD():
        msg = "#KD " +str(app.KD_setpoint_entry.get()) + "\n"
        s.write(msg.encode())

    def Send_command():
        msg = str(app.command_entry.get()) + "\n"
        s.write(msg.encode())
        app.command_entry.delete(0,tk.END)

    #Plots_frame()
    Top_frame()
    Bottom_frame()
    Logs_frame()
    Commands_frame1()
    Commands_frame2()
    Commands_frame3()
    Modes_frame()
    Position_mode()
    Current_mode()
    PD_mode()
    Speed_mode()
    Motor_info_frame()
    Active_errors()
    settings_mode()
    Pos_frame.tkraise()

    Stuff_To_Update()

    def calculate_fps():
        global start_time, frame_count
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= 1:
            fps = frame_count / elapsed_time
            #print(f"FPS: {fps:.2f}")
            start_time = current_time
            frame_count = 0
            app.FPS_label.configure(text = str(int(fps)) + " FPS")
        app.after(1000, calculate_fps)

    ani = animation.FuncAnimation(fig, animate_sine_wave, frames=20, fargs=(line1, x), interval=var, blit=True)
    ani2 = animation.FuncAnimation(fig, animate_square_wave, frames=20, fargs=(line2, x), interval=var, blit=True)
    ani3 = animation.FuncAnimation(fig, animate_sawtooth_wave, frames=20, fargs=(line3, x), interval=var, blit=True)

    app.after(1000, calculate_fps)
    app.mainloop() 



if __name__ == "__main__":
    var = 28
    #threading.Thread(target=Serial_handler, daemon=True).start()
    GUI(var)
    #app = customtkinter.CTk()
    #app.mainloop() 