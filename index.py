from ncclient import manager
import xmltodict
import xml.dom.minidom
import datetime
import time
import sys

#python index.py <IP> <Port> <username> <password> <On_hour> <On_min> <Off_hour> <Off_min> <SSID> <Interval>

host_ip = sys.argv[1]
host_port = sys.argv[2]
host_username = sys.argv[3]
host_password = sys.argv[4]

on_hour = sys.argv[5]   #Time (hour) to switch on SSID
on_min = sys.argv[6]    #Time (min) to switch on SSID
off_hour = sys.argv[7]    #Time (hour) to switch off SSID
off_min = sys.argv[8]   #Time (min) to switch off SSID

ssid = sys.argv[9]
interval = int(sys.argv[10])

status = "true"  #Configured dynamically based on time 
action = False   #Configured dynamically based on time - Trigger for Netconf script to run

while True:
  
  action = False #Reset control trigger

  current_time = datetime.datetime.now() 

  print("Current Time = " + str(current_time.hour) + ":" + str(current_time.minute))
  print("Enable Time  = " + str(on_hour) + ":" + str(on_min))
  print("Disable Time = " + str(off_hour) + ":" + str(off_min))
  print("")

  if int(current_time.hour) == int(on_hour):
    if int(current_time.minute) == int(on_min):

      #Time to enable SSID
      status = "true"
      action = True

  if int(current_time.hour) == int(off_hour):
    if int(current_time.minute) == int(off_min):

      #Time to disable SSID
      status = "false"
      action = True
  

  if action == True:

    m = manager.connect(
       host=host_ip,
       port=host_port,
       username=host_username,
       password=host_password,
       hostkey_verify=False
       )

    
    netconf_template = """
    <config>
      <wlan-cfg-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-wireless-wlan-cfg">
        <wlan-cfg-entries>
          <wlan-cfg-entry>
            <profile-name>{wifi_ssid}</profile-name>
            <apf-vap-id-data>
              <wlan-status>{wifi_status}</wlan-status>
            </apf-vap-id-data>
          </wlan-cfg-entry>
        </wlan-cfg-entries>
      </wlan-cfg-data>
    </config>"""

    netconf_data = netconf_template.format(
        wifi_ssid = ssid,
        wifi_status = status
      )

    if (status == "true"):
      print ("Enabling SSID")
    elif (status == "false"):
      print ("Disabling SSID")

    print("")
    
    netconf_reply = m.edit_config(netconf_data, target = 'running')

    m.close_session()

  time.sleep(interval)   #Check the time every 10 seconds