function(doc){
    if (doc.date[0]=='2012' && doc.date[1]=='04' && doc.date[2]=='03')
       {
	emit(doc['external_id'],doc['_rev']);
    }
}