### Summary (WIP)
This project is a script that connects to a device using Telnet, retrieves the device's current IMEI, generates an open lock hash and disables the open lock feature of the device. 
The script then updates the device's IMEI and reboots the device. The script uses various libraries such as telnetlib, re, sierrakeygen, luhn and sys. 

### How To
`python3 main.py "10.10.10.1" "your-imei-here"`

### Features:
- Connects to a device using Telnet
- Retrieves the device's current IMEI
- Generates an open lock hash and disables the open lock feature of the device
- Updates the device's IMEI and reboots the device
- Changes TTL custom values
- Restores to factory default if needed
- Band unlocking for T-mobile/ATT/Verizon etc.




TODO:
- Add root telnet via port `23`
- Add custom `ttl` values
- Add restore
- Add band unlocking

### Resources:
- https://docs.google.com/document/d/1IZ20oAdotWxXttYGAuFBCr8C6CdOx9G8rbC-FgJRVV8/edit
- https://parkercs.tech/netgear-mr1100-hotspot/