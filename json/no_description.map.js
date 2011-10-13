function(doc){
    var cats = [];
    for (var i=0;i<doc['catalogs'].length;i++){
	cats.push(doc['catalogs'][i]['id']);
    }
    function _in(name){	
	return cats.indexOf(name)>0;
    }
    if (doc.catalogs && doc.price 
	&& doc.price>0 && doc.stock1 
	&& doc.stock1>0 && !doc['description'] &&
	(_in("7394")//ram
	|| _in("7388")//mpother
	|| _in("7399")//proc
	|| _in("7396")//video
	|| _in("7406")//hdd
	|| _in("7383")//case
	|| _in("7384")//displ
	|| _in("7387")//kbrd
	|| _in("7390")//mouse
	|| _in("7389"))//audio
       ){	
	   emit(doc['_id']);
    }
}