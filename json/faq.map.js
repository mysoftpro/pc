function(doc){
    if (doc['type'] && doc['type']=='faq'){
	var to_emit = [];	
	if (doc['parent']){
	    for (var i=0;i<doc['parent'].length;i++){
		to_emit.push(doc['parent'][i]);
	    }
	}
	to_emit.push(doc['_id']);
	if (!doc['parent']){
	    to_emit.push('z');
	}
	emit(to_emit,doc['date']);
    }
}