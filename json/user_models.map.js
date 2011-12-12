function(doc){
    if (doc['building']&&doc['author']){
	var price = 0;
	if (doc.items['7396'])
	    emit(1);
	// for (var key in doc['original_prices']){
	//     var p =doc['original_prices'][key];
	//     //windows
	//     if (key==='17398' || key==='14439' || key==='19843' || key==='17571' || key==='17400')
	// 	p = p/31.5;
	//     price+=p;
	// }
	// emit(doc['author'],Math.round(price*31.5/1000));
    }
}