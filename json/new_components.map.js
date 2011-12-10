function(doc) {
 if (doc['_id'].indexOf('ew_')>0)
     emit(doc['_id']);
}