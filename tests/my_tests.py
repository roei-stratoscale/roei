from strato.tests.common.infra.suite import *
from strato.tests.integration.infra import scenario
from strato.openstackapi import types
from strato.openstackapi import config as openstackconfig



class roeiTestsUtil(object):
    def installRPMs(testsScenario, RPMs):
        """"
        Install RPMs packages

        :param testsScenario  scenario.Scenario subclass
        :param RPMs str list
        TODO: Check if RPMs can run Concurrently
        """
        admin = testsScenario.vm( 'controller' ).admin()

        for RPM in RPMs:
            admin.installRPMPackage( RPM )


class Test( scenario.Scenario ):
    ABORT_TEST_TIMEOUT = 120000000
    GUEST_VIRTUAL_MACHINES = { 'controller': dict( customVanilla='openstackcontroller' ),
                               'agent1': dict( customVanilla='openstackagent' ) }
    TEST_SERVER_CONFIGURATION = types.OpenStackServerConfiguration( 1, 256, 50 )
    TEST_VOLUMES = { 'volume1' : openstackconfig.DEFAULT_BACKEND }
    GOOD_MARK = 'GOOD'
    RPMs = [
        "build/bring/northbound/strato_api-1-0.x86_64.rpm",
        "build/bring/northbound/strato_cli-1-0.x86_64.rpm",
        "build/bring/northbound/strato_iodocs-1-0.x86_64.rpm"
    ]













    def setUp( self ):

        self.util = roeiTestsUtil()
        controller = self.vm( 'controller' )
        controller.openStackController().waitForController()
        controller.openStackController().setupNeutronDefaultSubnet()
        self.util.installRPMs(self.RPMs)




        self.vm( 'agent1' ).openStackAgent().addComputeNodeToCluster( self.vm( 'controller' ) )
        controller.openStackController().waitForController()
        controller.ceph().waitForCephCluster()

        self._driver = controller.openStackAPI().connect()
        self._image = controller.openStackAPI().uploadCirros()

    def run( self ):
        openStackAPI = self.vm( 'controller' ).openStackAPI()
        volumes = openStackAPI.createVolumes( Test.TEST_VOLUMES )
        server = openStackAPI.createAndPowerUpServer( "server1",
                                                                                Test.TEST_SERVER_CONFIGURATION,
                                                                                self._image[ 'id' ] )
        serverIP = server[ 'addresses' ][ 0 ]
        logging.progress( 'Waiting for TCP on server at %(serverIP)s', dict( serverIP = serverIP ) )
        openStackAPI.waitForTcpOnServer( serverIP )


        import pdb, sys
        pdb.set_trace()
        #self._verifyVmInfos()



        openStackAPI.attachVolumes( server, volumes )
        openStackAPI.writeMarkToVolumes( serverIP, Test.GOOD_MARK, len( Test.TEST_VOLUMES ) )
        openStackAPI.readMarkFromVolumes( serverIP, Test.GOOD_MARK, len( Test.TEST_VOLUMES ) )

        snapshots = self._createTestSnapshots( volumes )
        volumes = self._renameVolumes( volumes )
        snapshots = self._renameSnapshots( snapshots )
        openStackAPI.writeMarkToVolumes( serverIP, 'BAD2', len( Test.TEST_VOLUMES ) )
        openStackAPI.detachVolumes( server, volumes )

        volFromSnaps = self._createTestVolsFromSnaps( snapshots )
        self._deleteSnapshots( snapshots )
        openStackAPI.deleteVolumes( volumes )
        openStackAPI.attachVolumes( server, volFromSnaps )
        openStackAPI.readMarkFromVolumes( serverIP, Test.GOOD_MARK, len( Test.TEST_VOLUMES ) )

        volFromVols = self._createTestVolsFromVols( volFromSnaps )
        openStackAPI.writeMarkToVolumes( serverIP, 'BAD3', len( Test.TEST_VOLUMES ) )
        openStackAPI.readMarkFromVolumes( serverIP, 'BAD3', len( Test.TEST_VOLUMES ) )
        openStackAPI.detachVolumes( server, volFromSnaps )
        openStackAPI.deleteVolumes( volFromSnaps )

        openStackAPI.attachVolumes( server, volFromVols )
        openStackAPI.readMarkFromVolumes( serverIP, Test.GOOD_MARK, len( Test.TEST_VOLUMES ) )
        openStackAPI.detachVolumes( server, volFromVols )
        openStackAPI.deleteVolumes( volFromVols )


    def _verifyVmInfos( self ):
        import requests
        #vmId = "419eb057-9d5-4d21-80dc-bd2893bd9071"; _restApiUrl = 'http://192.168.122.254:7000/v1'; expectedFields = set( ( 'hostname', 'id', 'name', 'ramMB', 'status', 'addresses', 'diskGB', 'vcpus', 'networks', 'bootVolume', 'volumes' ) )

        vmId = "419eb057-9d55-4d21-80dc-bd2893bd9071"
        _restApiUrl = 'http://192.168.122.254:7000/v1'
        expectedFields = set( ( 'hostname', 'id', 'name', 'ramMB', 'status', 'addresses', 'diskGB', 'vcpus', 'networks', 'bootVolume', 'volumes' ) )
        vmInfoResponse = requests.get("%s/%s/%s" % ( _restApiUrl, "VMs", vmId ))
        vmInfo = vmInfoResponse.json()
        TS_ASSERT_EQUALS( set( vmInfo.keys() ), expectedFields )



    def _createTestSnapshots( self, volumes ):
        snapshots = []
        for volume in volumes:
            logging.progress( 'Creating snapshot of volume %(name)s', volume )
            snapshot = self._driver.volumes.createSnapshot( volume[ 'id' ], 'snap-of-%s' % volume[ 'name' ], description = 'snap' )
            self.vm( 'controller' ).openStackAPI().waitForSnapshotToChangeStatus( snapshot[ 'id' ], 'available', 180 )
            snapshot[ 'originalVolume' ] = volume
            snapshots.append( snapshot )
        return snapshots

    def _renameObjects( self, objects, origDesc, getFunc, renameFunc ):
        newObjs = []
        for obj in objects:
            logging.progress( 'Renaming %(name)s', obj )
            origObj = getFunc( obj[ 'id' ] )
            TS_ASSERT_EQUALS( origObj[ 'description' ], origDesc )
            newName = 'renamed-%s' % obj[ 'name' ]
            newObj = renameFunc( obj[ 'id' ], { 'name': newName, 'description': 'renamed' } )
            TS_ASSERT_EQUALS( newObj[ 'name' ], newName )
            TS_ASSERT_EQUALS( newObj[ 'description' ], 'renamed' )
            newObj = getFunc( obj[ 'id' ] )
            TS_ASSERT_EQUALS( newObj[ 'name' ], newName )
            TS_ASSERT_EQUALS( newObj[ 'description' ], 'renamed' )
            newObjs.append( newObj )
        return newObjs

    def _renameVolumes( self, volumes ):
        return self._renameObjects( volumes, 'vol',
                                    self._driver.volumes.getVolume,
                                    self._driver.volumes.renameVolume )

    def _renameSnapshots( self, snapshots ):
        return self._renameObjects( snapshots, 'snap',
                                    self._driver.volumes.getSnapshot,
                                    self._driver.volumes.renameSnapshot )

    def _createTestVolsFromSnaps( self, snapshots ):
        volumes = []
        for snapshot in snapshots:
            logging.progress( 'Creating volume from snapshot %(name)s', snapshot )
            volume = self._driver.volumes.createVolumeFrom( 'vol-from-%s' % snapshot[ 'name' ], snapshot[ 'id' ], 'snapshot', description = 'volfromsnap' )
            self.vm( 'controller' ).openStackAPI().waitForVolumeToChangeStatus( volume[ 'id' ], 'available', 180 )
            volumes.append( volume )
        return volumes

    def _createTestVolsFromVols( self, volumes ):
        clones = []
        for volume in volumes:
            logging.progress( 'Creating volume from volume %(name)s', volume )
            clone = self._driver.volumes.createVolumeFrom( 'vol-from-%s' % volume[ 'name' ], volume[ 'id' ], 'volume', description = 'volfromvol' )
            self.vm( 'controller' ).openStackAPI().waitForVolumeToChangeStatus( clone[ 'id' ], 'available', 180 )
            clones.append( clone )
        return clones

    def _deleteSnapshots( self, snapshots ):
        for snapshot in snapshots:
            logging.progress( 'Deleting snapshot %(name)s', snapshot )
            self._driver.volumes.deleteSnapshot( snapshot[ 'id' ] )
            self.vm( 'controller' ).openStackAPI().waitForSnapshotToBeDeleted( snapshot[ 'id' ], 180 )

    def tearDown( self ):
        self.vm( 'controller' ).openStackAPI().disconnect()
