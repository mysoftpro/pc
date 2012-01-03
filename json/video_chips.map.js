function(doc){
    if (doc['chip'] && doc['catalogs'])
	emit(doc['chip'], doc['_id']);
}