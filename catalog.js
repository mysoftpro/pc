(function() {
    var script = document.createElement("script");
    script.src = "http://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js";
    script.onload = script.onreadystatechange = function(){ /* your callback here */ };
    document.body.appendChild( script );
})()

var wurl = 'http://wit-tech.ru/get/itemdetails/cart/0/id/';
var storeDesc = function(code){
    if (code !== '19005' && code !== '19172'){
	return function(){};
    }
	
    console.log('pass!!!!');
    function store(){
	console.log('store!!!!');
	$jq.ajax({
		     url:wurl + id,
		     success:function(data){
			 console.log('success');
			 $jq.ajax({
				      type: 'POST',
				      url:'http://localhost/xml',
				      data:{'op':'descr','code':code, 'desription':data}
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

