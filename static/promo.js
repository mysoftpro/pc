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
