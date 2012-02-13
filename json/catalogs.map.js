function(doc){
    if (!doc['catalogs'])return;
    var catalog_item = doc.catalogs;
    var priced = doc.price && doc.price>0;
    var in_stock = doc.stock1  || doc.map_to_ne;
    if (catalog_item && priced && in_stock){
	var to_emit	 = [];
	for(var i=0;i<doc.catalogs.length;i++){
	    to_emit.push(doc.catalogs[i]['id']);
	}
	emit(to_emit);
    }
}