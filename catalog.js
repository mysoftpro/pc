// (function() {
//     var script = document.createElement("script");
//     script.src = "http://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js";
//     script.onload = script.onreadystatechange = function(){ /* your callback here */ };
//     document.body.appendChild( script );
// })();

var wurl = 'http://wit-tech.ru/get/itemdetails/cart/0/id/';
var storeDesc = function(code){
    function store(){
	console.log('store!!!!');
	$jq.ajax({
		     url:wurl + id,
		     success:function(data){
			 console.log('success');
			 $jq.ajax({
				      type: 'POST',
				      url:'http://localhost/xml',
				      data:{'op':'descr','code':code, 'desription':data,'key':'218b47411d2394b78810f7baaa000328'}
				    });
		     }
		 });
    }
    return store;
};


var rows = $jq('.row');
for (var i=0;i<rows.length;i++){
    var row = $jq(rows.get(i));
    var code = row.find('.code').text();
    var id = row.attr('id');
    var _storeDesc = storeDesc(code);
    _storeDesc();	  	  
}









var code_required = '19207';
var storeSingleDesc = function(code){
    function store(){
	console.log('store single!!!!');
	$jq.ajax({
		     url:wurl + id,
		     success:function(data){
			 console.log('success single');
			 $jq.ajax({
				      type: 'POST',
				      url:'http://localhost/xml',
				      data:{'op':'descr','code':code, 'desription':data, 'key':'see secure.py'}
				    });
		     }
		 });
    }
    return store;
};

function walk (){
var _rows = $jq('.row');
for (var j=0;j<_rows.length;j++){
    var row = $jq(_rows.get(j));
    var code = row.find('.code').text();
    console.log(code);
    if (code != code_required)
	continue;
    var id = row.attr('id');
    var _storeDesc = storeSingleDesc(code);
    _storeDesc();	  	  
}    
}
walk();