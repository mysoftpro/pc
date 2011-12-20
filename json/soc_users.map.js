function(doc){
    if (doc['soc_users']){
	for (var i=0;i<doc['soc_users'].length;i++){
	    emit(doc['soc_users'][i]['uid']);
	}
    }
}