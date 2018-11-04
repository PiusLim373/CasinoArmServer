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
    //$("#main").fadeOut();
    //$("#loader").fadeIn();
    $.ajax({
        method:'POST',
        url:"/FaceRecog",
        success: function(response){
            console.log(response);
            location.href=response;
        }   
    });


}


function OneMoreRound(){
    $.ajax({
        method:'POST',
        url:"/RestartWithoutReset",
        data:{},
        success: function(response){
            location.href=response;
        }
    })
}



//############################LOOP This All the time##################//
(function loopthis(i){
            setTimeout(function(){
                
                var RealtimeFeedback = new XMLHttpRequest();
                
                RealtimeFeedback.open('GET', 'http://192.168.1.101:5000/feedback', true);
                
                RealtimeFeedback.onload = function() {
                    var data = JSON.parse(this.responseText);
                    $("#Jumbotron_title h1").html(data.Jumbotron_title);
                    $("#Jumbotron_text1").html(data.Jumbotron_text1);
                    $("#Jumbotron_text2").html(data.Jumbotron_text2);
                    if(data.ExistingPlayer1 == 1){
                        $("#Player1Bet").html("S$" + data.Player1Bet);
                        $("#Player1Money").html("S$" + data.Player1Money);
                    }
                    else if (data.ExistingPlayer1 == 0){
                        $("#Player1Status").removeClass("table-active");
                        $("#Player1Status").addClass("table-danger");
                        $("#Player1Bet").html("Opted out");
                        $("#Player1Money").html("Opted out");
                    }
                    if(data.ExistingPlayer2 == 1){
                        $("#Player2Bet").html("S$" + data.Player2Bet);
                        $("#Player2Money").html("S$" + data.Player2Money);
                    }
                    else if (data.ExistingPlayer2 == 0){
                        $("#Player2Status").removeClass("table-active");
                        $("#Player2Status").addClass("table-danger");
                        $("#Player2Bet").html("Opted out");
                        $("#Player2Money").html("Opted out");
                    }
                    if(data.ExistingPlayer3 == 1){
                        $("#Player3Bet").html("S$" + data.Player3Bet);
                        $("#Player3Money").html("S$" + data.Player3Money);
                    }
                    else if (data.ExistingPlayer3 == 0){
                        $("#Player3Status").removeClass("table-active");
                        $("#Player3Status").addClass("table-danger");
                        $("#Player3Bet").html("Opted out");
                        $("#Player3Money").html("Opted out");
                    }
                    if(data.ResetBtn == "show"){
                        $("#ResetBtn").fadeIn('slow');
                        $("#ContinueBtn").fadeIn('slow');
                    }
                    if(data.ResetBtn == ""){
                        $("#ResetBtn").hide();
                        $("#ContinueBtn").hide();
                    }
                    if(data.BetPhase == "show"){
                        $("#BetDiv").fadeIn("slow");
                    } 
                    if(data.BetPhase == ""){
                        $("#BetDiv").fadeOut("slow");
                    } 
                    var ArduinoBetPerc = data.ArduinoBet + "%"
                    if (data.ArduinoBet == 100){
                        $("#betbar").css("width", "100%");
                        $("#betbar").html("ALL IN!");
                        $("#betbar").addClass("bg-success");
                    }
                    // else {
                    //     $("#betbar").removeClass("bg-success");
                    //     $("#betbar").css("width",ArduinoBetPerc);
                    //     if (data.CurrPlayer == 1){
                    //         $("#betbar").html("S$" + data.Player1Bet);
                    //     }
                    //     else if(data.CurrPlayer == 2){
                    //         $("#betbar").html("S$" + data.Player2Bet);
                    //     }
                    //     else if(data.CurrPlayer == 3){
                    //         $("#betbar").html("S$" + data.Player3Bet);
                    //     }
                    // }
                    else {
                        $("#betbar").removeClass("bg-success");
                        $("#betbar").css("width",ArduinoBetPerc);
                        if (data.CurrPlayer == 1){
                            $("#betbar").html("S$" + Math.round(data.Player1Money * (data.ArduinoBet/100)));
                        }
                        else if(data.CurrPlayer == 2){
                            $("#betbar").html("S$" + Math.round(data.Player2Money * (data.ArduinoBet/100)));
                        }
                        else if(data.CurrPlayer == 3){
                            $("#betbar").html("S$" + Math.round(data.Player3Money * (data.ArduinoBet/100)));
                        }
                    }
                };

                RealtimeFeedback.send();


                if (--i){
                    loopthis(i); 
                }
            }, 300);
        })(500000000);  
