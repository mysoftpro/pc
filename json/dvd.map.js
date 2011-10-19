function(doc) {
  if (doc['catalogs'] &&
     doc['catalogs'][0]['id']=='7363' &&
     doc['catalogs'][1]['id']=='7392' &&
     doc['catalogs'][2]['id']=='7538')
     emit(doc['_id']);
}
