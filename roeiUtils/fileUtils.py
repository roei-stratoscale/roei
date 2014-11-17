import simplejson as json
import os


class RecordState(object):
    TMP_DIR = '/tmp/RecordState'

    @staticmethod
    def fileWrite( filename, content, type='regular' ):
        """
        File write helper function

        :param filename: fullpath filename
        :param content: content to write to the file
        :param type: String (['regular', 'json'])
        :return:
        """
        with open( filename, 'w') as fd:
            if type == 'regular':
                fd.write( content )
            elif type == 'json':
                json.dump( content, fd )

    @staticmethod
    def record( name='default', objectMapping=None ):
        """
        Helper function that saves parameters state to multiple files.

        :param name: str (name of directory to save the record files)
        :param objectMapping:
        objectMapping = [
            {
                'filename': 'filename',
                'content': object(),
            }
        ]

        :usage:
        from roeiUtils.fileUtils import RecordState
                RecordState.record( 'stratocmd', [
                    {'filename': 'messageParameters', 'content': messageParameters},
                    {'filename': 'renderTemplate', 'content': renderTemplate}
                ])
        """
        directory = "{}/{}/".format( RecordState.TMP_DIR, name )
        if not os.path.exists(directory):
            os.makedirs(directory)

        for fileArray in objectMapping:
            filename, content = fileArray[ 'filename' ], fileArray[ 'content' ]
            if isinstance( content, str ):
                fullpath = directory + filename + '.txt'
                RecordState.fileWrite( fullpath, content)
                print "Copy '{0}' content to {1}".format( filename, fullpath )
            else:
                fullpath = directory + filename + '.json'
                RecordState.fileWrite( fullpath, content, type='json' )
                print "Copy '{0}' content to {1}\t\t run:  cat {1} | python -m json.tool ".format( filename, fullpath )

    """
    @staticmethod
    def play( name='default', objectFiles=None ):
        objectFiles = [{}]
        RecordState.record('template', [
                    {
                        'filename': 'messageParameters',

                    },
                    {
                        'filename': 'renderedTemplete',
                        'content': renderedTemplete,
                    }
                ])



        directory = "{}/{}/".format( RecordState.TMP_DIR, name )
        if not os.path.exists(directory):
            os.makedirs(directory)
    """

    """
        import logging
        logging.basicConfig(filename='/tmp/example.log',level=logging.DEBUG)
        import sys;
        logging.debug(sys.path)
    """