function(doc){
    if (doc.date[0]=='2012' && doc.date[1]=='03' && doc.date[2]=='26')
       {
	emit(doc['external_id'],doc['_rev']);
    }
}