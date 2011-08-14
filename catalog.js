var wurl = 'http://wit-tech.ru/get/itemdetails/cart/0/id/';
var storeDesc = function(code){
    function store(){
	$jq.ajax({
		     url:wurl + id,
		     success:function(data){
			 $jq.ajax({
				      url:'http://localhost/xml',
				      data:{'op':'descr','code':code, 'desription':data}
				    });
		     }
		 });
    }
    return store;
};


var rows = $jq('.row');
for (var i=0;i<3;i++){//rows.length
    var row = $jq(rows.get(i));
    var code = row.find('.code').text();	  
    var id = row.attr('id');
    var _storeDesc = storeDesc(code);
    _storeDesc();	  	  
}