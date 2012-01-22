function recalculate(e){
    var tot = $('#total');var t;
    if (tot[0].tagName.toLowerCase()=='input')
	t = parseInt($('#total').val());
    else
	t = parseInt($('#total').text());
    var m = parseInt($('#monthes').val());
    var k;
    var c = parseInt($('#cache').val());
    if (!c)c = 0;
    if (c >= t/5){
	k= monthly['20'][m];
    }
    else if(c >= t/10){
	 k= monthly['10'][m];
    }
    else{
	k= monthly['0'][m];
    }
    $('#monthly').text(parseInt((t-c)*k*100+0.01)/100).parent().show();
}
function init(){
    $('#calc').click(recalculate);
    var tot = $('#total');
    if (tot.text()==''){
	var pa = tot.parent();
	tot.remove();
	pa.append('<input style="margin-left:40px;" id="total" name="mock_total"/>');
    }
}
init();