# Basic Alarm Clock

# Importing the libraries
import datetime
import time
import winsound

# Defining the alarm function
def alarm(Timing):
    altime = str(datetime.datetime.now().strptime(Timing,"%I:%M %p"))
    altime = altime[11:-3]
    print(altime)
    Horeal = altime[:2]
    Horeal = int(Horeal)
    Mireal = altime[3:5]
    Mireal = int(Mireal)
    print(f"Done, alarm is set for {Timing}")
    while True:
        if Horeal  == datetime.datetime.now().hour:
            if Mireal == datetime.datetime.now().minute:
                print("Alarm is running")
                winsound.PlaySound('abc',winsound.SND_LOOP)
            
            elif Mireal<datetime.datetime.now().minute:
                break
            
# Taking user input
print("Set a time to alarm(HH:MM AM/PM)")
Alarm_Time = input("Enter the time of alarm to be set: ")
alarm(Alarm_Time)
