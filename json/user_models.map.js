function(doc){
    if (doc['author']){
	emit(doc['author'],doc);
    }
}