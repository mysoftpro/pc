function getNoteClass(note_div){
    return note_div.attr('class').split(' ')[0];
}
function sortNotes(el,extractor){
    var divs = el.find('.note');
    var divs_notes = [];
    for(var i=0;i<divs.length;i++){
        var d = $(divs.get(i));
        divs_notes.push([d,notebooks[getNoteClass(d)]]);
    }
    var sorted = divs_notes.sort(function(dn1,dn2){
                                     return extractor(dn1[1],dn2[1]);
                                 });
    var mock = $(document.createElement('div')).attr('id','notesort').css('display','none');
    $('body').append(mock);

    _(sorted).each(function(dn){
                       mock.append(dn[0]);
                   });
    _(sorted).each(function(dn){
                       el.append(dn[0]);
                   });

}
function sortByClick(el, fu){
    var reversed = function(some,some1){return 0-fu(some,some1);};
    el.find('.asc').click(function(e){
                              sortNotes(el,fu);
                              el.find('.asc').attr('class','asc asca');
                              el.find('.desca').attr('class','desc');
                          });
    el.find('.desc').click(function(e){
                               sortNotes(el,reversed);
                               el.find('.asca').attr('class','asc');
                               el.find('.desc').attr('class','desc desca');
                           });
}
var notes_active;

head.ready(function(){

	       

               sortByClick($('#s_performance'), function(doc1,doc2){
			       if (doc1['performance'] && doc2['performance'])
                                   return doc1.performance-doc2.performance;
			       else
				   return doc1.price-doc2.price;
			   });
	       
	       sortByClick($('#s_price'), function(doc1,doc2){
                               return doc1.price-doc2.price;});
	       sortByClick($('#s_size'), function(doc1,doc2){
			       if (doc1['size'] && doc2['size'])
				   return doc1.size-doc2.size;
			       else
				   return doc1.price-doc2.price;
			   });
	       $('.asc').click();
               $('.note').click(function(e){
                                    e.preventDefault();
                                    if (notes_active)
                                        notes_active.attr('class',
                                                          notes_active
                                                          .attr('class')
                                                          .replace(' nactive', ''));
                                    var target = $(e.target);
                                    if (target[0].tagName.toLowerCase()=='a')
                                        target = target.parent();
                                    while (!target.attr('class').match('note')){
                                        target = target.parent();
                                    }
                                    var klass = getNoteClass(target);
                                    notes_active = $('.'+klass);
                                    notes_active.attr('class',notes_active.attr('class')+' nactive');
                                });
	       var cols = $('.notebook_column');
	       cols.first().before('<div class="npane" id="left_pane"></div>');
	       cols.last().after('<div class="npane" id="right_pane"></div>');
           });