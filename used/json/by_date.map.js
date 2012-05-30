// && doc.date[2]=='14'
function(doc){
    if (doc.date[0]=='2012' && doc.date[1]=='05' && doc.date[2]=='30')
       {
	emit(doc['external_id'],doc['_rev']);
    }
}