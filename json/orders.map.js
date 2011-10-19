function(doc) {
  if (doc['_id'].match('order'))
     emit(doc['_id']);
}