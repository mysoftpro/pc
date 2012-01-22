function recalculate(e){
    var tot = $('#total');var total;
    if (tot[0].tagName.toLowerCase()=='input')
	total = parseInt($('#total').val());
    else
	total = parseInt($('#total').text());
    var m = parseInt($('#monthes').val());
    var k;
    var cache = parseInt($('#cache').val());
    if (!cache)cache = 0;
    if (cache >= total/5){
	k= monthly['20'][m];
    }
    else if(cache >= total/10){
	 k= monthly['10'][m];
    }
    else{
	k= monthly['0'][m];
    }
    var monthly_pay = parseInt((total-cache)*k*100+0.01)/100;
    $('#monthly').text(monthly_pay).parent().show();
    $('input[name="initPay"]').val(cache);
    $('input[name="creditAmount"]').val(total-cache);
    $('input[name="price"]').val(total);
    $('input[name="numInstalment"]').val(m);
    $('input[name="instalment"]').val(monthly_pay);
    var d = new Date();
    d.setDate(d.getDate()+20);
    var year = d.getFullYear();
    var month = (d.getMonth()+1).toString();
    if (month.length==1)
	month = "0"+month;
    var day = d.getDate().toString();
    if (day.length==1)
	day = "0"+day;
    $('input[name="annuityDate"]').val(day+'.'+month+'.'+year);
    $('input[name="annuityDay"]').val(day);
    
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