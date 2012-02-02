function(doc){
    if (doc['vendor'] &&
        doc['model'] &&
        doc['screen'] &&
        doc['memory'] &&
        doc['resolution'] &&
        doc['os']
       ){
	   var to_emit = doc['vendor']+'_'+doc['model'];
           emit(to_emit.replace(' ','_'));
    }
}