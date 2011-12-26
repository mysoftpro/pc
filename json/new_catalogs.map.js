function(doc){
    if (doc['new_catalogs'])
	emit(doc['new_catalogs']);
}