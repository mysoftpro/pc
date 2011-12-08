function(doc){
    if (doc['map_to_wi']){
	emit(doc['map_to_wi'], [doc['us_price'],doc['new_stock']]);
    }
}