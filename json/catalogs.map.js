function(doc){
    var catalog_item = doc.catalogs && doc.price && doc.price>0;
    var in_stock = (doc.stock1 && doc.stock1>0) || (doc.mystock && doc.mystock>0);
    if (catalog_item && in_stock){
	var to_emit	 = [];
	for(var i=0;i<doc.catalogs.length;i++){
	    to_emit.push(doc.catalogs[i]['id']);   
	}
	emit(to_emit);
    }
}