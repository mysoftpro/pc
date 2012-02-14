_.templateSettings = {
    interpolate : /\{\{(.+?)\}\}/g
    ,evaluate: /\[\[(.+?)\]\]/g
};

var dones=0;
var wits_for_new = [];
var news_for_wit = {};
function fillWit(data){
    var tr = $('#unique_wit').find('tr').first().next();
    _(data).each(function(li){
		     _(li[1]['rows']).each(function(row){
					       if (row['doc']['map_to_ne']){
						   wits_for_new
						       .push({'newid':row['doc']['map_to_ne'],
							      'doc':row['doc']});
						   return;
					       }
					       if (row['doc']['_id'].match('new_'))return;
					       var td = tr.children().first();
					       td.attr('id', row['doc']['_id']);
					       td.text(row['doc']['text']+ ' '+row['doc']['_id']+' $'+row['doc']['price']);
					       tr = tr.next();
					   });
		 });
    dones+=1;
    if (dones==2)
	init();
}
function fillNew(data){
    var tr = $('#unique_new').find('tr').first().next();
    _(data['rows']).each(function(row){
			     if (row['doc']['map_to_wi']){
				 var _id = row['doc']['_id'];
				 news_for_wit[_id] = row['doc'];
				 return;
			     }
			     var td = tr.children().last();
			     td.attr('id', row['doc']['_id']);
			     td.text(row['doc']['text']+' '+row['doc']['_id']+' $'+row['doc']['us_price']);
			     if (row['doc']['catalogs'])
				 td.css('color','green');
			     if (!row['doc']['stock1'] && !row['doc']['new_stock'])
				 td.css('color','blue');

			     tr = tr.next();
			 });
    dones+=1;
    if (dones==2)
	init();
}


function init(){
    var first_selected = $('#selected').find('tr').first();
    _(wits_for_new).each(function(ob){
			     var wi = ob['doc'];
			     var ne = news_for_wit[ob['newid']];
			     if (!ne){
				 console.log('no mapping for this!');
				 console.log(ob);
				 return;
			     }
			     var color = 'black';
			     if (ne['catalogs'])
				 color="blue";
			     first_selected.after(_.template('<tr><td id="{{witid}}">{{wittext}}</td><td style="color:{{color}}" id="{{newid}}">{{newtext}}</td><td><input type="submit" value="delete"/></td></tr>',
				      {
					  witid:wi['_id'],
					  newid:ne['_id'],
					  wittext:wi['text'],
					  newtext:ne['text'],
					  color:color
				      }));
			     first_selected.next()
				 .find('input').click(function(e){
							  $.ajax({
								     url:'delete_wit_new_map',
								     data:{
									 'wi':wi['_id'],
									 'ne':ne['_id']
										  },
								     success:function(data){
									 alert(data);
									 $(e.target)
									     .parent().parent()
									 .remove();
								     }
								 });
						      });

			 });

    $('#unique_wit').before('<div><input type="submit" id="mother" value="mother"/><input type="submit" id="video" value="video"/><input type="submit" id="proc" value="proc"/></div>');
    var wits = [];
    var news = [];
    _($('#unique_wit').find('tr')
      .toArray())
	.each(function(el){
		  var _el = $(el);
		  var wi = _el.children().first();
		  if (wi.text()=='Unique Wit')return;
		  wits.push(wi);
		  wi.next().find('input').click(function(e){
						    var old_parent = wi.parent();
						    var tr = $('#selected').find('tr').first();
						    tr.after(tr.clone());
						    tr.next().prepend(wi);
						    old_parent.remove();
						});
	      });
    _($('#unique_new').find('tr')
      .toArray())
	.each(function(el){
		  var _el = $(el);
		  var ne = _el.children().last();
		  if (ne.text()=='Unique New')return;
		  news.push(ne);
		  ne.prev().find('input').click(function(e){
						    var old_parent = ne.parent();
						    var tr = $('#selected').find('tr').first().next();
						    tr.append(ne);
						    tr.append('<td><input type="submit" name="save" value="save"/></td>');
						    tr.children()
							.last()
							.find('input')
							.click(function(e){
								   var wi = tr.children().first();
								   var ne = wi.next();
								   $.ajax({
									      url:'store_wit_new_map',
									      data:{
										  'wi':wi.attr('id'),
										  'ne':ne.attr('id')
										  },
									      success:function(data){
										  alert(data);
										  var target = $(e.target);
										  target.attr('value','delete');
										  target.unbind('click').click(function(e){
														   $.ajax({
															      url:'delete_wit_new_map',
															      data:{
																  'wi':wi.attr('id'),
																  'ne':ne.attr('id')
															      },
								     success:function(data){
									 alert(data);
									 $(e.target)
									     .parent().parent()
									     .remove();
								     }
															  });
													       });
									      }
									  });
							       });
						    old_parent.remove();
						});
	      });
    //sort wits and news by name
    // means by Ma, Про и Ви
    function so(t1,t2){
	wits.sort(function(el1,el2){
		      return el1.text().indexOf(t1) -
			  el2.text().indexOf(t2);
		  });
	news.sort(function(el1,el2){
		      return el1.text().indexOf(t2) -
			  el2.text().indexOf(t2);
		  });
	_(wits).each(function(el){
			 $('#unique_wit')
			     .children().first().prepend(el.parent());
		     });
	_(news).each(function(el){
			 $('#unique_new')
			     .children().first().prepend(el.parent());
		     });
    }
    $('#mother').click(function(e){
			   so('атеринская','ат. плата');
		       });
    $('#video').click(function(e){
			 so('идеокарта','идеокарта');
		     });
    $('#proc').click(function(e){
			  so('роцессор','роцессор');
		      });
    $('a').click(function(e){
		     e.preventDefault();
		     $(e.target).parent().parent().hide();
		 });
}

$(function(){
      var tr = $('#unique_wit').find('tr').first();
      for (var i=0;i<500;i++){
	  tr.parent().append(tr.clone());
      }
      tr = $('#unique_new').find('tr').first();
      for (var i=0;i<500;i++){
	  tr.parent().append(tr.clone());
      }
      // tr = $('#selected').find('tr').first();
      // for (var i=0;i<500;i++){
      // 	  tr.parent().append(tr.clone());
      // }

      $.ajax({
		 url:'wit_for_mapping'+document.location.search,
		 success:fillWit
	     });
      $.ajax({
		 url:'new_for_mapping'+document.location.search,
		 success:fillNew
	     });

  });