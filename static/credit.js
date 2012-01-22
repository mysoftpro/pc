var monthly =
{'20':{
	6:0.2012,
	8:0.1589,
	10:0.1337,
	12:0.1171,
	14:0.1053,
	18:0.0900,
	24:0.0772},
 '10':{     
     6:0.2039,
     8:0.1616,
     10:0.1364,
     12:0.1199,
     14:0.1082,
     18:0.093,
     24:0.0803
 },
  '0':{     
     6:0.2056,
     8:0.1633,
     10:0.1381,
     12:0.1216,
     14:0.1099,
     18:0.0948,
     24:0.0823
 }
};
function recalculate(e){
    var t = parseInt($('#total').text());
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
    console.log((t-c)*k);
    $('#monthly').text(parseInt((t-c)*k*100+0.01)/100).parent().show();
}
function init(){
    $('#calc').click(recalculate);

}
init();