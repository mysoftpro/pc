function(doc){
    if (doc['catalogs'] && doc['price'] && doc['_id'].indexOf('ew_')==-1 && doc['stock1']>0)
	emit(doc['_id'], doc['_rev']);
}