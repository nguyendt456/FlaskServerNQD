        $("#{{devices[i].uuid}}pass").keyup(function(event) {
            if (event.keyCode === 13) {
                $("#{{devices[i].uuid}}but").click();
            }
        });
        function encode_utf8(s) {
            return unescape(encodeURIComponent(s));
        };
        function drop(uuid) {
            let p = prompt('Hãy nhập mật khẩu để xác nhận');
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
                xmlhttp.open("POST", "/list");
                xmlhttp.setRequestHeader("Content-Type", "application/json");
                xmlhttp.send(JSON.stringify({uuid:uuid,p:p}));
        };
        function popup(uuid) {
            if (document.getElementById(uuid+"prompt").style.display == "none") {
                document.getElementById(uuid+"prompt").style.display = "block";
            }
            else document.getElementById(uuid+"prompt").style.display = "none";
        };
        function exe(uuid) {
            document.getElementById(uuid+"prompt").style.display = "none";
            var p = document.getElementById(uuid+"pass").value;
            var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
            xmlhttp.open("POST", "/list");
            xmlhttp.setRequestHeader("Content-Type", "application/json");
            xmlhttp.send(JSON.stringify({'uuid':uuid,p:p}));
        };
        $(document).ready(function(){
            var socketio = io.connect('http://'+document.domain+':'+location.port+'/sensor');
            var socket = io.connect('http://' + document.domain + ':' + location.port + '/user');
            socket.emit('user','{{content.username}}');
            socketio.on('temphum',function(msg){
                console.log('#'+String(msg.uuid)+'temp');
                $('#'+'temp'+String(msg.uuid)).html(msg.temp);
                $('#'+'humidity'+String(msg.uuid)).html(msg.humidity);
            });
            socketio.on('error',function(error){
                if(error.success==' ') {
                    alert(error.error);
                }
                if(error.error==' ') {
                    alert(error.success);
                    location.reload();
                }
            });
        });
