from jinja2 import Template
from fileUtils import RecordState



"""
HELP_MESSAGE_FORMAT calculations:

   [ undocumented function ]
|--|---------------------------------------------------------------------------------
a  b

   NAME
|--|---------------------------------------------------------------------------------
a  b
                volume-create-from: Create a volume from source on strato-rack
|--|------------|--------------------------------------------------------------------
a  b            c

a = PADDING
b = a + DESCRIPTION_PADDING
"""


HELP_MESSAGE_FORMAT = """\
{% set a = config.PADDING * " "%}\
{% set b = a + config.DESCRIPTION_PADDING * " "%}\
{% if data.documented == False %}
{{ a }}\033[{{ config.UNDOCUMENTED_COLOR }}m{{ config.UNDOCUMENTED_FUNCTION_STR }}\033[0m
{% endif %}\
{{ a + "NAME"}}
{{ b + data.funcName }}: {{ data.description }}
{{ a + "USAGE"}}
{{ b + data.funcName }}: {{ data.usage }}
"""


"""
ARGUMENTS_HELP_MESSAGE_FORMAT calculations:

   ARGUMENTS
|--|---------------------------------------------------------------------------------
a  b


  Documented argument case:

               name                  Name for the new volume [SusYeor]
|--|-----------|---------------------|-----------------------------------------------
a  b            c                    d
                                     VALUES:

                                     volume      Another data volume
|--|-----------|---------------------|-----------|-----------------------------------
a  b            c                    d           e



  Undocumented argument case:

   [ undocumented argument ]  name                  Name for the new volume [SusYeor]
|--|-------------------------|----------------------|--------------------------------
a  b                       c                        d

                                                    Valid values:
                                                    volume      Another data volume
|--|-------------------------|----------------------|-----------|---------------------
a  b                       c                        d           e


a = PADDING
b = a + config.DESCRIPTION_PADDING
if (config.HAS_UNDOCUMENTED_ARGS): b = a + len( config.UNDOCUMENTED_ARGUMENT_STR ) + 2
c = b + config.ARG_NAME_LEN
d = c + PADDING
e = d + config.CHOICE_KEY_LEN
"""

ELABORATED_HELP_MESSAGE_FORMAT = """ \
{% set a = config.PADDING * " " %}\
{% set b = a + config.DESCRIPTION_PADDING * " " %}\
{% if config.HAS_UNDOCUMENTED_ARGS %}\
{% set b = a + ( ( config.UNDOCUMENTED_ARGUMENT_STR | length ) + 2 ) * " " %}\
{% endif %}\
{% set c = b + config.ARG_NAME_LEN * " " %}\
{% set d = c + config.PADDING * " " %}\
{% if args != [] %}
{{ a + "ARGUMENTS"}} \
{% endif %} \
{% for arg in args %} \
{% set x = config.ARG_NAME_LEN - ( arg.name | length ) %}\
{% if arg.documented == False %}\
\n{{ a }}\033[{{ config.UNDOCUMENTED_COLOR }}m{{ config.UNDOCUMENTED_ARGUMENT_STR }}\033[0m  \
{% else %}\
\n{{ b }}\
{% endif %}\
{{ arg.name }}{{ x * " " }}{{ arg.description }}\
{%- if arg.default != None -%} \
     {{" "}}[{{ arg.default }}] \
{% endif %}
{% if arg.choices != None %}
{{ c + "VALUES:\n"}}
    {%- for choiceKey in arg.choices.keys() -%}
        {% set y = config.CHOICE_KEY_LEN - ( choiceKey | length ) -%}
{{"\n" + c + choiceKey + y * " " + arg.choices[ choiceKey ] }}
    {%- endfor %}
{% endif %}\
{% endfor %}\n
"""


args1 = [
   dict(documented=False, name='name', description='Name for the new volume', default="SusYeor", choices=None ),
   dict(documented=True, name='source-type', description='Type of entity to use as source', default=None, choices={
       'volume': 'Another data volume',
       'image': 'image',
       'snapshot': 'A snapshot of any volume'
   } ),
   dict(documented=False, name='source-id', description='ID of the source for the new volume', default=None, choices=None ),
   dict(documented=True, name='description', description='Description for the new volume', default=None, choices=None  )
]

args2 = [
   dict(documented=True, name='name', description='Name for the new volume', default="SusYeor", choices=None ),
   dict(documented=True, name='source-type', description='Type of entity to use as source', default=None, choices={
       'volume': 'Another data volume',
       'image': 'image',
       'snapshot': 'A snapshot of any volume'
   } ),
   dict(documented=True, name='source-id', description='ID of the source for the new volume', default=None, choices=None ),
   dict(documented=True, name='description', description='Description for the new volume', default=None, choices=None  )
]

data1 = {'documented': True, 'funcName': 'volume-create-from', 'description': 'Create a volume from source on strato-rack', 'usage': 'source-type=... name=... source-id=... description=...', 'args': args1 }
data2 = {'documented': True, 'funcName': 'volume-create-from', 'description': 'Create a volume from source on strato-rack', 'usage': 'source-type=... name=... source-id=... description=...', 'args': args1 }
data3 = {'documented': False, 'funcName': 'volume-create-from', 'description': 'Create a volume from source on strato-rack', 'usage': 'source-type=... name=... source-id=... description=...', 'args': args2 }





data = {
    "description": "Create a volume from source on strato-rack",
    "documented": False,
    "funcName": "volume-create-from",
    "usage": "source-type=... name=... source-id=... description=...",
    "args": [
        {
            "choices": None,
            "default": "SusYeor",
            "description": "Name for the new volume",
            "documented": False,
            "name": "name"
        },
        {
            "choices": {
                "image": "image",
                "snapshot": "A snapshot of any volume",
                "volume": "Another data volume"
            },
            "default": None,
            "description": "Type of entity to use as source",
            "documented": True,
            "name": "source-type"
        },
        {
            "choices": None,
            "default": None,
            "description": "ID of the source for the new volume",
            "documented": True,
            "name": "source-id"
        },
        {
            "choices": None,
            "default": None,
            "description": "Description for the new volume",
            "documented": True,
            "name": "description"
        }
    ]
}












def draw( messageParameters, record=False ):
    config = _calcStrLength( messageParameters )
    templateHelp = Template( HELP_MESSAGE_FORMAT )
    templateHelpStr = templateHelp.render( data = messageParameters, config=config ).encode( 'utf-8' )

    templateArg = Template( ELABORATED_HELP_MESSAGE_FORMAT )
    templateArgStr = templateArg.render( args = messageParameters[ 'args' ], config=config ).encode( 'utf-8' )
    renderedTemplete = templateHelpStr + templateArgStr
    print( renderedTemplete )

    if record:
        RecordState.record('template', [
                    {
                        'filename': 'messageParameters',
                        'content': messageParameters,
                    },
                    {
                        'filename': 'renderedTemplete',
                        'content': renderedTemplete,
                    }
                ])

def _calcStrLength( data ):
    MIN_ARG_NAME_LEN = 22
    MIN_CHOICE_KEY_LEN = 12
    PADDING = 3
    DESCRIPTION_PADDING = 12
    ANSI_SGR_COLOR_CODE = {'red': 31, 'green': 32, 'orange': 33, 'blue': 34, 'lightGreen': 92, 'yellow': 93, 'levenderPurple':94, 'pink': 95, 'babyBlue': 96, 'white': 97 }  #Used for the ANSI escape code SGR sequence: \033[<UNDOCUMENTED_COLOR>m ( example: \033[33m )
    UNDOCUMENTED_COLOR = ANSI_SGR_COLOR_CODE[ 'levenderPurple' ]
    UNDOCUMENTED_FUNCTION_STR = "[ UNDOCUMENTED FUNCTION ]"
    UNDOCUMENTED_ARGUMENT_STR = "[ UNDOCUMENTED ]"


    args = data[ 'args' ]
    return {
                'ARG_NAME_LEN': max(MIN_ARG_NAME_LEN, max( [len( arg['name'] ) + PADDING for arg in args ] ) ),
                'CHOICE_KEY_LEN': max( MIN_CHOICE_KEY_LEN, len (max( [ max( choice, key=len ) for choice in  [ arg[ 'choices' ] for arg in args if arg.has_key('choices') and arg[ 'choices' ] ] ], key=len ) ) ),
                'PADDING': PADDING,
                'DESCRIPTION_PADDING': DESCRIPTION_PADDING,
                'HAS_UNDOCUMENTED_ARGS': [] != [arg for arg in args if arg[ 'documented' ] == False ],
                'UNDOCUMENTED_FUNCTION_STR': UNDOCUMENTED_FUNCTION_STR,
                'UNDOCUMENTED_ARGUMENT_STR': UNDOCUMENTED_ARGUMENT_STR,
                'UNDOCUMENTED_COLOR': UNDOCUMENTED_COLOR
            }


def main():
    #draw(data2)
    #draw(data3)
    draw(data)


if __name__ == '__main__':
    main()


