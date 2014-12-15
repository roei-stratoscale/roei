#run file:
#PYTHONPATH="/usr/share/strato-api" python my.py

from strato.openstackapi import openstackapi
from strato.openstackapi import apiconfig

openStackAPI = openstackapi.OpenStackAPI(
connection = openStackAPI.connection
connection.connect( serverIp = "127.0.0.1", username = apiconfig.OPENSTACK_USERNAME, password = apiconfig.OPENSTACK_PASSWORD )

print openStackAPI.servers.listServers()
portsInfo = openStackAPI.servers._portsInfo()
import pdb; pdb.set_trace()

