var http = require('http');
var jade = require('jade');

apiDefinition = {'endpoints':[
               {name: 1, documented: false},
                              {name: 2, documented: true}
                     ]}
   path = "test.jade"
   //var fn = jade.compile('string of jade #{user}');
   //var html = fn({user: "roei"})
   
   
   //html = jade.render('string of jade #{user}', {user: "roei"});
   
   html = jade.renderFile(path, apiDefinition)
   console.log(html)


/*
http.createServer(function (req, res) {
      res.writeHead(200, {'Content-Type': 'text/plain'});

      //webpage = "This is my new <div>NODE JS</div> website"

      // Compile a function
      
      
      apiDefinition = {'endpoints':[
           {name: 1, documented: false},
           {name: 2, documented: true}
      ]}
      var fn = jade.compile('string of jade #{user}');
      
      //path = "my.jade"
      //var fn = jade.compileFile(path, {})

      // // Render the function
    var html = fn({user: "roei"})
    //var html = fn({'apiDefinition': apiDefinition})
    res.write(html)
    res.end()
      
    //res.end(html);
}).listen(1337, '127.0.0.1');
console.log('Server running at http://127.0.0.1:1337/');
*/




fs = require('fs')
var data = fs.readFileSync('/home/roei/work/mui/js/iodocs/public/data/stratoscale.json')
