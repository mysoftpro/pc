function(doc){
    if (doc.catalogs){
	var to_emit	 = [];
	for(var i=0;i<doc.catalogs.length;i++){
	 to_emit.push(doc.catalogs[i]['id']);   
	}
	emit(to_emit);
    }
}