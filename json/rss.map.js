function(doc){
    if (doc['type'] && doc['type']=='blog' && doc['title']){
        emit(doc['_id'],
	     {'title':doc['title'],
	      'desc':doc['txt'].substring(0,100)
	      .replace(/&/g, "&amp;")
	      .replace(/>/g, "&gt;")
	      .replace(/</g, "&lt;").replace(/"/g, "&quot;"),
	      'date':doc['date']
	     });
    }
}
var n = new Date();n.setFullYear(value[date][0]);n.setMonth(value[date][1]);n.setDate(value[date][2]);n.setHours(0);n.setMinutes(0);n.setSeconds(0);n = n.toUTCString()