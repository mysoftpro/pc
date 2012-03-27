function(doc) {
    if(doc['catalogs'] && doc['us_price'] && doc['stock1'] && !doc['price'])  
	emit(doc['_id']);
}