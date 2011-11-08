function(doc){
    if (doc['building']!==undefined&&doc['author']){
	var len = doc['_id'].length;
	emit(doc['_id'].substring(len-3,len),null);
    }    
}