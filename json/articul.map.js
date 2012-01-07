function(doc){
    if (doc['articul'])
	emit(doc['articul'].replace('\t',''));
    else{
	if (doc['vendor'])
	    emit(doc['_id'].replace('new_','_'));
    }
}