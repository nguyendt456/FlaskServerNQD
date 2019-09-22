#this is /list js
    $(document).ready(function(){
            var socketio = io.connect('http://'+document.domain+':'+location.port+'/sensor');
            var socket = io.connect('http://' + document.domain + ':' + location.port + '/user');
            socket.emit('user','{{content.username}}');
            socketio.on('temphum',function(msg){
                console.log('#'+String(msg.MAC)+'temp');
                $('#'+'temp'+String(msg.MAC)).html(msg.temp);
                $('#'+'humidity'+String(msg.MAC)).html(msg.humidity);
            });
        });
        function drop(mac) {
            let p = prompt('Hãy nhập mật khẩu để xác nhận');
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
                xmlhttp.open("POST", "/list");
                xmlhttp.setRequestHeader("Content-Type", "application/json");
                xmlhttp.send(JSON.stringify({MAC:mac,p:p}));
        };
