function(doc){
    if (doc['ours'] ){
	emit(doc['_id'],doc);
    }
}