var prcs = _($('.price').toArray());
var sz = prcs.size();
var tot = 0;
prcs.each(function(el,i){
	      var _int = parseInt($(el).text());
	      if (i!==sz-1){
		  tot+=_int*31.4;
	      }
	      else{
		  tot+=_int;
	      }
	  });
console.log(tot);
$('#promostuff td').click(function(e){
			      $('#promo_description p').hide();
			      $('td').css('color','#ddd');
			      var target = $(e.target);
			      //target.css('color','#aadd00');
			      var p = target.parent();
			      var all_td = _(p.children().toArray());
			      all_td.each(function(el){
					      if (!el.id)return;
					      $('#_'+el.id).show();
					      $(el).prev().css('color','#aadd00');
					  });
			  });
