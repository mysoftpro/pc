function(doc){
    if (doc['pc_key']){
	emit(doc['_id']);
   }
}