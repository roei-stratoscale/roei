fs = require('fs')                                                                                                                                                                                                                                                                        
//var data = fs.readFileSync('/home/roei/work/mui/js/iodocs/public/data/stratoscale.json')
var data = fs.readFileSync('/home/roei/work/mui/build/docs_output.json')

apiDefinition = JSON.parse(data.toString() )
endpoints = apiDefinition.endpoints
documentedEndpoints = []

endpoints_len = endpoints.length
for (var i=0; i<endpoints_len; i++) {
    endpoint = endpoints[i]
    console.log(i + ": " + endpoint['documented'] )
    if ( endpoint['documented'] == false ){
        console.log("Going to remove resource: " + endpoint['name'] )

    } else {
        methods = endpoint.methods
        documentedMethods = []
        methods_len = methods.length
        for ( var j=0; j<methods_len; j++){
            if ( methods[j]['documented'] == true ){
                documentedMethods.push(methods[j])
            }
        }

        if (documentedMethods.length) {
            endpoint.methods = documentedMethods
            documentedEndpoints.push(endpoint)
        }
    }
}

















/*
for (var endpoint in endpoints) {
        console.log(endpoint + ": " + endpoints[endpoint]['documented'] )
    if ( endpoints[endpoint]['documented'] == false ){
        console.log("Going to remove resource: " + endpoints[endpoint]['name'] )


    } else {
        methods = endpoints[endpoint].methods
        documentedMethods = []
        for ( method in methods){
            if ( methods[method]['documented'] == true ){
                documentedMethods.push(methods[method])
            }
        }
        if (documentedMethods.length)
            endpoints[endpoint].methods = documentedMethods
            documentedEndpoints.push(endpoints[endpoint])
    }
}



for (var endpoint in endpoints) {
    //if ( endpoints[endpoint]['documented'] )
        console.log(endpoint + ": " + endpoints[endpoint]['documented'] )
    if ( endpoints[endpoint]['documented'] == false ){
        console.log("Going to remove resource: " + endpoints[endpoint]['name'] )
        delete endpoints[endpoint]

    } else {
        methods = endpoints[endpoint].methods
        for ( method in methods){
            if ( methods[method]['documented'] == false ){
                console.log("       Going to remove method " + methods[method]['MethodName'] )
                delete methods[method]
            }
        }
    }
}*/



console.log("and again....")
console.log(getDocumentedJSON())
outputfile = "/tmp/nodejs.txt"

var fs = require('fs');
fs.writeFile(outputfile, getDocumentedJSON())
console.log("vim " + outputfile)




function getDocumentedJSON(){
    output = ''
    for (var endpoint in documentedEndpoints) {
        output += endpoint + " " + documentedEndpoints[endpoint]['documented'] + ": " + documentedEndpoints[endpoint]['name'] + '\n'
        methods = documentedEndpoints[endpoint].methods
        for ( method in methods){
            if ( methods[method]['documented'] == true ){
               output += "        method: " + methods[method]['MethodName'] + '\n'
            }
        }
    }
    return output
}
