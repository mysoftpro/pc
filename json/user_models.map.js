function(doc){
    if (doc['building']&&doc['author']){
	emit(doc['author'],doc['date']);
    }
}