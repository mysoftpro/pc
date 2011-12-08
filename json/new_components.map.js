function(doc) {
 if (doc['_id'].indexOf('ew_')>0 && !doc['map_to_wi'])
     emit(doc['_id']);
}