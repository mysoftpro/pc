function(doc) {
    var exceptions =["гарантия","кредит","доставка","руб....","возможно","недорого","гарантией.","состоянии","модель","большой","коробочке","полностью","гарантией","леонова","недорого.","продается","срочно","хорошая","хорошее"];
    if (doc.phone &&
	(doc.phone !== '') &&
        (doc.phone !== '89022506126') &&
	doc.phone.match(/\d+/g) &&
        doc.price && doc.price !=='' &&
        doc.date  &&
        doc.subj){
	var splitted = doc.subj.toLowerCase()
	    .replace('продам', '')
	    .replace('продаю', '')
	    .replace('Куплю', '')
	    .replace(/\,/g, '')
	    .replace(/\(/g, ' ')
	    .replace(/\)/g, '')
	    .split(' ');
	
	for (var i=0,l=splitted.length;i<l;i++){
	    var to_emit = splitted[i];
	    if (exceptions.indexOf(to_emit)>0)continue;
	    if (to_emit.length<=5)continue;
	    if (to_emit.charCodeAt(0)<=256)continue;
	    //.substring(0,to_emit.length-3)
	    emit(to_emit);
	}
            
    }
}