function(doc){
    if (doc.models){
	for(var m in doc.models)
	    emit(m.substring(26,32),doc.models[m].components);	
    }
}