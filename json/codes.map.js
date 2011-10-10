function(doc){
    if (doc['catalogs'] && doc['price']){
	emit(doc['_id'], doc['_rev']);
    }
}