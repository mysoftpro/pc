function(doc) {
    if(doc._id.match('new') && doc._attachments && !doc.description)  
	for (k in doc._attachments){    
	    emit(k);
	    break;
	}
}