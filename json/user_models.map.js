function(doc){
    if (doc['parent'] && doc['author'] && doc['building'] && !doc['ours']){
	emit(doc['_id']);
    }
}