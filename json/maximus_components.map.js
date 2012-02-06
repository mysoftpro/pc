function(doc) {
 if (doc['_id'].indexOf('ax_')>0)
     emit(doc['_id'],doc['_rev']);
}