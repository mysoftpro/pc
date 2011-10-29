function(doc){
    
    if (doc['type'] && doc['type']=='faq'){
	var to_emit = [];
	if (doc['answer_to'])
	    for (var i=0;i<doc['answer_to'];i++)
		to_emit.push(doc['answer_to'][i]);
	to_emit.push(doc['_id']);
	emit(to_emit);
    }
}