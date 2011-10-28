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
			      left_halfes= $('#s_price .nleft.half_vertical');
			      right_halfes= $('#s_price .nright.half_vertical');
			      if(notes_active)
				  $(notes_active.first()).click();
			  });
    el.find('.desc').click(function(e){
			       sortNotes(el,reversed);
			       el.find('.asca').attr('class','asc');
			       el.find('.desc').attr('class','desc desca');
			       left_halfes= $('#s_price .nleft.half_vertical');
			       right_halfes= $('#s_price .nright.half_vertical');
			       if(notes_active)
				   $(notes_active.first()).click();
			   });
}
var notes_active;
var left_halfes;
var right_halfes;
var halfes_offset = -4;
function showArrows(){
    var left,mid,right;
    var ob = {};
    if (!left_halfes)
	left_halfes= $('#s_price .nleft.half_vertical');
    if (!right_halfes)
	right_halfes= $('#s_price .nright.half_vertical');
    left_halfes.hide();
    right_halfes.hide();
    for (var i=0;i<notes_active.length;i++){
	var div = $(notes_active.get(i));
	var parent = div.parent();
	var fill = function(parent_id, token){
	    if (parent.attr('id') !==parent_id)
		return;
	    ob[token] = {'div':div};
	    ob[token]['index'] = parent.children().index(div);
	};
	fill('s_performance', 'left');
	fill('s_price', 'mid');
	fill('s_size', 'right');
    }
    if (ob['mid']['index']<ob['left']['index']){
	for (var i=ob['mid']['index'];i<ob['left']['index'];i++)
	    $(left_halfes.get(i+halfes_offset)).show();
	}
    else{
	for (var i=ob['left']['index'];i<ob['mid']['index'];i++)
	    $(left_halfes.get(i+halfes_offset)).show();
    }
    if (ob['mid']['index']<ob['right']['index']){
	for (var i=ob['mid']['index'];i<ob['right']['index'];i++)
	    $(right_halfes.get(i+halfes_offset)).show();
	}
    else{
	for (var i=ob['right']['index'];i<ob['mid']['index'];i++)
	    $(right_halfes.get(i+halfes_offset)).show();
    }
}


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
	       var note_description = $('#note_dscription');
	       var left_pane = $('#left_pane');
	       var right_pane = $('#right_pane');
	       var notebook_to_cart = $('#notebook_to_cart');
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
				    var doc = notebooks[klass];
				    var descr = doc['description'];
				    note_description.animate({'opacity':'0.0'}, 300);
				    note_description.jScrollPaneRemove();
				    var name = '<strong>'+descr['name']+'</strong>';
				    note_description
					.html(name+'<br/>'+descr['comments']);
				    note_description.jScrollPane();
				    note_description.animate({'opacity':'1.0'}, 300);

				    left_pane.html('');
				    right_pane.html('');
				    var i=0;
				    for (var a in doc._attachments){
					if (doc._attachments[a]['content_type']=="image/jpeg"){
					    var app = function(pane){
						pane
						.append('<img width="140" src="/image/' +
							doc['_id']+'/'+a+'"/>');
					    };
					    if (i>3 && i<10)
						app(right_pane);
					    else if (i<=3 && i<10)
						app(left_pane);
					    if (i==7)break;
					    i+=1;

					}

				    }
				    notebook_to_cart.find('h2').remove();
				    var dos = '';
				    if (doc['text'].toLowerCase().match('/dos'))
					dos = '<span>ВНИМАНИЕ! НЕТ ОПЕРАЦИОННОЙ СИСТЕМЫ!</span>';
				    var _header = doc['text'];
				    _header = _header.replace('Ноутбук Asus','');
				    _header = _header.replace('Ноутбук ASUS','');
				    var _price = '<strong>'+doc['price']+'р.</strong>';
				    notebook_to_cart.append('<h2>' + _header+_price
							    +dos+'</h2>');
				    showArrows();
				});
	       $('#tocart').click(function(e){
				       $.ajax({
						  url:'savenote',
						  data:{id:getNoteClass(notes_active)},
						  success:function(data){
						      if (data =='fail'){
							  alert('Что-то пошло не так :(');
							  return;
						      }

						      var cart_el = $('#cart');
						      if (cart_el.length>0){
							  cart_el.text('Корзина('+
								       $.cookie('pc_cart')
								       +')');
						      }
						      else{
							  $('#main_menu')
							      .append(_.
								      template('<li><a id="cart" href="/cart/{{cart}}">Корзина(1)</a></li>',
									       {
												cart:$.cookie('pc_user')
											    }));
						      }
						      alert('Получилось!');
						  }
					      });
				   });
	       $('.nname').first().click();
	       // var pop = $('.popup');
	       // pop.find('h3').text('Мастер выбора ноутбуков');
	       // pop.find('p').text('В каждом из трех столбцов находятся названия моделей ноутбуков,'+
	       // 			  ' занимая соответсвующую позицию. Можно менять порядок сортировки.'+
	       // 			  ' Кликайте название в любом столбце, чтобы посмотреть описание и'+
	       // 			  ' картинки.');
	       // pop.css('top',-pop.outerHeight());
	       // $('.popup').show();
	       // $('.popup').animate({top:"0",left:"0"}, 500);
	   });