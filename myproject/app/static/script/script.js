//****************************Basic Command*********************************//
function Initialize_AGV(){
        $.ajax({
                method: 'POST',
                url: "/kek",
                data: {
                    'mission': 'Initialize_AGV'
                },
                success: function(data, status){
                    
                    //$("#testtext").html(data);
                    ShowAlert_Success();
                }
        });
}

function StartGame(){
    $("#main").fadeOut();
    $("#loader").fadeIn();
    $.ajax({
        method:'POST',
        url:"/StartGame",
        success: function(response){
            console.log(response);
            location.href=response;
        }
    });
}
function Initiate(){
    $.ajax({
        method:'POST',
        url:"/initiate",
        success:function(response){
            console.log("SUCCESS!!!!!")
        }
    })
}

//############################LOOP This All the time##################//
(function loopthis(i){
            setTimeout(function(){
                
                var RealtimeFeedback = new XMLHttpRequest();
                
                RealtimeFeedback.open('GET', 'http://192.168.1.103:5000/feedback', true);
                
                RealtimeFeedback.onload = function() {
                    var data = JSON.parse(this.responseText);
                    $("#Jumbotron_title h1").html(data.Jumbotron_title);
                    $("#Jumbotron_text1").html(data.Jumbotron_text1);
                    $("#Jumbotron_text2").html(data.Jumbotron_text2);
                    if(data.ResetBtn == "show"){
                        $("#ResetBtn").show();
                    }
                    if(data.ResetBtn == ""){
                        $("#ResetBtn").hide();
                    }

                };

                RealtimeFeedback.send();


                if (--i){
                    loopthis(i); 
                }
            }, 300);
        })(500000000);  
