import time
import machine


# Function for syncing the rtc via ntp
def sync_time():
    rtc = machine.RTC()

    while not rtc.synced():
        rtc.ntp_sync("se.pool.ntp.org")
        machine.idle()
        if not rtc.synced():
            print("Failed to sync time. Trying again...")
            time.sleep(1)


    #time.timezone(3600) # adjust for local time zone (Sweden Winter time)
    time.timezone(7200)  # adjust for local time zone (Sweden Summer time)
    print("Time synced to: " + present(time.localtime()))


# Convert time tuple from time.localtime() to string.
# Makes it more neat and easier to read.
def present(input):
    year = str(input[0])
    month = str(input[1])
    day = str(input[2])

    if input[3] < 10:
        hour = "0" + str(input[3])
    else:
        hour = str(input[3])

    if input[4] < 10:
        minute = "0" + str(input[4])
    else:
        minute = str(input[4])

    return str(year + "-" + month + "-" + day + " " + hour + ":" + minute)
