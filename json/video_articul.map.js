function(doc){
    function hasField(field){
        return doc[field] && doc[field]!==-1 && doc[field]!=='-1';
    }
    if (hasField('articul') &&
        hasField('catalogs') &&
        hasField('chip') &&
        hasField('stock1') &&
        hasField('year') &&
        hasField('power') &&
        hasField('cores') &&
        hasField('memory') &&
        hasField('memory_ammo') &&
        hasField('rate') &&
        hasField('marketParams') &&
        hasField('marketComments') &&
        hasField('marketReviews') &&
        doc['stock1']>0 && doc['price']>=110){
        emit(doc['articul'].replace('\t',''), doc['chip']);
    }
}