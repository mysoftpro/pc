function(doc){
    if (doc['ours'] && !doc['promo']){
	emit(doc['_id']);
    }
}