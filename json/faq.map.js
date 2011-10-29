function(doc){
    if (doc['type'] && doc['type']=='faq')
	emit(doc['_id']);
}