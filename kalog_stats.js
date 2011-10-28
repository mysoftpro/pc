function(doc) {
  if (doc['stats'] && doc['stats'].indexOf('buiclick'))emit(null, doc['stats']);
}