from strato.tests.common.infra.suite import *
from strato.tests.integration.infra import scenario
from strato.openstackapi import types
from strato.tests.kvm import config
from strato.common import waitfortcpserver
from strato.openstackapi import apiconfig
from strato.northbound.api.storageapi import storagecluster
from strato.tests.common.seeds import physicalpropertiesretriever
from strato.tests.common.infra import imagery
from strato.buildeng import distrato
from strato.tests.common.infra.hostundertestserviceinfo import SERVICE_INFO
from strato.common import configfile
from strato.openstackapi.exceptions import ResourceNotFoundException
from strato.openstackapi.exceptions import BadRequestException
from strato.installation.common import netconfig
import logging
import json
import requests
import tempfile
import os
import sets
import pdb

class Test( scenario.Scenario ):
    GUEST_VIRTUAL_MACHINES = { 'controller': dict( customVanilla = 'openstackcontroller', memoryMegabytes = 4096, processors = 3 ),
                               'agent1': dict( customVanilla = 'openstackagent', memoryMegabytes = 3078, processors = 3 ),
                               'agent2': dict( customVanilla = 'openstackagent', memoryMegabytes = 3078, processors = 3 ) }
    ABORT_TEST_TIMEOUT = 10000
    TEST_VMS = { "vm1": types.OpenStackServerConfiguration( 1, 256, 50 ) }
    TEST_IMAGES = { "image1": dict( diskFormat = "qcow2", containerFormat = "bare" ),
                    "image2": dict( diskFormat = "raw", containerFormat = "bare" ) }
    TEST_VOLS = { 'vol1' : dict( sizeGB = 1, backend = 'rack-storage' ) }
    TEST_NETWORKS = { 'sharednet5' : dict( subnet_cidr = '33.0.0.0/24',
                        extra_args = { 'vlan-tag': 15, 'admin-state-up': True } ),
                      'vlantestnet' : dict( subnet_cidr = '44.0.0.0/24',
                          extra_args = { 'vlan-tag': 11, 'admin-state-up': True } ) }
    AGENTS_NAMES = [ name for name, prop in GUEST_VIRTUAL_MACHINES.iteritems()
                     if prop[ 'customVanilla' ] == 'openstackagent' ]
    HOSTNAMES = []
    HOST_TO_MACHINE_NAMES= {}

    def setUp( self ):
        controller = self.vm( 'controller' )
        controller.openStackController().waitForController()
        controller.openStackAgent().launchIridium( aggressiveScanner = False, enableEviction = True )
        controller.openStackController().setupNeutronDefaultSubnet()
        controller.admin().installRPMPackage( "build/bring/northbound/strato_api-1-0.x86_64.rpm" )
        controller.admin().installRPMPackage( "build/bring/northbound/strato_cli-1-0.x86_64.rpm" )
        for package in [ 'master-rpc',
                         'agent-rpc',
                         'iridium' ]:
            controller.admin().installRPMPackage( 'build/strato_%s-1-0.x86_64.rpm' % package )
        controller.admin().installRPMPackage( 'build/bring/abacus/strato_datacollection-server-1-0.x86_64.rpm' )
        controller.admin().serviceInstall( SERVICE_INFO.loadBalancer )
        controller.admin().serviceInstall( SERVICE_INFO.nrad )
        waitfortcpserver.waitForTCPServer( ( config.OPENSTACK_CONTROLLER_STATIC_IP, apiconfig.REST_PORT ), timeout = 60, interval = 1 )
        controller.openStackController().waitForController()
        self.HOSTNAMES.append( controller.openStackController().hostName() )
        controller.admin().installRPMPackage( "build/bring/noded/strato-noded-1-0.x86_64.rpm" )
        Test.HOST_TO_MACHINE_NAMES[ controller.openStackController().hostName() ] = 'controller'

        for idx, name in enumerate( Test.AGENTS_NAMES ):
            self.vm( name ).openStackAgent().addComputeNodeToCluster( self.vm( 'controller' ) )
            for package in [ 'agent-rpc',
                             'iridium' ]:
                self.vm( name ).admin().installRPMPackage( "build/strato_%s-1-0.x86_64.rpm" % package )
            self.vm( name ).admin().installRPMPackage( "build/bring/abacus/strato_datacollection-agent-1-0.x86_64.rpm" )
            self.vm( name ).admin().serviceInstall( SERVICE_INFO.nrad )
            self.vm( name ).openStackAgent().launchIridium( aggressiveScanner = False, enableEviction = True )
            Test.HOSTNAMES.append( self.vm( name ).openStackAgent().hostName() )
            Test.HOST_TO_MACHINE_NAMES[ self.vm( name ).openStackAgent().hostName() ] = name
            self.vm( name ).admin().installRPMPackage( "build/bring/noded/strato-noded-1-0.x86_64.rpm" )
        controller.openStackController().waitForController()
        controller.ceph().waitForCephCluster()

        controller.openStackAPI().connect()
        self._image = controller.openStackAPI().uploadCirros()

        self._cookies = None
        self._restApiUrl = "http://%s:%d/%s" % ( controller.publicIP(), apiconfig.REST_PORT, apiconfig.REST_VERSION )

    def run( self ):
	pdb.set_trace()

        """
	self._checkNodeStats()
        self._checkClusterStats()
        self._checkStorageClusterAPI()
        self._checkBackendsStats()
        self._verifyNodedServices()
        self._checkNotFound()
        self._createNetworkAndSubnet()
        self._checkPhysicalNetwork()
        self._getPhysicalProperties()
        self._uploadAndCheckTestFiles()
        self._uploadTestImages()
        self._checkUploadedTestImages()
        self._deleteAllTestImagesButCirros()
        self._createPersistentTestVMs()
        self._attachVm( self._net[ 'sharednet5' ][ 'id' ], self._vmNameToId[ 'vm1' ] )
        self.vm( 'controller' ).openStackREST().renameServer( self._vmNameToId[ 'vm1' ], 'vm2' )
        self.vm( 'controller' ).openStackREST().powerUpServer( self._vmNameToId[ 'vm1' ] )
        self.vm( 'controller' ).openStackREST().renameServer( self._vmNameToId[ 'vm1' ], 'vm1' )
        self.vm( 'controller' ).openStackREST().checkInvalidActionHttpStatus( self._vmNameToId[ 'vm1' ] )
        self._verifyNodes()
        self._checkIridium()
        self._checkNodeStats() # do it again now that we have VMs up
        self._checkClusterStats()
        self._checkPowerUpNotShutDownServer()
        self._checkDeleteNotShutDownServer()
        self._giggleVMs()
        self._verifyAttachedVms( self._net[ 'sharednet5' ][ 'id' ], self._vmNameToId[ 'vm1' ] )
        self._shutDownServer( self._vmNameToId[ 'vm1' ] )
        self._detachVm( self._net[ 'sharednet5' ][ 'id' ], self._vmNameToId[ 'vm1' ] )
        self._validateVolumeActions()
        self.vm( 'controller' ).openStackREST().deleteServer( self._vmNameToId[ 'vm1' ] )
        self.vm( 'controller' ).openStackREST().deleteNetwork( self._net[ 'sharednet5' ][ 'id' ] )
        self._shutDownAgent1()
        self._verifyDeleteNodeAgent2()
        self._checkShutDownNotRunningServer()
	"""

    def _sendRequestAndUpdateCookies( self, requestMethod, *args, **kws ):
        response = requestMethod( *args, cookies = self._cookies, **kws )
        self._cookies = response.cookies
        return response

    def _shutDownServer( self, serverId ):
        self.vm( 'controller' ).openStackREST().shutDownServer( serverId )

    def _checkStorageClusterAPI( self ):
        logging.progress( "Checking storage cluster API" )
        clusterStatus = self._sendRequestAndUpdateCookies( requests.get, "%s/storage/cluster" % self._restApiUrl )
        TS_ASSERT( clusterStatus.ok )
        TS_ASSERT_EQUALS( clusterStatus.json(), storagecluster.StatusEnum.UP )

        storageClusterNodes = self._sendRequestAndUpdateCookies( requests.get, "%s/storage/cluster/nodes" % self._restApiUrl )
        TS_ASSERT( storageClusterNodes.ok )
        for node in storageClusterNodes.json():
            nodeInfo = self._sendRequestAndUpdateCookies( requests.get, "%s/storage/cluster/nodes/%s" % ( self._restApiUrl, node[ 'name' ] ) )
            TS_ASSERT( nodeInfo.ok )
            TS_ASSERT_EQUALS( nodeInfo.json()[ 'status' ], storagecluster.StatusEnum.UP )

        storageClusterDisks = self._sendRequestAndUpdateCookies( requests.get, "%s/storage/cluster/disks" % self._restApiUrl )
        TS_ASSERT( storageClusterDisks.ok )
        for disk in storageClusterDisks.json():
            diskStatus = self._sendRequestAndUpdateCookies( requests.get, "%s/storage/cluster/disks/%s" % ( self._restApiUrl, disk[ 'id' ] ) )
            TS_ASSERT( diskStatus.ok )
            TS_ASSERT_EQUALS( diskStatus.json()[ 'status' ], storagecluster.StatusEnum.UP )

        for node in storageClusterNodes.json():
            getData = { 'node-name' : node[ 'name' ] }
            nodeDisksList = self._sendRequestAndUpdateCookies( requests.get, "%s/storage/cluster/disks" % ( self._restApiUrl ), data = getData )
            TS_ASSERT( nodeDisksList.ok )

    def _giggleVMs( self ):
        self._verifyVmInfos( self._vmNameToId, self._net[ 'sharednet1' ][ 'id' ] )

    def _shutDownAgent1( self ):
        logging.progress( 'Shutting agent1 down' )
        self.vm( 'agent1' ).run( 'shutdown' )
        TS_ASSERT_PREDICATE_TIMEOUT( self._verifyHostStatus, self.vm( 'agent1' ).openStackAgent().hostName(), TS_timeout = 240, TS_interval = 3 )

    def _validateVolumeActions( self ):
        self._createVolumes()
        vmId_1 = self.vm( 'controller' ).openStackREST().serverList()[ 0 ][ 'id' ]
        vol_1 = self.vm( 'controller' ).openStackREST().volumeList()[ 0 ]
        volId_1 = vol_1[ 'id' ]
        self.vm( 'controller' ).openStackREST().attachVolume( volId_1, vmId_1 )
        snap = self.vm( 'controller' ).openStackREST().createSnapshot( volId_1, 'snap', description = 'snap' )
        self.vm( 'controller' ).openStackREST().detachVolume( volId_1, vmId_1 )
        volFromSnap = self.vm( 'controller' ).openStackREST().createVolumeFrom( 'volfromsnap', 'snapshot', snap[ 'id' ], description = 'volfromsnap' )
        self.vm( 'controller' ).openStackREST().deleteSnapshot( snap[ 'id' ] )
        volFromVol = self.vm( 'controller' ).openStackREST().createVolumeFrom( 'volfromvol', 'volume', volFromSnap[ 'id' ], description = 'volfromvol' )
        self.vm( 'controller' ).openStackREST().deleteVolume( volFromSnap[ 'id' ] )
        self.vm( 'controller' ).openStackREST().deleteVolume( volFromVol[ 'id' ] )
        image = self.vm( 'controller' ).openStackREST().imageList()[ 0 ]
        volFromImage = self.vm( 'controller' ).openStackREST().createVolumeFrom( 'volfromimage', 'image', image[ 'id' ], description = 'volfromimage' )
        self.vm( 'controller' ).openStackREST().deleteVolume( volFromImage[ 'id' ] )


    def _checkBackendsStats( self ):
        logging.progress( "Checking backends types" )
        backends = self._sendRequestAndUpdateCookies( requests.get, "%s/%s" % ( self._restApiUrl, 'storage/backends' ) )
        TS_ASSERT( backends.ok )
        TS_ASSERT_EQUALS( len( backends.json() ), 1 )
        TS_ASSERT_EQUALS( backends.json()[ 0 ][ 'name' ], 'rack-storage' )
        rackstorage_backend = self._sendRequestAndUpdateCookies( requests.get, "%s/%s/%s" % ( self._restApiUrl, 'storage/backends', 'rack-storage' ) )
        TS_ASSERT( rackstorage_backend.ok )
        TS_ASSERT_EQUALS( rackstorage_backend.json()[ 'name' ], 'rack-storage' )

    def _verifyAttachedVms( self, networkId, vmId ):
        response = self.vm( 'controller' ).openStackREST( ).showNetwork( networkId )
        TS_ASSERT( vmId in response[ 'attachedTo' ] )

    def _attachVm( self, networkId, vmId ):
        response = self.vm( 'controller' ).openStackREST( ).attachNetwork( vmId, networkId )
        TS_ASSERT( response.ok )

    def _detachVm( self, networkId, vmId ):
        response = self.vm( 'controller' ).openStackREST( ).detachNetwork( vmId, networkId )
        TS_ASSERT( response.ok )

    def _verifyNodes( self ):
        logging.progress( "Verifying node list" )
        nodes = self.vm( 'controller' ).openStackREST().nodeList( getVms = True )
        TS_ASSERT_EQUALS( set( [ node[ 'status' ] for node in nodes ] ), set( [ 'up' ] ) )
        TS_ASSERT_EQUALS( set( [ node[ 'name' ] for node in nodes ] ),
                          set( self.HOSTNAMES ) )
        vmOnNodes = set()
        for node in nodes:
            vmsOnNode = set( node[ 'vms' ] )
            TS_ASSERT_EQUALS( vmsOnNode, set( self.vm( 'controller' ).openStackREST().getNodeResponse( node[ 'name'], getVms = True ).json()[ 'vms' ] ) )
            TS_ASSERT( vmOnNodes.isdisjoint( vmsOnNode ) )
            vmOnNodes.update( vmsOnNode )
        TS_ASSERT_EQUALS( vmOnNodes, set( self._vmNameToId.values() ) )

    def _verifyDeleteNodeAgent2( self ):
        logging.progress( "Verifying agent2 node deletion" )
        hostName = self.vm( 'agent2' ).openStackAgent().hostName()
        TS_ASSERT_THROWS_ANYTHING( self.vm( 'controller' ).openStackREST().deleteNode, hostName )
        self.vm( 'agent2' ).openStackAPI().stopNovaCompute()
        self.vm( 'controller' ).openStackController().subNovaComputeUpdateTimeForHost( hostName, 60 )
        self.vm( 'controller' ).openStackAPI().waitForNovaComputeToBeDownOnHost( hostName )
        self.vm( 'controller' ).openStackREST().deleteNode( hostName )
        nodes = self.vm( 'controller' ).openStackREST().nodeList()
        TS_ASSERT_EQUALS( [ n for n in nodes if n[ 'name' ] == hostName ], [] )

    def _verifyHostStatus( self, hostNameToBeDown ):
        logging.progress( "Verifying list hosts" )
        nodes = self.vm( 'controller' ).openStackREST().nodeList()
        return ( ( set( [ host[ 'status' ] for host in nodes if host[ 'name' ] != hostNameToBeDown ] ) == set( [ 'up' ] ) ) and
               ( set( [ host[ 'status' ] for host in nodes if host[ 'name' ] == hostNameToBeDown ] ) == set( [ 'down' ] ) ) )

    def _hostsList( self ):
        response = self._sendRequestAndUpdateCookies( requests.get, self._restApiUrl + "/nodes" )
        TS_ASSERT( response.ok )
        return response.json()

    def _createPersistentTestVMs( self ):
        self._vmNameToId = {}
        for vmName, vmConfiguration in Test.TEST_VMS.iteritems():
            self._vmNameToId[ vmName ] = self.vm( 'controller' ).openStackREST().createServer( vmName, vmConfiguration, self._image[ 'id' ], self._net[ 'sharednet1' ][ 'id' ] )

    def _verifyVmInfos( self, vmNameToId, networkName ):
        expectedFields = set( ( 'hostname', 'id', 'name', 'ramMB', 'status', 'addresses', 'diskGB', 'vcpus', 'networks',
                                'bootVolume', 'volumes' ) )
        for vmName, vmId in vmNameToId.iteritems():
            vmInfoResponse = self._sendRequestAndUpdateCookies( requests.get, "%s/%s/%s" % ( self._restApiUrl, "VMs", vmId ) )
            vmInfo = vmInfoResponse.json()
            TS_ASSERT_EQUALS( set( vmInfo.keys() ), expectedFields )
            TS_ASSERT_EQUALS( vmInfo[ 'name' ], vmName )
            TS_ASSERT_EQUALS( vmInfo[ 'id' ], vmId )
            TS_ASSERT_IN( networkName, vmInfo[ 'networks' ] )

    def _getPhysicalProperties( self ):
        hostname = self.vm( 'agent1' ).openStackAgent().hostName()
        hostIP = self.vm( 'controller' ).publicIP()
        TS_ASSERT_PREDICATE_TIMEOUT( self._hostPropertiesOk, hostIP, hostname, TS_timeout = 20, TS_interval = 1 )
        properties = self._hostPropertiesResponse.json()
        actualProperties = json.loads( self.vm( "agent1" ).runSeed( physicalpropertiesretriever.retrievePhysicalProperties ) )
        self._comparePhysicalProperties( hostname, actualProperties, properties )

    def _hostPropertiesOk( self, hostIP, hostname ):
        self._hostPropertiesResponse = self._sendRequestAndUpdateCookies( requests.get, "%s/%s/%s" % ( self._restApiUrl, "nodes", hostname ) )
        return self._hostPropertiesResponse.ok

    def _comparePhysicalProperties( self, hostname, actualProperties, openstackProperties ):
        TS_ASSERT_EQUALS( openstackProperties[ 'hostname'], hostname )
        TS_ASSERT_EQUALS( openstackProperties[ 'status'], "up" )
        TS_ASSERT_EQUALS( openstackProperties[ 'memoryMB' ], actualProperties[ "memoryMB" ] )
        TS_ASSERT_EQUALS( openstackProperties[ 'cpuInfo' ][ 'cores' ], actualProperties[ "cores" ] )
        TS_ASSERT_EQUALS( openstackProperties[ 'cpuInfo' ][ 'sockets' ], actualProperties[ "sockets" ] )

    def _uploadTestFile( self, path, content ):
        with tempfile.TemporaryFile() as f:
            f.write( content )
            f.seek( 0 )
            postData = { 'path' : path }
            response = self._sendRequestAndUpdateCookies( requests.post, self._restApiUrl + "/files", data = postData, files = { 'file' : f } )
            TS_ASSERT( response.ok )
            return response.json()

    def _uploadAndCheckTestFiles( self ):
        path = "rand.raw"
        content = os.urandom( 1024 )
        absPath = self._uploadTestFile( path, content )
        TS_ASSERT( absPath.endswith( path ) )
        remoteContent = self.vm( 'controller' ).get( absPath )
        TS_ASSERT_EQUALS( content, remoteContent )

    def _uploadTestImages( self ):
        for imageName, imageProperties in Test.TEST_IMAGES.iteritems():
            self.vm( 'controller' ).openStackREST().createCirrosImage( imageName,
                                                                       diskFormat = imageProperties[ 'diskFormat' ],
                                                                       containerFormat = imageProperties[ 'containerFormat' ] )

    def _imagesWithoutCirros( self ):
        images = self.vm( 'controller' ).openStackREST().imageList()
        imagesWithoutCirros = [ image for image in images if image[ 'name' ] != 'testImage' ]
        TS_ASSERT( len( imagesWithoutCirros ) == len( Test.TEST_IMAGES ) )
        return imagesWithoutCirros

    def _checkUploadedTestImages( self ):
        for image in self._imagesWithoutCirros():
            TS_ASSERT( Test.TEST_IMAGES.has_key( image[ 'name' ] ) )
            TS_ASSERT( 'raw' == image[ 'diskFormat' ] )
            TS_ASSERT( 'bare' == image[ 'containerFormat' ] )

    def _deleteAllTestImagesButCirros( self ):
        for image in self._imagesWithoutCirros():
            self.vm( 'controller' ).openStackREST().deleteImage( image[ 'id' ] )

    def _createVolumes( self ):
        volumes = []
        for volume, params in Test.TEST_VOLS.iteritems():
            volumes.append( self.vm( 'controller' ).openStackREST().createVolume( params[ 'sizeGB' ], volume, backend = params[ 'backend' ], description = 'volume' ) )
        return volumes

    def _checkVolumesAvailable( self, volumeIds ):
        return all( self.vm( 'controller' ).openStackREST().volume( volumeId )[ 'status' ] == 'available' for volumeId in volumeIds )

    def _checkPhysicalNetwork( self ):
        TMP_ANSWER_PATH = '/tmp/answerfile.ans'
        ANSWER_FILE_PATH = '/etc/stratoscale/answerfile.ans'
        physNet = self.vm( 'controller' ).openStackREST().physicalNetwork()
        answerFileContents = self.vm( 'controller' ).sshClient().get( ANSWER_FILE_PATH )
        with open( TMP_ANSWER_PATH, 'w' ) as f:
            f.write( answerFileContents )
        answerFile = configfile.ConfigFile( TMP_ANSWER_PATH )
        vlanRangeList = answerFile.get( 'vlanRange' ).split( ':' )
        TS_ASSERT_EQUALS( physNet[ 'name' ], netconfig.DEFAULT_PHYSICAL_NETWORK_NAME )
        TS_ASSERT_EQUALS( physNet[ 'vlanRangeLow' ], int( vlanRangeList[0] ) )
        TS_ASSERT_EQUALS( physNet[ 'vlanRangeHigh' ], int( vlanRangeList[1] ) )
        TS_ASSERT_EQUALS( physNet[ 'freeVlanTags' ], self._expectedFreeVlanTags( int( vlanRangeList[0] ), int( vlanRangeList[1] ) ) )

    def _expectedFreeVlanTags( self, vlanLowRange, vlanHighRange ):
        usedVlanTags = sets.Set( [ network[ 'extra_args' ][ 'vlan-tag' ] for network in Test.TEST_NETWORKS.itervalues() ] )
        totalVlanTags = sets.Set( range( vlanLowRange, vlanHighRange + 1 ) )
        return list( totalVlanTags.difference( usedVlanTags ) )

    def _createNetworkAndSubnet( self ):
        for name, params in Test.TEST_NETWORKS.iteritems():
            newNetwork = self.vm( 'controller' ).openStackREST().createNetwork( name, ** params.get( 'extra_args', {} ) )
            self.vm( 'controller' ).openStackREST().createSubnet( cidr = params[ 'subnet_cidr' ], networkId = newNetwork[ 'id' ] )
        networkList = self.vm( 'controller' ).openStackREST().networkList()
        TS_ASSERT( len( set( [ net[ 'name' ] for net in networkList ] ) ) == len( networkList ) )
        self._net = { net[ 'name' ] : net for net in networkList }
        subnetId = networkList[ 0 ][ 'subnets' ][ 0 ]
        subnet = self.vm( 'controller' ).openStackREST().showSubnet( subnetId )
        TS_ASSERT_EQUALS( subnet[ 'networkId' ], networkList[ 0 ][ 'id' ] )

    def _showNetwork( self, networkId ):
        response = self._sendRequestAndUpdateCookies( requests.get, self._restApiUrl + "/networks/%(network-id)s" % { 'network-id' : networkId } )
        TS_ASSERT( response.ok )
        return json.loads( response.content )

    def _enableWSM( self ):
        self.vm( 'controller' ).openStackREST().enableWSM()
        for nodeId in self.GUEST_VIRTUAL_MACHINES.keys():
            TS_ASSERT( self.vm( nodeId ).iridium().isDedupEnabled(), True )
            TS_ASSERT( self.vm( nodeId ).iridium().isEvictionEnabled(), True )
        TS_ASSERT_EQUALS( self.vm( 'controller' ).openStackREST().isWSMEnabled(), True )

    def _checkIridium( self ):
        self._enableWSM()

    def _verifyProcFile( self, agentHostName, machineName, expectedValue ):
        logging.progress( "Verifying proc file in %(agent)s is now %(expectedValue)s", { 'agent' : agentHostName, 'expectedValue' : expectedValue } )
        procFileValue = self.vm( machineName ).run( 'cat /proc/npm/dedup' )
        TS_ASSERT_EQUALS( procFileValue, expectedValue )

    def _checkNodeStats( self ):
        logging.progress( "Verifying Node stats" )
        hostnames = [ host[ 'name' ] for host in self.vm( 'controller' ).openStackREST().nodeList() ]
        for hostname in hostnames:
            response = self._sendRequestAndUpdateCookies( requests.get, self._restApiUrl + "/nodes/%(hostname)s/stats" % { 'hostname' : hostname } )
            TS_ASSERT( response.ok )
            logging.progress( "Got response %(response)s", dict( response = response.content ) )

    def _getAllDictValuesRecursive( self, resp ):
        values = []
        for val in resp.values():
            if isinstance( val, dict ):
                values.extend( self._getAllDictValuesRecursive( val ) )
            else:
                values.append( val )
        return values

    def _checkClusterStats( self ):
        logging.progress( "Verifying Cluster stats" )
        response = self._sendRequestAndUpdateCookies( requests.get, self._restApiUrl + "/cluster/stats" )
        TS_ASSERT( response.ok )
        TS_ASSERT( any( val != 0 for val in self._getAllDictValuesRecursive( response.json() ) ) )
        logging.progress( "Got response %(response)s", dict( response = response.content ) )

    def _checkNotFound( self ):
        logging.progress( "Verifying not found statuses" )
        BOGUS_ID = "THIS_IS_NOT_AN_ID_OF_ANYTHING_AND_NOT_EVEN_A_NAME_OF_A_NODE"

        response = self.vm( 'controller' ).openStackREST().getServerResponse( BOGUS_ID )
        logging.progress( "Got response %(response)s", dict( response = response.content ) )
        TS_ASSERT_EQUALS( response.status_code, ResourceNotFoundException.code )
        response = self.vm( 'controller' ).openStackREST().getNodeResponse( BOGUS_ID )
        logging.progress( "Got response %(response)s", dict( response = response.content ) )
        TS_ASSERT_EQUALS( response.status_code, ResourceNotFoundException.code )
        response = self.vm( 'controller' ).openStackREST().getVolumeResponse( BOGUS_ID )
        logging.progress( "Got response %(response)s", dict( response = response.content ) )
        TS_ASSERT_EQUALS( response.status_code, ResourceNotFoundException.code )

    def _checkPowerUpNotShutDownServer( self ):
        logging.progress( "Check response status for powering up a shut downed server" )
        response = self.vm( 'controller' ).openStackREST().sendPowerUpServerRequest( self._vmNameToId[ 'vm1' ] )
        TS_ASSERT_EQUALS( response.status_code, BadRequestException.code )

    def _checkShutDownNotRunningServer( self ):
        logging.progress( "Check response status for shutting down a not running server" )
        response = self.vm( 'controller' ).openStackREST().sendShutDownServerRequest( self._vmNameToId[ 'vm1' ] )
        TS_ASSERT_EQUALS( response.status_code, ResourceNotFoundException.code )

    def _checkDeleteNotShutDownServer( self ):
        logging.progress( "Check response status for deleting a not shut downed server" )
        response = self.vm( 'controller' ).openStackREST().sendDeleteServerRequest( self._vmNameToId[ 'vm1' ] )
        TS_ASSERT_EQUALS( response.status_code, BadRequestException.code )

    def _verifyNodedServices( self ):
        logging.progress( "Verifying service monitoring enabling/disabling" )
        serviceName = 'dummyNode'
        him = self.vm( 'agent1' )
        TS_ASSERT_PREDICATE_TIMEOUT( lambda: him.consul().get( him.openStackAgent().hostName(), 'status' ) == 'ready', TS_timeout = 300, TS_interval = 3 )
        endpoint = "/nodes/%s/services" % him.openStackAgent().hostName()
        data = { 'service-name' : serviceName }
        self._sendRequestAndUpdateCookies( requests.post, self._restApiUrl + endpoint, data = data )
        TS_ASSERT_PREDICATE_TIMEOUT( lambda: serviceName in self._sendRequestAndUpdateCookies( requests.get, self._restApiUrl + endpoint ).json(), TS_timeout = 60, TS_interval = 3 )
        self._sendRequestAndUpdateCookies( requests.delete, self._restApiUrl + endpoint, data = data )
        TS_ASSERT_PREDICATE_TIMEOUT( lambda: serviceName not in self._sendRequestAndUpdateCookies( requests.get, self._restApiUrl + endpoint ).json(), TS_timeout = 60, TS_interval = 3 )

    def tearDown( self ):
        self.vm( 'controller' ).openStackAPI().disconnect()
