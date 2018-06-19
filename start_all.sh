
clear
python handleDeviceDiscovery.py 239.255.255.250 1900 Socket-1_0-38323636-4558-4dda-9188-cda0e6196b1f- "LIGHT 1|LIGHT 2|LIGHT 3|LIGHT 4" "8001|8002|8003|8004" &

python2.7 Switch.py "LIGHT 1" 8001 Socket-1_0-38323636-4558-4dda-9188-cda0e6196b1f-8001 14 &

python2.7 Switch.py "LIGHT 2" 8002 Socket-1_0-38323636-4558-4dda-9188-cda0e6196b1f-8002 15 &

python2.7 Switch.py "LIGHT 3" 8003 Socket-1_0-38323636-4558-4dda-9188-cda0e6196b1f-8003 18 & 

python2.7 Switch.py "LIGHT 4" 8004 Socket-1_0-38323636-4558-4dda-9188-cda0e6196b1f-8004 23 &
