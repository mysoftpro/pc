function(doc){
    if (doc.date[1]=='01')
       {
	emit(doc['_id'],doc['_rev']);
    }
}