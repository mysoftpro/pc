function(doc) {
    if (doc.phone &&
	(doc.phone !== '') &&
        (doc.phone !== '89022506126') &&
	doc.phone.match(/\d+/g) &&
        doc.price && doc.price !=='' &&
        doc.date  &&
        doc.subj){
        emit(doc.date.concat(doc['_id']));
    }
}