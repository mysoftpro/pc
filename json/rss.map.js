function(doc){
    if (doc['type'] && doc['type']=='blog' && doc['title']){
        emit(doc['_id'],
	     {'title':doc['title'],
	      'desc':doc['txt']
	      .replace(/&/g, "&amp;")
	      .replace(/>/g, "&gt;")
	      .replace(/</g, "&lt;").replace(/"/g, "&quot;"),
	      'date':doc['date']
	     });
    }
}
