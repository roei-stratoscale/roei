from strato.common.log import configurelogging
configurelogging.configureLogging( 'hello' )


from strato.openstackapi import openstackapi
from strato.openstackapi import apiconfig
from strato.tests.common.infra.suite import *

api = openstackapi.OpenStackAPI()
connection = api.connection
connection.connect(
    serverIp = "192.168.122.254",
    username = apiconfig.OPENSTACK_USERNAME,
    password = apiconfig.OPENSTACK_PASSWORD )

servers = api.servers.listServers()

#import pdb
#pdb.set_trace()

api.servers.getServer(s)
