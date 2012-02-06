function(doc) {
 if (doc['_id'].indexOf('oh_')>0)
     emit(doc['_id']);
}