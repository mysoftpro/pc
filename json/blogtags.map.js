function(doc){
    if (doc['type'] && doc['type']=='blog' && doc['tags']){
	for(var i=0;i<doc.tags.length;i++){
	    emit([doc['tags'][i],doc['_id']]);
	}
    }
}