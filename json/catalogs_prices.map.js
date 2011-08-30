function(doc){
    if (doc.catalogs && doc.price && doc.price>0 && doc.stock1 && doc.stock1>0){
	var to_emit	 = [];
	for(var i=0;i<doc.catalogs.length;i++){
	    to_emit.push(doc.catalogs[i]['id']);   
	}
	emit(to_emit, doc.price);
    }
}