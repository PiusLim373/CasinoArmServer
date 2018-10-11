//****************************Basic Command*********************************//
function Initialize_AGV(){
    if (confirm("Proceed?")) {
        $.ajax({
                method: 'POST',
                url: "/script",
                data: {
                    'mission': 'Initialize_AGV'
                },
                success: function(data, status){
                    
                    $("#feedback-success p").html(data);
                    ShowAlert_Success();
                }
        });
    }
}



//****************************Others*********************************//
function ShowAlert_Success() {
    $("#feedback-danger").hide();
    $("#feedback-warning").hide();
    $("#feedback-success").show();
}
function ShowAlert_Danger() {
    $("#feedback-success").hide();
    $("#feedback-warning").hide();
    $("#feedback-danger").show();
}
function ShowAlert_Warning() {
    $("#feedback-success").hide();
    $("#feedback-danger").hide();
    $("#feedback-warning").show();
}
