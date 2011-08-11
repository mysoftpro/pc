function htmlDecode(value){
    return $('<div/>').html(value).text();
}

$(function(){
      try{
	  var middles = $('td.comp_middle');
	  for (var i=0;i<middles.length;i++){
	      var mid = $(middles.get(i));
	      var token = mid.text();
	      var prev = mid.prev();
	      var prev_text = prev.text().replace(token, '');	      
	      prev.html(prev_text);	      
	      var opts = mid.next().find('option');
	      for (var j=0;j<opts.length;j++){
		  var opt = $(opts.get(j));
		  var opt_text = opt.text().replace(token, '');
		  opt.html(opt_text);	  		  
	      }
	  }
	  $('font').remove();
	  $('select').chosen();
      } catch (x) {
	  
      }
  });